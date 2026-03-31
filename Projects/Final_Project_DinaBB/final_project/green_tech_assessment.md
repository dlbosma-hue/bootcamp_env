# Green Tech Assessment
## Spottr — Member Retention AI System
**Prepared by:** Dina Bosma-Buczynska
**Date:** March 2026
**Assessment type:** Design-time audit — system assessed at build stage, before live deployment
**Artifact:** Fitness churn prediction system — scikit-learn model, GPT-4o-mini briefing (via n8n), Plotly dashboard

---

## 1. Functional Unit (R)

One unit of value for this system is:

> **One weekly retention briefing delivered to one studio** — covering churn risk scores for all members, revenue at risk, WATCH alerts, and prioritised coaching notes for flagged members.

Everything in this assessment is measured relative to one R. This is the SCI framing: energy and carbon per useful output, not in total.

---

## 2. System Overview

The system consists of three components with distinct compute footprints:

| Component | What it does | Runs how often |
|---|---|---|
| scikit-learn model (local) | Logistic regression scores all members — runs on local CPU | Every Monday before email trigger |
| n8n workflow (full run) | Loads members, scores risk, calls GPT-4o-mini once, formats and sends weekly email | Every Monday at 07:00 (52×/year) |
| Plotly/Dash dashboard | Loads demo_members.csv, renders bar chart + priority table | On each browser refresh (on-demand only) |

The ML model itself (logistic regression on tabular data, 150 members) is computationally negligible — sub-second on any modern CPU, no GPU required. The single GPT-4o-mini API call is the dominant energy driver.

---

## 3. Hotspot Analysis

### Hotspot 1 — Single LLM call to US-hosted infrastructure (main carbon driver)

One GPT-4o-mini API call is made per weekly run. OpenAI infrastructure is US-hosted. US average grid carbon intensity is approximately 0.4 kgCO2/kWh versus approximately 0.2 kgCO2/kWh for EU West regions — roughly double.

Estimated tokens per run: ~1,000 input + ~400 output = ~1,400 tokens per R.

This is already optimised from the design stage: the system was deliberately built to send one batched prompt containing all flagged members, rather than one call per member. At a 10-member flagged list that would otherwise be 10 calls, batching provides an approximately 80% token reduction.

### Hotspot 2 — n8n workflow running weekly for a weekly service (aligned, low impact)

The n8n schedule trigger fires every Monday at 07:00. This is correctly aligned with the service cadence — one execution per week, 52 per year. No unnecessary executions at current design.

At scale (10 studios), each studio runs independently — 520 executions/year total, all producing actionable output.

### Hotspot 3 — Dashboard with no data caching (low now, medium at scale)

The Plotly/Dash app reloads `demo_members.csv` on every browser refresh. At one studio with occasional use, this is negligible. At 10+ studios with concurrent users, unoptimised data loading becomes a measurable energy cost.

---

## 4. Honest Assumptions

The following are estimates, not measured values. The system has not yet run live.

**Region and grid intensity:** OpenAI API calls route to US data centres. US average grid carbon intensity ~0.4 kgCO2/kWh vs ~0.2 kgCO2/kWh for EU West. This differential is assumed, not verified.

**Token counts:** Estimated at ~1,000 input tokens + ~400 output tokens per weekly run (one batched call for 5–10 flagged members). Actual token counts are returned in the OpenAI API response — logging these after the first live run is the immediate next step to replace estimates with real data.

**Model energy per token:** GPT-4o-mini is one of the smaller hosted models, chosen deliberately for cost and speed. OpenAI does not publish per-model energy figures, so relative efficiency vs. alternatives cannot be verified.

**ML model footprint:** Logistic regression on 150 tabular rows takes under 1 second on CPU. Energy cost is negligible and not included in per-R estimates.

**Idle infrastructure:** n8n Cloud runs continuously. Idle energy draw is shared across all workflows and not attributable to individual runs.

---

## 5. Green Software Foundation (GSF) Pillars Map

