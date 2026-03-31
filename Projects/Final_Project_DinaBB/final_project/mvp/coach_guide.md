# Spottr — Coach Quick-Start Guide
**For:** Fitness coaches and studio managers
**Last updated:** March 2026

---

## What Spottr does for you

Spottr watches your members' attendance data automatically. Every Monday morning it sends you an email with three things:

1. Which members have gone quiet and are at risk of leaving
2. A plain-language summary of what each at-risk member's pattern looks like
3. Any survey responses from members who gave feedback in the past week

You read it, you decide who to reach out to. The system does not contact members — you do.

---

## Part 1 — Your weekly email

### When it arrives
Every **Monday at 07:00**, automatically. Subject line: **Spottr Weekly Retention Report**.

### What's in it

**High-risk members** are listed first. For each one you'll see:
- Days since their last visit
- Average sessions per week (recent vs. their historical norm)
- A one-line coaching note — why this pattern is a concern and a suggested angle for outreach

**Medium-risk members** are listed below, same format but a lighter tone.

**Survey responses** (if any were received that week) appear at the bottom — member ID, their rating, and any free-text comment they left.

### What to do with it

The email is a starting point, not an instruction. For each high-risk member:

1. Check if you already know what's going on (injury, holiday, work travel)
2. If not — reach out. A short personal message works better than a formal one
3. Log the contact in your CRM or notebook so you can track whether they came back

There is no requirement to contact every flagged member. Use your judgment. The system flags; you decide.

### What the risk tiers mean

| Tier | What it means | Suggested response time |
|---|---|---|
| HIGH | Model probability ≥ 65%. Strong pattern of disengagement. | Within 48 hours ideally |
| MEDIUM | Model probability 35–65%. Early signal, not yet critical. | This week, lower urgency |
| LOW | Model probability < 35%. Attending normally. | No action needed |

The model was trained on 4,000 gym members with real churn outcomes. It achieves 92.5% accuracy on the test set. It will occasionally flag someone who is fine, and occasionally miss someone who is not. Treat it as a well-informed colleague, not an oracle.

---

## Part 2 — The Spottr dashboard

### What it is

A visual overview of all your members at once — one dot per person. Useful for a quick situational read before a coaching session, or for conversations with the studio owner about where retention effort is needed.

The dashboard is built on **check-in data only**: how often members come, how recently they last came, and how many sessions they have accumulated. That is the only data Spottr currently collects. No contract type, payment history, or demographic data is shown — because we don't have it.

### How to open it

The dashboard runs locally on the studio computer. To start it:

1. Open a terminal
2. Navigate to the project folder:
   ```
   cd Projects/Final_Project_DinaBB
   ```
3. Run:
   ```
   python dashboard/spottr_dashboard.py
   ```
4. Open your browser and go to: `http://127.0.0.1:8050`

Keep the terminal window open while you use the dashboard — closing it stops the server.

### Chart 1 — Churn risk overview (bar chart)

Three bars — HIGH (red), MEDIUM (amber), LOW (green) — showing how many members are in each tier this week. The headline at the top shows total members and total revenue at risk.

Use this chart when talking to your studio owner — it converts member counts into a financial number that makes the retention conversation concrete.

### Chart 2 — Priority member list (table)

A sortable table showing every HIGH and MEDIUM risk member ranked by churn probability. Columns: member ID, risk tier, churn probability %, days since last visit, sessions per week, revenue at risk.

Click any column header to re-sort. Use this to decide who to contact first — work top-down.

### How member data gets into the dashboard

```
Check-in / visit history (CSV export from gym management system)
        ↓
Spottr scoring pipeline (logistic regression, runs weekly)
        ↓
demo_members.csv (contains risk scores + member data)
        ↓
Dashboard reads file on startup
        ↓
Charts displayed in browser
```

**You do not need to do anything** to keep the dashboard updated. The pipeline runs automatically before the Monday email. If you open the dashboard on Monday morning, it reflects the same data as the email you received.

---

