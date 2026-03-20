"""
prepare_fitness_user_metrics_from_json.py
------------------------------------------
Streams the Endomondo JSONL file line by line, aggregates to user-level
metrics, and writes data/processed/fitness_user_metrics.csv.

Raw key → target field mapping
  userId          → user_id
  timestamp[0]    → start_time  (Unix epoch, first GPS point = workout start)
  timestamp[-1]   → end_time    (last GPS point; duration = end − start)
  sport           → sport
  (no explicit duration field in source — derived from timestamp list)

Speed note: each line contains 500-point GPS arrays. Rather than fully
parsing each object with ast.literal_eval, we use targeted regex to extract
only the three fields we need — ~10× faster on large files.

Synthetic recency: the source data is from 2014-2016 so all users appear
"churned" by calendar date. When SYNTHETIC_RECENCY = True we reassign
days_since_last_workout with a realistic distribution (correlated with
session frequency) so the dashboard shows a plausible churn mix for a
medium fitness chain today (~40% low, 20% medium, 40% high).
"""

import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ── File paths ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
FILENAME = BASE_DIR / "raw"       / "endomondo.json"
OUTPUT   = BASE_DIR / "processed" / "fitness_user_metrics.csv"

# ── Raw field keys (adjust here if source schema changes) ─────────────────────
RAW_USER_KEY     = "userId"     # integer user identifier
RAW_TIME_KEY     = "timestamp"  # list of Unix epoch ints; [0]=start, [-1]=end
RAW_DURATION_KEY = None         # not a direct field — computed from timestamp list
RAW_SPORT_KEY    = "sport"      # string, e.g. "bike", "running", "walking"

# ── Business constants ────────────────────────────────────────────────────────
ESTIMATED_LTV_EUR = 1500.0      # flat LTV assumption (tweak as needed)

# ── Synthetic recency settings ────────────────────────────────────────────────
# The source data ends in 2015-2016; without this all users appear "high churn".
# Set to True to replace days_since_last_workout with a realistic distribution
# anchored to today, correlated with each user's real session frequency.
SYNTHETIC_RECENCY      = True
SYNTHETIC_RECENCY_SEED = 42     # for reproducibility
REFERENCE_DATE         = date.today()   # anchor for days_since_last_workout

# ── Churn heuristic thresholds ────────────────────────────────────────────────
CHURN_LOW_MIN_SPW  = 2    # avg_sessions_per_week ≥ this AND days ≤ LOW_MAX  → low
CHURN_LOW_MAX_DAYS = 7
CHURN_MED_MIN_SPW  = 1    # avg_sessions_per_week ≥ this AND days ≤ MED_MAX  → medium
CHURN_MED_MAX_DAYS = 21
# otherwise → high

# ── Pre-compiled regexes (built from key constants above) ─────────────────────
_RE_USER  = re.compile(r"['\"]" + RAW_USER_KEY  + r"['\"]:\s*(\d+)")
_RE_SPORT = re.compile(r"['\"]" + RAW_SPORT_KEY + r"['\"]:\s*['\"]([^'\"]+)['\"]")
_RE_TS    = re.compile(r"['\"]" + RAW_TIME_KEY  + r"['\"]:\s*\[([^\]]+)\]")


def extract_record(line: str) -> dict | None:
    """Regex-extract user_id, start_time, duration_min, sport from one raw line."""
    m_user  = _RE_USER.search(line)
    m_ts    = _RE_TS.search(line)

    if not (m_user and m_ts):
        return None

    ts_nums = re.findall(r"\d+", m_ts.group(1))
    if len(ts_nums) < 2:
        return None

    first_ts     = int(ts_nums[0])
    last_ts      = int(ts_nums[-1])
    duration_min = (last_ts - first_ts) / 60.0

    if duration_min <= 0:
        return None

    m_sport = _RE_SPORT.search(line)
    return {
        "user_id":      int(m_user.group(1)),
        "start_time":   datetime.fromtimestamp(first_ts, tz=timezone.utc),
        "duration_min": duration_min,
        "sport":        m_sport.group(1).strip().lower() if m_sport else "unknown",
    }


