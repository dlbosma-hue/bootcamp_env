# Strategic Deployment Plan
### Spottr

---

## 5.1 Deployment Phases

### Overview

| Phase | Name | Duration | Studios | Goal |
|---|---|---|---|---|
| 1 | POC | 90 days | 1 | Validate hypothesis. Prove briefings change coach behaviour. |
| 2 | Pilot | 6 months | 3–5 | Validate across studio types. Tune model. Build repeatable onboarding. |
| 3 | Full Deployment | Ongoing | 10+ | Commercial rollout. Automated infrastructure. Coaching add-on live. |

---

### Phase 1 — Proof of Concept (Months 1–3)

**Goal:** Answer two questions in sequence:
1. Does the model accurately predict which members will churn?
2. When coaches act on those predictions, does churn measurably decrease?

Phase 2 is only entered if both questions are answered yes. Phase 1 is not a trial run — it is a validation gate.

**What is live:**
- Core churn prediction pipeline (visit data → logistic regression → risk scores → weekly email report)
- Weekly email report (Monday 07:00, n8n → all coaches + studio owner, full studio view)
- Retention dashboard (Plotly, runs on studio computer, accessible via browser — shows member risk overview and priority contact list)
- Event-triggered member survey (class attendance drop OR studio-wide check-in drop, max once per 5 weeks per member)
- Monthly survey summary email (1st of each month, studio owner — aggregated satisfaction scores, NPS, goal progress, all feedback quotes from the past month)
- Natural language coaching context per flagged member in weekly report
- Human-in-the-loop coaching workflow
- Manual GDPR deletion process (48-hour response on request)

**What is NOT live:**
- Coaching add-on (check-in tracking, wearable integration)
- Automated deletion scheduling
- Multi-studio infrastructure

**Milestones:**

*Stage 1 — Model validation (Weeks 1–6)*
- Week 1: DPA signed, first live briefing delivered, baseline churn rate established
- Week 2–4: System runs daily; flagged members logged; no intervention tracking yet — let the model predict without coaching interference to establish baseline
- Week 5–6: Review who actually cancelled. Do flagged members cancel at ≥ 2× the rate of unflagged members?
- **Week 6 gate:** If Stage 1 passes → proceed. If not → recalibrate thresholds with studio before moving on.

*Stage 2 — Intervention validation (Weeks 7–12)*
- Week 7: Coaches begin acting on briefings; outreach tracked per flagged member
- Week 8–10: Compare churn rate of contacted vs non-contacted flagged members
- Week 12: Final outcome data collected
- **Week 13: POC debrief** — full outcome matrix reviewed with studio. Go/no-go for Phase 2.

**Success criteria:**

| Question | Pass condition |
|---|---|
| Q1: Does the model predict churn? | Flagged members cancel at ≥ 2× the rate of unflagged members (Weeks 1–6) |
| Q2: Does intervention prevent churn? | Contacted flagged members retain at a measurably higher rate than non-contacted flagged members (Weeks 7–12) |
| Briefing usefulness | ≥ 2 of 3 coaches say they would miss the briefing if it stopped |
| Operational reliability | ≥ 95% of scheduled briefing runs succeed |

---

### Phase 2 — Pilot (Months 4–9)

**Goal:** Validate the system across 3–5 studios with different profiles (yoga, CrossFit, PT boutique). Build repeatable onboarding. Activate coaching add-on.

