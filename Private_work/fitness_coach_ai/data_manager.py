"""
Data persistence layer for saving/loading client data
"""

import json
import os
from pathlib import Path
from typing import List, Optional
import pandas as pd
from datetime import datetime

from models import Client, WorkoutEntry, NutritionEntry


class DataManager:
    """Manages client data persistence"""

    def __init__(self, data_dir: str = "data/clients"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_client(self, client: Client) -> bool:
        """Save client data to JSON file"""
        try:
            filepath = self.data_dir / f"{client.client_id}.json"
            with open(filepath, 'w') as f:
                json.dump(client.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving client: {e}")
            return False

    def load_client(self, client_id: str) -> Optional[Client]:
        """Load client data from JSON file"""
        try:
            filepath = self.data_dir / f"{client_id}.json"
            if not filepath.exists():
                return None

            with open(filepath, 'r') as f:
                data = json.load(f)
            return Client.from_dict(data)
        except Exception as e:
            print(f"Error loading client: {e}")
            return None

    def list_all_clients(self) -> List[str]:
        """List all client IDs"""
        client_ids = []
        for filepath in self.data_dir.glob("*.json"):
            client_ids.append(filepath.stem)
        return sorted(client_ids)

    def get_all_clients(self) -> List[Client]:
        """Load all clients"""
        clients = []
        for client_id in self.list_all_clients():
            client = self.load_client(client_id)
            if client:
                clients.append(client)
        return clients

    def delete_client(self, client_id: str) -> bool:
        """Delete client data"""
        try:
            filepath = self.data_dir / f"{client_id}.json"
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False

    def export_client_to_csv(self, client: Client, output_dir: str = "exports") -> bool:
        """Export client data to CSV files"""
        try:
            export_path = Path(output_dir)
            export_path.mkdir(parents=True, exist_ok=True)

            # Export workouts
            if client.workout_logs:
                workout_data = []
                for w in client.workout_logs:
                    workout_data.append({
                        'date': w.date,
                        'exercise': w.exercise,
                        'sets': w.sets,
                        'reps': w.reps,
                        'weight': w.weight,
                        'form_notes': w.form_notes,
                        'completed': w.completed
                    })
                df_workouts = pd.DataFrame(workout_data)
                df_workouts.to_csv(
                    export_path / f"{client.client_id}_workouts.csv",
                    index=False
                )

            # Export nutrition
            if client.nutrition_logs:
                nutrition_data = []
                for n in client.nutrition_logs:
                    nutrition_data.append({
                        'date': n.date,
                        'calories': n.calories,
                        'protein': n.protein,
                        'carbs': n.carbs,
                        'fats': n.fats,
                        'meals_logged': n.meals_logged,
                        'compliance_note': n.compliance_note
                    })
                df_nutrition = pd.DataFrame(nutrition_data)
                df_nutrition.to_csv(
                    export_path / f"{client.client_id}_nutrition.csv",
                    index=False
                )

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def import_workouts_from_csv(self, client_id: str, csv_path: str) -> bool:
        """Import workout data from CSV"""
        try:
            client = self.load_client(client_id)
            if not client:
                print(f"Client {client_id} not found")
                return False

            df = pd.read_csv(csv_path)

            for _, row in df.iterrows():
                workout = WorkoutEntry(
                    date=row['date'],
                    exercise=row['exercise'],
                    sets=int(row['sets']),
                    reps=int(row['reps']),
                    weight=float(row['weight']),
                    form_notes=row.get('form_notes', ''),
                    completed=bool(row.get('completed', True))
                )
                client.workout_logs.append(workout)

            return self.save_client(client)
        except Exception as e:
            print(f"Error importing workouts: {e}")
            return False

    def import_nutrition_from_csv(self, client_id: str, csv_path: str) -> bool:
        """Import nutrition data from CSV"""
        try:
            client = self.load_client(client_id)
            if not client:
                print(f"Client {client_id} not found")
                return False

            df = pd.read_csv(csv_path)

            for _, row in df.iterrows():
                nutrition = NutritionEntry(
                    date=row['date'],
                    calories=int(row['calories']),
                    protein=int(row['protein']),
                    carbs=int(row['carbs']),
                    fats=int(row['fats']),
                    meals_logged=int(row['meals_logged']),
                    compliance_note=row.get('compliance_note', '')
                )
                client.nutrition_logs.append(nutrition)

            return self.save_client(client)
        except Exception as e:
            print(f"Error importing nutrition: {e}")
            return False

    def backup_all_data(self, backup_dir: str = "backups") -> bool:
        """Create backup of all client data"""
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"backup_{timestamp}.json"

            all_clients = [c.to_dict() for c in self.get_all_clients()]

            with open(backup_file, 'w') as f:
                json.dump(all_clients, f, indent=2)

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
