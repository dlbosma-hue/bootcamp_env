"""
monitoring_setup.py
--------------------
Runs a LangSmith experiment on the "Fitness Retention Insights V1" dataset.

Target function: re-generates each insight from the query using the LLM.
Evaluators:
  1. relevance   – does the insight answer the question? (1–5)
  2. actionability – does it suggest a concrete action? (1–5)
  3. clarity      – is it understandable for a non-technical CEO? (1–5)

All three use an LLM-as-judge approach (Claude or GPT-4o-mini).

Run AFTER langsmith/dataset_creation.py:
    cd Project5_dashboard_project
    python langsmith/monitoring_setup.py
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import Client
from langsmith.evaluation import evaluate

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
DATASET_NAME    = "Fitness Retention Insights V1"
EXPERIMENT_NAME = "fitness-insights-llm-judge-v1"
DATA_PATH       = Path(__file__).parent.parent / "data" / "processed" / "fitness_user_metrics.csv"

client = Client()
llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ── Data context (loaded once) ─────────────────────────────────────────────────
_df = pd.read_csv(DATA_PATH)
_by_risk = _df.groupby("churn_risk").agg(
    avg_spw  = ("avg_sessions_per_week", "mean"),
    avg_dur  = ("avg_duration_min", "mean"),
    avg_days = ("days_since_last_workout", "mean"),
    count    = ("user_id", "count"),
    total_risk = ("revenue_at_risk_eur", "sum"),
).round(2).to_string()

DATA_CONTEXT = f"""Total members: {len(_df)}
Churn distribution: {_df['churn_risk'].value_counts().to_dict()}
Total revenue at risk: €{_df['revenue_at_risk_eur'].sum():,.0f}
Per-risk-group stats:
{_by_risk}"""

AGENT_SYSTEM_PROMPT = """You are a fitness industry retention analyst briefing a non-technical CEO.
Given member behaviour data and a question, respond with 2–4 clear, actionable sentences.
Focus on business impact and recommended action."""


# ── Target function ────────────────────────────────────────────────────────────
def run_agent(inputs: dict) -> dict:
    """Re-generate the insight from the query — this is what LangSmith evaluates."""
    query = inputs["query"]
    messages = [
        SystemMessage(content=AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"DATA:\n{DATA_CONTEXT}\n\nQUESTION: {query}"),
    ]
    response = llm.invoke(messages)
    return {"insight": response.content.strip()}


# ── LLM-as-judge evaluators ────────────────────────────────────────────────────
JUDGE_SYSTEM = """You are an expert evaluator assessing AI-generated business insights.
Score the insight on the given criterion from 1 to 5.
Return ONLY a JSON object: {"score": <int 1-5>, "reasoning": "<one sentence>"}"""

def _judge(criterion: str, description: str, query: str, insight: str) -> dict:
    prompt = f"""Criterion: {criterion}
Description: {description}

Question asked: {query}
AI insight: {insight}

Score 1–5 and explain briefly."""
    response = llm.invoke([
        SystemMessage(content=JUDGE_SYSTEM),
        HumanMessage(content=prompt),
    ])
    import json, re
    text = response.content.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            return {"score": int(result.get("score", 3)), "reasoning": result.get("reasoning", "")}
        except Exception:
            pass
    return {"score": 3, "reasoning": "Could not parse judge response"}


def evaluate_relevance(run, example) -> dict:
    result = _judge(
        criterion="Relevance",
        description="Does the insight directly answer the question asked?",
        query=example.inputs["query"],
        insight=run.outputs["insight"],
    )
    return {"key": "relevance", "score": result["score"] / 5, "comment": result["reasoning"]}


def evaluate_actionability(run, example) -> dict:
    result = _judge(
        criterion="Actionability",
        description="Does the insight suggest a concrete business action coaches or management can take?",
        query=example.inputs["query"],
        insight=run.outputs["insight"],
    )
    return {"key": "actionability", "score": result["score"] / 5, "comment": result["reasoning"]}


def evaluate_clarity(run, example) -> dict:
    result = _judge(
        criterion="Clarity",
        description="Is the insight understandable to a non-technical CEO with no data science background?",
        query=example.inputs["query"],
        insight=run.outputs["insight"],
    )
    return {"key": "clarity", "score": result["score"] / 5, "comment": result["reasoning"]}


# ── Run experiment ─────────────────────────────────────────────────────────────
def main():
    print(f"Running experiment '{EXPERIMENT_NAME}' on dataset '{DATASET_NAME}'...")

    results = evaluate(
        run_agent,
        data=DATASET_NAME,
        evaluators=[evaluate_relevance, evaluate_actionability, evaluate_clarity],
        experiment_prefix=EXPERIMENT_NAME,
        metadata={"model": "gpt-4o-mini", "project": "fitness-retention-p5"},
    )

    print("\nExperiment complete.")
    print("View results in LangSmith: https://smith.langchain.com → Experiments")
    print(f"Experiment name prefix: {EXPERIMENT_NAME}")


if __name__ == "__main__":
    main()