**What goes live in Phase 2:**
- Coaching add-on: check-in tracking + wearable integration (consented members only)
- Customisable threshold configuration per studio (config file per studio_id)
- Batched LLM calls (single call replaces 12 sequential — 80% token reduction)
- Weekly briefing trigger option (reduces n8n executions)
- Model retraining on real studio data (after 6–8 weeks data collection per studio)
- **Automated data feed (replaces manual CSV export):** During the POC, the studio manually exports a CSV from their gym management system once a week and places it in the pipeline folder. In Phase 2 this is replaced with one of the following, depending on the studio's system:
  - *Scheduled email export:* Mindbody and Glofox support automated CSV exports sent by email on a schedule. An n8n email-trigger node receives the attachment and saves it automatically — no manual step.
  - *Direct API integration:* Mindbody, Glofox, and Gymdesk all expose REST APIs. The n8n Monday trigger calls the API directly instead of reading a file, returning live member data with no studio involvement.
  - *Real-time webhook (Phase 3):* Glofox and some others can push a webhook event on every check-in. Enables near-real-time scoring instead of weekly batches.
  The pipeline, model, and dashboard require no changes — only the data source node in n8n is updated per studio.

**What goes live in Phase 2 — GDPR:**

**Automated Deletion Workflow — Technical Design**

Phase 1 handles erasure requests manually (studio emails consultant → consultant deletes within 48 hours). This does not scale beyond one studio. Phase 2 replaces it with a dedicated n8n workflow.

*Trigger options (one of two depending on studio setup):*
- **Scheduled (default):** n8n runs nightly at 02:00. Reads a shared `deletion_queue.csv` that studio staff update when a request comes in. Low-friction — no API integration needed.
- **Webhook (preferred for Phase 3):** Studio's management system (Mindbody / Glofox) fires a webhook on membership cancellation or explicit erasure request. n8n listens and triggers immediately — no human step required.

*What the workflow deletes, in order:*
1. Member rows from `data/processed/demo_members.csv` and any wearable data files (`fitbit_workouts.csv`, `fitbit_daily.csv`)
2. n8n execution history entries referencing that member purged
3. Fitbit OAuth token from `fitbit_tokens.json` (if wearable consent was given)
4. Survey responses from `survey_responses.csv` matching that member
5. Any cached briefing output referencing that member in n8n execution history

*What it produces:*
- A row appended to `deletion_log.csv`: member_id, request date, deletion date, systems cleared, confirmed by
- Automated confirmation email to the studio owner (sent via the same SMTP node used for weekly reports)

*Why this design:* All deletions happen in one auditable workflow run. The deletion log satisfies the DPA Clause 8.3 requirement for written certification within 10 business days. The nightly schedule keeps the execution window well within the 48-hour GDPR obligation even without a webhook.

*Not yet built — targeted for Month 7 of Phase 2. The manual process in Phase 1 is compliant for a single-studio POC.*

**Milestones:**
- Month 4: Second studio onboarded with coaching add-on active
- Month 5–6: Third studio onboarded; first cross-studio comparison
- Month 7: Model retrained on real data for each studio; accuracy validated ≥ 80%
- Month 8: Automated deletion workflow tested and verified
- Month 9: Pilot review — pricing confirmed, Phase 3 go/no-go

**Success criteria:**
- System onboards a new studio in < 5 days
- Model accuracy ≥ 80% on real studio data
- Automated deletion workflow executes and confirms within 24 hours
- At least one studio renews beyond initial pilot term

---

### Phase 3 — Full Deployment (Month 10+)

**Goal:** Commercial rollout at 10+ studios. Multi-studio infrastructure. Stable pricing model. Coaching add-on as standard offering.

**Infrastructure changes:**
- Role-based access control (studio owner view vs. coach view)
- Studio ID-based data isolation across all pipeline components
- Per-studio email recipient list configuration
- Centralized deletion queue management across studios
- Quarterly energy / carbon proxy reporting per studio

**Commercial model active:** See Section 5.3.

**Ongoing model operations (required at scale):**

As the studio's member base evolves — new instructors, pricing changes, demographic shifts, seasonal patterns — the statistical relationship between visit behaviour and churn changes over time. A model trained once on a generic dataset will gradually make worse predictions. This is known as concept drift.

To address this at Phase 3 scale:

