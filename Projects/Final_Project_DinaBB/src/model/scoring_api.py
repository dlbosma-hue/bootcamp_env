"""
scoring_api.py
--------------
Lightweight Flask API that scores a single member using the trained model.
Called by the n8n Score Churn Risk node.

Run from project root:
    python src/model/scoring_api.py

Endpoint:
    POST /score
    Body: { "avg_sessions_per_week": 2.1, "active_weeks": 18, "days_since_last_workout": 5 }
    Response: { "churn_probability": 0.31, "churn_risk_tier": "LOW" }
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"
FEATS_PATH = BASE_DIR / "models" / "feature_names.json"
TRAIN_PATH = BASE_DIR / "data" / "gym_churn_us.csv"

# ── Thresholds ─────────────────────────────────────────────────────────────────
HIGH_THRESHOLD   = 0.65
MEDIUM_THRESHOLD = 0.35

app = Flask(__name__)

# Load model and training medians once at startup
_pipeline      = None
_feature_names = None
_train_medians = None


def _load():
    global _pipeline, _feature_names, _train_medians
    if _pipeline is None:
        _pipeline      = joblib.load(MODEL_PATH)
        _feature_names = json.loads(FEATS_PATH.read_text())
        train_df       = pd.read_csv(TRAIN_PATH)
        _train_medians = train_df[_feature_names].median().to_dict()


def _build_feature_row(data: dict) -> pd.DataFrame:
    """
    Map incoming member fields to the model's feature vector.
    Any field not provided falls back to the training-set median.
    """
    _load()

    avg_spw   = float(data.get("avg_sessions_per_week", _train_medians["Avg_class_frequency_total"]))
    weeks     = float(data.get("active_weeks",          _train_medians["Lifetime"]))
    days_out  = float(data.get("days_since_last_workout", 0))

    row = {feat: _train_medians[feat] for feat in _feature_names}

    # Apply same mapping logic as score_members.py
    row["Lifetime"]                          = weeks
    row["Avg_class_frequency_total"]         = avg_spw
    row["Avg_class_frequency_current_month"] = avg_spw if days_out <= 30 else 0.0

    return pd.DataFrame([row])[_feature_names]


def _tier(probability: float) -> str:
    if probability >= HIGH_THRESHOLD:
        return "HIGH"
    elif probability >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


@app.route("/score", methods=["POST"])
def score():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON body received"}), 400

    X           = _build_feature_row(data)
    probability = float(_pipeline.predict_proba(X)[0, 1])
    tier        = _tier(probability)

    response = {
        "churn_probability": round(probability, 4),
        "churn_risk_tier":   tier,
    }
    if "member_id" in data:
        response["member_id"] = data["member_id"]

    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    _load()
    return jsonify({"status": "ok", "model": str(MODEL_PATH.name)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