| Pillar | Where it appears in this system |
|---|---|
| **Carbon** | One LLM call per week routes to US infrastructure (~0.4 kgCO2/kWh). No EU-hosted LLM alternative currently used. Reducing call frequency or switching to EU-hosted inference would reduce carbon per R. |
| **Energy** | Batching all members into one prompt (already implemented) eliminates redundant context injection. Single call per R is the minimum viable LLM energy footprint for this service. |
| **Hardware** | n8n trigger fires once per week — aligned with service cadence. ML model runs on local CPU with no cloud inference required. Dashboard only renders on user request. |
| **Measurement** | Token count is returned in the OpenAI API response. Logging it to a CSV in n8n after each run gives a concrete energy proxy metric with no new tooling required. |

---

## 6. Green Decisions Already Implemented

These are choices made at design stage that reduce the system's environmental footprint:

| Decision | Alternative that was rejected | Energy saving |
|---|---|---|
| One batched GPT-4o-mini call per run | One call per flagged member (N sequential calls) | ~80% token reduction for a 10-member flagged list |
| Weekly trigger (52×/year) | Daily trigger (365×/year) | 86% reduction in n8n executions |
| Local logistic regression (CPU) | Hosted ML inference API (cloud GPU) | Eliminates cloud inference entirely for scoring |
| On-demand dashboard (user opens browser) | Always-on rendered dashboard with polling | Eliminates unnecessary compute between sessions |
| GPT-4o-mini (small, fast model) | GPT-4o or larger model | Lower per-token energy footprint |

---

## 7. Remaining Improvements

### Improvement 1 — Log token count as energy proxy metric
**Pillar:** Measurement
**Status:** Not yet implemented
**Change:** Read the `usage.total_tokens` field from the OpenAI API response inside the n8n `Build HTML Email` node. Append it to a simple `token_log.csv` after each weekly run.
**Expected outcome:** A concrete, trackable proxy for energy per R. No new tooling required.
**Success:** Stable or declining token count per R as the system matures.

### Improvement 2 — Dashboard data caching for Phase 2
**Pillar:** Energy, Hardware
**Status:** Not needed at Phase 1 scale
**Change:** Cache `demo_members.csv` in memory on Dash startup rather than re-reading on every refresh. At Phase 2 (hosted on Railway, multiple studios), add a cache invalidation trigger that refreshes only after the Monday pipeline run.
**Expected outcome:** Eliminates redundant file reads for all non-Monday sessions.

### Improvement 3 — EU-hosted LLM inference (Phase 2 consideration)
**Pillar:** Carbon
**Status:** Not available from OpenAI today; monitor
**Change:** If OpenAI introduces EU-region inference endpoints, route API calls there. Alternatively, evaluate Mistral (EU-based, GDPR-native, EU data centres) as a Phase 2 LLM option for coaching briefings.
**Expected outcome:** ~50% reduction in carbon per LLM call (from ~0.4 to ~0.2 kgCO2/kWh grid intensity).

---

## 8. Measurement Plan

Track the following per R (per weekly briefing run) from the first live deployment:

| Metric | How to measure | Target |
|---|---|---|
| Total tokens per run | `usage.total_tokens` from OpenAI API response, logged in n8n | < 2,000 tokens per R |
| LLM calls per run | n8n execution log — count of `Message a model` node executions | 1 per R |
| n8n executions per month | n8n execution history | 4–5 per studio per month |
| Dashboard loads per week | n8n or server access log (Phase 2) | Track trend only |

---

## 9. Caveats

This system is not carbon neutral and this assessment does not claim it is.

At current pilot scale — one studio, one weekly briefing run — the absolute energy impact is small. One GPT-4o-mini call consuming ~1,400 tokens uses a fraction of a kWh. The decisions above are proportionally significant and represent good engineering practice, but they are not the difference between a harmful and a safe system at this scale.

No carbon offset claims are made. Offsets are not equivalent to emissions reductions and are not included in SCI-style assessments.

The value of applying green software thinking at this stage is threefold:
1. **Measurement infrastructure** — token logging from day one means drift is visible before it becomes costly
2. **Efficient patterns** — a system designed for batching and weekly cadence is significantly easier to scale responsibly than one retrofitted later
3. **Credibility** — demonstrating awareness of environmental impact as a design constraint, not an afterthought, is increasingly relevant to enterprise buyers and regulators under the EU AI Act's emerging sustainability provisions

**What would be validated next with a real client:** Actual token counts from the first live n8n run replace the estimated figures in Section 4 with real measurements. This single data point would validate or revise every calculation in this document.