- **Model retraining schedule:** Every 6 months per studio, using accumulated outcome data from that studio's real cancellations. Retraining uses the same pipeline (`src/model/train_churn_model.py`) with a minimum accuracy threshold of ≥ 80% on a held-out test set before the new model goes live.
- **Drift detection metric:** The Stage 1 churn rate ratio (flagged members cancelling at ≥ 2× the rate of unflagged members) is tracked monthly post-POC as the model health indicator. If this ratio drops below 1.5 on two consecutive months, retraining is triggered ahead of schedule.
- **Monthly drift monitoring** is a standard support activity included in the monthly retainer. The retainer is not just hosting — it covers active model maintenance, threshold review, and outcome data collection per studio.

This also means a degree of ongoing consultant involvement is required per studio at scale. A fully automated self-serve model is not viable without per-studio retraining infrastructure and human sign-off on retrained model performance.

---

## 5.2 Timeline with Milestones

```
           [STAGE 1: Does the model predict who churns?]

Month 1    ├── POC studio signed, DPA executed
           ├── First live briefing delivered
           └── Baseline membership + churn rate documented (pre-system)

Month 1.5  ├── Week 6: First churn outcome check
           ├── Do flagged members cancel at ≥ 2× rate of unflagged members?
           └── ── STAGE 1 GATE: Pass → Stage 2. Fail → recalibrate thresholds first.

           [STAGE 2: Do coach interventions based on predictions prevent churn?]

Month 2    ├── Coaches begin acting on briefings; outreach tracked per flagged member
           ├── Contacted vs non-contacted flagged members logged weekly
           └── Threshold calibration with coaching team based on Stage 1 learnings

Month 3    ├── Week 12: Final outcome data collected
           ├── Churn comparison: contacted vs non-contacted flagged members
           ├── POC debrief — full outcome matrix reviewed with studio
           └── ── STAGE 2 GATE: Both Q1 + Q2 answered yes → Go/no-go for Phase 2

Month 4    ├── Phase 2 begins — second studio onboarded
           └── Coaching add-on live (check-in + wearable consent gate)

Month 5    ├── Third studio onboarded
           └── Batched LLM calls deployed (80% token reduction)

Month 6    ├── Cross-studio model comparison
           └── Model retraining on real data for first two studios

Month 7    ├── Automated deletion workflow live and tested
           └── Weekly briefing trigger option deployed

Month 8    ├── Pricing model confirmed
           └── Pilot review — at least one renewal secured

Month 9    ├── Phase 3 go/no-go decision
           └── Full deployment infrastructure design finalised

Month 10+  └── Commercial rollout — 10+ studios
```

---

## 5.3 Go-to-Market Strategy

### Who the buyers are

**Primary buyer:** Boutique fitness studio owner-operator in a major European city (Berlin, Amsterdam, Vienna, Zurich). Solo owner or small team (2–5 staff). No in-house data capability. Revenue €150k–€600k/year. Directly manages member retention.

**Why this buyer:** They feel the churn problem personally. Every member who leaves is someone they know. They are scared of GDPR but do not have time to become experts. They will pay for something that saves them time and is already compliant when they sign it.

**Secondary buyer (Phase 3):** Fitness franchise or multi-location operator looking to standardise retention tooling across locations.

**Who is NOT a target buyer:**
- Studios where > 30% of members are on Urban Sports Club / Gympass (different retention economics)
- Large commercial gyms with in-house BI teams
- Studios with < 80 direct members (signal-to-noise ratio too low)

### How to reach them

**Phase 1–2 (direct, relationship-based):**
- Personal introductions through fitness industry networks in Berlin
- Speaking at boutique fitness events (e.g., EuropeActive, local studio owner meetups)
- LinkedIn content: short posts on boutique fitness churn data, GDPR compliance tips for studios — establish credibility before pitching
- Referrals from POC studio once results are visible

