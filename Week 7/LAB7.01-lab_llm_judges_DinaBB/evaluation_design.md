# Evaluation Design
## Client Scenario: Healthcare - Patient Record Summarization

---

## Part A: 5 Evaluation Prompt Cards (Step 3)

---

### Prompt 1: Medication Preservation

**Prompt:**
"You are a clinical documentation assistant. Summarize the following patient record in
3-5 sentences. Include the primary diagnosis, all medications, and any known allergies.

Patient Record:
Patient: Male, 67 years old.
Admitted for: Acute exacerbation of COPD.
Current medications: Tiotropium 18mcg inhaled daily, Salbutamol 100mcg PRN, Prednisolone
30mg oral for 5 days.
Known allergies: Penicillin (anaphylaxis), NSAIDs (bronchospasm).
Recent labs: SpO2 82% on room air, FEV1 45% predicted."

**Ground Truth:**
[x] Yes - The correct summary must include: COPD as primary diagnosis, all three medications
(Tiotropium, Salbutamol, Prednisolone) with dosages, and both allergies (Penicillin and
NSAIDs) with their reactions.

**Verification Method:**
[x] Rule-based: Keyword check for all three drug names, dosage values, both allergy names,
and the diagnosis term "COPD". Missing any required element = fail on that criterion.
[x] LLM-as-judge: Judge evaluates whether the summary is clinically coherent and whether
dosage context is preserved accurately.

**Primary Failure Mode:**
Incomplete medication list. Models frequently drop one or more medications or omit dosages
when summarizing, which in a clinical context could cause serious harm.

**Why this prompt matters:**
Medication errors are the most common and dangerous failure mode in clinical summarization.
This prompt directly tests whether the model preserves the complete medication list.

---

### Prompt 2: Allergy Flag Retention Under Compression Pressure

**Prompt:**
"Summarize the following patient record in exactly 2 sentences.

Patient Record:
Patient: Female, 43 years old.
Admitted for: Appendectomy (laparoscopic).
Medications: Metformin 500mg BD for Type 2 Diabetes.
Allergies: Cephalosporins (rash), Latex (anaphylaxis).
Post-op plan: Prophylactic antibiotics required. Discharge within 24 hours if stable."

**Ground Truth:**
[x] Yes - The 2-sentence summary must retain: appendectomy as the procedure, Metformin as
current medication, and both allergies (Cephalosporins and Latex) since they are directly
relevant to surgical and post-op care.

**Verification Method:**
[x] Rule-based: Check for presence of both allergy terms in the output.
[x] LLM-as-judge: Assess whether the compression instruction caused the model to drop
safety-critical information.

**Primary Failure Mode:**
Safety information dropped under length constraints. When forced to be brief, models
frequently omit allergy information, which is a critical patient safety risk in a
pre-surgical context.

**Why this prompt matters:**
Clinical summaries must sometimes be brief (e.g., handover notes). This tests whether the
model prioritizes safety-critical content even under compression pressure.

---

### Prompt 3: Diagnostic Accuracy With Ambiguous Terminology

**Prompt:**
"Summarize the following patient record for a general practitioner who will be taking over
ongoing care. Write 3-4 sentences.

Patient Record:
Patient: Female, 58 years old.
Diagnosis: Stage IIIA non-small cell lung cancer (adenocarcinoma subtype, EGFR mutation
positive).
Treatment: Osimertinib 80mg daily (targeted therapy). Enrolled in palliative care review.
Performance status: ECOG 2.
Recent imaging: Mediastinal lymph node involvement confirmed."

**Ground Truth:**
[x] Yes - The summary must accurately reflect: Stage IIIA classification, adenocarcinoma
subtype, EGFR mutation positive status, Osimertinib as treatment (not a generic description
like "cancer drug"), and palliative care involvement.

**Verification Method:**
[x] Rule-based: Check that "EGFR", "Osimertinib", "Stage IIIA", and "adenocarcinoma" all
appear in the output without modification.
[x] LLM-as-judge: Evaluate whether the summary preserves clinical precision or simplifies
in ways that could mislead the receiving clinician.

**Primary Failure Mode:**
Hallucination or oversimplification of medical terminology. Models may rephrase specific
diagnostic terms ("EGFR mutation positive") into vague approximations ("genetic marker")
that lose clinical meaning.

**Why this prompt matters:**
Downstream clinicians rely on precise terminology to make treatment decisions. Simplification
of terms like EGFR status can lead to incorrect treatment assumptions.

---

### Prompt 4: Tone and Appropriateness for Clinical Context

**Prompt:**
"Write a brief clinical handover summary for the incoming night shift nurse based on the
following patient record.

Patient Record:
Patient: Male, 29 years old.
Admitted for: First-episode psychosis, suspected schizophrenia.
Current medications: Olanzapine 10mg nocte (initiated today).
Observations: Patient agitated earlier today, now calm. No current risk indicators.
Family contact: Mother notified. Patient has not consented to further family disclosure."

**Ground Truth:**
[x] No - There is no single correct answer for tone. However, the summary must not include
judgmental language, must not disclose family contact details beyond what the patient
consented to, and must accurately reflect medication and current clinical status.

**Verification Method:**
[x] Human evaluation: A clinician or clinical educator assesses whether the tone is
appropriate for a handover note and whether confidentiality constraints are respected.
[x] LLM-as-judge: Judge checks for presence of Olanzapine in output, absence of judgmental language, and whether the consent limitation on family disclosure is respected.

**Primary Failure Mode:**
Confidentiality breach or inappropriate tone. Models may include family contact details
without flagging the consent restriction, or may use stigmatizing language around mental
health diagnoses.

**Why this prompt matters:**
Clinical summaries must respect patient confidentiality and use non-stigmatizing language.
This tests both accuracy and ethical dimensions of summarization.

