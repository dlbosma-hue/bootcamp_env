# MVP Documentation
### Spottr

---

## MVP Scope

The MVP demonstrates two things end-to-end:

1. **Core system:** Visit data → churn risk scores → weekly email report for all members
2. **Coaching add-on:** Check-in data + optional wearable data → coaching-specific risk scores → coaching section in daily briefing

Everything runs on synthetic data for the demo. The architecture mirrors what a real studio deployment would use.

---

## Data Inputs

### Core system (all members)

Two datasets serve two distinct roles in the pipeline — they are not the same data:

| File | Role | Contents |
|---|---|---|
| `gym_churn_us.csv` | Model training only | 4,000 labelled gym members with real churn outcomes. Used once to train `churn_model.pkl`. Never shown to coaches or displayed in the dashboard. |
| `demo_members.csv` | Demo member population | 150 members sampled from Endomondo workout data (167,783 sessions), sized to boutique gym scale (60 HIGH / 30 MEDIUM / 60 LOW). Replaced with a real studio CSV export at go-live. |
| `demo_scored.csv` | Pipeline output | Churn probabilities from the trained model applied to `demo_members.csv`. Feeds the weekly email and dashboard. |

- `demo_members.csv` fields: `user_id`, `total_sessions`, `active_weeks`, `avg_sessions_per_week`, `avg_duration_min`, `days_since_last_workout`, `churn_risk`, `churn_probability`, `churn_risk_tier`, `estimated_ltv_eur`, `revenue_at_risk_eur`
- Member names never enter the pipeline. `user_id` is pseudonymous.

### Coaching add-on
- `coaching_sessions.csv` — synthetic coaching attendance log
  - Fields: `member_id`, `session_date`, `session_booked` (bool), `session_attended` (bool), `coach_id`
- `wearable_sessions.csv` — synthetic wearable workout data (consent-flagged members only)
  - Fields: `member_id`, `session_date`, `workout_type`, `duration_min`, `calories`, `hr_avg`, `hr_peak`
- `coaching_consent_flags.csv` — which members have consented to which data types
  - Fields: `member_id`, `checkin_consent` (bool), `general_attendance_consent` (bool), `wearable_consent` (bool)

---

## n8n Workflow — Two Pipelines

### Pipeline 1 — Weekly email report (Monday 07:00)
```
Schedule trigger (Monday 07:00)
    → Read demo_members.csv (all members, full risk ranking)
    → Score churn risk (logistic regression model → churn_probability → HIGH / MEDIUM / LOW tier)
    → Read survey_responses.csv (responses from past 7 days)
    → Merge: risk list + survey responses
    → Split flagged members → HTTP Request → AI agent (coaching context per flagged member)
    → Aggregate: risk overview + survey responses + coaching context paragraphs
    → Format HTML email (3 sections: risk overview / survey responses / coaching context)
    → n8n Send Email node → all coaches + studio owner (individual email, full studio view)
```

### Pipeline 2 — Survey trigger (event-based)
```
Trigger A: Class attendance check (runs after each class session)
    → Read class_attendance.csv (today's class vs 4-week rolling average)
    → IF attendance dropped >30% vs average for 2+ consecutive sessions:
        → Fetch attendees of that class
        → Filter: last_survey_sent > 5 weeks ago (prevent fatigue)
        → Send survey email to eligible members (Tally webhook or SMTP link)
        → Log: survey_sent_log.csv (member_id, date, trigger_type)

Trigger B: Studio-wide check-in drop (runs daily)
    → Read demo_members.csv (today's total check-ins)
    → IF total check-ins dropped >20% vs prior 7-day average:
        → Fetch all active members
        → Filter: last_survey_sent > 5 weeks ago
        → Send survey email to eligible members
        → Log: survey_sent_log.csv

Survey response received (Tally/Typeform webhook → n8n):
    → Tag response to member_id
    → Append to survey_responses.csv (member_id, date, rating, free_text, wants_checkin)
```