**Phase 3 (scalable):**
- Partnerships with gym management software providers (e.g., Mindbody, Glofox, Virtuagym) — integration as an add-on creates distribution
- Content marketing: "2025 Spottr Report" — generates inbound leads from studio owners searching for churn benchmarks
- Case study from POC studio (with consent): concrete numbers on retained revenue

### What the pitch sounds like

*"Before we start, we sign a contract. It takes 20 minutes. You update one paragraph in your privacy notice — I'll tell you exactly what to write. Then every Monday your coaches get a short note about which members are going quiet and a bit of context about what's happening. They decide whether to reach out. You own the relationship. I just make sure they have the right information at the right time."*

---

## 5.4 Pricing Model

### Phase 1 (POC) — Partnership Investment

| Item | Price |
|---|---|
| POC setup, configuration, onboarding | 2,000 EUR (one-time) |
| 90-day POC operation | Included |
| POC debrief and outcome report | Included |

Rationale: The studio invests in the setup. We invest in proving the system works. If it doesn't, the studio has lost 2,000 EUR. If it does, they know exactly what the value is before signing a recurring contract.

### Phase 2–3 (Ongoing) — Monthly Retainer

| Studio Size | Monthly Retainer | What's Included |
|---|---|---|
| Small (< 120 members) | 149 EUR/month | Core churn briefings, n8n execution monitoring, quarterly threshold review |
| Medium (120–250 members) | 249 EUR/month | Core + coaching add-on (check-in tracking), automated deletion |
| Large (250+ members) | 399 EUR/month | Full stack including wearable integration, monthly outcome report, priority support |

**Annual commitment discount:** 15% for 12-month upfront payment.

**Per-studio cost at scale:** ~10–15 EUR/month infrastructure. Retainer margin is high once onboarding cost is recovered (typically within 2–3 months of retainer payments).

### Comparison to value delivered

At the base case (33% intervention success, IHRSA blended churn benchmark), the system generates ~32,600 EUR/year in retained revenue per studio. A 149 EUR/month retainer (1,788 EUR/year) represents an **18x return on the retainer fee** — or 8x on the conservative boutique-specific case (20% intervention success, 40% churn, €1,000 LTV). Both figures are pre-POC projections. Lead with the conservative case in the pitch; use the base case only once POC data validates it.

---

## 5.5 Stakeholder Communication Map

### Studio Owner

**What they care about:** Revenue, compliance risk, time.

