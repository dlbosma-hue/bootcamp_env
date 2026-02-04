import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# Use absolute path
script_dir = Path("/Users/dinabosmabuczynska/Desktop/bootcamp_env/Lab2_Day1")
csv_file = script_dir / "data" / "titanic.csv"
json_file = script_dir / "data" / "titanic_processed.json"

df = pd.read_csv(csv_file)

df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

def age_group(age):
    if pd.isna(age):
        return 'Unknown'
    elif age < 18:
        return 'Child'
    elif age < 30:
        return 'Young Adult'
    elif age < 50:
        return 'Middle Age'
    else:
        return 'Senior'

df['AgeGroup'] = df['Age'].apply(age_group)

print("="*70)
print("STEPS 1-5 COMPLETE")
print("="*70)

class Passenger:
    def __init__(self, passenger_id, name, age, sex, survived, pclass, fare, embarked=None, family_size=None, is_alone=None, age_group=None):
        self.passenger_id = int(passenger_id) if pd.notna(passenger_id) else None
        self.name = str(name) if pd.notna(name) else None
        self.age = float(age) if pd.notna(age) else None
        self.sex = str(sex) if pd.notna(sex) else None
        self.survived = int(survived) if pd.notna(survived) else None
        self.pclass = int(pclass) if pd.notna(pclass) else None
        self.fare = float(fare) if pd.notna(fare) else None
        self.embarked = str(embarked) if pd.notna(embarked) else None
        self.family_size = int(family_size) if pd.notna(family_size) else None
        self.is_alone = int(is_alone) if pd.notna(is_alone) else None
        self.age_group = str(age_group) if pd.notna(age_group) else None
    
    def to_dict(self):
        return {'passenger_id': self.passenger_id, 'name': self.name, 'age': self.age, 'sex': self.sex, 'survived': self.survived, 'pclass': self.pclass, 'fare': self.fare, 'embarked': self.embarked, 'family_size': self.family_size, 'is_alone': self.is_alone, 'age_group': self.age_group}

class TitanicDataset:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.passengers = []
        self._create_passengers()
    
    def _create_passengers(self):
        for idx, row in self.dataframe.iterrows():
            passenger = Passenger(passenger_id=row['PassengerId'], name=row['Name'], age=row['Age'], sex=row['Sex'], survived=row['Survived'], pclass=row['Pclass'], fare=row['Fare'], embarked=row.get('Embarked'), family_size=row.get('FamilySize'), is_alone=row.get('IsAlone'), age_group=row.get('AgeGroup'))
            self.passengers.append(passenger)
    
    def get_summary_stats(self):
        total = len(self.passengers)
        survived = sum(1 for p in self.passengers if p.survived == 1)
        not_survived = total - survived
        ages = [p.age for p in self.passengers if p.age is not None]
        fares = [p.fare for p in self.passengers if p.fare is not None]
        avg_age = np.mean(ages) if ages else 0
        avg_fare = np.mean(fares) if fares else 0
        return {'total_passengers': total, 'survived': survived, 'not_survived': not_survived, 'survival_rate': (survived / total * 100) if total > 0 else 0, 'average_age': round(avg_age, 2), 'average_fare': round(avg_fare, 2)}
    
    def to_json(self, filename):
        stats = self.get_summary_stats()
        data = {'metadata': {'dataset_name': 'Titanic Passenger Dataset', 'total_passengers': stats['total_passengers'], 'survived_count': stats['survived'], 'not_survived_count': stats['not_survived'], 'survival_rate_percent': round(stats['survival_rate'], 2), 'average_age': stats['average_age'], 'average_fare': stats['average_fare'], 'export_date': datetime.now().isoformat()}, 'passengers': [p.to_dict() for p in self.passengers]}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"OK: Data exported to {filename}")
        return data

print("\n" + "="*70)
print("STEP 6: CLASSES CREATED")
print("="*70)

dataset = TitanicDataset(df)
stats = dataset.get_summary_stats()

print(f"Total passengers: {stats['total_passengers']}")
print(f"Survived: {stats['survived']}")
print(f"Not survived: {stats['not_survived']}")
print(f"Survival rate: {stats['survival_rate']:.2f}%")
print(f"Average age: {stats['average_age']}")
print(f"Average fare: ${stats['average_fare']}")

print("\n" + "="*70)
print("STEP 7: EXPORTING TO JSON")
print("="*70)

dataset.to_json(str(json_file))

print("\n" + "="*70)
print("VALIDATING JSON")
print("="*70)

try:
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    print("OK: JSON file is valid")
    print(f"Passengers in JSON: {len(json_data['passengers'])}")
    print(f"First passenger: {json_data['passengers'][0]['name']}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
