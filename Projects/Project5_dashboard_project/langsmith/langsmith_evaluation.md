# LangSmith Evaluation Documentation
**Project:** Fitness Chain Retention – AI Insights Monitoring
**Dataset:** Fitness Retention Insights V1

---

## Overview

LangSmith is used here to demonstrate **AI transparency** to Chleo — showing not just what the AI said, but how well it performed, measured by three independent criteria. This directly addresses the concern that "AI is not transparent."

---

## Dataset Creation (`dataset_creation.py`)

### Process
1. Run `agent/agent.py` → generates `agent/insights_generated.json` (12 insights)
2. Run `langsmith/dataset_creation.py` → creates the LangSmith dataset

### Dataset structure
Each of the 12 examples contains:

| Field | Content |
|---|---|
| `inputs.query` | Business question asked to the agent |
| `inputs.context` | Dataset reference (`fitness_user_metrics.csv`) |
| `outputs.insight` | Agent-generated insight text |

### Example entry
```json
{
  "inputs": {
    "query": "What percentage of members are at high churn risk, and what does that mean for the business?",
    "context": "fitness_user_metrics.csv — 1,059 members"
  },
  "outputs": {
    "insight": "22% of members (230 people) are classified as high churn risk, representing €345,000 in revenue at risk. These are members who haven't visited in over 3 weeks and have low session frequency. Immediate coach outreach to this group could recover a significant share of that revenue before they cancel."
  }
}
```

**Dataset URL:** https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/c7204587-7dea-4db1-bbee-8ea45c99ca7e

---

## Experiment Setup (`monitoring_setup.py`)

### Target function: `run_agent(inputs)`
Re-generates each insight live from the query using `gpt-4o-mini`.
This tests whether the agent gives **consistent, quality outputs** — not just whether it can produce text.

### Evaluators (LLM-as-judge)

Three evaluators, each scoring 1–5, normalised to 0–1:

#### 1. Relevance
> "Does the insight directly answer the question asked?"

**Why this matters:** An insight that doesn't address the question wastes the coach's time and erodes trust.

#### 2. Actionability
> "Does the insight suggest a concrete business action coaches or management can take?"

**Why this matters:** Chleo needs to know what to *do*, not just what's happening. Pure statistics without recommendations have no business value.

#### 3. Clarity
> "Is the insight understandable to a non-technical CEO with no data science background?"

**Why this matters:** The whole point of this demo is to show AI can communicate in plain language. If the CEO can't understand it, it fails.

### Judge prompt (full)
```
You are an expert evaluator assessing AI-generated business insights.
Score the insight on the given criterion from 1 to 5.
Return ONLY a JSON object: {"score": <int 1-5>, "reasoning": "<one sentence>"}

Criterion: [Relevance | Actionability | Clarity]
Description: [criterion description]
Question asked: [query]
AI insight: [insight text]

Score 1–5 and explain briefly.
```

### Bias considerations
- **Self-referential bias:** GPT-4o-mini judges outputs from GPT-4o-mini — same model family may rate its own outputs favourably. Mitigation: use Claude as judge in production.
- **Length bias:** Longer, more detailed answers may score higher on clarity even if less focused. Mitigation: clarity rubric explicitly asks about understandability, not detail.
- **Calibration:** 1–5 scores are normalised to 0–1 in LangSmith. Absolute scores matter less than relative ranking across insights.

---

## Running the Pipeline

```bash
# 1. Generate insights
cd Project5_dashboard_project
python agent/agent.py

# 2. Create LangSmith dataset
python langsmith/dataset_creation.py

# 3. Run experiment with LLM-as-judge
python langsmith/monitoring_setup.py
```

**Required env vars in `.env`:**
```
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=fitness-retention-p5
```

---

## Results

See [`evaluation_report.md`](./evaluation_report.md) for the full results including per-insight scores, key findings, bias discussion, and recommendations.

**Experiment URL:** https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/c7204587-7dea-4db1-bbee-8ea45c99ca7e/compare?selectedSessions=a268c42b-92e4-4201-bc1d-892c629af741

**Public shareable link (no login required):** https://eu.smith.langchain.com/public/9114327b-af22-4991-b756-8b31be6c9b7e/d
