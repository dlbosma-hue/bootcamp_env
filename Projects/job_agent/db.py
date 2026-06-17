"""
Deduplication via a JSON file committed back to the repo after each run.
This works across GitHub Actions runs without needing a database server.
"""

import json
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "seen_jobs.json")
TTL_DAYS = 30


def _load() -> dict:
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            return json.load(f)
    return {}


def _save(db: dict) -> None:
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _prune(db: dict) -> dict:
    cutoff = str(date.today() - timedelta(days=TTL_DAYS))
    return {k: v for k, v in db.items() if v.get("first_seen", "9999") >= cutoff}


def filter_new(jobs: list[dict]) -> list[dict]:
    db = _prune(_load())
    return [j for j in jobs if j["id"] not in db]


def mark_seen(jobs: list[dict]) -> None:
    db = _prune(_load())
    today = str(date.today())
    for job in jobs:
        db[job["id"]] = {
            "title": job["title"],
            "company": job["company"],
            "first_seen": today,
        }
    _save(db)
