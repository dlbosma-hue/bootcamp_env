"""
Generate synthetic Fitbit data for POC testing.

Run: python src/data_loaders/generate_fake_fitbit.py

Outputs:
  data/processed/fitbit_workouts.csv   — workout sessions per member
  data/processed/fitbit_daily.csv      — daily activity summaries (full-consent members only)

Members and their consent tiers are defined in MEMBERS below.
This mirrors the coaching intake form consent boxes:
  Box 3a (workout_only): session type, duration, calories, in-session HR
  Box 3b (full):         workout_only PLUS daily steps, resting HR, active minutes
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "processed"

# Simulated coaching clients with different consent levels
MEMBERS = [
    {"member_id": "M-001", "consent_tier": "full",         "risk_profile": "declining"},
    {"member_id": "M-002", "consent_tier": "workout_only", "risk_profile": "stable"},
    {"member_id": "M-003", "consent_tier": "full",         "risk_profile": "at_risk"},
    {"member_id": "M-004", "consent_tier": "none",         "risk_profile": "stable"},
    {"member_id": "M-005", "consent_tier": "workout_only", "risk_profile": "declining"},
]

WORKOUT_TYPES = ["Strength Training", "Cycling", "Running", "HIIT", "Yoga", "Pilates"]

def random_date_in_window(days_ago_min, days_ago_max):
    offset = random.randint(days_ago_min, days_ago_max)
    return (datetime.today() - timedelta(days=offset)).strftime("%Y-%m-%d")

def generate_workout_sessions(member_id, risk_profile, weeks=8):
    sessions = []
    today = datetime.today()

    # Risk profiles determine frequency drop-off
    if risk_profile == "stable":
        weekly_sessions = [random.randint(2, 4) for _ in range(weeks)]
    elif risk_profile == "declining":
        # Starts regular, drops off in recent weeks
        weekly_sessions = [random.randint(3, 5) for _ in range(4)] + \
                          [random.randint(0, 1) for _ in range(4)]
    elif risk_profile == "at_risk":
        # Very low throughout
        weekly_sessions = [random.randint(0, 2) for _ in range(weeks)]

    for week_idx, n_sessions in enumerate(weekly_sessions):
        week_start = today - timedelta(weeks=weeks - week_idx)
        for _ in range(n_sessions):
            session_date = week_start + timedelta(days=random.randint(0, 6))
            duration = random.randint(25, 75)
            hr_avg = random.randint(128, 158)
            hr_peak = hr_avg + random.randint(10, 30)
            sessions.append({
                "member_id": member_id,
                "session_date": session_date.strftime("%Y-%m-%d"),
                "workout_type": random.choice(WORKOUT_TYPES),
                "duration_min": duration,
                "calories": int(duration * random.uniform(5.5, 9.0)),
                "hr_avg": hr_avg,
                "hr_peak": min(hr_peak, 195),
            })

    return sorted(sessions, key=lambda x: x["session_date"])


def generate_daily_summaries(member_id, risk_profile, weeks=8):
    summaries = []
    today = datetime.today()

    for day_offset in range(weeks * 7):
        date = (today - timedelta(days=weeks * 7 - day_offset)).strftime("%Y-%m-%d")
        recency_factor = day_offset / (weeks * 7)  # 0 = oldest, 1 = most recent

        if risk_profile == "declining":
            # Activity drops off toward recent dates
            steps = int(random.gauss(9000 - 4000 * recency_factor, 1500))
            active_min = int(random.gauss(45 - 25 * recency_factor, 10))
        elif risk_profile == "at_risk":
            steps = int(random.gauss(4500, 1200))
            active_min = int(random.gauss(18, 8))
        else:  # stable
            steps = int(random.gauss(8500, 1500))
            active_min = int(random.gauss(40, 12))

        summaries.append({
            "member_id": member_id,
            "date": date,
            "steps": max(steps, 0),
            "active_minutes": max(active_min, 0),
            "resting_hr": random.randint(54, 72),
            "calories_out": int(max(steps, 0) * 0.04 + 1400),
        })

    return summaries


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_workouts = []
    all_daily = []

    for m in MEMBERS:
        if m["consent_tier"] == "none":
            print(f"  {m['member_id']}: no wearable consent — skipping")
            continue

        # All consented members get workout sessions
        sessions = generate_workout_sessions(m["member_id"], m["risk_profile"])
        all_workouts.extend(sessions)
        print(f"  {m['member_id']} ({m['consent_tier']}): {len(sessions)} workout sessions")

        # Only full-consent members get daily summaries
        if m["consent_tier"] == "full":
            daily = generate_daily_summaries(m["member_id"], m["risk_profile"])
            all_daily.extend(daily)
            print(f"  {m['member_id']} (full): {len(daily)} daily summary records")

    workouts_df = pd.DataFrame(all_workouts)
    workouts_df.to_csv(OUTPUT_DIR / "fitbit_workouts.csv", index=False)
    print(f"\nSaved {len(workouts_df)} workout sessions → data/processed/fitbit_workouts.csv")

    if all_daily:
        daily_df = pd.DataFrame(all_daily)
        daily_df.to_csv(OUTPUT_DIR / "fitbit_daily.csv", index=False)
        print(f"Saved {len(daily_df)} daily records    → data/processed/fitbit_daily.csv")


if __name__ == "__main__":
    print("Generating synthetic Fitbit data...\n")
    main()
