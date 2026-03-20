"""
agent.py
---------
Reads fitness_user_metrics.csv, computes a statistical summary,
and calls an LLM to generate 12 human-readable business insights.

Insights are saved to agent/insights_generated.json so they can be
loaded directly into the LangSmith dataset (langsmith/dataset_creation.py).

Run:
    cd Project5_dashboard_project
    python agent/agent.py
"""

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
DATA_PATH   = BASE_DIR / "data" / "processed" / "fitness_user_metrics.csv"
OUTPUT_PATH = Path(__file__).parent / "insights_generated.json"

# ── LLM setup ─────────────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ── Insight queries ────────────────────────────────────────────────────────────
INSIGHT_QUERIES = [
    "What percentage of members are high churn risk and what € revenue is at risk?",
    "List the top 3 behavioural signals that predict high churn risk (with numbers).",
    "How many high-risk members have >30 days since last workout? List the top 5 by user_id.",
    "What is the avg sessions/week for high-risk vs low-risk members?",
    "Create a 1-paragraph coaching brief: what should coaches do THIS WEEK for high-risk members?",
    "How does sport variety differ between risk groups?",
    "How many members have avg_sessions_per_week <1.5? What %?",
    "If coaches re-engage the top 20% most at-risk members, what € value?",
    "What % of high-risk members show high duration_variability (inconsistent)?",
    "Generate a 3-bullet CEO summary of retention health + 1 urgent action.",
    "Flag the 3 most urgent members for coach outreach (lowest sessions + longest inactive).",
    "What is the typical profile of a high-risk member? (avg metrics).",
]


def build_data_context(df: pd.DataFrame) -> str:
    """Compute key stats and format them as a plain-text context block for the LLM."""
    churn_counts = df["churn_risk"].value_counts().to_dict()
    by_risk = df.groupby("churn_risk").agg(
        avg_spw=("avg_sessions_per_week", "mean"),
        avg_dur=("avg_duration_min", "mean"),
        avg_days=("days_since_last_workout", "mean"),
        avg_variety=("sport_variety", "mean"),
        avg_weeks=("active_weeks", "mean"),
        avg_var=("duration_variability", "mean"),
        count=("user_id", "count"),
        total_risk=("revenue_at_risk_eur", "sum"),
    ).round(2)

    lines = [
        "=== FITNESS CHAIN MEMBER RETENTION DATA ===",
        f"Total members: {len(df)}",
        f"Churn risk distribution: {churn_counts}",
        f"Total revenue at risk: €{df['revenue_at_risk_eur'].sum():,.0f}",
        f"Estimated LTV per member: €{df['estimated_ltv_eur'].iloc[0]:,.0f}",
        "",
        "Per-risk-group statistics:",
        by_risk.to_string(),
        "",
        "Overall stats:",
        f"  Avg sessions/week (all): {df['avg_sessions_per_week'].mean():.2f}",
        f"  Avg duration (all): {df['avg_duration_min'].mean():.1f} min",
        f"  Avg days since last workout (all): {df['days_since_last_workout'].mean():.1f}",
        f"  Members with >21 days inactive: {(df['days_since_last_workout'] > 21).sum()}",
        f"  Members with <1 session/week: {(df['avg_sessions_per_week'] < 1).sum()}",
        f"  Sport variety range: {df['sport_variety'].min()}–{df['sport_variety'].max()} types",
    ]
    return "\n".join(lines)


SYSTEM_PROMPT = """You are a fitness industry retention analyst preparing a briefing for Chleo,
CEO of a European medium-sized fitness chain (50–200 studios).
You will be given statistical data about 1,059 members and a specific question.
Answer with a clear, concise, non-technical insight (2–4 sentences).
Focus on business impact — what it means and what action to take.
Do not repeat the numbers robotically; interpret them."""


def generate_insights(df: pd.DataFrame) -> list[dict]:
    context = build_data_context(df)
    insights = []

    for i, query in enumerate(INSIGHT_QUERIES, 1):
        print(f"[{i}/{len(INSIGHT_QUERIES)}] {query[:70]}...")
        try:
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"DATA:\n{context}\n\nQUESTION: {query}"),
            ]
            response = llm.invoke(messages)
            insight_text = response.content.strip()
            status = "success"
        except Exception as e:
            insight_text = f"Error: {e}"
            status = "error"
            print(f"  ERROR: {e}")

        insights.append({
            "query_id": i,
            "query": query,
            "insight": insight_text,
            "status": status,
        })
        print(f"  -> {insight_text[:100]}...")

    return insights


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} members from {DATA_PATH}\n")

    insights = generate_insights(df)

    successful = [r for r in insights if r["status"] == "success"]
    print(f"\n{len(successful)}/{len(insights)} insights generated successfully.")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(insights, f, indent=2)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
