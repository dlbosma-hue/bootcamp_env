# Proof of Concept Documentation
### Spottr

---

## Purpose

The POC is a structured 90-day partnership with one boutique studio designed to answer two sequential questions:

> **Question 1 — Can predicted churn be proven?**
> Does the model correctly identify members who are actually going to churn — before they cancel?

> **Question 2 — Do coach interventions based on those predictions prevent churn?**
> When coaches reach out to members the model flagged as at-risk, do those members retain at a higher rate than flagged members who were not contacted?

These questions must be answered in order. Question 2 is only meaningful if Question 1 is first answered yes. If the model does not predict actual churn accurately, improving the intervention design is the wrong next step — the model needs recalibration first.

This is not a pilot of a finished product. It is a structured validation exercise. The studio contributes domain expertise and real outcome data. We contribute the pipeline, the measurement framework, and the briefing layer. Together we find out whether both questions can be answered yes — and under what conditions.

---

## Technical Overview

### Tools Used and Why

| Tool | Role | Why chosen |
|---|---|---|
| **scikit-learn** (Python) | Logistic regression churn model | Lightweight, interpretable, runs locally — no cloud compute needed for a 150-member studio |
| **pandas** | Data ingestion and feature engineering | Standard library for CSV processing; handles the member visit data pipeline |
| **n8n** (self-hosted) | Workflow automation — weekly email, survey trigger, monthly summary | No-code/low-code; all three workflows are exportable JSON; runs on a schedule without any manual input |
| **Plotly Dash** (Python) | Retention dashboard | Browser-based, no login required, bookmarkable URL; studio computer opens it like any website |
| **OpenAI GPT-4o-mini** | Coaching note generation | Cost-effective (approx. €0.10–0.20 per weekly studio run); consistent tone and format |
| **Tally** | Member satisfaction survey form | Free, no-login-required form; webhook output writes directly to `survey_responses.csv` |
| **SMTP (Gmail or Outlook)** | Email delivery for weekly briefing and monthly summary | Studio already has an email account; no additional service required |

---

### What the POC Does — Step by Step

**1. Data ingestion**
The studio exports member visit data from their booking system (Mindbody, Glofox, Gymdesk, or a spreadsheet). The file is loaded into `demo_members.csv` with pseudonymous member IDs. No names enter the pipeline.

**2. Churn scoring**
A logistic regression model (trained on 4,000 labelled gym members from a public dataset) scores each active member daily. Output fields: `churn_risk_tier` (HIGH / MEDIUM / LOW / WATCH), `churn_probability` (0–1), `revenue_at_risk_eur`.

**3. Coaching note generation**
For each HIGH and MEDIUM-risk member, GPT-4o-mini generates one plain-English paragraph summarising the member's attendance pattern and suggesting a coaching angle. The AI does not contact members. The note goes to the coach only.

**4. Weekly email briefing (Monday 07:00)**
The `Spottr — Weekly Email Report.json` n8n workflow triggers every Monday at 07:00. It reads the latest scored output, formats the briefing email (members ranked by risk, coaching notes, WATCH flags, any survey responses from that week), and sends it to the coaching team via SMTP.

**5. Event-triggered member survey**
The `Spottr — Survey Trigger.json` n8n workflow monitors class attendance. When a class records a drop in attendees, it sends a 3-question Tally survey link by email to the members who have been attending that class. Responses are written to `survey_responses.csv` via webhook.

**6. Monthly summary (1st of month, 08:00)**
The same survey workflow runs a separate trigger on the 1st of every month. It aggregates all survey responses from the calendar month and sends a summary email to the studio owner: satisfaction scores, NPS trend, WATCH candidate count, and every free-text quote.

**7. Retention dashboard**
A Plotly Dash app reads `demo_scored.csv` and renders a live browser dashboard: all members colour-coded by risk tier, total revenue at risk, and a sortable priority table. Refreshes automatically before each Monday briefing.

---

### Known Limitations (POC vs. Production)

| Limitation | POC behaviour | Production fix |
|---|---|---|
| Manual data ingestion | Studio exports CSV manually and shares with consultant | API integration with Mindbody / Glofox / Gymdesk booking systems |
| Single-studio model | Logistic regression trained on generic dataset, calibrated per studio | Per-studio retraining with accumulated outcome data after 2–3 POC completions |
| No automated deletion | Manual deletion on request within 48 hours | Automated scheduled deletion job with audit log |
| n8n self-hosted | Runs on consultant's local machine or a single VPS | Cloud-hosted n8n instance with uptime monitoring per studio |
| Survey delivery via email only | Tally link sent by email | Native SMS or WhatsApp delivery option for higher response rates |
| Dashboard not authenticated | Anyone with the URL can view the dashboard | Auth layer (simple password or OAuth) before multi-studio rollout |
| GPT-4o-mini hallucination risk | Coaching notes reviewed manually by consultant before go-live | Structured output validation + automated tone/length checks |

