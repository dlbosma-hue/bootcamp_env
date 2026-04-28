from dotenv import load_dotenv
load_dotenv()

from db import filter_new, mark_seen
from fetcher import fetch_all_jobs
from notifier import send_digest
from scorer import score_jobs


def run():
    # 1. Fetch jobs from all sources (max 1 week old)
    all_jobs = fetch_all_jobs()
    total_fetched = len(all_jobs)

    # 2. Filter out jobs already notified
    new_jobs = filter_new(all_jobs)
    already_seen = total_fetched - len(new_jobs)
    print(f"[pipeline] {len(new_jobs)} new jobs to score ({already_seen} already seen)")

    if not new_jobs:
        print("[pipeline] Nothing new today.")
        return

    # 3. Score each job against resume via Claude
    scored = score_jobs(new_jobs)

    # 4. Mark all new jobs as seen (regardless of score) to avoid re-notifying
    mark_seen(new_jobs)

    # 5. Send email digest for matches above threshold
    send_digest(scored, total_fetched=len(new_jobs), already_seen=already_seen)


if __name__ == "__main__":
    run()