**Consent gate (coaching add-on members — private_coaching_workflow.json):** The wearable data branch only executes for members where `wearable_consent = true` in the consent flags table. Changing the flag to `false` immediately stops wearable data from being pulled on the next run.

---

## AI Agent — Coaching Risk Scoring

### Input context block (per coaching client)
```json
{
  "member_id": "M-4821",
  "coaching_sessions_booked_30d": 8,
  "coaching_sessions_attended_30d": 4,
  "coaching_attendance_rate": 0.50,
  "days_since_last_checkin": 11,
  "general_visits_30d": 14,
  "wearable_sessions_14d": 1,
  "wearable_consented": true
}
```

### System prompt (coaching agent)
```
You are a coaching support assistant for a boutique fitness studio.
You receive data about private coaching clients and write a short briefing
for the client's coach — in natural, conversational language.

Rules:
- Never mention the member by name. Use their member ID only.
- Summarise what the data shows, not what the coach should do.
- Write as if you are giving the coach helpful context before a conversation,
  not issuing an instruction.
- Distinguish clearly between coaching-specific disengagement and broader
  membership churn risk — these are different situations.
- Keep the tone warm and human. The coach will use this as background
  for their own outreach in their own words.
- Keep the summary under 80 words.
- Do not speculate about personal reasons for absence.
- Do not use words like "alert", "risk tier", or "recommended action" in
  the output — those are internal labels, not coach language.
```

### Risk tier logic

The core churn model is a scikit-learn `LogisticRegression` pipeline (StandardScaler + classifier, `max_iter=1000`) trained on `gym_churn_us.csv` — 4,000 gym members with real binary churn labels, 80/20 train/test split. Test-set performance: **92.5% accuracy, 0.977 ROC-AUC**.

The model outputs a churn probability per member. Probabilities are mapped to tiers:

| Probability | Tier | Meaning |
|---|---|---|
| ≥ 0.65 | HIGH | Strong disengagement pattern — coach outreach within 48 hours |
| 0.35 – 0.64 | MEDIUM | Early signal — monitor, lower urgency |
| < 0.35 | LOW | Attending normally — no action needed |

**Why probability thresholds rather than fixed rules:**
The previous approach used fixed attendance and recency thresholds (e.g. "flag if <1 session/week AND >21 days inactive"). This treats all members identically regardless of their history. The model weights signals in proportion to their actual predictive power across 4,000 real outcomes — tenure and current-month class frequency are the strongest signals; visit recency alone is insufficient. A probability output also lets coaches prioritise within a tier: a member at 0.91 is more urgent than one at 0.67, even though both are HIGH.

**Coaching add-on override:**
For members enrolled in private coaching, an attendance-based override applies on top of the model output: if coaching attendance rate < 0.50 OR days since last coaching check-in > 14, the member is flagged HIGH regardless of general churn probability. Coaching disengagement is a distinct signal from general membership churn.

**Retraining path:**
After 6–8 weeks of real studio data, the model is retrained on that studio's actual churn outcomes using the same script (`src/model/train_churn_model.py`). Minimum accuracy threshold for production use: ≥ 80% on held-out test set.

---

## Output Formats

### Weekly email report (Monday 07:00 — all coaches + studio owner)
Full studio view. Sent individually to each coach and the studio owner via n8n SMTP node. Contains three sections:

**Section 1 — Member risk overview**
Full ranked list of members by risk score, with days inactive and revenue at risk.

**Section 2 — Survey responses (if any triggered that week)**
Any survey responses received since the last report, shown alongside the member's risk score.
```
Survey responses this week:

M-0391 — Rating: 2/5
Free text: "Work has been really busy, hard to keep the routine."
Wants coach check-in: Yes

M-2817 — Rating: 3/5
Free text: (no response)
Wants coach check-in: No
```

**Section 3 — Coaching context per flagged member**
One natural language paragraph per high/medium-risk member. Written by GPT-4o-mini at temperature 0. Gives the coach background before they decide whether to reach out. No scripts, no instructions.

