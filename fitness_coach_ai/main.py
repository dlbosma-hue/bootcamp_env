"""
Fitness Coach AI - Main Entry Point
"""

import sys
import argparse
from datetime import datetime, timedelta

from models import Client, WorkoutEntry, NutritionEntry
from data_manager import DataManager
from cli import run as run_cli


def generate_demo_data():
    """Generate demo client data for testing"""
    data_manager = DataManager()

    print("Generating demo data...")

    # Client 1: At-risk client
    client1 = Client(
        name="John Smith",
        client_id="JS001",
        start_date=(datetime.now() - timedelta(weeks=6)).isoformat(),
        email="john.smith@example.com",
        phone="555-0101",
        target_workouts_per_week=4,
        target_calories=2200,
        target_protein=160
    )

    exercises = ["Squat", "Bench Press", "Deadlift", "Overhead Press"]
    base_date = client1.start_date_obj

    # Weeks 1-3: Good progression
    for week in range(3):
        for day in [0, 2, 4, 6]:
            workout_date = base_date + timedelta(weeks=week, days=day)
            for exercise in exercises:
                base_weight = 135 + (week * 10)
                client1.workout_logs.append(WorkoutEntry.from_datetime(
                    date=workout_date,
                    exercise=exercise,
                    sets=3,
                    reps=8,
                    weight=base_weight,
                    form_notes="Good form" if week < 2 else "Form breaking down slightly",
                    completed=True
                ))

    # Weeks 4-5: Plateau and missed workouts
    for week in range(3, 5):
        for day in [0, 4]:
            workout_date = base_date + timedelta(weeks=week, days=day)
            for exercise in exercises:
                client1.workout_logs.append(WorkoutEntry.from_datetime(
                    date=workout_date,
                    exercise=exercise,
                    sets=3,
                    reps=8,
                    weight=165,
                    form_notes="Struggling with weight",
                    completed=True
                ))

    # Week 6: More missed workouts
    workout_date = base_date + timedelta(weeks=5, days=0)
    for exercise in exercises:
        client1.workout_logs.append(WorkoutEntry.from_datetime(
            date=workout_date,
            exercise=exercise,
            sets=3,
            reps=8,
            weight=165,
            form_notes="Low energy",
            completed=True
        ))

    # Nutrition data
    for week in range(6):
        for day in range(7):
            nutrition_date = base_date + timedelta(weeks=week, days=day)
            compliance_factor = 1.0 - (week * 0.1)
            client1.nutrition_logs.append(NutritionEntry.from_datetime(
                date=nutrition_date,
                calories=int(client1.target_calories * compliance_factor),
                protein=int(client1.target_protein * compliance_factor),
                carbs=250,
                fats=70,
                meals_logged=max(3, 5 - week),
                compliance_note="On track" if week < 3 else "Missing meals"
            ))

    data_manager.save_client(client1)
    print(f"✓ Created client: {client1.name}")

    # Client 2: Successful client
    client2 = Client(
        name="Sarah Johnson",
        client_id="SJ002",
        start_date=(datetime.now() - timedelta(weeks=6)).isoformat(),
        email="sarah.johnson@example.com",
        phone="555-0102",
        target_workouts_per_week=3,
        target_calories=1800,
        target_protein=130
    )

    exercises2 = ["Squat", "Bench Press", "Deadlift"]
    base_date2 = client2.start_date_obj

    # Consistent progression over 6 weeks
    for week in range(6):
        for day in [0, 2, 5]:
            workout_date = base_date2 + timedelta(weeks=week, days=day)
            for exercise in exercises2:
                base_weight = 95 + (week * 5)
                client2.workout_logs.append(WorkoutEntry.from_datetime(
                    date=workout_date,
                    exercise=exercise,
                    sets=3,
                    reps=10,
                    weight=base_weight,
                    form_notes="Excellent form",
                    completed=True
                ))

    # Consistent nutrition
    for week in range(6):
        for day in range(7):
            nutrition_date = base_date2 + timedelta(weeks=week, days=day)
            client2.nutrition_logs.append(NutritionEntry.from_datetime(
                date=nutrition_date,
                calories=client2.target_calories,
                protein=client2.target_protein,
                carbs=180,
                fats=60,
                meals_logged=5,
                compliance_note="Excellent compliance"
            ))

    data_manager.save_client(client2)
    print(f"✓ Created client: {client2.name}")

    # Client 3: New client with limited data
    client3 = Client(
        name="Mike Davis",
        client_id="MD003",
        start_date=(datetime.now() - timedelta(weeks=2)).isoformat(),
        email="mike.davis@example.com",
        phone="555-0103",
        target_workouts_per_week=3,
        target_calories=2400,
        target_protein=180
    )

    # Only 2 weeks of data
    exercises3 = ["Squat", "Bench Press", "Barbell Row", "Overhead Press"]
    base_date3 = client3.start_date_obj

    for week in range(2):
        for day in [1, 3, 5]:
            workout_date = base_date3 + timedelta(weeks=week, days=day)
            for exercise in exercises3:
                client3.workout_logs.append(WorkoutEntry.from_datetime(
                    date=workout_date,
                    exercise=exercise,
                    sets=4,
                    reps=6,
                    weight=185 + (week * 5),
                    form_notes="Good",
                    completed=True
                ))

    # Nutrition
    for week in range(2):
        for day in range(7):
            nutrition_date = base_date3 + timedelta(weeks=week, days=day)
            client3.nutrition_logs.append(NutritionEntry.from_datetime(
                date=nutrition_date,
                calories=client3.target_calories + 100,
                protein=client3.target_protein + 10,
                carbs=300,
                fats=80,
                meals_logged=5,
                compliance_note="Great start"
            ))

    data_manager.save_client(client3)
    print(f"✓ Created client: {client3.name}")

    print("\nDemo data generated successfully!")
    print("You can now view and manage these clients in the application.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Fitness Coach AI Assistant - Intelligent client management"
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Generate demo data for testing'
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run interactive CLI (default)'
    )

    args = parser.parse_args()

    if args.demo:
        generate_demo_data()
        return

    # Default to CLI
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
