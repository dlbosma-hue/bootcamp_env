# N8N Workflow: Media Diversity Watch

## Overview

This workflow automates weekly inclusivity monitoring for 5 major news outlets.
It supports two operation modes:

**Scheduled (primary):** Runs every Monday at 6am automatically.
Researches BBC, The Guardian, CNN, New York Times, and Reuters.
Saves all 5 reports to Notion before the researcher starts work.

**On-demand:** Researcher opens the form at the N8N URL,
types any company name, selects a focus community, and gets a report.

## Workflow Nodes

| Node | Type | Purpose |
|------|------|---------|
| Schedule Trigger 6am Weekdays | scheduleTrigger | Fires Mon-Fri at 6am |
| Split Into 5 Companies | code | Generates one item per outlet |
| Form Trigger On-Demand | formTrigger | Web form for on-demand research |
| Webhook Trigger API | webhook | Programmatic access |
| Manual Trigger | manualTrigger | Testing in N8N canvas |
| Prepare Input | set | Normalises input from all 4 triggers |
| HTTP Request to FastAPI | httpRequest | Calls the LangGraph agent |
| Check If Success | if | Routes success vs error |
| Success Output | set | Formats successful result |
| Save to Notion | notion | Saves report to Notion database |
| Respond Success | respondToWebhook | Returns 200 with result |
| Error Output | set | Formats error details |
| Respond Error | respondToWebhook | Returns 500 with error |

## Setup

1. Import `media_agent_workflow.json` into your N8N instance
2. Replace `YOUR_NGROK_URL` in the HTTP Request node with your actual ngrok URL
3. Connect your Notion account in the Save to Notion node
4. Set up your Notion database with these properties:
   - Score (number)
   - Date (date)
   - Harm Flags (rich text)
   - Community Scores (rich text)
   - Triggered By (select)
5. Activate the workflow

## How Reports Are Saved

Each Notion page is titled: `[Company] | Week [N] [YYYY]`
Example: `BBC | Week 9 2026`

This naming convention enables trend tracking -- you can filter
all BBC entries and see score changes across weeks.

## Monitored Outlets

BBC, The Guardian, CNN, New York Times, Reuters
