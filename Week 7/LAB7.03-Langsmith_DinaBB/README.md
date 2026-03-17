### LAB 7.03 – Custom Dataset Creation & Evaluation with LangSmith
Dina Bosma-Buczynska

---

#### Domain & Dataset

**Domain:** Digital Marketing Analytics Q&A
**Dataset name:** `marketing-analytics-qa-DinaBB` (hosted on LangSmith)
**Size:** 20 examples across 5 categories: KPI, Platform, Statistics, Budget, Strategy

Hand-authored questions grounded in industry benchmarks and the Kaggle Digital Marketing Performance Dataset from Lab 7.02. Each example pairs a marketing analyst question (with category metadata) with an expert reference answer.

---

#### What I did

1. Created a 20-example custom dataset and uploaded it to LangSmith
2. Implemented a `gpt-4o-mini` target function with `@traceable` decorator
3. Ran LLM-as-judge correctness evaluation using `openevals.CORRECTNESS_PROMPT`
4. Added a custom **Actionability** evaluator (direct OpenAI JSON-mode call) to measure whether answers are decision-ready
5. Ran a gpt-4o A/B comparison for cost-performance analysis (Optional Part 2)

---

#### Files

| File | Description |
|------|-------------|
| `lab_langsmith_DinaBB.ipynb` | Main notebook — Parts 1–5 + both optional sections |
| `evaluation_report.md` | Full evaluation report including Optimization Report |
| `evaluation_results_mini.png` | Score distribution + category breakdown chart |
| `dual_evaluator_scatter.png` | Correctness vs Actionability scatter plot |
| `ab_model_comparison.png` | gpt-4o-mini vs gpt-4o performance + cost chart |
| `experiments.png` | LangSmith UI — Experiments view |
| `examples.png` | LangSmith UI — Dataset examples view |
| `evaluation.png` | LangSmith UI — Individual run evaluation detail |
| `.env` | API keys (not committed) |

---

#### Key Results

| Metric | gpt-4o-mini | gpt-4o |
|--------|------------|--------|
| Mean correctness | 0.950 | 1.000 |
| Mean actionability | 0.940 | — |
| Est. cost / example | $0.000070 | $0.001836 |
| Cost ratio | 1× | 26× |

**Bottom line:** gpt-4o-mini is the better choice here — near-identical accuracy at 1/26th the cost.

---

#### How to Run

1. Add `OPENAI_API_KEY` and `LANGSMITH_API_KEY` to `.env`
2. Open `lab_langsmith_DinaBB.ipynb` — select kernel **bootcamp_py311**
3. Run all cells top-to-bottom
4. At the two marked `STOP` cells, check LangSmith UI before continuing

---

#### LangSmith Links

- **Project:** https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/projects/p/lab7-marketing-qa-eval
- **Dataset (20 examples):** https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/da5b9809-4ef5-4a7b-9454-182216820a37

#### Experiments

| Experiment | Link | Notes |
|------------|------|-------|
| gpt-4o-mini | https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/da5b9809-4ef5-4a7b-9454-182216820a37/compare?selectedSessions=6042d414-b019-4f5a-93a0-d3f95c85567c | Base run — 95% correctness |
| gpt-4o-mini + Actionability | https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/da5b9809-4ef5-4a7b-9454-182216820a37/compare?selectedSessions=d044a860-de0a-4a7b-b7c4-26fa50937e86 | Dual-evaluator run |
| gpt-4o | https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/da5b9809-4ef5-4a7b-9454-182216820a37/compare?selectedSessions=cb3fd1d1-6bdd-4764-8369-7008ee8e893c | A/B premium model — 100% correctness |

---

#### Environment

- Python 3.11 (`bootcamp_py311` conda env)
- Key packages: `langsmith==0.7.18`, `openai==2.28.0`, `openevals`, `python-dotenv`
