import sqlite3
from datetime import date

DB_PATH = "jobs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_jobs (
    id          TEXT PRIMARY KEY,
    title       TEXT,
    company     TEXT,
    location    TEXT,
    url         TEXT,
    score       INTEGER,
    flag        TEXT,
    match_reason TEXT,
    source      TEXT,
    first_seen  DATE DEFAULT CURRENT_DATE
);
"""


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.execute(_SCHEMA)
    c.commit()
    return c


def is_seen(job_id: str) -> bool:
    with _conn() as c:
        row = c.execute("SELECT 1 FROM seen_jobs WHERE id = ?", (job_id,)).fetchone()
        return row is not None


def mark_seen(job: dict, score: int, flag: str, match_reason: str) -> None:
    with _conn() as c:
        c.execute(
            """INSERT OR IGNORE INTO seen_jobs
               (id, title, company, location, url, score, flag, match_reason, source, first_seen)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job["id"], job["title"], job["company"], job["location"],
                job["url"], score, flag, match_reason, job.get("source", ""),
                date.today().isoformat(),
            ),
        )


def filter_new(jobs: list[dict]) -> list[dict]:
    return [j for j in jobs if not is_seen(j["id"])]