def apply_synthetic_recency(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Replace days_since_last_workout and last_workout_date with realistic
    synthetic values anchored to today.  Recency is correlated with each
    user's real avg_sessions_per_week so the dataset stays internally
    coherent:
      high frequency (≥2 spw)  → mostly active  (1–14 days)
      mid  frequency (1–2 spw) → mixed           (1–45 days)
      low  frequency (<1 spw)  → mostly lapsed   (7–180 days)
    Target churn split for a medium fitness chain: ~40% low, 20% medium, 40% high.
    """
    rng = np.random.default_rng(SYNTHETIC_RECENCY_SEED)
    n   = len(agg)
    days = np.zeros(n, dtype=int)

    for i, spw in enumerate(agg["avg_sessions_per_week"]):
        if spw >= 2:          # high-frequency member — likely still active
            # 70% in 1-7 days, 20% in 8-21, 10% in 22-90
            bucket = rng.choice([0, 1, 2], p=[0.70, 0.20, 0.10])
        elif spw >= 1:        # moderate member
            bucket = rng.choice([0, 1, 2], p=[0.35, 0.30, 0.35])
        else:                 # low-frequency / sporadic
            bucket = rng.choice([0, 1, 2], p=[0.10, 0.20, 0.70])

        if bucket == 0:
            days[i] = int(rng.integers(1, 8))      # 1–7  → churn_risk low
        elif bucket == 1:
            days[i] = int(rng.integers(8, 22))     # 8–21 → churn_risk medium
        else:
            days[i] = int(rng.integers(22, 181))   # 22–180 → churn_risk high

    agg = agg.copy()
    agg["days_since_last_workout"] = days
    agg["last_workout_date"] = [
        REFERENCE_DATE - timedelta(days=int(d)) for d in days
    ]
    return agg


def assign_churn_risk(row: pd.Series) -> str:
    spw  = row["avg_sessions_per_week"]
    days = row["days_since_last_workout"]
    if spw >= CHURN_LOW_MIN_SPW and days <= CHURN_LOW_MAX_DAYS:
        return "low"
    if spw >= CHURN_MED_MIN_SPW and days <= CHURN_MED_MAX_DAYS:
        return "medium"
    return "high"


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # ── 1. Stream and parse ───────────────────────────────────────────────────
    records = []
    skipped = 0

    print(f"Streaming {FILENAME} ...")
    with open(FILENAME, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = extract_record(line)
            if rec is None:
                skipped += 1
            else:
                records.append(rec)
            if i % 20_000 == 0:
                print(f"  {i:,} lines read | {len(records):,} records collected ...")

    print(f"\nDone: {len(records):,} workouts parsed | {skipped:,} lines skipped\n")

    if not records:
        raise RuntimeError("No records parsed — check FILENAME and RAW_* constants.")

    df = pd.DataFrame(records)
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["week"]       = df["start_time"].dt.to_period("W")

    # ── 2. Aggregate to user level ────────────────────────────────────────────
    agg = (
        df.groupby("user_id")
        .agg(
            total_sessions       = ("duration_min", "count"),
            active_weeks         = ("week",          lambda s: s.nunique()),
            avg_duration_min     = ("duration_min",  "mean"),
            duration_variability = ("duration_min",  "std"),
            sport_variety        = ("sport",          "nunique"),
            last_workout_date    = ("start_time",     "max"),
        )
        .reset_index()
    )

    # std is NaN for single-session users → 0
    agg["duration_variability"] = agg["duration_variability"].fillna(0.0).round(2)
    agg["avg_duration_min"]     = agg["avg_duration_min"].round(2)

    agg["avg_sessions_per_week"] = (
        agg["total_sessions"] / agg["active_weeks"]
    ).round(4)

    # days_since_last_workout: relative to the most recent workout across ALL users
    reference_date = df["start_time"].max()
    agg["last_workout_date"]       = agg["last_workout_date"].dt.date
    agg["days_since_last_workout"] = (
        (reference_date - pd.to_datetime(agg["last_workout_date"], utc=True))
        .dt.days
    )

    # ── 3. Synthetic recency (optional) ──────────────────────────────────────
    if SYNTHETIC_RECENCY:
        agg = apply_synthetic_recency(agg)
        print(f"Synthetic recency applied (seed={SYNTHETIC_RECENCY_SEED}, "
              f"reference={REFERENCE_DATE})")

    # ── 4. Churn risk & LTV ───────────────────────────────────────────────────
    agg["churn_risk"]          = agg.apply(assign_churn_risk, axis=1)
    agg["estimated_ltv_eur"]   = ESTIMATED_LTV_EUR
    agg["revenue_at_risk_eur"] = agg["churn_risk"].apply(
        lambda r: ESTIMATED_LTV_EUR if r == "high" else 0.0
    )

    # ── 5. Final column order ─────────────────────────────────────────────────
    final_cols = [
        "user_id", "total_sessions", "active_weeks", "avg_sessions_per_week",
        "avg_duration_min", "duration_variability", "sport_variety",
        "last_workout_date", "days_since_last_workout", "churn_risk",
        "estimated_ltv_eur", "revenue_at_risk_eur",
    ]
    agg = agg[final_cols]

    # ── 6. Write CSV ──────────────────────────────────────────────────────────
    agg.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(agg):,} users → {OUTPUT}\n")

    # ── 7. Preview ────────────────────────────────────────────────────────────
    print(agg.head(10).to_string(index=False))
    print("\nChurn distribution:")
    print(agg["churn_risk"].value_counts().to_string())


if __name__ == "__main__":
    main()