**What to tell them:**
- The system pays for itself in the first month. Here is the calculation.
- You do not become liable for GDPR — we handle the technical compliance, you update your privacy notice (one paragraph, I'll write it). We sign a contract before we touch any data.
- Your coaches get a short note every Monday. Nothing changes for them except they have better information.

**When to communicate:** Before signing (pitch), at POC kickoff (onboarding), at month 3 (outcome review), quarterly thereafter.

### Coaches

**What they care about:** Not more admin. Tools that work with how they already operate.

**What to tell them:**
- You'll get an email every Monday morning. It tells you which members are going quiet and gives you a bit of context. You decide what to do with it.
- The AI doesn't tell you what to say. It just makes sure you don't miss someone.
- Your judgment matters. The system is wrong sometimes. When it seems off, ignore it and tell us so we can fix it.

**When to communicate:** At onboarding training (1–2 hours), monthly retrospective check-in.

### Legal / DPA (if studio has one)

**What they care about:** GDPR liability, contractual protection.

**What to tell them:**
- We arrive with a signed DPA template (Article 28 compliant). This is not a gap you need to fill.
- Wearable data requires explicit consent under Article 9(2)(a). The consent form and technical consent gate are already designed. Here is the documentation.
- The system is classified Limited Risk under the EU AI Act (Article 50). No conformity assessment body certification required.

**When to communicate:** Before deployment. Provide DPA, consent form, DPIA, and EU AI Act classification reasoning upfront.

### Members (indirect)

**What they care about:** Not feeling surveilled.

**What to tell them (via studio's privacy notice):**
- "We use an AI tool to help our coaches understand when members may benefit from additional support. Your coach reviews this information and decides whether to reach out. You can ask us not to use this tool on your data at any time."

This goes in the studio's privacy notice — one paragraph. The studio writes it; we tell them what it needs to say.

---

## 5.6 Success Metrics by Phase

### Phase 1 — POC

**Stage 1 — model validation (Weeks 1–6)**

| Metric | Target |
|---|---|
| Churn rate — high-risk flagged members | ≥ 2× churn rate of unflagged members |
| Model flags genuinely inactive members | Manual spot-check: ≥ 80% of flagged members show verifiable drop in visits |
| Time to first live briefing | ≤ 5 days from DPA signing |

**Stage 2 — intervention validation (Weeks 7–12)**

| Metric | Target |
|---|---|
| Churn rate — contacted flagged members vs non-contacted flagged members | Contacted cohort retains at measurably higher rate |
| Coach outreach rate on high-risk alerts | > 60% contacted within 7 days of flag |
| Coach satisfaction with weekly email report | ≥ 2 of 3 coaches say they would miss it if it stopped |
| Survey response rate (when triggered) | > 20% of recipients respond |
| Survey trigger fires correctly | Fires when class or studio-wide drop threshold is met; does not fire otherwise |
| Operational reliability | ≥ 95% of scheduled runs succeed (email delivery) |

### Phase 2 — Pilot

| Metric | Target |
|---|---|
| Onboarding time (new studio) | < 5 days |
| Model accuracy on real studio data | ≥ 80% |
| Automated deletion execution time | < 24 hours end-to-end |
| Studio renewal rate at pilot end | ≥ 50% |
| Token reduction (batched LLM calls) | ≥ 70% vs. baseline |

### Phase 3 — Full Deployment

| Metric | Target |
|---|---|
| Monthly recurring revenue | 2,500 EUR (at 10 studios average 249 EUR/month) |
| Gross margin per studio (ongoing) | > 85% |
| Churn rate among studio clients | < 20%/year |
| Net Promoter Score (studio owners) | > 40 |
| Time to positive ROI per new studio | < 3 months |

---

## 5.7 Commercialisation Model

**Model: Consulting Service → Managed SaaS**

**Phase 1–2: Consulting service**
The product is delivered as a managed service. Dina owns and operates the pipeline. The studio pays for setup + ongoing retainer. This keeps overhead low, allows fast customisation, and builds the case studies needed for Phase 3.

**Phase 3: Lightweight SaaS transition**
As onboarding becomes repeatable and multi-studio infrastructure is standardised, the service transitions toward a self-serve or low-touch model:
- Studio owner onboards via a short form (gym management system export format, coach email addresses, threshold preferences)
- n8n workflow auto-configures per studio_id
- Briefings delivered without manual consultant involvement per studio
- Consultant role shifts to: quarterly outcome reviews, model retraining, product development

**The retainer is a subscription:**
The monthly retainer is a subscription product. Studios do not own the system — they subscribe to its operation. This is intentional: it creates predictable recurring revenue, keeps the consultant in the loop for ongoing recalibration and compliance, and means the studio is never left operating something they cannot maintain. Studios are already accustomed to subscription tools (Mindbody, Gymdesk, Glofox) — this is a familiar commercial structure, not a new ask.

**Why not start as SaaS:**
Building a proper SaaS product (auth, billing, self-serve onboarding) before validating the hypothesis is premature investment. The consulting model generates revenue from day one and produces the learnings that inform a good product design. The transition to SaaS is a Phase 3 decision, not a Phase 1 requirement.

**Partnership track (Phase 3):**
Integration partnerships with gym management software providers (Mindbody, Glofox, Virtuagym) create distribution without requiring a direct sales motion for every studio. The AI retention layer becomes an add-on within software studios are already paying for. Revenue share model: 30% to platform partner, 70% retained.
