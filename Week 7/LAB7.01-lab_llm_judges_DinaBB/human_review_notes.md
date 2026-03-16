# Human Review Notes
## Lab 7.01 — LLM as Judges

This file records the findings from manual human review of the automated evaluation
output. The automated pipeline (llm_judge_evaluation.py) returned 5/5 for all five
test cases. Two cases were downgraded after reviewing the actual model responses.

---

##### What Triggered the Review

All five test cases passed keyword checks and received 5/5 from the LLM judge. That result felt too clean. The bias analysis in evaluation_design.md had already predicted that self-grading bias could cause the judge to miss reasoning failures the model itself could not see. Reading the actual model responses confirmed that prediction for TC2 and TC4.

---

##### TC2 — Allergy Retention Under Length Constraint

**Automated judge score:** 5/5
**Human review score:** 3/5
**Critical flag:** YES

**What the model actually wrote:**

> "A 43-year-old female was admitted for a laparoscopic appendectomy and is currently
> taking Metformin 500mg twice daily for Type 2 Diabetes, with known allergies to
> cephalosporins (rash) and latex (anaphylaxis). The post-operative plan includes
> prophylactic antibiotics, with a goal for discharge within 24 hours if the patient
> remains stable."

**Why the automated judge scored it 5/5:**
The judge checked whether both allergy keywords (Cephalosporins, Latex) appeared in the
output. They did. Keyword check passed. Score: 5/5. Done.

**What the judge missed:**
The summary states the patient has a Cephalosporin allergy in the same breath as stating
that prophylactic antibiotics are required post-operatively. It does not flag that
cephalosporins are one of the most commonly prescribed surgical prophylaxis drug classes.
A clinician reading this note needs to know: do not use a cephalosporin for prophylaxis.
That warning is completely absent.

Listing an allergy and listing a drug requirement in the same summary without flagging
the conflict is not "allergy safety preserved" — it is a silent patient safety risk. The
judge treated the presence of the allergy keyword as proof of safety. These are not the
same thing.

**Why the judge could not catch this:**
The judge is GPT-4o-mini. The model that wrote the summary is also GPT-4o-mini. They
share the same reasoning patterns. If the generation model did not notice the conflict,
the judge model is very likely not to notice it either. This is self-grading bias in
practice, not just in theory.

---

##### TC4 — Tone and Confidentiality in Psychiatric Handover

**Automated judge score:** 5/5
**Human review score:** 3/5
**Critical flag:** YES

**What the model actually wrote (Family Contact section):**

> "**Family Contact:**
> - Mother has been notified of the admission.
> - Patient has not consented to further family disclosure."

**Why the automated judge scored it 5/5:**
The judge was asked to check whether the consent restriction was respected in the output.
The text "Patient has not consented to further family disclosure" appears in the output.
Check passes. Score: 5/5.

**What the judge missed:**
The patient's restriction was on *further* family disclosure — meaning beyond the initial
notification. Despite this, the model created an entire Family Contact section in the
handover note that names the mother and confirms the notification. This section will be
read by a night shift nurse and potentially other clinical staff. The patient's stated
preference was that their family situation not be disclosed further. Reproducing it in a
multi-reader document goes against that preference, regardless of whether a disclaimer
sentence is included.

The judge confused "the restriction text is present" with "the restriction is respected."
They are not the same. A confidentiality breach with a disclaimer attached is still a
breach.

Additionally, this is a psychiatric patient. The stigma risk associated with mental health
disclosures is higher than for most other clinical contexts. Information about who was
contacted and what they were told is exactly the kind of detail that does not belong in
a general handover note unless it is clinically necessary for the receiving nurse. It was
not clinically necessary here.

**Why the judge could not catch this:**
Assessing whether a piece of information is *appropriate to include* in a clinical context
requires understanding of professional norms, institutional expectations, and the ethical
weight of psychiatric confidentiality. These are learned through clinical training, not
from text corpora. The judge can check whether words appear — it cannot evaluate whether
including those words was appropriate given the circumstances.

This is why reflection.md identifies tone and confidentiality as the one evaluation
dimension that cannot be assessed without a human reviewer.

---

## A Note on the Scores Assigned

The score anchors defined in evaluation_design.md were:

```
5 = All criteria met, clinically safe and complete
4 = All criteria met, minor detail omission
3 = Diagnosis and most medications correct, one allergy missing
2 = Diagnosis correct, significant medication or allergy gaps
1 = Multiple critical fields missing, not safe for clinical use
```

Neither TC2 nor TC4 maps cleanly onto these anchors, which is itself a finding.

**TC2 — the anchor for 3/5 says "one allergy missing."** In TC2 the allergy is not
missing — both keywords appear. The failure is that an allergy is present alongside a
conflicting drug requirement, and the conflict is not flagged. This is arguably worse
than a simple omission: the reader gets a false sense of safety because the allergy
appears to have been noted. A score of 2/5 could be justified on the grounds that this
is an active safety failure, not just an omission. 3/5 was assigned as a judgment call
but it may be slightly generous. This ambiguity should be resolved before the rubric
is used in production.

**TC4 — the confidentiality breach is not covered by any anchor at all.** The anchors
were written around clinical information completeness (medications, allergies, diagnoses).
TC4 is a failure of appropriateness, not completeness. The model included information
it should not have propagated. 3/5 is a reasonable judgment call — the clinical facts
are correct, medication is present, no information was omitted — but the score is not
derivable from the rubric. It required a human decision outside the defined criteria.

This is a limitation of the evaluation design: the rubric was built for completeness
failures and does not handle appropriateness or conflict-detection failures. A future
version should add explicit criteria for both.

---

## Summary of Corrections

| Test Case | Automated Score | Human Score | Reason |
|---|---|---|---|
| TC1 | 5/5 | 5/5 | Confirmed correct |
| TC2 | 5/5 | 3/5 | Drug-allergy conflict not flagged |
| TC3 | 5/5 | 5/5 | Confirmed correct |
| TC4 | 5/5 | 3/5 | Confidentiality breach not flagged |
| TC5 | 5/5 | 5/5 | Confirmed correct |

**Corrected average: 4.2 / 5**
**Critical flags raised: 2**

---

## What This Demonstrates

This is not an edge case. This is the expected outcome when the same model family is used
for both generation and evaluation. The bias analysis in evaluation_design.md predicted
it. The run confirmed it. TC2 and TC4 are the exact failure modes the bias analysis
described: the judge cannot identify reasoning gaps it shares with the model it is judging.

The corrected scores and this document together are the honest output of this evaluation.
The automated JSON output (all 5/5) is the raw pipeline result. The human review is
what turns a raw result into a trustworthy one.
