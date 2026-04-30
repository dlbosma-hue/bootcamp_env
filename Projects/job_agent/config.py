SEARCH_TERMS = [
    "IT Leiter",
    "Head of IT",
    "IT Director",
    "IT Strategist",
    "IT Architect",
    "CIO Advisory",
    "IT Governance",
    "IT Infrastructure Manager",
    "Abteilungsleiter IT",
    "Gruppenleiter IT",
    "IT Consulting",
    "Digital Transformation Lead",
    "IT Portfolio Manager",
    "PMO Lead IT",
    "IT Service Management",
]

SECONDARY_TERMS = [
    "Senior IT Manager",
    "Enterprise Architect",
    "IT Operations Manager",
    "Cloud Infrastructure Manager",
    "IT-Berater",
    "Management Consultant IT",
]

EXCLUDE_TERMS = [
    "junior", "trainee", "werkstudent", "praktikum", "ausbildung", "quereinsteiger",
]

LOCATION = "Berlin, Germany"
DISTANCE_KM = 30
MAX_HOURS_OLD = 48  # daily run — look back 48h for safety

RESULTS_PER_TERM = 10  # per search term per source

SCORE_THRESHOLDS = {
    "apply": 8,
    "maybe": 5,
}

