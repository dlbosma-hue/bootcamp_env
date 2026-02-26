# LAB M1.01 - HomeGuard Security System

## Use Case
Build a smart home monitoring simulator for the Peterson family's vacation home. The system reads sensor data, checks thresholds, triggers alerts, and logs events.

## Key Concepts
- Conditional logic with if/else to check sensor thresholds
- Dictionaries to represent sensors, alerts, and system state
- Functions to process data and trigger alerts
- A Sensor class with properties and methods

## Core Functions Built
- `generate_reading(sensor)` - produces a simulated sensor value within a defined range
- `process_reading(sensor, reading)` - checks if the reading exceeds the threshold and returns alert status
- `trigger_alert(sensor, reading)` - formats and prints an alert message when a threshold is crossed
- `log_event(event_type, sensor_name, value)` - appends a timestamped event to the event log list

## The Sensor Class
```python
class Sensor:
    def __init__(self, name, sensor_type, min_val, max_val, threshold):
        self.name = name
        self.sensor_type = sensor_type
        self.min_val = min_val
        self.max_val = max_val
        self.threshold = threshold
```

## Key Learning
- Always define functions BEFORE calling them to avoid NameError
- Dictionaries are used to group related data (e.g. one dict per sensor with name, type, threshold)
- The golden rule: define all functions first, then data setup, then usage

## Submission
Jupyter notebook with all sensors readable, alerts triggered correctly, formatted output matching sample, and comments on each section.
