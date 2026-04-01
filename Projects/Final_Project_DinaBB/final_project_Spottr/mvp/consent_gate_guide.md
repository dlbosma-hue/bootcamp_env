# Spottr — Consent Gate Guide
**For:** Studio managers and the Spottr consultant
**Applies to:** Wearable data (Fitbit) — coaching add-on only
**Last updated:** March 2026

---

## What the consent gate is

The consent gate is a hard check built into the private coaching workflow. Before the pipeline fetches any wearable data for a member, it reads that member's row in `coaching_consent_flags.csv`. If `wearable_consent` is `false`, the wearable data branch is skipped entirely — no API call is made, no data is fetched, and the coaching briefing is generated from check-in data only.

This is not a soft filter applied after data collection. The gate prevents collection from happening in the first place.

---

## Why this matters under GDPR

Wearable data (heart rate, active minutes, session type) qualifies as **health data under Article 9 GDPR**. Health data requires **explicit, prior, written consent** from the member before any processing can take place. Legitimate interest — the legal basis used for general visit history — is not sufficient.

The consent gate enforces this at the workflow level so that a misconfigured flag or a missing consent form cannot result in wearable data being processed without authorisation.

---

## The consent flags file

**File:** `data/coaching_consent_flags.csv`

| Field | Type | Meaning |
|---|---|---|
| `member_id` | String | Pseudonymous member ID (e.g. M-4821) |
| `checkin_consent` | Boolean | Member consents to coaching check-in attendance being used |
| `general_attendance_consent` | Boolean | Member consents to general class visit history being used |
| `wearable_consent` | Boolean | Member explicitly consents to Fitbit data being pulled |

**Example:**
```
member_id,checkin_consent,general_attendance_consent,wearable_consent
M-4821,true,true,true
M-3304,true,true,false
M-1107,true,false,false
```

Only members with `wearable_consent = true` have Fitbit data fetched. The other two consent fields control whether check-in and general attendance data appear in the coaching briefing.

---

## How to grant wearable consent for a member

1. Member completes the **Wearable Data Consent Form** (see `compliance/member_wearable_consent_form.md`) and signs it — paper or digital
2. Studio manager stores the signed form in the studio's records
3. Open `data/coaching_consent_flags.csv`
4. Find the member's row by `member_id`
5. Set `wearable_consent` to `true`
6. Save the file

The change takes effect on the **next workflow run** (Monday 07:00). No restart required.

---

## How to withdraw wearable consent for a member

A member can withdraw wearable consent at any time, verbally or in writing. Consent withdrawal must be actioned within **48 hours** under Article 17(1) GDPR.

1. Open `data/coaching_consent_flags.csv`
2. Set `wearable_consent` to `false` for that member
3. Save the file
4. Delete the member's cached wearable data:
   - Remove their rows from `data/processed/fitbit_daily.csv`
   - Remove their rows from `data/processed/fitbit_workouts.csv`
5. Revoke the Fitbit OAuth token from the Fitbit developer dashboard (prevents future API calls)
6. Send written confirmation to the member that their wearable data has been deleted

**Timeline:** Flag change and CSV deletion within 48 hours. Written confirmation within 72 hours.

---

## What the n8n workflow does with this flag

In `Spottr — Private Coaching Workflow.json`, the wearable branch is controlled by an **IF node** that reads `wearable_consent` for each member before making any Fitbit API call:

```
For each coaching client:
    → Read consent flags row for member_id
    → IF wearable_consent = true:
        → Call Fitbit API → fetch session data → append to feature set
    → ELSE:
        → Skip wearable branch entirely
        → Generate briefing from check-in data only
```

The coaching briefing is generated either way — it just reflects check-in data only for members without wearable consent. The coach is not told which path was taken; the briefing reads naturally in both cases.

---

## Adding a new coaching client

When a new member joins the private coaching programme:

1. Create a row in `coaching_consent_flags.csv` with their `member_id`
2. Set `checkin_consent = true` (required for coaching programme participation)
3. Set `general_attendance_consent = true` (required for coaching programme participation)
4. Set `wearable_consent = false` by default
5. If the member wishes to share wearable data, follow the consent grant process above

Default state for all new clients is **wearable consent off**. Opt-in only.

---

## Audit trail

The consent flags file is version-controlled in the GitHub repository. Every change to a consent flag creates a git commit with a timestamp and author — this serves as the audit trail for consent decisions.

For production deployment, a dedicated consent management log (`consent_audit_log.csv`) with columns `member_id`, `action` (granted/withdrawn), `date`, `actioned_by` is recommended. This is a Phase 2 item.

---

## What to do if wearable data has been collected without consent

1. Set `wearable_consent` to `false` immediately
2. Delete all wearable data for that member from `fitbit_daily.csv` and `fitbit_workouts.csv`
3. Revoke their Fitbit OAuth token from the Fitbit developer dashboard
4. Notify the member within 72 hours explaining what happened and confirming deletion
5. Document the incident in writing and notify the data controller (studio owner)
6. If the breach involves health data and is likely to result in a risk to the member's rights, the data controller must notify the relevant supervisory authority (e.g. Berlin DPA) within 72 hours under Article 33 GDPR

In practice, this scenario should not occur if the default-off consent flag procedure is followed for all new clients.
