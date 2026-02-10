"""
AI recommendation engine
"""

from typing import List
from models import Client, AnalysisResult, Prediction, Recommendation


def generate_recommendations(
    client: Client,
    analysis: AnalysisResult,
    prediction: Prediction
) -> List[Recommendation]:
    """Generate AI recommendations for coach to review and approve"""
    recommendations = []

    # High priority: Dropout risk
    if prediction.dropout_risk == "high":
        recommendations.append(Recommendation(
            priority="high",
            category="motivation",
            suggestion=f"Schedule urgent check-in call with {client.name} this week",
            reasoning=(
                f"Dropout risk is HIGH ({prediction.dropout_risk_score:.0f}%). "
                f"Client has missed {analysis.missed_workouts_pct:.1f}% of workouts "
                f"and shows declining engagement. Early intervention critical."
            )
        ))

    # Medium priority dropout risk
    elif prediction.dropout_risk == "medium":
        recommendations.append(Recommendation(
            priority="medium",
            category="motivation",
            suggestion=f"Send check-in message to {client.name}",
            reasoning=(
                f"Dropout risk is MEDIUM ({prediction.dropout_risk_score:.0f}%). "
                f"Proactive communication may prevent further decline."
            )
        ))

    # Plateau intervention
    if prediction.plateau_detected and prediction.weeks_at_plateau >= 3:
        recommendations.append(Recommendation(
            priority="high",
            category="workout",
            suggestion="Implement deload week or program variation",
            reasoning=(
                f"Strength plateau detected for {prediction.weeks_at_plateau} weeks. "
                f"Options: (1) Deload to 80% for 1 week, "
                f"(2) Switch to different rep range (5x5 → 3x12), "
                f"(3) Change exercise variation, or (4) Video form analysis."
            )
        ))

    # Missed workouts - suggest frequency adjustment
    if analysis.missed_workouts_pct > 30 and analysis.missed_workouts_pct < 70:
        recommendations.append(Recommendation(
            priority="medium" if prediction.dropout_risk == "low" else "high",
            category="workout",
            suggestion="Reduce workout frequency to build consistency",
            reasoning=(
                f"Client missing {analysis.missed_workouts_pct:.1f}% of workouts. "
                f"Current target of {client.target_workouts_per_week}x/week may be too ambitious. "
                f"Suggest reducing to {max(2, client.target_workouts_per_week - 1)}x/week "
                f"to establish sustainable habit."
            )
        ))

    # Very poor attendance
    if analysis.missed_workouts_pct >= 70:
        recommendations.append(Recommendation(
            priority="high",
            category="motivation",
            suggestion="Reassess client goals and barriers",
            reasoning=(
                f"Client attending only {100 - analysis.missed_workouts_pct:.1f}% of planned workouts. "
                f"Schedule call to identify barriers: time constraints, injury, motivation, "
                f"or need to pause program."
            )
        ))

    # Nutrition compliance
    if analysis.nutrition_compliance < 70 and analysis.nutrition_compliance >= 40:
        recommendations.append(Recommendation(
            priority="medium",
            category="nutrition",
            suggestion="Simplify nutrition tracking approach",
            reasoning=(
                f"Nutrition compliance at {analysis.nutrition_compliance:.1f}%. "
                f"Options: (1) Track protein only, "
                f"(2) Use hand-portion method, "
                f"(3) Reduce to 3 meals/day tracking, or "
                f"(4) Weekly check-ins instead of daily."
            )
        ))

    # Very poor nutrition tracking
    elif analysis.nutrition_compliance < 40:
        recommendations.append(Recommendation(
            priority="high",
            category="nutrition",
            suggestion="Address nutrition tracking barriers",
            reasoning=(
                f"Nutrition compliance critically low ({analysis.nutrition_compliance:.1f}%). "
                f"Schedule call to identify if: tracking is too complex, "
                f"client doesn't see value, or different approach needed."
            )
        ))

    # Declining performance
    if analysis.strength_trend == "declining":
        recommendations.append(Recommendation(
            priority="high",
            category="workout",
            suggestion="Investigate causes of performance decline",
            reasoning=(
                "Strength is declining. Possible causes: "
                "(1) Inadequate recovery/sleep, "
                "(2) Under-eating, "
                "(3) Life stress, "
                "(4) Overtraining, or "
                "(5) Injury/pain. Schedule assessment call."
            )
        ))

    # Poor progression but attending workouts
    if (analysis.progression_rate < 5 and
        analysis.consistency_score > 70 and
        not prediction.plateau_detected):
        recommendations.append(Recommendation(
            priority="medium",
            category="workout",
            suggestion="Review progressive overload strategy",
            reasoning=(
                f"Client consistent ({analysis.consistency_score:.1f}%) "
                f"but minimal progression ({analysis.progression_rate:.1f}%). "
                f"May need: (1) Smaller weight jumps, "
                f"(2) Focus on volume progression, or "
                f"(3) Different periodization scheme."
            )
        ))

    # Positive reinforcement for good progress
    if (analysis.progression_rate > 10 and
        analysis.consistency_score > 80 and
        prediction.dropout_risk == "low"):
        recommendations.append(Recommendation(
            priority="low",
            category="motivation",
            suggestion=f"Celebrate {client.name}'s excellent progress",
            reasoning=(
                f"Outstanding results: {analysis.progression_rate:.1f}% strength improvement "
                f"with {analysis.consistency_score:.1f}% consistency. "
                f"Send recognition message or consider milestone reward."
            ),
            requires_coach_approval=False
        ))

    # Good consistency but can optimize nutrition
    if (analysis.consistency_score > 85 and
        70 <= analysis.nutrition_compliance < 90):
        recommendations.append(Recommendation(
            priority="low",
            category="nutrition",
            suggestion="Fine-tune nutrition for optimal results",
            reasoning=(
                f"Excellent workout adherence ({analysis.consistency_score:.1f}%). "
                f"Small nutrition improvements could enhance results. "
                f"Consider macro adjustments or meal timing optimization."
            )
        ))

    # Suggest progression to next phase
    if (analysis.progression_rate > 15 and
        analysis.consistency_score > 85 and
        analysis.nutrition_compliance > 85):
        recommendations.append(Recommendation(
            priority="medium",
            category="workout",
            suggestion="Consider advancing to next training phase",
            reasoning=(
                f"Client excelling across all metrics. "
                f"Ready for: (1) More advanced program, "
                f"(2) Additional training days, "
                f"(3) New skill development, or "
                f"(4) Performance testing."
            )
        ))

    return recommendations


def prioritize_recommendations(recommendations: List[Recommendation]) -> List[Recommendation]:
    """Sort recommendations by priority"""
    priority_order = {"high": 0, "medium": 1, "low": 2}
    return sorted(recommendations, key=lambda r: priority_order[r.priority])


def format_recommendation_for_display(rec: Recommendation, index: int) -> str:
    """Format recommendation for terminal display"""
    priority_emoji = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    output = f"\n{priority_emoji[rec.priority]} Recommendation #{index} [{rec.category.upper()}]\n"
    output += f"   {rec.suggestion}\n\n"
    output += f"   Reasoning:\n"

    for line in rec.reasoning.split(". "):
        if line.strip():
            output += f"   • {line.strip('.')}.\n"

    if rec.requires_coach_approval:
        status_emoji = "⏳" if rec.status == "pending" else "✓" if rec.status == "approved" else "❌"
        output += f"\n   {status_emoji} Status: {rec.status.upper()}"
        if rec.coach_notes:
            output += f"\n   Coach Notes: {rec.coach_notes}"
    else:
        output += f"\n   ✓ Status: AUTO-APPROVED"

    return output
