# Spottr
### AI-powered member retention for boutique fitness studios
**Capstone Project · Dina Bosma-Buczynska · March 2026**

---

Spottr predicts which gym members are at risk of cancelling 4–6 weeks before they do, and surfaces that risk to coaches every Monday morning in plain English. Coaches decide whether and how to reach out. The AI provides context. The human makes the call.

Built for boutique studios (80–250 members) where every coach knows every member personally and every cancellation is real revenue — but no coach can mentally track attendance patterns for 150 people at once.

---

## How it works

Three automated outputs:

| Output | Trigger | Who receives it |
|---|---|---|
| Weekly briefing email | Monday 07:00 | All coaches + studio owner |
| Event-triggered member survey | Class or studio-wide attendance drop | At-risk members (max once per 5 weeks) |
| Retention dashboard | Always on | Coaches (browser bookmark) |
| Monthly survey summary | 1st of every month | Studio owner |

**Churn model:** scikit-learn logistic regression trained on 4,000 labelled gym members. Outputs a churn probability per member, mapped to HIGH / MEDIUM / LOW tiers. Members in private coaching get an additional attendance-based override.

**WATCH flag:** Members who still attend regularly but rate their satisfaction low in a survey. Attendance alone would not flag them. The survey signal does. These are often the most fixable churns — the member hasn't checked out yet.

**AI coaching note:** GPT-4o-mini writes one short paragraph per flagged member — background for the coach before they decide whether to reach out. Not a script. Not a message to send.

---

## What's in this directory

### Documentation

| File | Contents |
|---|---|
| [use_case_definition.md](use_case_definition.md) | Use case framing, target user, problem definition, scope boundaries |
| [strategic_plan.md](strategic_plan.md) | Deployment phases (POC → Pilot → Full), GTM strategy, pricing, commercialisation model |
| [roi_risk_assessment.md](roi_risk_assessment.md) | Revenue impact projections, cost model, risk register |
| [green_tech_assessment.md](green_tech_assessment.md) | Energy usage, carbon proxy estimates, design decisions that reduce compute |

### MVP

| File | Contents |
|---|---|
| [mvp/mvp_documentation.md](mvp/mvp_documentation.md) | Full MVP scope: data inputs, pipeline design, n8n workflow architecture, AI prompts, output formats |
| [mvp/coach_guide.md](mvp/coach_guide.md) | Plain-English guide for coaches: what the briefing contains and how to use it |
| [mvp/consent_gate_guide.md](mvp/consent_gate_guide.md) | How the wearable data consent gate works technically and operationally |

### POC

| File | Contents |
|---|---|
| [poc/poc_documentation.md](poc/poc_documentation.md) | POC scope, success criteria, what is and isn't live, validation methodology |
| [poc/Spottr — Weekly Email Report.json](poc/Spottr%20—%20Weekly%20Email%20Report.json) | n8n workflow: Monday briefing email |
| [poc/Spottr — Survey Trigger.json](poc/Spottr%20—%20Survey%20Trigger.json) | n8n workflow: event-triggered member survey |
| [poc/Spottr — Private Coaching Workflow.json](poc/Spottr%20—%20Private%20Coaching%20Workflow.json) | n8n workflow: coaching add-on briefing (Phase 2) |

### Compliance

| File | Contents |
|---|---|
| [compliance/gdpr_documentation.md](compliance/gdpr_documentation.md) | GDPR framework: lawful basis, data minimisation, deletion procedure, member rights |
| [compliance/eu_ai_act_compliance.md](compliance/eu_ai_act_compliance.md) | EU AI Act classification (Limited Risk), obligations, human oversight design |
| [compliance/data_processing_agreement_template.md](compliance/data_processing_agreement_template.md) | Article 28-compliant DPA template, ready to sign before go-live |
| [compliance/member_wearable_consent_form.md](compliance/member_wearable_consent_form.md) | Article 9(2)(a) consent form for wearable data (Phase 2 coaching add-on) |

### Pitch deck

| File | Contents |
|---|---|
| [spottr_pitch_deck.html](spottr_pitch_deck.html) | 10-slide HTML pitch deck. Open in browser, navigate with arrow keys. |

---

## Key numbers

| Metric | Value |
|---|---|
| Demo member population | 150 (boutique studio scale) |
| Source dataset | Endomondo workout data, 167,783 sessions |
| Training data | 4,000 labelled gym members (gym_churn_us.csv) |
| Model accuracy | 92.5% on held-out test set |
| ROC-AUC | 0.977 |
| High-risk members in demo | 60 (40%) |
| Revenue at risk in demo | ~€90,000 |
| Estimated AI cost per weekly run | €0.10–0.20 across all members |
| POC duration | 90 days |
| POC price | €2,000 (setup + operation) |
| Monthly retainer post-POC | €149–€399 depending on studio size |

---

## Deployment phases

| Phase | Duration | Studios | Gate to proceed |
|---|---|---|---|
| POC | 90 days | 1 | Flagged members cancel at ≥2× rate AND contacted members retain better AND ≥2 of 3 coaches say they'd miss the briefing |
| Pilot | 6 months | 3–5 | New studio onboards in <5 days, model accuracy ≥80% on real data, at least one studio renews |
| Full deployment | Ongoing | 10+ | Commercial infrastructure live, automated deletion workflow verified |

---

## What is and isn't live in the POC

**Live:**
- Churn prediction pipeline (visit data → logistic regression → risk scores)
- Weekly email briefing (n8n, Monday 07:00, all coaches + studio owner)
- Event-triggered member survey (Tally, class or studio-wide drop threshold)
- Monthly survey summary email (studio owner, 1st of month)
- Retention dashboard (Plotly, runs locally on studio computer)
- AI coaching note per flagged member (GPT-4o-mini, one batch per week)
- Manual GDPR deletion process (48-hour response)

**Not live (Phase 2):**
- Coaching add-on (check-in tracking + wearable integration)
- Automated deletion scheduling
- Multi-studio infrastructure
- Direct API integration with gym management systems (Mindbody, Glofox)

---

*The system runs on synthetic demo data. Architecture mirrors a real studio deployment — only the data source changes at go-live.*

---

## Live demo

- n8n workflow: [dina2.app.n8n.cloud](https://dina2.app.n8n.cloud)
- Demo walkthrough: https://github.com/dlbosma-hue/bootcamp_env/issues/2#issue-4186433120

