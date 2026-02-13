"""
Client performance analysis functions
"""

import statistics
from datetime import datetime, timedelta
from typing import Dict, List

from models import Client, ValidationResult, AnalysisResult


def validate_client_data(client: Client) -> ValidationResult:
    """Validate client data for completeness and consistency"""
    result = ValidationResult(is_valid=True)

    # Check for data completeness
    if not client.workout_logs:
        result.errors.append("No workout data found")
        result.is_valid = False

    if not client.nutrition_logs:
        result.errors.append("No nutrition data found")
        result.is_valid = False

    if not result.is_valid:
        return result

    # Check for inconsistencies
    cutoff = datetime.now() - timedelta(days=21)
    recent_workouts = [w for w in client.workout_logs if w.date_obj >= cutoff]

    for workout in recent_workouts:
        if "struggling" in workout.form_notes.lower() or "breaking down" in workout.form_notes.lower():
            result.warnings.append(
                f"Form issues noted on {workout.date} for {workout.exercise} "
                f"at {workout.weight} lbs - may need weight reduction or form check"
            )

    # Check nutrition completeness
    recent_nutrition = [n for n in client.nutrition_logs
                        if (datetime.now() - n.date_obj).days <= 7]

    incomplete_days = [n for n in recent_nutrition if n.meals_logged < 4]
    if len(incomplete_days) > 3:
        result.warnings.append(
            f"Nutrition tracking incomplete on {len(incomplete_days)}/7 days - "
            f"data may not be reliable"
        )

    return result


def calculate_progression_rate(client: Client, exercise: str = None,
                                weeks: int = 4) -> float:
    """Calculate rate of progression for exercises"""
    cutoff = datetime.now() - timedelta(weeks=weeks)
    recent_workouts = [w for w in client.workout_logs if w.date_obj >= cutoff]

    if exercise:
        recent_workouts = [w for w in recent_workouts if w.exercise == exercise]

    recent_workouts.sort(key=lambda x: x.date_obj)

    if len(recent_workouts) < 2:
        return 0.0

    # Compare first 3 vs last 3 workouts
    n = min(3, len(recent_workouts) // 2)
    first_weights = [w.weight for w in recent_workouts[:n]]
    last_weights = [w.weight for w in recent_workouts[-n:]]

    avg_first = statistics.mean(first_weights)
    avg_last = statistics.mean(last_weights)

    if avg_first == 0:
        return 0.0

    progression_pct = ((avg_last - avg_first) / avg_first) * 100
    return round(progression_pct, 2)


def assess_consistency(client: Client, weeks: int = 4) -> Dict[str, float]:
    """Assess workout consistency over specified weeks"""
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    recent_workouts = [w for w in client.workout_logs if w.date_obj >= cutoff_date]

    # Count unique workout days
    unique_days = len(set(w.date_obj.date() for w in recent_workouts))
    expected_workouts = client.target_workouts_per_week * weeks

    consistency_score = (unique_days / expected_workouts) * 100 if expected_workouts > 0 else 0
    missed_workouts_pct = 100 - consistency_score

    return {
        "consistency_score": round(min(consistency_score, 100), 2),
        "missed_workouts_pct": round(max(missed_workouts_pct, 0), 2),
        "actual_workouts": unique_days,
        "expected_workouts": expected_workouts
    }


def analyze_nutrition_compliance(client: Client, days: int = 14) -> Dict[str, float]:
    """Analyze nutrition tracking and compliance"""
    recent_nutrition = [n for n in client.nutrition_logs
                        if (datetime.now() - n.date_obj).days <= days]

    if not recent_nutrition:
        return {"compliance_score": 0, "avg_protein": 0, "avg_calories": 0}

    avg_protein = statistics.mean([n.protein for n in recent_nutrition])
    avg_calories = statistics.mean([n.calories for n in recent_nutrition])

    # Compliance based on hitting targets and logging meals
    protein_compliance = (avg_protein / client.target_protein) * 100 if client.target_protein > 0 else 0
    calorie_compliance = (avg_calories / client.target_calories) * 100 if client.target_calories > 0 else 0

    avg_meals_logged = statistics.mean([n.meals_logged for n in recent_nutrition])
    logging_compliance = (avg_meals_logged / 5) * 100

    overall_compliance = (protein_compliance + calorie_compliance + logging_compliance) / 3

    return {
        "compliance_score": round(min(overall_compliance, 100), 2),
        "avg_protein": round(avg_protein, 1),
        "avg_calories": round(avg_calories, 1),
        "protein_target_pct": round(protein_compliance, 2),
        "logging_compliance": round(logging_compliance, 2)
    }


def detect_strength_trend(client: Client, weeks: int = 3) -> str:
    """Detect if client is progressing, plateauing, or declining"""
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    recent_workouts = [w for w in client.workout_logs if w.date_obj >= cutoff_date]

    if not recent_workouts:
        return "insufficient_data"

    # Group by exercise and check trends
    exercises = set(w.exercise for w in recent_workouts)
    trends = []

    for exercise in exercises:
        exercise_logs = [w for w in recent_workouts if w.exercise == exercise]
        exercise_logs.sort(key=lambda x: x.date_obj)

        if len(exercise_logs) < 3:
            continue

        # Split into first half and second half
        mid = len(exercise_logs) // 2
        first_half = exercise_logs[:mid]
        second_half = exercise_logs[mid:]

        avg_first = statistics.mean([w.weight for w in first_half])
        avg_second = statistics.mean([w.weight for w in second_half])

        change_pct = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0

        if change_pct > 2:
            trends.append("improving")
        elif change_pct < -2:
            trends.append("declining")
        else:
            trends.append("plateau")

    if not trends:
        return "insufficient_data"

    return max(set(trends), key=trends.count)


def get_exercise_history(client: Client, exercise: str, weeks: int = 8) -> List[Dict]:
    """Get historical data for a specific exercise"""
    cutoff = datetime.now() - timedelta(weeks=weeks)
    exercise_logs = [
        w for w in client.workout_logs
        if w.exercise == exercise and w.date_obj >= cutoff
    ]
    exercise_logs.sort(key=lambda x: x.date_obj)

    return [{
        'date': w.date,
        'weight': w.weight,
        'sets': w.sets,
        'reps': w.reps,
        'volume': w.weight * w.sets * w.reps
    } for w in exercise_logs]


def analyze_client(client: Client) -> AnalysisResult:
    """Perform comprehensive client analysis"""
    progression = calculate_progression_rate(client)
    consistency = assess_consistency(client)
    nutrition = analyze_nutrition_compliance(client)
    trend = detect_strength_trend(client)

    return AnalysisResult(
        client_id=client.client_id,
        analysis_date=datetime.now().isoformat(),
        progression_rate=progression,
        consistency_score=consistency["consistency_score"],
        nutrition_compliance=nutrition["compliance_score"],
        missed_workouts_pct=consistency["missed_workouts_pct"],
        strength_trend=trend,
        actual_workouts=consistency["actual_workouts"],
        expected_workouts=consistency["expected_workouts"]
    )
