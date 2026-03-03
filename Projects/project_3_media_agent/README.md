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
│   ├── day2_rag.ipynb            # RAG pipeline and Pinecone ingestion
│   ├── day3_agent.ipynb          # LangGraph agent build and tool testing
│   └── day4_integration.ipynb   # FastAPI, N8N integration, end-to-end testing
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
OPENAI_API_KEY=sk-...           # used by LangGraph agent (gpt-4o-mini)
PINECONE_API_KEY=pcsk_...       # used by RAG pipeline (media-inclusivity-index)
NEWSAPI_KEY=...                  # used by newsapi_tool.py
ANTHROPIC_API_KEY=sk-ant-...    # required — used by report_generator.py (claude-sonnet-4-6)
GUARDIAN_API_KEY=...             # used by rss_tool.py for Guardian full article body
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

result = run_research('The Guardian')
report = generate_report('The Guardian', result['final_analysis'])
path = save_report('The Guardian', report)
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
     -d '{"company": "The Guardian"}'
```

Or visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Option C: N8N automation

**Prerequisites:** N8N Cloud requires a publicly reachable URL. Use ngrok to expose your local FastAPI server:

```bash
# Terminal 1 — start FastAPI
cd project_3_media_agent
uvicorn app:app --port 8000

# Terminal 2 — expose via ngrok
ngrok http 8000
# Copy the https://xxxxx.ngrok-free.app URL
```

1. Import `n8n/media_agent_workflow_updated.json` into your N8N instance
2. In the **HTTP Request** node, replace the placeholder URL with your ngrok URL + `/analyse`
3. Connect your Notion account and create the required database (see `n8n/README.md`)
4. Connect your Slack account in the Slack DM node (recipient: your Slack user ID)
5. Activate the workflow

---

## Monitored Outlets

| Outlet | Data Source | Notes |
|---|---|---|
| Al Jazeera English | RSS | ~25 articles, no named bylines |
| The Guardian | Guardian Open Platform API | Full article body + 30 named bylines |
| NPR | RSS (5 topic feeds combined) | ~30 articles, named bylines |
| New York Times | RSS | ~25 articles, named bylines |

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
- **9–10**: Industry leader — strong positive evidence across multiple angles
- **7–8**: Above average — clear positive evidence, minor gaps only
- **5–6**: Meets minimum standards — typical industry performance, OR data too thin to score higher or lower
- **3–4**: Below average — specific failures or gaps identified in the evidence
- **1–2**: Active harm only — dehumanising language, deliberate exclusion, or documented harm found

> **Note on data limitations:** RSS feeds provide headlines and short teasers, not full article text. When community coverage is simply absent from a thin sample, the score reflects insufficient data (4–5), not confirmed harm. Scores of 1–2 are reserved for cases where harmful content was explicitly found.

Companies are additionally flagged (`⚠️`) if they cause active harm — for example, consistent dehumanising language or crime-framing of minority groups.

---

## Design Decisions

### HTTP Request node + FastAPI instead of Execute Command node

The N8N workflow uses an **HTTP Request node** calling a local FastAPI server (`POST /analyse`) rather than an Execute Command node running Python directly. This was a deliberate architectural choice for three reasons:

1. **Separation of concerns** — the agent logic lives entirely in Python, independently testable with `curl` or the Swagger UI at `/docs`, without touching N8N.
2. **N8N Cloud compatibility** — Execute Command node is only available in self-hosted N8N. HTTP Request works in both cloud and self-hosted instances.
3. **Production readiness** — a FastAPI server can be deployed to any cloud provider or container platform and called by any orchestration tool, not just N8N.

The trade-off is that a locally running FastAPI server requires ngrok (or equivalent) to be reachable from N8N Cloud. This is documented in the setup steps above.

### Dual-LLM pipeline

The agent uses two models at different stages:
- **gpt-4o-mini** (OpenAI) — drives the LangGraph ReAct tool-calling loop. Cost-efficient for iterative reasoning across up to 15 steps.
- **claude-sonnet-4-6** (Anthropic) — generates the final structured report. Superior at long-form structured writing and consistent section formatting.

### N8N workflow error handling

The workflow includes three layers of error handling:
- HTTP Request node has an **error output wire** routed to an Error Output node (catches network/timeout failures)
- Notion and Slack nodes have `continueOnFail: true` (third-party API errors don't abort the run)
- The Code node uses a **try/catch** block so a malformed report doesn't crash the entire batch
