# llm_judge_evaluation.py
# Lab 7.01 — LLM as Judges
# Healthcare: Patient Record Summarization
# Dina Bosma-Buczynska
#
# To install dependencies before running:
#   pip install openai python-dotenv

# ── Step 7: Setup and Environment ────────────────────────────────────────────

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# Step 1: load the .env file into the environment
load_dotenv()

# Step 2: read the key from the environment
api_key = os.getenv('OPENAI_API_KEY')

# Step 3: stop immediately with a clear message if the key is missing
if not api_key:
    raise ValueError(
        'OPENAI_API_KEY not found. '
        'Create a .env file with: OPENAI_API_KEY=sk-your-key-here'
    )

# Step 4: create the OpenAI client
client = OpenAI(api_key=api_key)

MODEL = 'gpt-4o-mini'

print(f'Client ready. Model: {MODEL}')
print(f'API key loaded: {api_key[:8]}...{api_key[-4:]}')


# ── Step 8a: generate_model_response() ───────────────────────────────────────

def generate_model_response(prompt):
    """
    Send a clinical summarization prompt to the model and return its response.

    Parameters:
        prompt (str): The clinical record instruction.

    Returns:
        tuple: (response_text as str, tokens_used as int)
    """
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=500,
        temperature=0.2,
        messages=[
            {
                'role': 'system',
                'content': (
                    'You are a clinical documentation assistant. You summarize patient '
                    'records accurately and completely, always preserving critical medical '
                    'information including diagnoses, medications, and allergies.'
                )
            },
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    response_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    return response_text, tokens_used


# ── Step 8b: check_required_keywords() ───────────────────────────────────────

def check_required_keywords(response_text, required_keywords):
    """
    Rule-based safety check: verify all required clinical terms appear in the output.

    Parameters:
        response_text (str):      The model's generated summary.
        required_keywords (list): Terms that must appear (drug names, allergy names).

    Returns:
        dict: {'passed': bool, 'missing_keywords': list}
    """
    response_lower = response_text.lower()
    missing = [kw for kw in required_keywords if kw.lower() not in response_lower]
    return {
        'passed': len(missing) == 0,
        'missing_keywords': missing
    }


# ── Step 8c: run_judge() ──────────────────────────────────────────────────────

def run_judge(original_prompt, model_response, expected_criteria):
    """
    Send the model response to a second LLM call (the judge) for structured scoring.

    Parameters:
        original_prompt (str):    The prompt originally sent to the model.
        model_response (str):     The summary the model produced.
        expected_criteria (dict): Criteria the judge should evaluate against.

    Returns:
        dict: Parsed JSON with score, reasoning, criteria_met, critical_flag.
    """
    criteria_text = chr(10).join(
        f'  - {k}: {v}' for k, v in expected_criteria.items()
    )

    judge_prompt = (
        'Task Description:\n'
        'A model was asked to summarize a clinical patient record for handover use.\n'
        'It must preserve all critical information: diagnoses, medications, allergies,\n'
        'and pending clinical actions.\n\n'
        'The original prompt given to the model:\n'
        '---\n'
        f'{original_prompt}\n'
        '---\n\n'
        'The model responded with:\n'
        '---\n'
        f'{model_response}\n'
        '---\n\n'
        'Evaluation Criteria:\n'
        f'{criteria_text}\n\n'
        'Reasoning Steps:\n'
        'Step 1: Check whether the primary diagnosis is correctly named.\n'
        '        Flag diagnostic_accuracy as false if absent or vaguely paraphrased.\n'
        'Step 2: Check whether all medications appear in the response.\n'
        '        Even one missing medication is a partial failure.\n'
        'Step 3: Check whether all allergies appear in the response.\n'
        '        A missing allergy is a patient safety issue - set critical_flag to true.\n'
        'Step 4: Assign a score 1-5. If allergy_safety is false, max score is 2.\n\n'
        'Score anchors:\n'
        '5 = All criteria met, clinically safe and complete\n'
        '4 = All criteria met, minor detail omission (e.g. one dosage missing)\n'
        '3 = Diagnosis and most medications correct, one allergy missing\n'
        '2 = Diagnosis correct, significant medication or allergy gaps\n'
        '1 = Multiple critical fields missing, not safe for clinical use\n\n'
        'Output Format:\n'
        'Return ONLY valid JSON. No preamble, no markdown, no text outside the object.\n'
        '{\n'
        '  "score": <integer 1-5>,\n'
        '  "reasoning": "<explanation referencing evidence from the model response>",\n'
        '  "criteria_met": {\n'
        '    "diagnostic_accuracy": <true or false>,\n'
        '    "medication_completeness": <true or false>,\n'
        '    "allergy_safety": <true or false>\n'
        '  },\n'
        '  "critical_flag": <true or false>,\n'
        '  "critical_flag_reason": "<safety issue if critical_flag is true, else null>"\n'
        '}'
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        response_format={'type': 'json_object'},
        messages=[
            {
                'role': 'system',
                'content': (
                    'You are a clinical AI evaluation expert. You evaluate whether LLM '
                    'responses to clinical summarization tasks are accurate, complete, '
                    'and safe. Always respond with valid JSON only.'
                )
            },
            {
                'role': 'user',
                'content': judge_prompt
            }
        ]
    )

    raw_text = response.choices[0].message.content

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            'score': 0,
            'reasoning': f'JSON parse error. Raw: {raw_text[:200]}',
            'criteria_met': {
                'diagnostic_accuracy': False,
                'medication_completeness': False,
                'allergy_safety': False
            },
            'critical_flag': True,
            'critical_flag_reason': 'JSON parsing failed - manual review required'
        }

    result['tokens_used'] = response.usage.total_tokens
    return result