---

### How to Reproduce / Run It

**Requirements**
- Python 3.10+
- n8n (self-hosted or cloud)
- OpenAI API key
- SMTP credentials (Gmail app password or Outlook)

**Step 1 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 2 — Configure environment variables**
Copy `.env.example` to `.env` and fill in:
```
OPENAI_API_KEY=your_key_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
BRIEFING_RECIPIENTS=coach1@studio.com,coach2@studio.com
```

**Step 3 — Run the churn model**
```bash
python mvp/run_pipeline.py
```
This reads `demo_members.csv`, scores all members, and writes `demo_scored.csv`.

**Step 4 — Start the dashboard**
```bash
python dashboard/spottr_dashboard.py
```
Open `http://127.0.0.1:8050` in a browser.

**Step 5 — Import n8n workflows**
In your n8n instance, import all three JSON files from the `poc/` folder:
- `Spottr — Weekly Email Report.json`
- `Spottr — Survey Trigger.json`
- `Spottr — Private Coaching Workflow.json`

Update the SMTP credentials and file paths inside each workflow to match your environment.

**Step 6 — Trigger the weekly briefing manually (for demo)**
In n8n, open the Weekly Email Report workflow and click "Execute workflow" to send a test briefing immediately without waiting for Monday 07:00.

> **Demo recording:** [Watch demo](https://github.com/dlbosma-hue/bootcamp_env/issues/2#issue-4186433120)

---

## Two-Stage Validation Structure

### Stage 1 — Model Validation (Weeks 1–6)
*Does the system predict who actually churns?*

The model flags members as high, medium, or low risk each day. Over the first six weeks, we track what actually happens to flagged members — do the high-risk members cancel at a meaningfully higher rate than unflagged members?

**Pass condition:** High-risk flagged members churn at ≥ 2× the rate of unflagged members over the observation window.

**If Stage 1 fails:** The signals do not predict churn for this studio's member base. We recalibrate thresholds, reweight features, or re-examine the churn definition with the studio before proceeding. The POC does not move to Stage 2 until Stage 1 is passed.

**If Stage 1 passes:** We have evidence that the model identifies real risk. Proceed to Stage 2.

---

### Stage 2 — Intervention Validation (Weeks 7–12)
*When coaches act on predictions, does churn decrease?*

Flagged members fall into two groups naturally: those coaches contacted within 7 days of the alert, and those they did not (due to time, judgment, or priority). We compare churn rates between these two groups over weeks 7–12.

**Pass condition:** Flagged members who were contacted churn at a measurably lower rate than flagged members who were not contacted.

**If Stage 2 fails:** The model is working but the intervention design is not. This could mean the briefing format is wrong, coaches need different training, or the outreach timing is off. These are all fixable. The finding is still commercially useful — it tells us exactly what to improve for the next studio.

**If Stage 2 passes:** The full loop is validated. Predicted churn → coach intervention → measurable retention improvement. This is the commercial proof point for Phase 2.

---

## What We Are Testing

### Primary hypotheses (in order)
1. The model correctly identifies members who will churn — flagged members cancel at a higher rate than unflagged members.
2. When coaches act on model alerts, contacted at-risk members retain at a higher rate than non-contacted at-risk members.

### Secondary hypotheses
- Visit frequency and recency are reliable leading indicators of churn for this studio's specific member base.
- Natural language briefings increase the frequency and timeliness of coach outreach compared to the studio's prior approach.
- Coaches find the briefing format useful enough that they act on it consistently.

### What we are explicitly not testing in the POC
- Whether the AI model is more accurate than an experienced coach's intuition (requires longer timeframe and controlled design)
- Wearable data value (coaching add-on is out of POC scope)
- Multi-studio generalisability (single-studio POC by design)

---

## Partner Studio Requirements

The right POC partner is a boutique studio that:
- Has at least 150 active members (below this, the signal-to-noise ratio is too low)
- Has at least 3 coaches or staff who interact regularly with members
- Can export visit/attendance data in any structured format (CSV, spreadsheet, booking system export)
- Is willing to share churn outcome data (who actually cancelled) for the 90-day window
- Has not recently run a structured retention programme (baseline behaviour needs to be observable)

The studio does not need technical expertise. Data export and an email address for the coaching team is all that is required from their side.

---

## POC Setup — Week 1

**Day 1–2: Studio configuration session**
- Review member data structure and agree field mapping
- Agree churn definition: what does "churned" mean for this studio? (cancelled membership, no visit in X days, etc.)
- Set thresholds together: days inactive, visit drop %, briefing delivery time, email recipients
- Sign DPA

**Day 3–4: Pipeline configuration**
- Load historical member data (pseudonymised)
- Run model on historical data, review first briefing output with studio owner
- Adjust thresholds if outputs don't match intuition
- Configure n8n email delivery (SMTP credentials, recipient list)

**Day 5: Briefing review**
- Studio owner and one coach review the first live briefing
- Collect initial feedback on tone, length, and usefulness
- Make any immediate adjustments to the system prompt

---

## Measurement Framework

### Stage 1 metrics — model validation (Weeks 1–6)

| Metric | Measured how | Frequency |
|---|---|---|
| Members flagged high-risk | System log | Daily |
| Members flagged medium-risk | System log | Daily |
| Members flagged low-risk / not flagged | System log | Daily |
| Actual cancellations — high-risk cohort | Studio membership records | Weekly |
| Actual cancellations — low/unflagged cohort | Studio membership records | Weekly |
| Churn rate ratio (flagged vs unflagged) | Calculated from above | End of Week 6 |

**Stage 1 pass gate:** Flagged (high-risk) members cancel at ≥ 2× the rate of unflagged members by end of Week 6. If not met, pause and recalibrate before proceeding.

**How the Stage 1 comparison is done in practice:**

At the start of Week 1, Spottr produces its first risk list. Every active member receives a label — HIGH, MEDIUM, or LOW — based on their visit history. That list is frozen. Coaches receive their Monday briefings as normal during Weeks 1–6, but do not act on them yet. This is deliberate: if coaches start reaching out to flagged members during the observation window, we can no longer tell whether a member stayed because the model was right or because the outreach saved them. The observation period needs to be clean.

At the end of Week 6, the studio owner exports a cancellation list from their gym management system — this is a standard report available in Mindbody, Glofox, Gymdesk, and most booking tools, or it can be a simple spreadsheet the front desk updates. We then do one calculation: what percentage of HIGH-risk flagged members cancelled, and what percentage of unflagged members cancelled? Dividing the first number by the second gives the churn rate ratio. A ratio of 2 or above means the model is identifying the right people. A ratio below 2 means the model needs recalibration before coaches start acting on it.

One practical caveat: if fewer than five members cancel in total during the six-week window, the sample is too small for the comparison to be conclusive. This can happen at studios with very low monthly churn or seasonal patterns. In that case the Stage 1 window is extended by four weeks and the same calculation is repeated. This possibility should be discussed with the studio owner at setup and noted in the Week 1 configuration session.

---

### Stage 2 metrics — intervention validation (Weeks 7–12)

| Metric | Measured how | Frequency |
|---|---|---|
| Flagged members contacted within 7 days | Coach self-report or CRM log | Weekly |
| Flagged members NOT contacted within 7 days | Derived from above | Weekly |
| Churn rate — contacted flagged members | Studio outcome data | End of Week 12 |
| Churn rate — non-contacted flagged members | Studio outcome data | End of Week 12 |
| Coach outreach rate vs pre-system baseline | Coach self-report, compared to weeks 1–6 | Monthly |
| Coach satisfaction with weekly email report | Short survey (3 questions) | Monthly |
| Survey trigger accuracy | Does the event-trigger fire when class/check-in drops? Manual check | Per trigger event |
| Survey response rate | Responses received / surveys sent | Per trigger event |
| Survey responses surfaced in weekly report | Manual review: are relevant responses visible to coaches? | Weekly |

**Stage 2 pass gate:** Contacted at-risk members retain at a measurably higher rate than non-contacted at-risk members by end of Week 12.

---

### Full POC outcome matrix

| Stage 1 | Stage 2 | Interpretation | Next step |
|---|---|---|---|
| ✓ Pass | ✓ Pass | Full loop validated: model predicts, intervention retains | Proceed to Phase 2 commercial rollout |
| ✓ Pass | ✗ Fail | Model works, intervention design needs improvement | Redesign briefing format or coach outreach process; retest |
| ✗ Fail | — | Model does not predict churn for this studio | Recalibrate thresholds or signals; Stage 2 not meaningful yet |
| ✗ Fail | ✗ Fail | Neither validated | Deeper investigation of data quality and studio fit |

---

## Coaching Add-On — POC Decision

The coaching add-on (check-in tracking + wearable integration) is **out of scope for the POC** for two reasons:

1. **Consent overhead:** The coaching intake form, wearable OAuth setup, and consent gate configuration add 2–3 weeks of onboarding complexity that risks derailing the core POC.
2. **Hypothesis sequencing:** We need to prove the core briefing loop works before adding signals on top of it.

The coaching module is demonstrated as a capability in the MVP demo but is positioned as Phase 2 in the go-to-market plan. A studio that completes the 90-day POC successfully and wants to extend to coaching is the natural entry point.

---

## Data Deletion — POC Approach

Automated scheduled deletion of wearable data is **not required for the POC** because wearable data is not collected in the POC.

For core member data (visit history), deletion is handled manually on request:
1. Studio owner emails deletion request with member ID
2. We remove the member row from the pipeline CSV and n8n execution logs within 48 hours
3. We confirm deletion in writing

This is documented in the DPA and is sufficient for the POC period. Automated deletion scheduling is a go-to-market requirement and will be implemented before any multi-studio rollout.

---

## POC Timeline

| Week | Activity |
|---|---|
| 1 | Setup, configuration, first live briefing |
| 2–4 | System running, weekly coach check-ins, threshold tuning |
| 5–8 | Stable operation, begin tracking outreach rates |
| 9–12 | Outcome data collection, churn comparison, final review |
| 13 | POC debrief with studio — continue / adjust / stop decision |

---

## Monthly Survey Summary Report

In addition to the weekly email briefing, the system sends a **monthly survey summary** to the studio owner on the 1st of every month.

### What it contains

| Section | Detail |
|---|---|
| Headline numbers | Total responses received, average satisfaction score (1–5), average NPS (0–10), count of members rated 2/5 or below |
| Goal progress breakdown | How many members self-reported as on track / falling behind / getting started |
| Full response table | Every survey response that month — member ID, satisfaction score (colour-coded), NPS score, free-text feedback quote |

### Why it matters for the POC

The weekly email surfaces individual survey responses alongside each at-risk member's risk score — so coaches can act on them in real time. The monthly summary answers a different question: **is member satisfaction trending up or down across the whole studio?**

During the 90-day POC, this gives both the studio owner and the consultant a studio-level sentiment signal that is separate from churn predictions. A studio where satisfaction scores improve over 12 weeks — even before churn rate data is conclusive — is a strong early indicator that coach outreach is working.

### Measurement role in the POC

The monthly summary is tracked as a secondary metric alongside the primary Stage 1 and Stage 2 gates:

| Metric | Target | When measured |
|---|---|---|
| Average satisfaction score per month | Stable or improving trend across 3 months | Monthly (1st of month) |
| % members rated ≤ 2/5 (WATCH candidates) | Declining over POC period | Monthly |
| Survey response rate | ≥ 20% of triggered members respond | Per trigger event |

These do not replace the primary pass/fail gates but provide qualitative evidence for the Week 13 debrief.

### How it is generated

The monthly summary is produced by the Survey Trigger workflow (`Spottr — Survey Trigger.json`), which runs a separate trigger on the 1st of every month at 08:00. It reads all survey responses from the current calendar month, aggregates the metrics, and sends the formatted email to the studio owner via the same SMTP setup used for the weekly briefing.

At go-live, this reads from `survey_responses.csv` — the same file the webhook writes to when members submit their Tally form.

---

## From POC to Partnership

If the POC shows positive signal, the natural next step is a formal partnership agreement:
- Monthly retainer covering system operation, monitoring, and briefing quality
- Studio has input into ongoing threshold calibration
- Outcome data shared quarterly so both parties can see whether retention is improving
- Coaching add-on activated for studios that run private coaching programmes

The POC is not a free trial. It is a structured collaboration where both parties invest time and share data. The studio's investment is access to outcome data and coach feedback. Ours is the technical build and ongoing operation.

---

## Model Health Monitoring Post-POC

The Stage 1 churn rate ratio — the ratio of cancellations among flagged members vs. unflagged members — is not only a POC gate. It is also the primary ongoing indicator of whether the model is still working correctly for this studio.

**Why this matters:** As the studio's context changes over time (new instructors, pricing changes, membership demographic shifts, seasonal patterns), the statistical relationship between visit behaviour and churn can change. A model that was accurate at month 3 may degrade by month 12 if it is never updated. This is known as concept drift.

**Post-POC monitoring protocol:**
- The churn rate ratio is tracked monthly after the POC ends as part of standard retainer operations
- A ratio above 2.0 indicates the model remains healthy for this studio
- A ratio dropping below 1.5 on two consecutive months is a trigger for model recalibration or retraining
- Retraining uses accumulated real outcome data from this studio, not the original public dataset

**Support implication:** This monitoring cannot be fully automated at current scale. It requires monthly manual review of cancellation outcomes against model predictions. This activity is included in the monthly retainer and is a core reason ongoing engagement is required beyond hosting alone.
