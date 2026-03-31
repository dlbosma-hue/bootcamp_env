"""
train_churn_model.py
--------------------
Trains a logistic regression churn model on gym_churn_us.csv.
Saves model to models/churn_model.pkl and feature list to models/feature_names.json.

Run from project root:
    python src/model/train_churn_model.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent.parent   # project root
DATA_PATH  = BASE_DIR / "data" / "gym_churn_us.csv"
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"
FEATS_PATH = BASE_DIR / "models" / "feature_names.json"

# ── Feature selection ──────────────────────────────────────────────────────────
# All features are available at prediction time:
#   - Contract_period, Month_to_end_contract: known from membership record
#   - Lifetime: tenure in months, available from sign-up date
#   - Avg_class_frequency_*: computed from attendance logs
#   - Age, gender, Near_Location, Partner, Promo_friends, Phone, Group_visits:
#     captured at sign-up or derivable from CRM
# No leakage — Churn is the label, not a feature.
FEATURES = [
    "Age",
    "Lifetime",
    "Contract_period",
    "Month_to_end_contract",
    "Avg_class_frequency_total",
    "Avg_class_frequency_current_month",
    "Avg_additional_charges_total",
    "Near_Location",
    "Partner",
    "Promo_friends",
    "Phone",
    "Group_visits",
    "gender",
]
TARGET = "Churn"


def main():
    # ── 1. Load data ───────────────────────────────────────────────────────────
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} rows from {DATA_PATH.name}")
    print(f"Churn rate: {df[TARGET].mean():.1%}\n")

    X = df[FEATURES]
    y = df[TARGET]

    # ── 2. Train / test split ──────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train: {len(X_train):,} rows  |  Test: {len(X_test):,} rows\n")

    # ── 3. Train pipeline (scaler + logistic regression) ──────────────────────
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  LogisticRegression(max_iter=1000, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    # ── 4. Evaluate ────────────────────────────────────────────────────────────
    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall    = recall_score(y_test, y_pred)
    f1        = f1_score(y_test, y_pred)
    roc_auc   = roc_auc_score(y_test, y_proba)

    print("── Test-set metrics ─────────────────────────────────────────────────")
    print(f"  Accuracy : {accuracy:.4f}  ({accuracy:.1%})")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall   : {recall:.4f}")
    print(f"  F1       : {f1:.4f}")
    print(f"  ROC-AUC  : {roc_auc:.4f}\n")

    # ── 5. Top coefficients ────────────────────────────────────────────────────
    coefs = pipeline.named_steps["model"].coef_[0]
    coef_df = (
        pd.DataFrame({"feature": FEATURES, "coefficient": coefs})
        .sort_values("coefficient", ascending=False)
    )
    print("── Feature coefficients (positive = churn risk, negative = retention) ─")
    for _, row in coef_df.iterrows():
        direction = "↑ churn" if row["coefficient"] > 0 else "↓ churn"
        print(f"  {row['feature']:<40} {row['coefficient']:+.4f}  {direction}")
    print()

    # ── 6. Save model and feature list ────────────────────────────────────────
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    FEATS_PATH.write_text(json.dumps(FEATURES, indent=2))

    print(f"Model saved → {MODEL_PATH}")
    print(f"Feature list saved → {FEATS_PATH}")


if __name__ == "__main__":
    main()
