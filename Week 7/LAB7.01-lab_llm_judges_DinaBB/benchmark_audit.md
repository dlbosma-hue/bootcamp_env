# Benchmark Audit
## Client Scenario: Healthcare - Patient Record Summarization

A hospital wants to use an LLM to automatically summarize patient records.
The summaries must preserve all critical medical information including diagnoses,
medications, allergies, and treatment plans. Key concerns are accuracy,
completeness, and correct use of medical terminology.

---

## Benchmark 1: MedQA (USMLE-style)

**Benchmark Name:** MedQA
**Year:** 2021
**Source:** Jin et al., "What Disease does this Patient Have?" - https://arxiv.org/abs/2009.13081

**Why it seemed relevant:**
MedQA tests medical knowledge using questions drawn from US Medical Licensing Examination
(USMLE) style scenarios. Since patient record summarization requires the model to correctly
interpret medical terminology, diagnoses, and clinical reasoning, this benchmark seemed like
a reasonable proxy for domain knowledge quality.

**Contamination risk:**
[x] High - Model definitely saw this during training
Explanation: MedQA has been publicly available since 2021 and is widely used as a benchmark.
Most frontier LLMs are very likely to have encountered this dataset or similar USMLE-style
questions during pretraining.

**Saturation risk:**
[x] High - Many models achieve near-perfect scores
Explanation: GPT-4 and similar models now exceed passing scores on USMLE-style questions.
The benchmark is no longer sufficiently differentiating between models at the high end.

**Format:**
[x] Multiple Choice

**Verdict:**
[x] Reject it
Explanation: While MedQA tests medical knowledge, it does not test the specific capability
we need: summarization of clinical documents. A model that can answer multiple-choice
medical questions may still produce inaccurate or incomplete patient record summaries.
High contamination and saturation risks make it unreliable for evaluation purposes.

---

## Benchmark 2: MeQSum (Medical Question Summarization)

**Benchmark Name:** MeQSum
**Year:** 2019
**Source:** Ben Abacha & Demner-Fushman - https://aclanthology.org/P19-1215/

**Why it seemed relevant:**
MeQSum is specifically designed for medical summarization tasks. It contains consumer health
questions paired with human-written summaries. This is closer to the real task of condensing
medical text into shorter, accurate summaries, which is the core capability the hospital needs.

**Contamination risk:**
[x] Medium - Some overlap possible
Explanation: MeQSum is a smaller, more specialized dataset published in 2019. It is possible
some training corpora include it, but it is less universally included than major benchmarks
like MMLU or MedQA.

**Saturation risk:**
[x] Medium - Some models perform well
Explanation: ROUGE scores on this dataset have improved steadily but there is still meaningful
variance between models, especially on preserving clinical specificity in summaries.

**Format:**
[x] Free-form text

**Verdict:**
[x] Adapt it (explain how)
Explanation: MeQSum focuses on consumer-written health questions, not clinical records.
For this scenario, the benchmark should be adapted by replacing consumer-written input with
de-identified clinical record excerpts. The evaluation metric should also move beyond ROUGE
scores to include clinical completeness checks (e.g., were medications mentioned? were
allergies preserved?).

---

## Benchmark 3: MIMIC-III Clinical Note Summarization (Discharge Summaries)

**Benchmark Name:** MIMIC-III Discharge Summary Benchmark
**Year:** 2019 (dataset); summarization benchmarks built on it from 2020 onward
**Source:** Johnson et al. - https://physionet.org/content/mimiciii/

**Why it seemed relevant:**
MIMIC-III is the most widely used real-world clinical dataset in NLP research. It contains
de-identified clinical notes including discharge summaries, which are structurally similar
to the patient records the hospital wants to summarize. Several research groups have built
summarization evaluation tasks directly on MIMIC-III data.

**Contamination risk:**
[x] Low - Model likely not trained on this data
Explanation: MIMIC-III requires a credentialed data access application through PhysioNet.
It is not publicly downloadable and therefore unlikely to appear in standard web crawl
training datasets. This makes it one of the more contamination-resistant medical benchmarks
available.

**Saturation risk:**
[x] Low - Benchmark is challenging
Explanation: Clinical summarization remains genuinely difficult. Even state-of-the-art models
struggle with preserving all medications, allergy flags, and diagnostic nuance consistently
across complex cases. Performance variance between models is meaningful.

**Format:**
[x] Free-form text

**Verdict:**
[x] Adapt it (explain how)
Explanation: MIMIC-III is the strongest candidate but requires credentialed access, which
adds a setup barrier. The evaluation should be adapted to include a structured checklist
alongside ROUGE: did the summary include the primary diagnosis? Were all listed medications
preserved? Were allergy flags retained? This moves evaluation from fluency-based to
clinically grounded.