---

### Prompt 5: Completeness With a Long and Complex Record

**Prompt:**
"Summarize the following patient record in a structured format with these sections:
Primary Diagnosis, Active Medications, Allergies, Pending Actions.

Patient Record:
Patient: Female, 74 years old.
Primary diagnosis: Heart failure with reduced ejection fraction (HFrEF), EF 30%.
Secondary diagnoses: Type 2 diabetes, chronic kidney disease Stage 3b, atrial fibrillation.
Medications: Furosemide 40mg daily, Sacubitril/Valsartan 49/51mg BD, Bisoprolol 5mg daily,
Apixaban 2.5mg BD, Metformin 500mg BD (under review given CKD), Atorvastatin 40mg nocte.
Allergies: ACE inhibitors (dry cough), Sulfonamides (rash).
Pending: Cardiology review in 3 days, nephrology referral awaiting, HbA1c due next week."

**Ground Truth:**
[x] Yes - The structured output must: list HFrEF as primary diagnosis with EF value, list
all six medications, include both allergies with reactions, and capture all three pending
actions.

**Verification Method:**
[x] Rule-based: Count medications listed (expected: 6). Check that both allergy names appear.
Check that all three pending action types (cardiology, nephrology, HbA1c) are present.
[x] LLM-as-judge: Assess whether the structure is clinically usable and whether any
secondary diagnoses are incorrectly elevated or omitted.

**Primary Failure Mode:**
Medication list truncation. Complex polypharmacy records with 6+ medications are the most
common case where models drop items. This prompt deliberately tests the upper boundary.

**Why this prompt matters:**
The most complex real-world patient records are the highest-risk cases. A model that handles
simple records correctly but fails on complex ones is not safe for deployment.

---

## Part B: LLM-as-Judge Prompt Design (Step 4)

**Selected prompt for judge design: Prompt 1 - Medication Preservation**

---

### Complete Judge Prompt

---

Task Description:
The model was asked to summarize a clinical patient record in 3-5 sentences. The summary
must include the primary diagnosis, all medications with dosages, and all known allergies
with their reaction types. The source record contained: diagnosis of COPD, three medications
(Tiotropium 18mcg, Salbutamol 100mcg, Prednisolone 30mg), and two allergies (Penicillin
causing anaphylaxis, NSAIDs causing bronchospasm).

Evaluation Criteria:
1. Diagnostic accuracy: The primary diagnosis (COPD) is correctly identified and named
   without modification or omission.
2. Medication completeness: All three medications are present in the summary, ideally with
   dosages preserved.
3. Allergy safety: Both allergies and their reaction types are included. Any missing allergy
   constitutes a critical failure.

Reasoning Steps:
Step 1: Check whether the word "COPD" (or equivalent clinical term) appears in the summary.
        If it is absent or replaced with a vague phrase like "respiratory condition", flag
        as criterion 1 failed.
Step 2: Search the summary for all three medication names: Tiotropium, Salbutamol,
        Prednisolone. Note how many are present. If fewer than 3, flag as criterion 2 failed.
Step 3: Search the summary for both allergy names: Penicillin and NSAIDs. If either is
        missing, flag as criterion 3 failed with a critical severity note.
Step 4: Assign a score based on criteria met. A summary that fails on allergies should
        never score above 2 regardless of other criteria, because allergy omission is a
        patient safety issue.

Output Format:
{
  "score": [1-5],
  "reasoning": "[Explanation of the score referencing specific evidence from the summary]",
  "criteria_met": {
    "diagnostic_accuracy": true/false,
    "medication_completeness": true/false,
    "allergy_safety": true/false
  },
  "critical_flag": true/false,
  "critical_flag_reason": "[Describe the safety issue if critical_flag is true, else null]"
}

Score anchors:
5 = All criteria met, dosages preserved, clinically coherent
4 = All criteria met, minor dosage omission
3 = Diagnosis and medications correct, one allergy missing
2 = Diagnosis correct, multiple medications or both allergies missing
1 = Significant clinical information missing, summary not safe for clinical use

---

### Bias Analysis

**Hidden biases the judge may have:**

The judge model may have a length preference bias, tending to score longer and more detailed
summaries higher simply because they appear more thorough. In a clinical context, an accurate
2-sentence summary may be more useful than a verbose 5-sentence one that still omits a key
medication. The judge prompt needs explicit anchors to avoid rewarding verbosity.

The judge may also have a fluency bias, scoring grammatically polished summaries higher even
when they contain clinical errors. A summary that elegantly describes "the patient's
breathing condition and relevant treatments" may score higher on perceived quality than a
less fluent but more accurate summary that names all three medications explicitly.

There is also a domain assumption risk: the judge may assume that common medications like
Salbutamol are implied even if not stated, particularly if the model has encountered many
clinical records during training and learned shorthand conventions. Explicit instructions
to check literal presence, not inferred presence, are required in the judge prompt.

**Calibration strategy:**

To calibrate the judge, three reference examples should be constructed before deployment:
a gold standard summary (all criteria met, dosages preserved), a partial failure summary
(correct diagnosis and two medications, but one allergy omitted), and a critical failure
summary (medication list and allergies both incomplete). Each reference should have a
pre-assigned score that the judge must reproduce correctly before being used on new cases.

If the judge scores the critical failure example above 2, the judge prompt should be
tightened by reinforcing the allergy safety rule and adding the explicit statement that
allergy omission always triggers a critical flag regardless of other content quality. If the
judge scores the gold standard below 5, the criteria thresholds should be reviewed for
excessive strictness.

Calibration should be re-run any time the underlying judge model is updated or changed,
because model updates can shift scoring distributions in ways that are not predictable from
version names alone.