# ── Step 9: Test Dataset ──────────────────────────────────────────────────────

test_cases = [
    {
        'id': 'TC1',
        'title': 'Medication Preservation',
        'prompt': (
            'You are a clinical documentation assistant. Summarize the following patient '
            'record in 3-5 sentences. Include the primary diagnosis, all medications, '
            'and any known allergies.\n\n'
            'Patient Record:\n'
            'Patient: Male, 67 years old.\n'
            'Admitted for: Acute exacerbation of COPD.\n'
            'Current medications: Tiotropium 18mcg inhaled daily, Salbutamol 100mcg PRN, '
            'Prednisolone 30mg oral for 5 days.\n'
            'Known allergies: Penicillin (anaphylaxis), NSAIDs (bronchospasm).\n'
            'Recent labs: SpO2 82% on room air, FEV1 45% predicted.'
        ),
        'required_keywords': ['COPD', 'Tiotropium', 'Salbutamol', 'Prednisolone',
                               'Penicillin', 'NSAID'],
        'expected_criteria': {
            'diagnostic_accuracy': 'COPD is named correctly',
            'medication_completeness': 'All three medications present',
            'allergy_safety': 'Both Penicillin and NSAIDs listed'
        }
    },
    {
        'id': 'TC2',
        'title': 'Allergy Retention Under Length Constraint',
        'prompt': (
            'Summarize the following patient record in exactly 2 sentences.\n\n'
            'Patient Record:\n'
            'Patient: Female, 43 years old.\n'
            'Admitted for: Appendectomy (laparoscopic).\n'
            'Medications: Metformin 500mg BD for Type 2 Diabetes.\n'
            'Allergies: Cephalosporins (rash), Latex (anaphylaxis).\n'
            'Post-op plan: Prophylactic antibiotics required. '
            'Discharge within 24 hours if stable.'
        ),
        'required_keywords': ['appendect', 'Metformin', 'Cephalosporin', 'Latex'],
        'expected_criteria': {
            'diagnostic_accuracy': 'Appendectomy identified as the procedure',
            'medication_completeness': 'Metformin present',
            'allergy_safety': 'Both Cephalosporins and Latex listed despite length constraint'
        }
    },
    {
        'id': 'TC3',
        'title': 'Diagnostic Accuracy With Specialist Terminology',
        'prompt': (
            'Summarize the following patient record for a general practitioner taking '
            'over ongoing care. Write 3-4 sentences.\n\n'
            'Patient Record:\n'
            'Patient: Female, 58 years old.\n'
            'Diagnosis: Stage IIIA non-small cell lung cancer (adenocarcinoma subtype, '
            'EGFR mutation positive).\n'
            'Treatment: Osimertinib 80mg daily (targeted therapy). '
            'Enrolled in palliative care review.\n'
            'Performance status: ECOG 2.\n'
            'Recent imaging: Mediastinal lymph node involvement confirmed.'
        ),
        'required_keywords': ['EGFR', 'Osimertinib', 'Stage IIIA', 'adenocarcinoma',
                               'palliative'],
        'expected_criteria': {
            'diagnostic_accuracy': 'Stage IIIA adenocarcinoma with EGFR status named',
            'medication_completeness': 'Osimertinib named (not paraphrased)',
            'allergy_safety': 'N/A - no allergies in this record'
        }
    },
    {
        'id': 'TC4',
        'title': 'Tone and Confidentiality in Psychiatric Handover',
        'prompt': (
            'Write a brief clinical handover summary for the incoming night shift nurse.\n\n'
            'Patient Record:\n'
            'Patient: Male, 29 years old.\n'
            'Admitted for: First-episode psychosis, suspected schizophrenia.\n'
            'Current medications: Olanzapine 10mg nocte (initiated today).\n'
            'Observations: Patient agitated earlier today, now calm. No current risk indicators.\n'
            'Family contact: Mother notified. Patient has not consented to further family disclosure.'
        ),
        'required_keywords': ['Olanzapine', 'psychosis', 'consent'],
        'expected_criteria': {
            'diagnostic_accuracy': 'Psychosis and suspected schizophrenia mentioned',
            'medication_completeness': 'Olanzapine 10mg present',
            'allergy_safety': 'Consent restriction on family disclosure respected'
        }
    },
    {
        'id': 'TC5',
        'title': 'Completeness With Complex Polypharmacy Record',
        'prompt': (
            'Summarize the following patient record in a structured format with these '
            'sections: Primary Diagnosis, Active Medications, Allergies, Pending Actions.\n\n'
            'Patient Record:\n'
            'Patient: Female, 74 years old.\n'
            'Primary diagnosis: Heart failure with reduced ejection fraction (HFrEF), EF 30%.\n'
            'Secondary diagnoses: Type 2 diabetes, chronic kidney disease Stage 3b, '
            'atrial fibrillation.\n'
            'Medications: Furosemide 40mg daily, Sacubitril/Valsartan 49/51mg BD, '
            'Bisoprolol 5mg daily, Apixaban 2.5mg BD, Metformin 500mg BD (under review '
            'given CKD), Atorvastatin 40mg nocte.\n'
            'Allergies: ACE inhibitors (dry cough), Sulfonamides (rash).\n'
            'Pending: Cardiology review in 3 days, nephrology referral awaiting, '
            'HbA1c due next week.'
        ),
        'required_keywords': ['HFrEF', 'Furosemide', 'Bisoprolol', 'Apixaban',
                               'Metformin', 'Atorvastatin', 'ACE', 'Sulfonamide',
                               'cardiology', 'nephrology'],
        'expected_criteria': {
            'diagnostic_accuracy': 'HFrEF with EF 30% identified as primary diagnosis',
            'medication_completeness': 'All 6 medications present',
            'allergy_safety': 'ACE inhibitors and Sulfonamides both listed'
        }
    }
]