> **POC note — demo data**
>
> During the POC, the dashboard shows **150 demo members** — a representative sample drawn from a real public workout dataset (Endomondo, 167,000 sessions) and sized to match a typical boutique fitness studio. The sample contains 60 high-risk, 30 medium-risk, and 60 low-risk members (realistic distribution for a studio with ~40% annual churn). Visit frequency and sport variety are real; recency has been re-anchored to today. Churn probabilities are assigned by the trained logistic regression model.
>
> This is placeholder data used to demonstrate the system. When Spottr goes live with a real studio, the demo files are replaced with a CSV export from that studio's gym management system (Mindbody, Glofox, Gymdesk, or equivalent). The pipeline, the model, and the dashboard all stay exactly the same — only the input data changes.

---

## Part 3 — Setting up coaching contracts with wearables

### What this is

For members enrolled in personal or small-group coaching, Spottr can optionally use Fitbit data (workout sessions, active minutes) to give you a more complete picture of their activity between scheduled sessions.

This is entirely optional — both for you and for the member. The core system works without it.

### What data is used

Only workout session data:
- Session start and end time
- Workout type (strength, running, cycling, etc.)
- Active minutes
- Calories burned
- Heart rate during the session (average and peak only)

**What is never used:** resting heart rate, sleep data, step count, GPS location.

### Step-by-step: enrolling a member

**Step 1 — Have the conversation first**
Before anything technical, tell the member what you are asking for and why:

> *"I use an app called Spottr to keep track of how you're doing between sessions. If you're happy to share your Fitbit workout data, I can see when you've been active even if we haven't trained together. It helps me tailor sessions and spot if you need a check-in. You can turn it off at any time."*

Only proceed if they say yes clearly. No ambiguity.

**Step 2 — Give them the consent form**
The consent form is in `final_project/compliance/member_wearable_consent_form.md`. Print it or share as PDF. The member signs it. You keep a copy.

The form covers:
- Exactly what data is collected
- How it is used
- How to withdraw consent
- Retention period (data deleted within 48 hours of withdrawal)

**Step 3 — Record consent in the system**
Open `data/fitbit_tokens.json` and add the member:

```json
{
  "member_id": "M_027",
  "consent_wearable": true,
  "consent_tier": "workout_only",
  "consent_date": "2026-03-27",
  "consent_signed": true
}
```

Set `consent_tier` to:
- `"workout_only"` — session data only (recommended for most members)
- `"full"` — session data plus daily activity summary (only if member explicitly agreed to this level)

**Step 4 — Fitbit OAuth (one-time per member)**
The studio manager or consultant runs the Fitbit authentication script once per member:

```
python src/data_loaders/fitbit_auth.py --member M_027
```

This opens a browser window. The member logs in to their Fitbit account and approves the connection. The OAuth token is saved locally. The member never needs to do this again unless they revoke access.

**Step 5 — Confirm in private coaching workflow**
The private coaching n8n workflow (`private_coaching_workflow.json`) automatically checks the `consent_wearable` flag before fetching any Fitbit data. If it is false, the workflow sends a check-in email only — no Fitbit data is fetched.

You do not need to change anything in n8n after completing steps 3–4.

### Stopping wearable tracking — manual deletion process

A member can withdraw wearable consent at any time, for any reason, with no penalty. When they do, you must complete all five steps below within 48 hours. This is a GDPR requirement, not optional.

**Step 1 — Take the request**
A member can withdraw verbally, by email, or in person. Note the date and time. You do not need a reason from them.

**Step 2 — Turn off the consent flag**
Open `data/fitbit_tokens.json`. Find the member's entry and change `consent_wearable` from `true` to `false`:

```json
{
  "member_id": "M_027",
  "consent_wearable": false,
  "consent_tier": "workout_only",
  "consent_date": "2026-03-27",
  "consent_signed": true,
  "consent_withdrawn": "2026-04-15"
}
```

