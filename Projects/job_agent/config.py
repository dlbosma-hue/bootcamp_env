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
MAX_HOURS_OLD = 180  # ~1 week with buffer — covers Mon-to-Mon window

RESULTS_PER_TERM = 10  # per search term per source

SCORE_THRESHOLDS = {
    "apply": 8,
    "maybe": 5,
}

STEPSTONE_RSS_TEMPLATE = (
    "https://www.stepstone.de/stellenangebote--{keyword}-berlin.html"
    "?rssFeed=true&radius=30"
)

JOBWARE_RSS_TEMPLATE = (
    "https://www.jobware.de/suche/stellen/"
    "?was={keyword}&wo=Berlin&umkreis=30&rss=1"
)