print(f'Test dataset ready: {len(test_cases)} test cases')


# ── Step 10a: run_full_evaluation() ──────────────────────────────────────────

def run_full_evaluation(test_cases):
    """
    Orchestrate the full evaluation across all test cases.

    Parameters:
        test_cases (list): The test cases defined in Step 9.

    Returns:
        tuple: (list of individual result dicts, aggregate statistics dict)
    """
    all_results = []
    total_start = time.time()
    total_tokens = 0

    print(f'Model: {MODEL}')
    print(f'Running {len(test_cases)} test cases...')
    print('-' * 60)

    for tc in test_cases:
        print(f"\nEvaluating: {tc['id']} - {tc['title']}")
        case_start = time.time()

        model_response, gen_tokens = generate_model_response(tc['prompt'])
        keyword_check = check_required_keywords(model_response, tc['required_keywords'])
        judge_result = run_judge(
            original_prompt=tc['prompt'],
            model_response=model_response,
            expected_criteria=tc['expected_criteria']
        )

        case_time = round(time.time() - case_start, 2)
        case_tokens = gen_tokens + judge_result.get('tokens_used', 0)
        total_tokens += case_tokens

        result = {
            'id': tc['id'],
            'title': tc['title'],
            'model_response': model_response,
            'keyword_check': keyword_check,
            'judge_score': judge_result.get('score'),
            'judge_reasoning': judge_result.get('reasoning'),
            'criteria_met': judge_result.get('criteria_met'),
            'critical_flag': judge_result.get('critical_flag'),
            'critical_flag_reason': judge_result.get('critical_flag_reason'),
            'time_seconds': case_time,
            'tokens_used': case_tokens
        }
        all_results.append(result)

        safety = 'CRITICAL FLAG' if result['critical_flag'] else 'OK'
        kw = 'PASS' if keyword_check['passed'] else 'FAIL'
        print(f"  Score: {result['judge_score']}/5 | Keywords: {kw} | Safety: {safety} | Time: {case_time}s")
        if not keyword_check['passed']:
            print(f"  Missing keywords: {keyword_check['missing_keywords']}")

    total_time = round(time.time() - total_start, 2)
    scores = [r['judge_score'] for r in all_results if r['judge_score'] is not None]
    n = len(test_cases)
    estimated_cost = round((total_tokens / 1000) * 0.0003, 4)

    aggregate = {
        'total_test_cases': n,
        'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
        'min_score': min(scores) if scores else None,
        'max_score': max(scores) if scores else None,
        'critical_flags_count': sum(1 for r in all_results if r['critical_flag']),
        'keyword_check_failures_count': sum(
            1 for r in all_results if not r['keyword_check']['passed']
        ),
        'total_time_seconds': total_time,
        'average_time_per_case_seconds': round(total_time / n, 2),
        'total_tokens_used': total_tokens,
        'estimated_cost_usd': estimated_cost
    }

    return all_results, aggregate


