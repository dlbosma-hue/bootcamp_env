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

## From POC to Partnership

If the POC shows positive signal, the natural next step is a formal partnership agreement:
- Monthly retainer covering system operation, monitoring, and briefing quality
- Studio has input into ongoing threshold calibration
- Outcome data shared quarterly so both parties can see whether retention is improving
- Coaching add-on activated for studios that run private coaching programmes

The POC is not a free trial. It is a structured collaboration where both parties invest time and share data. The studio's investment is access to outcome data and coach feedback. Ours is the technical build and ongoing operation.
