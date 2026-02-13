"""
Data models for Fitness Coach AI
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
import json


@dataclass
class WorkoutEntry:
    """Single workout session data"""
    date: str  # ISO format string for JSON serialization
    exercise: str
    sets: int
    reps: int
    weight: float
    form_notes: str = ""
    completed: bool = True

    @property
    def date_obj(self) -> datetime:
        """Convert string date to datetime object"""
        return datetime.fromisoformat(self.date)

    @staticmethod
    def from_datetime(date: datetime, exercise: str, sets: int, reps: int,
                      weight: float, form_notes: str = "", completed: bool = True):
        """Create WorkoutEntry from datetime object"""
        return WorkoutEntry(
            date=date.isoformat(),
            exercise=exercise,
            sets=sets,
            reps=reps,
            weight=weight,
            form_notes=form_notes,
            completed=completed
        )


@dataclass
class NutritionEntry:
    """Daily nutrition tracking"""
    date: str  # ISO format string
    calories: int
    protein: int
    carbs: int
    fats: int
    meals_logged: int
    compliance_note: str = ""

    @property
    def date_obj(self) -> datetime:
        return datetime.fromisoformat(self.date)

    @staticmethod
    def from_datetime(date: datetime, calories: int, protein: int,
                      carbs: int, fats: int, meals_logged: int,
                      compliance_note: str = ""):
        return NutritionEntry(
            date=date.isoformat(),
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            meals_logged=meals_logged,
            compliance_note=compliance_note
        )


@dataclass
class Client:
    """Client profile with workout and nutrition history"""
    name: str
    client_id: str
    start_date: str  # ISO format string
    workout_logs: List[WorkoutEntry] = field(default_factory=list)
    nutrition_logs: List[NutritionEntry] = field(default_factory=list)
    target_workouts_per_week: int = 3
    target_calories: int = 2000
    target_protein: int = 150
    email: str = ""
    phone: str = ""
    notes: str = ""

    @property
    def start_date_obj(self) -> datetime:
        return datetime.fromisoformat(self.start_date)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'client_id': self.client_id,
            'start_date': self.start_date,
            'email': self.email,
            'phone': self.phone,
            'notes': self.notes,
            'target_workouts_per_week': self.target_workouts_per_week,
            'target_calories': self.target_calories,
            'target_protein': self.target_protein,
            'workout_logs': [asdict(w) for w in self.workout_logs],
            'nutrition_logs': [asdict(n) for n in self.nutrition_logs]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Client':
        """Create Client from dictionary"""
        client = Client(
            name=data['name'],
            client_id=data['client_id'],
            start_date=data['start_date'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            notes=data.get('notes', ''),
            target_workouts_per_week=data.get('target_workouts_per_week', 3),
            target_calories=data.get('target_calories', 2000),
            target_protein=data.get('target_protein', 150)
        )

        # Reconstruct workout logs
        for workout_data in data.get('workout_logs', []):
            client.workout_logs.append(WorkoutEntry(**workout_data))

        # Reconstruct nutrition logs
        for nutrition_data in data.get('nutrition_logs', []):
            client.nutrition_logs.append(NutritionEntry(**nutrition_data))

        return client


@dataclass
class ValidationResult:
    """Results from data validation checks"""
    is_valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Client performance analysis"""
    client_id: str
    analysis_date: str
    progression_rate: float
    consistency_score: float
    nutrition_compliance: float
    missed_workouts_pct: float
    strength_trend: str
    actual_workouts: int = 0
    expected_workouts: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """AI predictions about client behavior"""
    dropout_risk: str
    dropout_risk_score: float
    plateau_detected: bool
    weeks_at_plateau: int
    intervention_needed: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Recommendation:
    """AI-generated recommendations"""
    priority: str
    category: str
    suggestion: str
    reasoning: str
    requires_coach_approval: bool = True
    status: str = "pending"  # pending, approved, rejected
    coach_notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