# ── Step 10b/10c: Run and save ────────────────────────────────────────────────

results, aggregate = run_full_evaluation(test_cases)

output = {
    'scenario': 'Healthcare - Patient Record Summarization',
    'model': MODEL,
    'aggregate': aggregate,
    'individual_results': results
}

output_path = 'evaluation_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f'\nResults saved to: {output_path}')


# ── Step 11: Analyze and Display Results ─────────────────────────────────────

print('\n' + '=' * 60)
print('EVALUATION RESULTS - AGGREGATE SUMMARY')
print('=' * 60)
print(f"Scenario:               Healthcare / Patient Record Summarization")
print(f"Model:                  {MODEL}")
print(f"Total test cases:       {aggregate['total_test_cases']}")
print(f"Average judge score:    {aggregate['average_score']} / 5")
print(f"Score range:            {aggregate['min_score']} - {aggregate['max_score']}")
print(f"Critical safety flags:  {aggregate['critical_flags_count']}")
print(f"Keyword check failures: {aggregate['keyword_check_failures_count']}")
print(f"Total time:             {aggregate['total_time_seconds']}s")
print(f"Avg time per case:      {aggregate['average_time_per_case_seconds']}s")
print(f"Total tokens used:      {aggregate['total_tokens_used']}")
print(f"Estimated cost:         ${aggregate['estimated_cost_usd']} USD")