Add the `consent_withdrawn` date. Save the file. The n8n coaching workflow will immediately stop fetching Fitbit data for this member on its next run.

**Step 3 — Delete their workout data from the local files**
Open a terminal and run:

```
python src/data_loaders/fitbit_loader.py --delete M_027
```

This removes the member's rows from `data/processed/fitbit_workouts.csv` and `data/processed/fitbit_daily.csv`. If the script is not available, open both CSV files in Excel or any text editor, find rows where `member_id = M_027`, delete them, and save.

**Step 4 — Revoke the Fitbit OAuth token**
The member does this themselves in their Fitbit account, or you can do it on their behalf if they hand you their phone:

> Fitbit app → Account (top left) → Manage Data → Connected Apps → Spottr → Remove

Alternatively via Fitbit web: fitbit.com → Settings → Applications → Revoke next to Spottr.

Once revoked, the token stored locally is also invalidated. No further data can be fetched even if the consent flag is accidentally set back to true.

**Step 5 — Confirm in writing to the member**
Send a short email or written note (same day if possible, within 48 hours at most):

> *"Hi [Name], confirming that your Fitbit data has been deleted from Spottr and no further wearable data will be collected. Your general coaching sessions continue as normal. Let me know if you have any questions."*

Keep a copy of this confirmation. The DPA requires written confirmation of deletion.

**After deletion: what still happens**
- The member still receives the weekly email if their check-in data triggers a risk flag
- Their check-in history (visit dates, frequency) is still used for churn scoring — this is under legitimate interest, not consent, and is separate from wearable data
- If they want to be excluded from churn scoring entirely, that is a separate request — see below

**If a member wants no AI analysis at all**
This is a right under GDPR Article 21 (right to object). Handle it the same day:
1. Add the member's ID to a manual exclusion list in `data/fitbit_tokens.json` with a flag `"exclude_from_scoring": true`
2. Inform the consultant (Dina) so the pipeline excludes them on the next run
3. Confirm in writing to the member within 24 hours

---

## Part 4 — How the member survey works

### What triggers a survey

Spottr monitors two things automatically:

| Trigger | Condition | Fires when |
|---|---|---|
| Individual drop | Member's class attendance falls >30% across 2 consecutive sessions | That member's session data is processed |
| Studio-wide drop | Overall studio check-in volume falls >20% vs the prior 7-day average | The evening check runs at 22:00 |

When either condition is met, eligible members receive a short survey by email. A member cannot receive a survey more than once every 5 weeks — the system enforces this automatically.

### What the member receives

A short email with a link to a Tally.so form. It asks:
- How are you finding your training lately? (1–5 scale)
- Is there anything getting in the way? (optional free text)
- Would you like a coach to reach out? (yes/no)

The tone is casual. It takes under 60 seconds to complete.

### Where the responses go

Responses are logged automatically to `data/survey_responses.csv` via an n8n webhook. They appear in the following Monday's weekly email report — alongside the member's risk score.

You do not need to check anything separately. If a member responds, you will see it in Monday's email.

### What to do if a member says "yes, please reach out"

Contact them the same week. Reference something specific from their response if they left a comment. Do not mention Spottr by name unless they ask — just reach out naturally.

### What to do if a member doesn't respond

Nothing. Non-response is not a signal on its own. The risk scoring continues normally. They may receive another survey after the 5-week cooldown if the trigger fires again.

---

## Quick reference

| Task | Where |
|---|---|
| Read weekly report | Email (Monday 07:00) |
| Open dashboard | `http://127.0.0.1:8050` (run `python dashboard/plotly_dashboard.py` first) |
| Enrol member for wearable | `data/fitbit_tokens.json` → `python src/data_loaders/fitbit_auth.py` |
| Member consent form | `final_project/compliance/member_wearable_consent_form.md` |
| Member withdraws consent | Set flag to false → delete CSV rows → revoke Fitbit token → confirm in writing |
| Survey responses | Appear in Monday email automatically |
| Something looks wrong | Contact the studio manager or Dina (consultant) |
