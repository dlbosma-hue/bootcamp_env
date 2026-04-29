import os
from dotenv import load_dotenv

load_dotenv()

from db import filter_new, mark_seen
from fetcher import fetch_all_jobs
from notifier import send_digest
from scorer import score_job


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    resume_text       = _load("resume.md")
    reference_text    = _load("reference.md")
    certification_text = _load("certification.md")

    print("[pipeline] Fetching jobs...")
    all_jobs = fetch_all_jobs()

    print("[pipeline] Filtering already-seen jobs...")
    new_jobs = filter_new(all_jobs)
    print(f"  → {len(new_jobs)} new (of {len(all_jobs)} fetched)")

    if not new_jobs:
        print("[pipeline] Nothing new — skipping scoring and email.")
        return

    print("[pipeline] Scoring jobs...")
    scored = []
    for i, job in enumerate(new_jobs, 1):
        result = score_job(job, resume_text, reference_text, certification_text)
        job_scored = {**job, **result}
        mark_seen(job, result["score"], result["flag"], result["match_reason"])
        scored.append(job_scored)
        flag_icon = {"apply": "✅", "maybe": "🤔", "skip": "⬜"}.get(result["flag"], "")
        print(f"  [{i}/{len(new_jobs)}] {flag_icon} {result['score']}/10 — {job['title']} @ {job['company']}")

    print("[pipeline] Sending digest...")
    send_digest(scored, total_seen=len(new_jobs))
    print("[pipeline] Done.")


if __name__ == "__main__":
    main()
