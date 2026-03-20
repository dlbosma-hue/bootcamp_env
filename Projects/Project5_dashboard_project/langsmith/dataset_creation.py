"""
dataset_creation.py
--------------------
Creates / refreshes the LangSmith dataset "Fitness Retention Insights V1"
from agent/insights_generated.json.

Requires LANGCHAIN_ENDPOINT=https://eu.api.smith.langchain.com in .env
(EU accounts) plus a valid LANGCHAIN_API_KEY.

Run AFTER agent/agent.py:
    cd Project5_dashboard_project
    python langsmith/dataset_creation.py
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DATASET_NAME  = "Fitness Retention Insights V1"
DATASET_DESC  = (
    "Agent-generated insights about member churn risk for a medium European "
    "fitness chain (50–200 studios). Each example is a business question "
    "answered by an LLM given aggregated member behaviour data from Endomondo."
)
INSIGHTS_PATH = Path(__file__).parent.parent / "agent" / "insights_generated.json"

client = Client()


def get_or_create_dataset():
    try:
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
        print(f"Found existing dataset: {DATASET_NAME} (id={dataset.id})")
        # Clear existing examples so we can replace with fresh ones
        existing = list(client.list_examples(dataset_id=dataset.id))
        if existing:
            for ex in existing:
                client.delete_example(ex.id)
            print(f"  Deleted {len(existing)} old examples")
        return dataset
    except Exception:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESC,
        )
        print(f"Created dataset: {DATASET_NAME} (id={dataset.id})")
        return dataset


def main():
    with open(INSIGHTS_PATH) as f:
        insights = json.load(f)

    successful = [r for r in insights if r["status"] == "success"]
    print(f"Loaded {len(successful)} insights from {INSIGHTS_PATH}\n")

    dataset = get_or_create_dataset()

    inputs  = [{"query": r["query"], "context": "fitness_user_metrics.csv — 1,059 members"} for r in successful]
    outputs = [{"insight": r["insight"]} for r in successful]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    print(f"Added {len(successful)} examples to '{DATASET_NAME}'")
    print(f"\nView dataset: https://eu.smith.langchain.com/o/561aa291-0a5c-4c0b-aad9-85d2023d43c6/datasets/{dataset.id}")


if __name__ == "__main__":
    main()
