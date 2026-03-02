# N8N Workflow: Media Diversity Watch

## Overview

This workflow automates weekly inclusivity monitoring for 4 major news outlets.
It supports two operation modes:

**Scheduled (primary):** Runs every Monday at 6am automatically.
Researches Al Jazeera English, The Guardian, NPR, and New York Times.
Saves all 4 reports to Notion before the researcher starts work.

**On-demand:** Researcher opens the form at the N8N URL,
types any company name, selects a focus community, and gets a report.

## Workflow Nodes

| Node | Type | Purpose |
|------|------|---------|
| Schedule Trigger 6am Monday | scheduleTrigger | Fires every Monday at 6am |
| Split Into 4 Companies | code | Generates one item per outlet |
| Form Trigger On-Demand | formTrigger | Web form for on-demand research |
| Webhook Trigger API | webhook | Programmatic access |
| Manual Trigger | manualTrigger | Testing in N8N canvas |
| Prepare Input | set | Normalises input from all 4 triggers |
| HTTP Request to FastAPI | httpRequest | Calls POST http://localhost:8000/research |
| Check If Success | if | Routes success vs error |
| Success Output | set | Formats successful result |
| Save to Notion | notion | Saves report to Notion database |
| Respond Success | respondToWebhook | Returns 200 with result |
| Error Output | set | Formats error details |
| Respond Error | respondToWebhook | Returns 500 with error |

## Setup

1. Import `media_agent_workflow_updated.json` into your N8N desktop instance
2. The HTTP Request node calls `http://localhost:8000/research` (no ngrok needed — N8N and FastAPI run on the same machine)
3. Connect your Notion account in the Save to Notion node
4. Set up your Notion database with these properties:
   - Score (number)
   - Date (date)
   - Summary (rich text)
   - Harm Flags (rich text)
   - Community Scores (rich text)
   - Triggered By (select)
5. Start the FastAPI server: `python run.py`
6. Activate the workflow

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
- **< 4.0** → Flagged (red Notion status + Slack alert)