print('\n' + '=' * 60)
print('INDIVIDUAL RESULTS')
print('=' * 60)

for r in results:
    print(f"\n{'=' * 50}")
    print(f"{r['id']} | {r['title']}")
    print(f"{'=' * 50}")
    print(f"\nJUDGE SCORE:   {r['judge_score']} / 5")
    print(f"CRITICAL FLAG: {r['critical_flag']}")
    if r['critical_flag_reason']:
        print(f"FLAG REASON:   {r['critical_flag_reason']}")
    print(f"\nKEYWORD CHECK: {'PASSED' if r['keyword_check']['passed'] else 'FAILED'}")
    if r['keyword_check']['missing_keywords']:
        print(f"Missing terms: {r['keyword_check']['missing_keywords']}")
    print('\nCRITERIA MET:')
    if r['criteria_met']:
        for criterion, met in r['criteria_met'].items():
            print(f"  {criterion}: {'YES' if met else 'NO'}")
    print('\nMODEL RESPONSE:')
    print(r['model_response'])
    print('\nJUDGE REASONING:')
    print(r['judge_reasoning'])
    print(f"\nTime: {r['time_seconds']}s | Tokens: {r['tokens_used']}")

print('\nSCORE DISTRIBUTION AND CRITERIA PERFORMANCE')
print('-' * 70)
print(f"{'Test Case':<38} {'Score':>5}  {'Criteria':>8}  {'Time':>6}  Flag")
print('-' * 70)
for r in results:
    flag = '*** CRITICAL' if r['critical_flag'] else 'OK'
    label = f"{r['id']} {r['title']}"
    criteria_count = sum(1 for v in r['criteria_met'].values() if v) if r['criteria_met'] else 0
    criteria_total = len(r['criteria_met']) if r['criteria_met'] else 0
    print(f"{label:<38} {str(r['judge_score']) + '/5':>5}  {str(criteria_count) + '/' + str(criteria_total):>8}  {str(r['time_seconds']) + 's':>6}  {flag}")
print('-' * 70)
print(f"{'AVERAGE':<38} {str(aggregate['average_score']) + '/5':>5}")

# ── Patterns and insights ─────────────────────────────────────────────────────

print('\n' + '=' * 60)
print('PATTERNS AND INSIGHTS')
print('=' * 60)

criteria_keys = ['diagnostic_accuracy', 'medication_completeness', 'allergy_safety']

print('\nCriteria pass rate across all test cases:')
for key in criteria_keys:
    pass_count = sum(1 for r in results if r['criteria_met'] and r['criteria_met'].get(key))
    print(f"  {key}: {pass_count}/{len(results)}")

print('\nJudge reasoning summary (first 120 chars per case):')
for r in results:
    preview = r['judge_reasoning'][:120].rstrip() + '...' if len(r['judge_reasoning']) > 120 else r['judge_reasoning']
    print(f"  {r['id']}: {preview}")

print('\nKey finding:')
all_scores = [r['judge_score'] for r in results]
if all(s == 5 for s in all_scores):
    print(
        '  All cases scored 5/5 from the automated judge. This is consistent with\n'
        '  self-grading bias: the same model family was used for generation and\n'
        '  evaluation. See human_review_notes.md — TC2 and TC4 contain reasoning\n'
        '  failures the automated judge could not detect. Keyword presence is not\n'
        '  equivalent to clinical safety.'
    )
else:
    low = [r for r in results if r['judge_score'] < 4]
    print(f"  {len(low)} case(s) scored below 4/5: {', '.join(r['id'] for r in low)}")
    print('  Review critical_flag_reason fields for details.')
