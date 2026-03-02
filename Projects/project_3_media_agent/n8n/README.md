# N8N Workflow: Media Diversity Watch

## Overview

This workflow automates weekly inclusivity monitoring for 4 major news outlets.
It supports two operation modes:

**Scheduled (primary):** Runs every Monday at 6am automatically.
Researches Al Jazeera English, The Guardian, NPR, and New York Times.
Saves all 4 reports to Notion before the researcher starts work.

**On-demand:** Researcher opens the form at the N8N URL,
types any company name, selects a focus community, and gets a report.

## Architecture Note: N8N Cloud + ngrok

This project uses **N8N cloud** (`dlbosma.app.n8n.cloud`), not N8N desktop.

Because N8N runs in the cloud and FastAPI runs locally on your laptop,
N8N cannot reach `localhost:8000` directly. **ngrok** is required to create
a public tunnel from the internet to your local FastAPI server.

```
N8N cloud → ngrok public URL → your laptop → FastAPI (port 8000) → LangGraph agent
```

ngrok is already installed (`ngrok version 3.36.1`). Before running the workflow:

```bash
# Terminal 1 — FastAPI (real agent)
python run.py

# Terminal 2 — ngrok tunnel
ngrok http 8000
```

Copy the `https://...ngrok-free.app` URL from ngrok and update the
HTTP Request node URL in N8N to point to it.

**Important:** The ngrok free tier generates a new URL every time you restart it.
Update the HTTP Request node URL each session.

## Workflow Nodes

| Node | Type | Purpose |
|------|------|---------|
| Schedule Trigger 6am Monday | scheduleTrigger | Fires every Monday at 6am |
| Split Into 4 Companies | code | Generates one item per outlet |
| Form Trigger On-Demand | formTrigger | Web form for on-demand research |
| Webhook Trigger API | webhook | Programmatic access |
| Manual Trigger | manualTrigger | Testing in N8N canvas |
| Prepare Input | set | Normalises input from all 4 triggers |
| HTTP Request to FastAPI | httpRequest | Calls POST {ngrok_url}/research |
| Check If Success | if | Routes success vs error |
| Success Output | set | Formats successful result |
| Score >= 7? | if | Routes to Good Standing or lower |
| Score >= 4? | if | Routes to Needs Review or Flagged |
| Notion — Good Standing | notion | Saves report, status = Good Standing |
| Notion — Needs Review | notion | Saves report, status = Needs Review |
| Notion — Flagged for Action | notion | Saves report, status = Flagged for Action |
| Slack DM — Low Score Alert | slack | DM alert when score < 4 |
| Respond Success | respondToWebhook | Returns 200 with result |
| Error Output | set | Formats error details |
| Respond Error | respondToWebhook | Returns 500 with error |

## Setup

1. Import `media_agent_workflow_updated.json` into N8N cloud
2. Start FastAPI locally: `python run.py`
3. Start ngrok: `ngrok http 8000` — copy the public URL
4. Update the HTTP Request node URL to your ngrok URL + `/research`
5. Connect your Notion account credential in all 3 Notion nodes
6. Set up your Notion database with these properties:
   - Score (number)
   - Date (date)
   - Status (select: Good Standing / Needs Review / Flagged for Action)
   - Summary (rich text)
   - Harm Flags (rich text)
   - Community Scores (rich text)
   - Triggered By (select: schedule / form / webhook / manual)
7. Activate the workflow

## Day 2 Mock Testing

For Day 2 smoke testing (before the LangGraph agent is built), use `mock_server.py`
instead of the real FastAPI server. The mock runs on **port 8001** so it does not
conflict with the real server on port 8000.

```bash
python mock_server.py   # starts on localhost:8001
ngrok http 8001         # expose mock to N8N cloud
```

Update the HTTP Request node to the port 8001 ngrok URL for mock testing,
then switch back to the port 8000 URL when the real agent is ready (Day 4).

## How Reports Are Saved

Each Notion page is titled: `[Company] | Week [N] [YYYY]`
Example: `The Guardian | Week 9 2026`

This naming convention enables trend tracking — filter by outlet to see score changes across weeks.

## Monitored Outlets

| Outlet | Data source |
|---|---|
| Al Jazeera English | RSS (~25 articles, no named bylines) |
| The Guardian | Guardian Open Platform API (full body + 30 named bylines) |
| NPR | RSS — 5 topic feeds combined (~30 articles, named bylines) |
| New York Times | RSS (~25 articles, named bylines) |

## Score Routing

The workflow routes completed reports based on overall score:
- **≥ 7.0** → Good Standing (green Notion status)
- **4.0 – 6.9** → Needs Review (yellow Notion status)
- **< 4.0** → Flagged for Action (red Notion status + Slack DM alert)
