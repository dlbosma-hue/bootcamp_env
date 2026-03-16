# Evaluation Memo

TO: Hospital Clinical Informatics Team
FROM: Dina Bosma-Buczynska
DATE: March 2026
SUBJECT: LLM Evaluation Results - Patient Record Summarization

---

## EXECUTIVE SUMMARY

This evaluation assessed GPT-4o-mini's ability to summarize de-identified patient records
for clinical handover use. Five custom prompts were tested covering medication preservation,
allergy retention, diagnostic accuracy, clinical tone, and polypharmacy completeness. The
automated judge initially returned 5/5 for all cases. After human review, TC2 and TC4 were
downgraded to 3/5 following identification of clinical reasoning failures the judge could
not detect. Corrected average: 4.2/5 with two critical safety flags.

---

## METHODOLOGY

Three existing benchmarks were reviewed (MedQA, MeQSum, MIMIC-III). All were rejected or
not used directly — MedQA due to contamination and saturation risk, MeQSum as too dissimilar
to clinical records, and MIMIC-III due to credentialed access requirements. Five custom
prompts were authored instead, evaluated using LLM-as-judge with structured JSON output plus
rule-based keyword checks. Both generation and judging used GPT-4o-mini (temperature 0.2 and
0 respectively). Automated scores were reviewed by the consultant and corrected where needed.

---

## RESULTS

TC1, TC3, and TC5 confirmed at 5/5. The model preserved all medications and dosages, retained
specialist terminology (EGFR status, Osimertinib), and listed all six medications and both
allergies in the complex polypharmacy case.

TC2 downgraded to 3/5 (critical flag): the model listed a Cephalosporin allergy and a
prophylactic antibiotic requirement without flagging the drug-allergy conflict. The judge
missed this because both allergy keywords were present — keyword presence is not clinical safety.

TC4 downgraded to 3/5 (critical flag): the model included a Family Contact section naming
the patient's mother despite the patient restricting further family disclosure. The judge
scored it 5/5 because the restriction text appeared — but including the disclosure alongside
the restriction does not undo the disclosure.

---

## CAVEATS AND LIMITATIONS

Five synthetic test cases are not sufficient to characterise model behaviour across clinical
specialties or edge cases. More critically, using the same model family for generation and
judging created self-grading bias in TC2 and TC4 — the judge could not detect failures it
was itself prone to making. Human review is a mandatory component of this evaluation approach,
not an optional one.

---

## RECOMMENDATION

Under these conditions, the model is adequate for low-risk summarization of straightforward
single-diagnosis records. It is not recommended for unsupervised use on records involving
drug interactions or psychiatric confidentiality until conflict-checking and mandatory human
review are added. Confidence level: medium. A minimum of 30 cases with a cross-model judge
would be needed before a production deployment decision.

---

## ADDITIONAL METRICS

10 API calls total. ~5,331 tokens. Estimated cost: $0.0016 USD. Average time per case:
6.08 seconds. Full run: 30.38 seconds.
