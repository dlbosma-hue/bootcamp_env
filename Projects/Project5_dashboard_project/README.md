# Project 5 – Fitness Chain Retention: AI Early Warning System

**Sector:** Fitness / Health Tech — European boutique fitness chains
**Company size:** Boutique (up to 200 members per studio, premium pricing, coaching-led model)
**Scenario:** Dropout prediction, coach balancing, class optimisation
**Interactive dashboard (Plotly/Dash):** `python dashboard/plotly_dashboard.py` → http://127.0.0.1:8050
**Tableau (published):** [Member Retention Risk Overview](https://public.tableau.com/authoring/MemberRetentionRiskEarlyWarningSystem/MemberRetentionRiskOverview#1)

---

## What this is

A two-day consulting sprint built for a meeting with Chleo, CEO of a medium-sized European fitness chain. The pitch: AI can be **transparent and financially justified** — not a black box. The system surfaces member churn risk and estimated revenue at risk *before* it materialises, and gives coaches a daily action list, not a report to dig through.

Three use cases:
1. **Dropout prediction** — early-warning system flagging members likely to stop coming, 2–4 weeks before they cancel
2. **Coach balancing** — which coaches are overloaded, which high-risk members need attention first
3. **Class optimisation** — attendance and completion patterns by sport type and time slot

---

## Project Structure

```
Project5_dashboard_project/
├── data/
│   ├── raw/
│   │   ├── endomondo.json                    # 167k workout sessions (Endomondo/FitRec)
│   │   └── gym_churn_us.csv                  # Supplementary labelled churn dataset (Kaggle)
│   ├── processed/
│   │   └── fitness_user_metrics.csv          # Main output: 1 row per user
│   └── prepare_fitness_user_metrics_from_json.py
├── agent/
│   ├── agent.py                              # LLM insight generator
│   └── insights_generated.json              # 12 AI-generated insights
├── langsmith/
│   ├── dataset_creation.py                   # Pushes examples to LangSmith
│   ├── monitoring_setup.py                   # LLM-as-judge evaluation
│   ├── langsmith_evaluation.md               # Setup + methodology docs
│   └── evaluation_report.md                 # Results with scores and analysis
├── n8n/
│   ├── workflow.json                         # Importable n8n cloud workflow (live: https://dina2.app.n8n.cloud/workflow/GlYboQAG5jk11eQR)
│   └── workflow_documentation.md
├── dashboard/
│   ├── dashboard_documentation.md
│   └── Member Retention Risk – Early Warning System.twbx
├── research/
│   ├── sector_research.md
│   ├── use_cases.md
│   └── opportunities_risks.md
├── cost_estimation/
│   ├── cost_analysis.md
│   └── timeline_estimate.md
├── presentation_pitch_deck.html
├── BoutiqueFitnessChurnPrediction_documentation.docx.pdf
├── requirements.txt
├── .env.example
└── README.md
```

---

## Dataset

### Primary: Endomondo Fitness Trajectories
- **Source:** Kaggle – Endomondo workout logs
- **Size:** 167,783 workout sessions across 1,059 unique users
- **Fields used:** `userId`, `timestamp` (GPS track → start/end), `sport`
- **Why:** Real behavioural signals — session frequency, duration consistency, sport variety — the same signals that predict dropout in a real gym environment

### Supplementary: gym_churn_us.csv
- **Source:** Kaggle – Model Fitness / Gym Customer Churn
- **Fields:** age, contract type, visits/week, promo, churn label
- **Why:** Provides real labelled churn targets to validate heuristics and give context on demographic patterns

---

## What's in the Data

### `fitness_user_metrics.csv` — Behavioural (Endomondo)
**1,059 members · 12 columns**

| Column | Range / values | What it tells us |
|---|---|---|
| `total_sessions` | 1 – 1,301 (avg 158) | Overall engagement depth |
| `avg_sessions_per_week` | 1.0 – 8.1 (avg 2.3) | Habit strength — key churn signal |
| `avg_duration_min` | 11 – 284 min (avg 89 min) | Workout intensity / commitment |
| `duration_variability` | 0 – 128 min std | Consistency signal (high = erratic routine) |
| `sport_variety` | 1 – 12 sport types | Engagement breadth across classes |
| `days_since_last_workout` | 1 – 180 days | Recency — most immediate dropout indicator |
| `churn_risk` | low / medium / high | 382 / 447 / 230 members |
| `revenue_at_risk_eur` | €0 or €1,500 | **€345,000 total at risk** |

---

## Data Pipeline

### Script: `data/prepare_fitness_user_metrics_from_json.py`

Streams `endomondo.json` line by line using regex (not full JSON parse — the file is 167k lines with GPS arrays, so regex on target fields only keeps it fast) and outputs `fitness_user_metrics.csv`.

**Raw key → target field mapping:**

| Raw key | Target field | Notes |
|---|---|---|
| `userId` | `user_id` | Integer member identifier |
| `timestamp[0]` | `start_time` | Unix epoch → UTC datetime |
| `timestamp[-1]` | *(end time)* | Used to compute duration |
| `(end − start) / 60` | `duration_min` | No explicit duration field in source |
| `sport` | `sport` | Lowercased string (e.g. `bike`, `running`) |

**User-level aggregations:**

| Column | How it's computed |
|---|---|
| `total_sessions` | Count of workouts per user |
| `active_weeks` | Distinct ISO weeks with ≥1 workout |
| `avg_sessions_per_week` | `total_sessions / active_weeks` |
| `avg_duration_min` | Mean session duration |
| `duration_variability` | Std dev of duration (0 if only 1 session) |
| `sport_variety` | Count of distinct sport types |
| `last_workout_date` | Most recent session date |
| `days_since_last_workout` | `today − last_workout_date` (see note below) |

**Synthetic recency note:**
The Endomondo dataset ends in 2015–2016, so raw calendar dates would make every member look like they've churned already. `SYNTHETIC_RECENCY = True` reassigns `days_since_last_workout` with a realistic distribution correlated with each user's real session frequency:

| Frequency | Recency bucket (days) | Probability |
|---|---|---|
| High (≥ 2 sessions/week) | 1–7 / 8–21 / 22–180 | 70% / 20% / 10% |
| Medium (1–2 sessions/week) | 1–7 / 8–21 / 22–180 | 35% / 30% / 35% |
| Low (< 1 session/week) | 1–7 / 8–21 / 22–180 | 10% / 20% / 70% |

**Churn heuristic:**

| Risk | Condition |
|---|---|
| `low` | `avg_sessions_per_week ≥ 2` AND `days_since_last_workout ≤ 7` |
| `medium` | `avg_sessions_per_week ≥ 1` AND `days_since_last_workout ≤ 21` |
| `high` | everything else |

**Output (1,059 users):**

| Churn risk | Users | Share |
|---|---|---|
| low | 382 | 36% |
| medium | 447 | 42% |
| high | 230 | 22% |

**Revenue at risk:** 230 high-risk users × €1,500 LTV = **€345,000**

---

## Running the Agent

```bash
cd Project5_dashboard_project
python agent/agent.py
```

Generates 12 AI insights from `fitness_user_metrics.csv` → saved to `agent/insights_generated.json`.

---

## Running LangSmith Evaluation

```bash
# 1. Push dataset to LangSmith
python langsmith/dataset_creation.py

# 2. Run LLM-as-judge experiment
python langsmith/monitoring_setup.py
```

**Required `.env` vars:**
```
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=fitness-retention-p5
LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com
```

> **EU accounts:** `LANGCHAIN_ENDPOINT` must be set to the EU endpoint — without it all API calls return 403.

**Public experiment link (no login required):** https://eu.smith.langchain.com/public/9114327b-af22-4991-b756-8b31be6c9b7e/d

---

## Viewing the Dashboard

**Option 1 — Plotly/Dash (interactive, runs locally):**
```bash
python dashboard/plotly_dashboard.py
```
Opens at http://127.0.0.1:8050 — 5 charts, KPI cards, both datasets loaded automatically.

**Option 2 — Tableau Public (published, no setup needed):**
[Member Retention Risk Overview](https://public.tableau.com/authoring/MemberRetentionRiskEarlyWarningSystem/MemberRetentionRiskOverview#1)

See `dashboard/dashboard_documentation.md` for chart-by-chart breakdown and design notes.

---

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# fill in API keys
```

Run data pipeline:
```bash
python data/prepare_fitness_user_metrics_from_json.py
```

---

## Key Business Context

European boutique fitness chains operate on a fundamentally different model to large commercial gyms. Premium pricing, smaller member bases, and a coaching relationship where staff know every member by name. When a member cancels, it is not a lapsed direct debit quietly dropping off a spreadsheet — it is a person who made an active, conscious decision to leave, almost certainly after weeks of disengagement.

- **LTV per member: €1,500+** — at premium pricing, every cancellation is a meaningful financial event
- **~60% annual churn** (IHRSA benchmark) → **€90–120K in preventable lost revenue per 100-member studio/year**
- Members show behavioural drop-off **4–6 weeks** before cancelling — that's the intervention window
- In a boutique studio with personal coaching relationships, that window is exactly where an intervention can work
- This system targets that window using `days_since_last_workout` and `avg_sessions_per_week` as leading indicators

**Full business context and problem statement:** `BoutiqueFitnessChurnPrediction_documentation.docx.pdf`
