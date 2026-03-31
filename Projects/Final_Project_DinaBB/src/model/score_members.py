"""
score_members.py
----------------
Scores fitness_user_metrics.csv members using the trained logistic regression.

The gym_churn_us.csv training set and fitness_user_metrics.csv have different
schemas. The mapping below documents every decision honestly.

Run from project root:
    python src/model/score_members.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent.parent
DATA_PATH   = BASE_DIR / "data" / "fitness_user_metrics.csv"
MODEL_PATH  = BASE_DIR / "models" / "churn_model.pkl"
FEATS_PATH  = BASE_DIR / "models" / "feature_names.json"
OUTPUT_PATH = BASE_DIR / "data" / "scored_members.csv"

# ── Probability → risk tier thresholds ────────────────────────────────────────
HIGH_THRESHOLD   = 0.65
MEDIUM_THRESHOLD = 0.35


def map_features(df: pd.DataFrame, feature_names: list, train_path: Path) -> pd.DataFrame:
    """
    Map fitness_user_metrics columns to the model's expected feature set.

    Available in fitness_user_metrics:
      - total_sessions, active_weeks, avg_sessions_per_week
      - avg_duration_min, duration_variability, sport_variety
      - days_since_last_workout

    Not available (imputed with training-set median):
      - Age, Contract_period, Month_to_end_contract,
        Avg_additional_charges_total, Near_Location, Partner,
        Promo_friends, Phone, Group_visits, gender

    Closest available mappings:
      - Lifetime          ← active_weeks (proxy: weeks active ≈ tenure in weeks)
      - Avg_class_frequency_total         ← avg_sessions_per_week
      - Avg_class_frequency_current_month ← derived from days_since_last_workout:
            if days_since_last_workout <= 30: use avg_sessions_per_week
            else: 0.0  (member hasn't visited in over a month)
    """
    # Load training data to compute medians for imputed columns
    train_df = pd.read_csv(train_path)

    imputed = {
        "Age":                           train_df["Age"].median(),
        "Contract_period":               train_df["Contract_period"].median(),
        "Month_to_end_contract":         train_df["Month_to_end_contract"].median(),
        "Avg_additional_charges_total":  train_df["Avg_additional_charges_total"].median(),
        "Near_Location":                 train_df["Near_Location"].median(),
        "Partner":                       train_df["Partner"].median(),
        "Promo_friends":                 train_df["Promo_friends"].median(),
        "Phone":                         train_df["Phone"].median(),
        "Group_visits":                  train_df["Group_visits"].median(),
        "gender":                        train_df["gender"].median(),
    }

    mapped = pd.DataFrame(index=df.index)

    # Direct mappings
    mapped["Lifetime"]                         = df["active_weeks"]
    mapped["Avg_class_frequency_total"]        = df["avg_sessions_per_week"]
    mapped["Avg_class_frequency_current_month"] = np.where(
        df["days_since_last_workout"] <= 30,
        df["avg_sessions_per_week"],
        0.0,
    )

    # Imputed columns (no equivalent in source data)
    for col, median_val in imputed.items():
        mapped[col] = median_val

    # Return columns in the exact order the model expects
    return mapped[feature_names]


def risk_tier(probability: float) -> str:
    if probability >= HIGH_THRESHOLD:
        return "HIGH"
    elif probability >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def main():
    # ── 1. Load model and feature list ────────────────────────────────────────
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run src/model/train_churn_model.py first."
        )
    pipeline      = joblib.load(MODEL_PATH)
    feature_names = json.loads(FEATS_PATH.read_text())
    print(f"Model loaded from {MODEL_PATH}")

    # ── 2. Load member data ────────────────────────────────────────────────────
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} members from {DATA_PATH.name}\n")

    # ── 3. Map features ────────────────────────────────────────────────────────
    train_path = BASE_DIR / "data" / "gym_churn_us.csv"
    X = map_features(df, feature_names, train_path)

    print("Feature mapping summary:")
    print("  Mapped   : Lifetime, Avg_class_frequency_total, Avg_class_frequency_current_month")
    print("  Imputed  : Age, Contract_period, Month_to_end_contract,")
    print("             Avg_additional_charges_total, Near_Location, Partner,")
    print("             Promo_friends, Phone, Group_visits, gender")
    print("  (Imputed columns use training-set medians)\n")

    # ── 4. Score ───────────────────────────────────────────────────────────────
    probabilities = pipeline.predict_proba(X)[:, 1]

    output = df[["user_id", "estimated_ltv_eur", "revenue_at_risk_eur"]].copy()
    output["churn_probability"] = probabilities.round(4)
    output["churn_risk_tier"]   = output["churn_probability"].apply(risk_tier)

    # ── 5. Write output ────────────────────────────────────────────────────────
    output.to_csv(OUTPUT_PATH, index=False)
    print(f"Scored {len(output):,} members → {OUTPUT_PATH}\n")

    # ── 6. Summary ────────────────────────────────────────────────────────────
    tier_counts = output["churn_risk_tier"].value_counts()
    print("── Risk tier distribution ───────────────────────────────────────────")
    for tier in ["HIGH", "MEDIUM", "LOW"]:
        count = tier_counts.get(tier, 0)
        pct   = count / len(output) * 100
        print(f"  {tier:<8} {count:>5,}  ({pct:.1f}%)")

    print("\n── Top 10 highest-risk members ──────────────────────────────────────")
    top10 = output.nlargest(10, "churn_probability")[
        ["user_id", "churn_probability", "churn_risk_tier", "revenue_at_risk_eur"]
    ]
    print(top10.to_string(index=False))


if __name__ == "__main__":
    main()
