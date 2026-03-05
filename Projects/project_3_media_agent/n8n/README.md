# N8N Workflow: Media Diversity Watch

## Overview

This workflow automates weekly inclusivity monitoring for 4 major news outlets.
It supports two operation modes:

**Scheduled (primary):** Runs every Monday morning automatically via 4 staggered triggers.
Each outlet gets its own independent execution: NPR at 6:00, New York Times at 6:10,
The Guardian at 6:20, Al Jazeera English at 6:30.
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
| Schedule NPR | scheduleTrigger | Fires every Monday at 6:00am |
| Schedule NYT | scheduleTrigger | Fires every Monday at 6:10am |
| Schedule Guardian | scheduleTrigger | Fires every Monday at 6:20am |
| Schedule Al Jazeera | scheduleTrigger | Fires every Monday at 6:30am |
| Set Company NPR/NYT/Guardian/Al Jazeera | set | Hardcodes company name and focus=all for each scheduled execution |
| Form Trigger On-Demand | formTrigger | Web form for on-demand research |
| Webhook Trigger API | webhook | Programmatic access |
| Prepare Input | set | Normalises input from all triggers (schedule, form, webhook) |
| HTTP Request to FastAPI | httpRequest | Calls POST {ngrok_url}/research |
| Check If Success | if | Routes success vs error |
| Code in JavaScript | code | Parses overall_score from report text; chunks report into 1900-char blocks |
| Success Output | set | Formats successful result |
| Notion — Save Report | notion | Saves report; Status set inline (Good Standing / Needs Review / Flagged for Action) |
| Slack DM — Low Score Alert | slack | Sends Slack DM summary for every completed report (status emoji reflects score) |
| Respond Success | respondToWebhook | Returns 200 with result (no-op for scheduled executions) |
| Error Output | set | Formats error details |
| Respond Error | respondToWebhook | Returns 500 with error (no-op for scheduled executions) |

## Setup

1. Import `Media Inclusivity Research Agent.json` into N8N cloud
2. Start FastAPI locally: `python run.py`
3. Start ngrok: `ngrok http 8000` — copy the public URL
4. Update the HTTP Request node URL to your ngrok URL + `/research`
5. Connect your Notion account credential in the Notion node
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

The Status property in Notion is set via an inline expression in the single `Notion — Save Report` node:
- **≥ 7.0** → Good Standing (green Notion status)
- **4.0 – 6.9** → Needs Review (yellow Notion status)
- **< 4.0** → Flagged for Action (red Notion status)

A Slack DM summary is sent for **every** completed report regardless of score.
The message includes the company name, score, status emoji (✅ / ⚠️ / 🚨), and summary.
