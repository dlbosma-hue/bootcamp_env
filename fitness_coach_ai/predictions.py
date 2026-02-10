"""
ML-based prediction models
"""

import statistics
from datetime import datetime, timedelta
from typing import List, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler

from models import Client, AnalysisResult, Prediction


class DropoutPredictor:
    """Predicts client dropout risk using ML"""

    def __init__(self):
        self.model = LogisticRegression(random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def extract_features(self, client: Client, analysis: AnalysisResult) -> np.ndarray:
        """Extract features from client data for ML model"""
        features = [
            analysis.missed_workouts_pct,
            analysis.nutrition_compliance,
            analysis.consistency_score,
            analysis.progression_rate,
            1 if analysis.strength_trend == "declining" else 0,
            1 if analysis.strength_trend == "plateau" else 0,
            len(client.workout_logs),
            len(client.nutrition_logs),
            (datetime.now() - client.start_date_obj).days
        ]
        return np.array(features).reshape(1, -1)

    def train(self, clients: List[Client], dropout_labels: List[int]):
        """Train the model on historical client data"""
        if len(clients) < 5:
            # Not enough data to train
            return False

        from analysis import analyze_client

        X = []
        for client in clients:
            analysis = analyze_client(client)
            features = self.extract_features(client, analysis)
            X.append(features[0])

        X = np.array(X)
        y = np.array(dropout_labels)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        return True

    def predict(self, client: Client, analysis: AnalysisResult) -> float:
        """Predict dropout probability (0-1)"""
        if not self.is_trained:
            # Fallback to rule-based prediction
            return self._rule_based_prediction(client, analysis)

        features = self.extract_features(client, analysis)
        features_scaled = self.scaler.transform(features)

        # Get probability of dropout
        dropout_prob = self.model.predict_proba(features_scaled)[0][1]
        return dropout_prob

    def _rule_based_prediction(self, client: Client, analysis: AnalysisResult) -> float:
        """Fallback rule-based prediction when not enough training data"""
        risk_score = 0

        # Factor in missed workouts
        if analysis.missed_workouts_pct > 50:
            risk_score += 30
        elif analysis.missed_workouts_pct > 30:
            risk_score += 20

        # Factor in nutrition compliance
        if analysis.nutrition_compliance < 50:
            risk_score += 20
        elif analysis.nutrition_compliance < 70:
            risk_score += 10

        # Factor in strength trend
        if analysis.strength_trend == "declining":
            risk_score += 25
        elif analysis.strength_trend == "plateau":
            risk_score += 15

        # Factor in consistency
        if analysis.consistency_score < 50:
            risk_score += 25

        return min(risk_score / 100, 1.0)


class PerformancePredictor:
    """Predicts future performance trends"""

    def __init__(self):
        self.model = LinearRegression()

    def predict_future_strength(self, client: Client, exercise: str,
                                weeks_ahead: int = 4) -> List[float]:
        """Predict future strength progression"""
        from analysis import get_exercise_history

        history = get_exercise_history(client, exercise, weeks=8)

        if len(history) < 3:
            return []

        # Prepare time series data
        X = np.array(range(len(history))).reshape(-1, 1)
        y = np.array([h['weight'] for h in history])

        # Fit linear regression
        self.model.fit(X, y)

        # Predict future
        future_X = np.array(range(len(history), len(history) + weeks_ahead)).reshape(-1, 1)
        predictions = self.model.predict(future_X)

        return predictions.tolist()


def detect_plateau(client: Client, weeks: int = 5) -> Tuple[bool, int]:
    """Detect if client is at a plateau and for how long"""
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    recent_workouts = [w for w in client.workout_logs if w.date_obj >= cutoff_date]

    if not recent_workouts:
        return False, 0

    # Group by week and check if weights are stagnant
    weights_by_week = {}
    for w in recent_workouts:
        week_num = (w.date_obj - cutoff_date).days // 7
        if week_num not in weights_by_week:
            weights_by_week[week_num] = []
        weights_by_week[week_num].append(w.weight)

    if len(weights_by_week) < 3:
        return False, 0

    # Calculate average weight per week
    avg_weights = {}
    for week, weights in weights_by_week.items():
        avg_weights[week] = statistics.mean(weights)

    # Count consecutive weeks at similar weight
    weeks_at_plateau = 0
    prev_weight = None

    for week in sorted(avg_weights.keys()):
        weight = avg_weights[week]
        if prev_weight and abs(weight - prev_weight) < 5:  # Within 5 lbs
            weeks_at_plateau += 1
        else:
            weeks_at_plateau = 0
        prev_weight = weight

    plateau_detected = weeks_at_plateau >= 3
    return plateau_detected, weeks_at_plateau if plateau_detected else 0


def predict_dropout_risk(client: Client, analysis: AnalysisResult,
                         predictor: DropoutPredictor = None) -> Prediction:
    """Predict client dropout risk"""
    if predictor is None:
        predictor = DropoutPredictor()

    # Get dropout probability
    dropout_prob = predictor.predict(client, analysis)
    risk_score = dropout_prob * 100

    # Determine risk level
    if risk_score >= 60:
        risk_level = "high"
    elif risk_score >= 35:
        risk_level = "medium"
    else:
        risk_level = "low"

    # Detect plateau
    plateau_detected, weeks_at_plateau = detect_plateau(client)

    # Determine if intervention needed
    intervention_needed = risk_score >= 35 or (plateau_detected and weeks_at_plateau >= 3)

    return Prediction(
        dropout_risk=risk_level,
        dropout_risk_score=min(risk_score, 100),
        plateau_detected=plateau_detected,
        weeks_at_plateau=weeks_at_plateau,
        intervention_needed=intervention_needed
    )


def detect_anomalies(client: Client) -> List[str]:
    """Detect unusual patterns in client behavior"""
    anomalies = []

    # Check for sudden drop in workout frequency
    recent_4_weeks = datetime.now() - timedelta(weeks=4)
    recent_8_weeks = datetime.now() - timedelta(weeks=8)

    recent_workouts = [w for w in client.workout_logs
                       if recent_4_weeks <= w.date_obj <= datetime.now()]
    older_workouts = [w for w in client.workout_logs
                      if recent_8_weeks <= w.date_obj < recent_4_weeks]

    if older_workouts and recent_workouts:
        recent_freq = len(set(w.date_obj.date() for w in recent_workouts)) / 4
        older_freq = len(set(w.date_obj.date() for w in older_workouts)) / 4

        if recent_freq < older_freq * 0.5:
            anomalies.append(
                f"Sudden drop in workout frequency: "
                f"{older_freq:.1f} → {recent_freq:.1f} workouts/week"
            )

    # Check for sudden weight decreases
    for exercise in set(w.exercise for w in client.workout_logs):
        ex_logs = [w for w in recent_workouts if w.exercise == exercise]
        if len(ex_logs) >= 2:
            ex_logs.sort(key=lambda x: x.date_obj)
            recent_weights = [w.weight for w in ex_logs[-3:]]
            if len(recent_weights) >= 2:
                decrease = recent_weights[0] - recent_weights[-1]
                if decrease > 20:  # 20+ lbs drop
                    anomalies.append(
                        f"Significant weight decrease in {exercise}: "
                        f"-{decrease:.0f} lbs"
                    )

    return anomalies
