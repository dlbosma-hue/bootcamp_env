"""
monitoring_setup.py
--------------------
Runs a LangSmith experiment on the "Fitness Retention Insights V1" dataset.

GREEN PATTERN: Demand Shaping / Cached Computation
  The target function now loads cached insights from insights_generated.json
  instead of re-running the agent live for each evaluation example.
  This eliminates 12 live LLM calls per evaluation cycle (was: 12, now: 0).
  The LLM-as-judge evaluators still run — they evaluate the cached outputs.

Evaluators:
  1. relevance      – does the insight answer the question? (1–5)
  2. actionability  – does it suggest a concrete action? (1–5)
  3. clarity        – is it understandable for a non-technical CEO? (1–5)

Run AFTER langsmith/dataset_creation.py:
    cd Project5_dashboard_project
    python langsmith/monitoring_setup.py
"""

import json
import os
import re
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
INSIGHTS_PATH   = Path(__file__).parent.parent / "agent" / "insights_generated.json"

client = Client()
llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# GREEN: load cached insights once at startup — no repeated file reads per example
_cached_insights: dict[str, str] = {}
if INSIGHTS_PATH.exists():
    with open(INSIGHTS_PATH) as f:
        for item in json.load(f):
            if item.get("status") == "success":
                _cached_insights[item["query"]] = item["insight"]
    print(f"[GREEN] Loaded {len(_cached_insights)} cached insights from {INSIGHTS_PATH.name}")
    print("  Evaluation will compare cached outputs — 0 live LLM calls for the target function.")
else:
    print(f"[WARNING] {INSIGHTS_PATH} not found — run agent/agent.py first to generate cached insights.")


# ── Target function ────────────────────────────────────────────────────────────
def run_agent(inputs: dict) -> dict:
    """
    GREEN: returns the cached insight for this query instead of re-running the LLM.
    Eliminates 12 live LLM calls per evaluation cycle with no loss of evaluation quality.
    """
    query = inputs["query"]
    insight = _cached_insights.get(query, "")
    if not insight:
        print(f"  [WARNING] No cached insight found for query: {query[:60]}...")
    return {"insight": insight}


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
    if not _cached_insights:
        print("No cached insights available. Run agent/agent.py first.")
        return

    print(f"\nRunning experiment '{EXPERIMENT_NAME}' on dataset '{DATASET_NAME}'...")
    print("[GREEN] Target function uses cached outputs — live LLM calls for this run: 0\n")

    results = evaluate(
        run_agent,
        data=DATASET_NAME,
        evaluators=[evaluate_relevance, evaluate_actionability, evaluate_clarity],
        experiment_prefix=EXPERIMENT_NAME,
        metadata={"model": "gpt-4o-mini", "project": "fitness-retention-p5", "green": "cached-target"},
    )

    print("\nExperiment complete.")
    print("View results in LangSmith: https://smith.langchain.com → Experiments")
    print(f"Experiment name prefix: {EXPERIMENT_NAME}")


if __name__ == "__main__":
    main()