```
M-1042 — Hasn't been in for 28 days, which is a long gap for someone who was
coming in 4 times a week until last month. No survey response this cycle. The
drop is sharp enough that something changed — worth knowing what before the
membership lapses further.

M-0391 — Attendance has been patchy for three weeks and they rated their last
session 2 stars with a note about work being busy. They've also asked for a
coach check-in, so the door is open for a conversation.
```

### Coaching section (appended, coaching clients only)
```
🏋️ Coaching update — [DATE]

M-4821 — They've made it to 4 of their last 8 sessions and haven't checked in
for 11 days. Still visiting the studio for classes regularly, so it's more a
coaching momentum thing than a full drop-off. One wearable session in the past
two weeks. Might be worth a low-key check-in before their next session.

M-3304 — Attended 2 of 3 recent sessions, last one 8 days ago. Engagement is
a little softer than usual but nothing dramatic yet. On your radar for this week.
```

---

## Workflow Architecture Decision — Why Three Separate Workflows

The system uses three separate n8n workflows rather than one combined workflow. This is a deliberate design decision, not an oversight.

| Workflow | Schedule | Scope |
|---|---|---|
| `weekly_email_workflow.json` | Monday 07:00 | All studio members |
| `survey_trigger_workflow.json` | Daily 20:00 + 22:00 (event-based) | All active members |
| `private_coaching_workflow.json` | Monday 07:00 | Coaching clients only |

**Why not merge the two Monday workflows into one?**

`weekly_email_workflow` and `private_coaching_workflow` both run at Monday 07:00 and both send email. Merging them into a single workflow with the coaching section appended is architecturally cleaner and would deliver one email per coach instead of two.

However, keeping them separate is the right decision for the POC period for two reasons:

1. **Not every studio has private coaching clients.** For a studio without a coaching programme, the private coaching workflow is simply not imported. A merged workflow would require disabling or removing the coaching branch per studio — more configuration overhead, not less.
2. **Failure isolation.** If the Fitbit API is unavailable or the coaching pipeline fails, a separate workflow fails independently without blocking the main weekly report from sending. In a merged workflow, a coaching branch error could delay or prevent the entire report.

**Phase 2 decision:** Once the POC studio profile is known and onboarding is standardised, merging both Monday workflows into a single workflow with a conditional coaching section is the right next step. Studios without coaching simply skip that branch via an IF node checking whether any coaching clients exist.

---

## What the MVP Does Not Include

- Real Fitbit OAuth flow (synthetic data used instead)
- Real booking system integration (CSV used instead)
- Studio-facing dashboard for coaching clients (Plotly dashboard covers general members only)
- Multi-studio deployment
- **Automated wearable data deletion** — manual deletion process is sufficient for POC; automated scheduled deletion is a go-to-market requirement, not a proof-of-concept requirement

These are Phase 2 / GTM items. The MVP proves the pipeline logic and briefing quality end-to-end.

---

## Customisable Configuration (set per studio before go-live)

These values are not hard-coded. They are agreed with the partner studio during onboarding and stored as environment variables or a config file:

```python
CHURN_THRESHOLD_DAYS_INACTIVE = 21        # days without visit = high risk
CHURN_VISIT_DROP_THRESHOLD = 0.50         # % drop vs prior 4-week avg
COACHING_ATTENDANCE_RISK_FLOOR = 0.60     # below this = surface in briefing
COACHING_CHECKIN_WARNING_DAYS = 10        # days since last check-in = medium risk
COACHING_CHECKIN_ALERT_DAYS = 14          # days since last check-in = high priority
BRIEFING_DELIVERY_TIME = "07:00"          # when weekly email is sent
BRIEFING_RECIPIENTS = "coaches@studio.com" # configurable per studio
```

This is what makes the system a partnership product rather than a one-size-fits-all tool. The studio helps define what the model is looking for in their specific member base.
