from dotenv import load_dotenv

load_dotenv()

# ── Search ────────────────────────────────────────────────────────────────────

SEARCH_TERMS = [
    "AI Product Manager",
    "Product Manager AI",
    "Senior Product Manager",
    "Platform Product Manager",
    "Product Manager Platform",
    "Technical Product Manager",
    "AI Consultant",
    "AI Integration Consultant",
    "AI Implementation Consultant",
    "AI Strategy Consultant",
    "AI Transformation Consultant",
    "Product Owner AI",
    "Digital Product Manager",
    "Product Manager Automation",
    "Product Manager SaaS",
    "Product Manager Operations",
    "KI Produktmanager",
    "Produktmanager KI",
    "KI Berater",
    "AI Produktmanager",
]

SECONDARY_TERMS = [
    "Product Manager",
    "LangChain",
    "LangGraph",
    "RAG Product Manager",
    "RAG Architect",
    "Agentic AI",
    "AI Workflow",
    "Workflow Automation PM",
    "Automation Consultant",
    "Product Manager e-commerce",
    "Product Manager Scrum",
    "Product Manager OKR",
    "AI-powered products",
    "Machine Learning Product Manager",
    "Product Manager Python",
    "Digitalisierung Produktmanagement",
    "Digitalisierungsberater",
    "AI Beratung",
    "n8n automation",
    "Prompt Engineering",
    "LLM Product Manager",
    "EU AI Act",
]

EXCLUDE_TERMS = [
    "junior",
    "trainee",
    "werkstudent",
    "praktikum",
    "ausbildung",
    "kein homeoffice",
    "data scientist",
    "data engineer",
    "software engineer",
    "developer",
    "vollzeit vor ort",
]

# ── Location & scraping ───────────────────────────────────────────────────────

LOCATION = "Berlin, Germany"
DISTANCE_KM = 30
RESULTS_PER_TERM = 20
MAX_HOURS_OLD = 48          # daily run — look back 48h for safety

# ── Scoring ───────────────────────────────────────────────────────────────────

SCORE_THRESHOLDS = {
    "apply": 8,
    "maybe": 5,
    "skip":  4,
}

OPENAI_MODEL        = "gpt-4o"        # second pass + cover letters
OPENAI_FILTER_MODEL = "gpt-4o-mini"   # first pass — filters all jobs fast
FILTER_PASS_THRESHOLD = 4             # re-score with gpt-4o only if mini scores ≥ this
SCORING_WORKERS = 8                   # parallel scoring threads

# ── Email ─────────────────────────────────────────────────────────────────────

MIN_EMAIL_SCORE = 5         # include "maybe" (5-7) and "apply" (8-10) in digest
