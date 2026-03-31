"""
Fetch Fitbit data for consented coaching clients.

Usage:
  python src/data_loaders/fitbit_loader.py              # real API (requires tokens)
  python src/data_loaders/fitbit_loader.py --fake       # use synthetic data (no device needed)

Consent tiers (set per member in coaching intake form):
  workout_only — fetches manually-started workout sessions only
                 (session type, duration, calories, in-session HR avg/peak)
  full         — fetches workout sessions PLUS daily activity summaries
                 (steps, resting HR, active minutes per day)

Output:
  data/processed/fitbit_workouts.csv
  data/processed/fitbit_daily.csv  (full-consent members only)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["FITBIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["FITBIT_CLIENT_SECRET"]
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
TOKEN_FILE = Path(__file__).parent.parent.parent / "data" / "fitbit_tokens.json"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
WEEKS_BACK = 8

# In production: loaded from database or consent flags CSV per member
# For POC: defined here to mirror the n8n workflow mock members
CONSENTED_MEMBERS = [
    {"member_id": "M-001", "consent_tier": "full"},
    {"member_id": "M-003", "consent_tier": "full"},
    {"member_id": "M-002", "consent_tier": "workout_only"},
    {"member_id": "M-005", "consent_tier": "workout_only"},
    # M-004 has no wearable consent — not in this list
]


def get_session():
    from requests_oauthlib import OAuth2Session

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"Token file not found at {TOKEN_FILE}.\n"
            "Run: python src/data_loaders/fitbit_auth.py\n"
            "Or use --fake for synthetic data."
        )

    token = json.loads(TOKEN_FILE.read_text())

    def save_token(new_token):
        TOKEN_FILE.write_text(json.dumps(new_token, indent=2))

    return OAuth2Session(
        CLIENT_ID,
        token=token,
        auto_refresh_url=TOKEN_URL,
        auto_refresh_kwargs={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        token_updater=save_token,
    )


def fetch_workout_sessions(session, member_id="me"):
    start_date = (datetime.today() - timedelta(weeks=WEEKS_BACK)).strftime("%Y-%m-%d")
    url = (
        f"https://api.fitbit.com/1/user/{member_id}/activities/list.json"
        f"?afterDate={start_date}&sort=asc&limit=100&offset=0"
    )
    r = session.get(url)
    r.raise_for_status()
    activities = r.json().get("activities", [])

    rows = []
    for a in activities:
        zones = a.get("heartRateZones", [])
        hr_peak = next((z.get("max") for z in zones if z.get("name") == "Peak"), None)
        rows.append({
            "member_id": member_id,
            "session_date": a.get("startTime", "")[:10],
            "workout_type": a.get("activityName", "Unknown"),
            "duration_min": round(a.get("activeDuration", 0) / 60000, 1),
            "calories": a.get("calories", 0),
            "hr_avg": a.get("averageHeartRate", None),
            "hr_peak": hr_peak,
        })
    return rows


def fetch_daily_summary(session, member_id="me"):
    rows = []
    for days_ago in range(WEEKS_BACK * 7):
        date = (datetime.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        url = f"https://api.fitbit.com/1/user/{member_id}/activities/date/{date}.json"
        r = session.get(url)
        if r.status_code != 200:
            continue
        data = r.json()
        summary = data.get("summary", {})
        rows.append({
            "member_id": member_id,
            "date": date,
            "steps": summary.get("steps", 0),
            "active_minutes": summary.get("veryActiveMinutes", 0) + summary.get("fairlyActiveMinutes", 0),
            "resting_hr": summary.get("restingHeartRate", None),
            "calories_out": summary.get("caloriesOut", 0),
        })
    return rows


def run_real(members):
    import pandas as pd
    session = get_session()
    all_workouts, all_daily = [], []

    for m in members:
        mid = m["member_id"]
        tier = m["consent_tier"]
        print(f"  Fetching {mid} ({tier})...")

        workouts = fetch_workout_sessions(session, "me")  # "me" = authenticated user
        for w in workouts:
            w["member_id"] = mid  # relabel with pseudonymous ID
        all_workouts.extend(workouts)

        if tier == "full":
            daily = fetch_daily_summary(session, "me")
            for d in daily:
                d["member_id"] = mid
            all_daily.extend(daily)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_workouts).to_csv(OUTPUT_DIR / "fitbit_workouts.csv", index=False)
    print(f"\nSaved {len(all_workouts)} workout sessions → data/processed/fitbit_workouts.csv")
    if all_daily:
        pd.DataFrame(all_daily).to_csv(OUTPUT_DIR / "fitbit_daily.csv", index=False)
        print(f"Saved {len(all_daily)} daily records    → data/processed/fitbit_daily.csv")


def run_fake():
    print("Using synthetic data generator (--fake mode)...")
    script = Path(__file__).parent / "generate_fake_fitbit.py"
    subprocess.run([sys.executable, str(script)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake", action="store_true", help="Use synthetic data instead of live Fitbit API")
    args = parser.parse_args()

    if args.fake:
        run_fake()
    else:
        run_real(CONSENTED_MEMBERS)
