# Implementation Timeline
**Project:** AI Retention Early Warning System
**Sector:** Fitness / Health Tech
**Company size:** Medium (50–200 studios)

---

## Overview

Total estimated timeline from decision to full rollout: **16–20 weeks** across three phases.
This is realistic for a medium-sized chain that already collects member check-in and booking data.

---

## Phase 1 — Pilot (Weeks 1–6)

**Goal:** Prove the system works in 3–5 studios before rolling out chain-wide.

| Week | Activity |
|---|---|
| 1–2 | Data audit — assess quality of check-in, booking, and membership data across pilot studios |
| 2–3 | Data pipeline setup — connect source data, build `fitness_user_metrics` aggregation |
| 3–4 | Churn model + dashboard — deploy retention risk dashboard in pilot studios |
| 4–5 | n8n alert workflow — set up daily Slack/email alerts for high-risk members |
| 5–6 | Coach training — 1-hour session per studio: how to read the dashboard and act on alerts |
| 6 | Pilot review — measure early engagement, collect coach feedback, adjust thresholds |

**Milestone:** At least 1 confirmed retention from AI alert by end of Week 6.

---

## Phase 2 — Rollout (Weeks 7–14)

**Goal:** Scale to all studios, add LLM-generated insight layer and LangSmith monitoring.

| Week | Activity |
|---|---|
| 7–8 | Chain-wide data integration — connect all studio data sources |
| 8–10 | LLM insight layer — AI-generated summaries for high-risk members, logged via LangSmith |
| 10–11 | Monitoring setup — LangSmith tracing live, transparency dashboard available to management |
| 11–12 | Personalised engagement — n8n triggers personalised re-engagement messages to at-risk members |
| 12–14 | Full rollout — all 50–200 studios live, coaches briefed |

**Milestone:** Full chain on the system, LangSmith monitoring visible to Chleo's team.

---

## Phase 3 — Optimise (Weeks 15–20)

**Goal:** Refine model, add forecasting, measure ROI.

| Week | Activity |
|---|---|
| 15–16 | Model retraining — update churn heuristics based on 8 weeks of real intervention data |
| 16–17 | Demand forecasting — add class attendance prediction (Phase 2 use case) |
| 17–18 | Coach utilisation balancing — integrate coach schedule optimisation |
| 18–20 | ROI reporting — build revenue recovery dashboard, present results to Chleo |

**Milestone:** Documented ROI report showing retained revenue vs system cost.

---

## Resource Requirements

| Role | Effort | Notes |
|---|---|---|
| Data engineer / analyst | 60–80 hrs (Phase 1) | Data pipeline, CSV processing, model |
| BI developer | 20–30 hrs | Dashboard build and iteration |
| AI/automation engineer | 30–40 hrs | LLM integration, n8n, LangSmith |
| Project manager | 10–15 hrs | Coordination, stakeholder updates |
| Coaches (per studio) | 1–2 hrs | Training session |

**Total internal setup effort:** ~120–165 hours across Phases 1–2.

---

## Risk Factors That Could Extend Timeline

| Risk | Impact | Mitigation |
|---|---|---|
| Poor data quality at studios | +2–3 weeks | Run data audit in Week 1 before committing |
| Staff resistance to AI alerts | +1–2 weeks | Frame as "coach assistant", involve coaches early |
| GDPR consent process | +1–2 weeks | Start legal review in parallel with Phase 1 |
| Studio IT infrastructure varies | +1–2 weeks | Standardise data export format in pilot phase |

---

## Summary for Chleo

| Phase | Duration | What you get |
|---|---|---|
| Pilot | 6 weeks | Working system in 3–5 studios, first retentions |
| Rollout | 8 weeks | All studios live, AI monitoring transparent to management |
| Optimise | 6 weeks | Proven ROI, forecasting, schedule balancing |
| **Total** | **~20 weeks** | **Full early warning system across the chain** |

> Starting March 2026 → full chain live by late July / early August.
> Conservative ROI break-even: within the first 3 months of full rollout.
