#### Evaluation Report: Digital Marketing Analytics Q&A
Dina Bosma-Buczynska
**Dataset:** `marketing-analytics-qa-DinaBB` (LangSmith)
**Project:** `lab7-marketing-qa-eval`

---

##### Executive Summary

I built a 20-question marketing analytics Q&A dataset and evaluated `gpt-4o-mini` on two dimensions: factual correctness and actionability (does the answer actually help someone make a decision?). The model performed really well — 95–100% correctness and 94% actionability — but the small gap between the two metrics tells an interesting story about what "correct" and "useful" actually mean.

For the optional A/B test, gpt-4o scored a perfect 1.000 vs gpt-4o-mini's 0.950, but costs 26× more. For this domain, gpt-4o-mini wins on value.

---

#### Methodology

##### Dataset
- 20 hand-authored Q&A examples across 5 categories: KPI (6), Platform (4), Statistics (6), Budget (1), Strategy (3)
- Each example: a marketing analyst question + a reference answer covering formulas, benchmarks, and action steps
- Grounded in industry benchmarks and the Kaggle Digital Marketing Performance Dataset from Lab 7.02

##### Target Function
- **Model:** `gpt-4o-mini` (temperature=0, max_tokens=300)
- **Persona:** Senior digital marketing analyst — concise answers under 150 words
- All calls traced to LangSmith via `@traceable` decorator

##### Evaluators
1. **Correctness** — `openevals.CORRECTNESS_PROMPT` with `gpt-4o-mini` as judge (scores 0.0 or 1.0)
2. **Actionability** *(custom)* — direct OpenAI JSON-mode call scoring 0.0–1.0 on whether the answer gives concrete steps, thresholds, or decision criteria a practitioner can use immediately

---

### Results

#### Overall — gpt-4o-mini

| Metric | Value |
|--------|-------|
| Mean correctness | **0.950–1.000** |
| Median correctness | **1.000** |
| Pass rate (≥ 0.8) | **19–20 / 20** |
| Mean actionability | **0.940** |

> Minor run-to-run variation (one Strategy example flipped between 0.0 and 1.0 across runs) is LLM judge stochasticity, not a real model failure.

#### By Category

| Category | Correctness | Actionability | n |
|----------|------------|---------------|---|
| KPI | 0.950–1.000 | 0.833 | 6 |
| Platform | 1.000 | 1.000 | 4 |
| Statistics | 1.000 | 0.967 | 6 |
| Budget | 1.000 | 1.000 | 1 |
| Strategy | 0.667–1.000 | 1.000 | 3 |
| **Overall** | **0.950–1.000** | **0.940** | **20** |

#### A/B Model Comparison

| Model | Mean Correctness | Est. Cost / Example | Total Cost |
|-------|-----------------|---------------------|------------|
| gpt-4o-mini | 0.950 | $0.000070 | $0.0014 |
| gpt-4o | 1.000 | $0.001836 | $0.0367 |
| Δ | +0.050 | **26× more expensive** | +$0.0353 |

---

### Analysis

The two most interesting findings:

**Correctness ≠ Actionability.** KPI questions scored the lowest on actionability (0.833) despite near-perfect correctness. The model accurately defines ROAS or CPA but doesn't always say "pause a campaign when CPM exceeds X" — it explains the formula but skips the decision trigger. Platform and Strategy questions scored 1.0 on both, because recommending a channel or tactic is inherently action-oriented.

**gpt-4o-mini is good enough here.** The 5pp correctness gap between models doesn't justify 26× the cost for marketing Q&A. The failure cases are edge cases driven by judge stochasticity anyway.

---

#### Limitations

- **Ceiling effect** — 95–100% correctness means this dataset doesn't challenge the model enough to reveal real failure modes.
- **LLM judge stochasticity** — even at temperature=0, the judge isn't fully deterministic. Averaging over multiple runs would be more reliable.
- **Self-evaluation bias** — gpt-4o-mini judging gpt-4o-mini answers is lenient by nature.
- **Hand-authored references** — semantically equivalent but differently phrased answers could be penalised unfairly.

---

#### Recommendations

1. **Stick with gpt-4o-mini** for this domain — near-identical accuracy at 1/26th the cost. Revisit if a harder dataset opens up a bigger gap.
2. **Fix the actionability gap cheaply** — add a system prompt instruction like "always include a decision threshold or action step" for KPI questions. No model upgrade needed.
3. **Harden the dataset** — replace easy definition questions with harder scenarios: conflicting KPIs, ambiguous attribution, multi-step calculations. This breaks the ceiling effect.
4. **Use a stronger judge** — swap gpt-4o-mini evaluator for gpt-4o or Claude to reduce leniency bias.
5. **Add RAG** — for questions requiring live benchmark data, a retrieval layer using the Lab 7.02 dataset would ground answers in real campaign numbers.

---

#### Optimization Report *(Optional Part 2)*

| Model | Experiment ID | n | Mean Correctness | Est. Cost |
|-------|--------------|---|-----------------|-----------|
| gpt-4o-mini | gpt-4o-mini-d259fb3e | 20 | 0.950 | $0.0014 |
| gpt-4o | gpt-4o-86dd71b3 | 20 | 1.000 | $0.0367 |

**Cost-performance winner: gpt-4o-mini** — 26× cheaper for only a 5pp accuracy drop.

| Scenario | Recommended Model | Why |
|----------|------------------|-----|
| High-volume production | gpt-4o-mini | Near-identical accuracy, fraction of cost |
| Single high-stakes decision ($500K budget call) | gpt-4o | Marginal accuracy gain worth the cost |
| R&D / evaluation pipeline | gpt-4o-mini | Fast iteration at low cost |
| Harder question set | Re-evaluate | Current gap too small to decide definitively |

---

## Next Steps

- [ ] Expand to 50+ harder, scenario-based examples to break the ceiling effect
- [ ] Re-run A/B comparison on the improved dataset to test if the gpt-4o gap widens
- [ ] Add human evaluation on 20% sample to validate LLM judge reliability
- [ ] Test RAG-augmented target function using the Lab 7.02 marketing dataset
- [ ] Run experiments at temperature=0.7 to measure output variance
