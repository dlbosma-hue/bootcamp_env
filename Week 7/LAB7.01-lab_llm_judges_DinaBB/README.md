# Lab: LLM as Judges
## Student: Dina Bosma

---

## Chosen Scenario

Option B: Healthcare

A hospital wants to use an LLM to automatically summarize patient records. Summaries must
preserve all critical medical information including diagnoses, medications, allergies, and
treatment plans. Key concerns are accuracy, completeness, and medical terminology.

---

## Approach

The lab is divided into two parts:

Part 1 (written deliverables) covers a benchmark audit of three existing benchmarks
(MedQA, MeQSum, MIMIC-III), five custom evaluation prompts designed for this specific
clinical use case, a complete LLM-as-judge prompt with bias analysis, a client evaluation
memo, and reflection responses.

Part 2 (implementation) is a Python script that runs a complete evaluation pipeline:
generating model responses, running rule-based keyword checks, running an LLM judge, and
collecting metrics including score, time, token usage, and estimated cost.

---

## Files

| File | Description |
|---|---|
| benchmark_audit.md | Three evaluated benchmark cards (Step 2) |
| evaluation_design.md | Five prompt cards and judge prompt (Steps 3-4) |
| evaluation_memo.md | One-page client memo (Step 5) |
| reflection.md | Reflection on evaluation design (Step 6) |
| llm_judge_evaluation.ipynb | Complete evaluation pipeline as a Jupyter notebook (Steps 7-11) |
| evaluation_results.json | Results output from running the pipeline (includes human-reviewed corrections for TC2 and TC4) |
| human_review_notes.md | Standalone record of human review findings — explains why TC2 and TC4 were downgraded |
| implementation_summary.md | Written summary of the implementation and findings |
| README.md | This file |

---

## How to Run the Code

1. Make sure you have Python 3.8 or newer installed.

2. Install dependencies:
   pip install openai python-dotenv

3. Create a .env file in this folder with your OpenAI API key:
   OPENAI_API_KEY=sk-your-key-here

4. Open and run the notebook:
   jupyter notebook llm_judge_evaluation.ipynb

   Or if you prefer to run it as a script, you can export the notebook first:
   jupyter nbconvert --to script llm_judge_evaluation.ipynb && python llm_judge_evaluation.py

5. Results are saved to evaluation_results.json and printed to the terminal.

Note: The script uses gpt-4o-mini for both generation and judging. A full evaluation run
of 5 test cases costs approximately $0.01-0.02 USD in API credits.

---

## Dependencies

- openai
- python-dotenv
- jupyter (if running as notebook)

---

## Note on Evaluation Results

The automated LLM judge initially returned 5/5 for all five test cases. After human review,
TC2 and TC4 were downgraded to 3/5 with critical flags. Both cases passed keyword checks
but contained clinical reasoning failures the judge could not detect because it shares the
same blind spots as the model it was evaluating (self-grading bias). See implementation_summary.md
for a full explanation.
