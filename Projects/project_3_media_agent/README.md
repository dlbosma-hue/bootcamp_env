# Autonomous Media Inclusivity Research Agent

**Organisation:** Media Diversity Watch
**Stack:** Python · LangGraph · OpenAI · Pinecone · FastAPI · N8N

An autonomous AI agent that investigates major news outlets and evaluates them through an intersectional inclusivity lens across four evaluation angles and four marginalised communities. The agent reasons, calls tools, retrieves benchmarks from a vector knowledge base, and generates structured audit reports without human intervention.

---

## What the Agent Does

The agent evaluates media companies across **4 communities**:
- Women and gender equality
- LGBTQ+ communities
- Racial and ethnic minorities
- People with disabilities

For each community, it investigates **4 angles**:
1. **Bylines and Story Selection** — who writes the stories, and which topics are they assigned to
2. **Portrayal Within Content** — are marginalised groups shown as experts/leaders or only as victims/statistics
3. **Sourcing Diversity** — who gets quoted as an authority
4. **Language and Framing** — inclusive vs harmful language patterns

Each company receives a score (1–10) per community, an overall average, and a list of harm flags and recommendations.

---

## Architecture

```
N8N Trigger (schedule / webhook / form)
        │
        ▼
POST /analyse  (FastAPI — app.py)
        │
        ▼
LangGraph ReAct Agent  (src/agents/media_agent.py)
        │
        ├── Tool 1: rag_query_tool       → Pinecone knowledge base (benchmarks)
        ├── Tool 2: search_wikipedia     → Company background (Wikipedia REST API)
        ├── Tool 3: search_newsapi       → Critic perspectives (NewsAPI)
        └── Tool 4: analyse_rss_feed     → Primary source: live RSS feed
        │
        ▼
Report Generator  (src/report_generator.py)
        │
        ▼
Markdown report saved to reports/  +  returned via API
```

---

## Project Structure

```
project_3_media_agent/
├── app.py                        # FastAPI server (entry point for N8N)
├── requirements.txt              # Python dependencies
├── .env                          # API keys (never commit this)
│
├── src/
│   ├── agents/
│   │   └── media_agent.py        # LangGraph ReAct agent
│   ├── tools/
│   │   ├── rss_tool.py           # Tool 4: RSS feed analyser
│   │   ├── wikipedia_tool.py     # Tool 2: Wikipedia search
│   │   ├── newsapi_tool.py       # Tool 3: NewsAPI search
│   │   └── rag_tool.py           # Tool 1: Pinecone RAG query
│   ├── rag_pipeline.py           # Core RAG retrieval function
│   └── report_generator.py       # Markdown report formatter
│
├── data/
│   └── project_config.json       # Research dimensions, scoring config
│
├── notebooks/
│   ├── day1_planning.ipynb       # Architecture planning and API setup
│   └── day2_rag.ipynb            # RAG pipeline and Pinecone ingestion
│
├── n8n/
│   ├── media_agent_workflow_updated.json  # N8N workflow (import this)
│   └── README.md                 # N8N setup instructions
│
├── reports/                      # Generated Markdown reports (auto-created)
└── media_inclusivity_kb.md       # Knowledge base source documents
```

---

## Setup

### 1. Clone and install dependencies

```bash
cd project_3_media_agent
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (never commit this):

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
NEWSAPI_KEY=...
ANTHROPIC_API_KEY=sk-ant-...   # optional, not used by default
```

### 3. Ensure the Pinecone index is populated

If you haven't run the Day 2 notebook yet, open and run all cells in:

```
notebooks/day2_rag.ipynb
```

This creates the `media-inclusivity-index` in Pinecone and ingests all 18 knowledge base documents.

---

## Running the Agent

### Option A: Python directly (quickest test)

From the project root:

```bash
python -c "
from src.agents.media_agent import run_research
from src.report_generator import generate_report, save_report

result = run_research('BBC')
report = generate_report('BBC', result['final_analysis'])
path = save_report('BBC', report)
print(f'Report saved to: {path}')
"
```

### Option B: FastAPI server (for N8N integration)

```bash
uvicorn app:app --reload --port 8000
```

Then trigger a report:

```bash
curl -X POST http://localhost:8000/analyse \
     -H "Content-Type: application/json" \
     -d '{"company": "BBC"}'
```

Or visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Option C: N8N automation

1. Import `n8n/media_agent_workflow_updated.json` into your N8N instance
2. Replace the placeholder ngrok URL in the HTTP Request node with your server URL
3. Connect your Notion account and create the required database (see `n8n/README.md`)
4. Activate the workflow

---

## Monitored Outlets

| Outlet | RSS Feed |
|---|---|
| BBC | `feeds.bbci.co.uk/news/rss.xml` |
| The Guardian | `theguardian.com/world/rss` |
| CNN | `rss.cnn.com/rss/edition.rss` |
| New York Times | `rss.nytimes.com/.../HomePage.xml` |
| Reuters | `feeds.reuters.com/reuters/topNews` |

---

## Report Format

Each generated report covers 11 sections:

1. Company Overview
2. Bylines and Story Selection
3. Portrayal Within Content
4. Sourcing Diversity
5. Language and Framing
6. Community-by-Community Findings
7. Key Strengths
8. Areas of Concern and Harm Flags
9. Inclusivity Score (1–10 per community + overall)
10. Recommendations
11. Sources and Evidence

Reports are saved to `reports/{company}_{date}.md`.

---

## Scoring System

Equal weight across all four communities. Scores based on:
- **9–10**: Industry leader — demonstrably above sector benchmarks
- **7–8**: Above average — solid practices with room for growth
- **5–6**: Meets minimum standards — typical for the industry
- **3–4**: Below average — systemic gaps identified
- **1–2**: Serious concerns — active harm patterns flagged

Companies are additionally flagged (`⚠️`) if they cause active harm — for example, consistent dehumanising language or crime-framing of minority groups.
