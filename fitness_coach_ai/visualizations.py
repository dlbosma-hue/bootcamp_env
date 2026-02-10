"""
Data visualization and charting
"""

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List
import statistics
from pathlib import Path

from models import Client
from analysis import get_exercise_history

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_strength_progression(client: Client, exercise: str,
                              output_path: str = None) -> str:
    """Plot strength progression over time for an exercise"""
    history = get_exercise_history(client, exercise, weeks=12)

    if not history:
        return None

    dates = [datetime.fromisoformat(h['date']) for h in history]
    weights = [h['weight'] for h in history]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, weights, marker='o', linewidth=2, markersize=8,
            label='Actual Weight')

    # Add trend line
    x_numeric = list(range(len(dates)))
    z = np.polyfit(x_numeric, weights, 1)
    p = np.poly1d(z)
    ax.plot(dates, p(x_numeric), "--", alpha=0.5, linewidth=2,
            label='Trend', color='orange')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Weight (lbs)', fontsize=12)
    ax.set_title(f'{client.name} - {exercise} Progression', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        output_dir = Path("exports/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{client.client_id}_{exercise}_progression.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
    return str(output_path)


def plot_workout_consistency(client: Client, weeks: int = 8,
                             output_path: str = None) -> str:
    """Plot workout consistency over time"""
    cutoff = datetime.now() - timedelta(weeks=weeks)
    workouts = [w for w in client.workout_logs if w.date_obj >= cutoff]

    if not workouts:
        return None

    # Count workouts per week
    workouts_by_week = {}
    for w in workouts:
        week_num = (w.date_obj - cutoff).days // 7
        workouts_by_week[week_num] = workouts_by_week.get(week_num, 0) + 1

    # Get unique days per week (more accurate)
    unique_days_by_week = {}
    for w in workouts:
        week_num = (w.date_obj - cutoff).days // 7
        if week_num not in unique_days_by_week:
            unique_days_by_week[week_num] = set()
        unique_days_by_week[week_num].add(w.date_obj.date())

    weeks_list = sorted(unique_days_by_week.keys())
    workout_counts = [len(unique_days_by_week[w]) for w in weeks_list]

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['green' if count >= client.target_workouts_per_week else 'orange'
              if count >= client.target_workouts_per_week - 1 else 'red'
              for count in workout_counts]

    ax.bar(weeks_list, workout_counts, color=colors, alpha=0.7, edgecolor='black')
    ax.axhline(y=client.target_workouts_per_week, color='blue', linestyle='--',
               linewidth=2, label=f'Target ({client.target_workouts_per_week}/week)')

    ax.set_xlabel('Week Number', fontsize=12)
    ax.set_ylabel('Workouts Completed', fontsize=12)
    ax.set_title(f'{client.name} - Workout Consistency', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        output_dir = Path("exports/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{client.client_id}_consistency.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
    return str(output_path)


def plot_nutrition_compliance(client: Client, weeks: int = 4,
                              output_path: str = None) -> str:
    """Plot nutrition compliance over time"""
    cutoff = datetime.now() - timedelta(weeks=weeks)
    nutrition = [n for n in client.nutrition_logs if n.date_obj >= cutoff]

    if not nutrition:
        return None

    # Group by week
    protein_by_week = {}
    calories_by_week = {}

    for n in nutrition:
        week_num = (n.date_obj - cutoff).days // 7
        if week_num not in protein_by_week:
            protein_by_week[week_num] = []
            calories_by_week[week_num] = []
        protein_by_week[week_num].append(n.protein)
        calories_by_week[week_num].append(n.calories)

    weeks_list = sorted(protein_by_week.keys())
    avg_protein = [statistics.mean(protein_by_week[w]) for w in weeks_list]
    avg_calories = [statistics.mean(calories_by_week[w]) for w in weeks_list]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Protein plot
    ax1.plot(weeks_list, avg_protein, marker='o', linewidth=2, markersize=8,
             color='red', label='Actual')
    ax1.axhline(y=client.target_protein, color='blue', linestyle='--',
                linewidth=2, label=f'Target ({client.target_protein}g)')
    ax1.set_xlabel('Week Number', fontsize=12)
    ax1.set_ylabel('Protein (g)', fontsize=12)
    ax1.set_title(f'{client.name} - Protein Intake', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Calories plot
    ax2.plot(weeks_list, avg_calories, marker='o', linewidth=2, markersize=8,
             color='green', label='Actual')
    ax2.axhline(y=client.target_calories, color='blue', linestyle='--',
                linewidth=2, label=f'Target ({client.target_calories} cal)')
    ax2.set_xlabel('Week Number', fontsize=12)
    ax2.set_ylabel('Calories', fontsize=12)
    ax2.set_title(f'{client.name} - Calorie Intake', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        output_dir = Path("exports/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{client.client_id}_nutrition.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
    return str(output_path)


def plot_multi_exercise_comparison(client: Client, exercises: List[str],
                                   weeks: int = 8, output_path: str = None) -> str:
    """Plot multiple exercises on the same chart for comparison"""
    fig, ax = plt.subplots(figsize=(14, 7))

    colors = plt.cm.tab10(range(len(exercises)))

    for exercise, color in zip(exercises, colors):
        history = get_exercise_history(client, exercise, weeks=weeks)
        if history:
            dates = [datetime.fromisoformat(h['date']) for h in history]
            weights = [h['weight'] for h in history]
            ax.plot(dates, weights, marker='o', linewidth=2, markersize=6,
                   label=exercise, color=color)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Weight (lbs)', fontsize=12)
    ax.set_title(f'{client.name} - Multi-Exercise Progression', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        output_dir = Path("exports/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{client.client_id}_multi_exercise.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
    return str(output_path)


def plot_volume_progression(client: Client, exercise: str,
                           weeks: int = 8, output_path: str = None) -> str:
    """Plot training volume (weight x sets x reps) over time"""
    history = get_exercise_history(client, exercise, weeks=weeks)

    if not history:
        return None

    dates = [datetime.fromisoformat(h['date']) for h in history]
    volumes = [h['volume'] for h in history]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, volumes, marker='o', linewidth=2, markersize=8,
            color='purple', label='Training Volume')

    # Add trend line
    x_numeric = list(range(len(dates)))
    z = np.polyfit(x_numeric, volumes, 1)
    p = np.poly1d(z)
    ax.plot(dates, p(x_numeric), "--", alpha=0.5, linewidth=2,
            label='Trend', color='orange')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume (lbs × reps)', fontsize=12)
    ax.set_title(f'{client.name} - {exercise} Volume Progression', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        output_dir = Path("exports/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{client.client_id}_{exercise}_volume.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.close()
    return str(output_path)


def generate_all_charts(client: Client) -> List[str]:
    """Generate all relevant charts for a client"""
    chart_paths = []

    # Get all exercises
    exercises = list(set(w.exercise for w in client.workout_logs))

    # Consistency chart
    consistency_path = plot_workout_consistency(client)
    if consistency_path:
        chart_paths.append(consistency_path)

    # Nutrition chart
    nutrition_path = plot_nutrition_compliance(client)
    if nutrition_path:
        chart_paths.append(nutrition_path)

    # Individual exercise progressions (top 4 exercises by frequency)
    exercise_counts = {}
    for w in client.workout_logs:
        exercise_counts[w.exercise] = exercise_counts.get(w.exercise, 0) + 1

    top_exercises = sorted(exercise_counts.items(), key=lambda x: x[1], reverse=True)[:4]

    for exercise, _ in top_exercises:
        strength_path = plot_strength_progression(client, exercise)
        if strength_path:
            chart_paths.append(strength_path)

    # Multi-exercise comparison
    if len(top_exercises) > 1:
        multi_path = plot_multi_exercise_comparison(
            client,
            [ex for ex, _ in top_exercises]
        )
        if multi_path:
            chart_paths.append(multi_path)

    return chart_paths


# Import numpy for trend lines
import numpy as np
