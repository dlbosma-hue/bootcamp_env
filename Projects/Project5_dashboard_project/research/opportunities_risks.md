# AI Opportunity & Risk Mapping
**Sector:** Fitness / Health Tech
**Company size:** Medium (50–200 studios / coaches)
**Prepared for:** Chleo – CEO briefing

---

## 1. Opportunity Map

### O1 – Dropout Prediction (Early Warning System)
**What:** ML model flags members at risk of cancellation 4–6 weeks before they leave, based on visit frequency, session duration trends, and recency.
**Business value:** Intervene before churn — targeted retention offer costs ~€20–50 vs. €150–300 customer acquisition cost.
**Feasibility:** High. Behavioural data (check-ins, bookings, app logins) is already collected. Logistic regression or gradient boosting on tabular data; no complex infrastructure needed.
**KPI impact:** Reduce churn rate from ~60% → ~45% = ~€72K saved per studio per year.

---

### O2 – Coach & Class Utilisation Balancing
**What:** Dashboard + alert system that surfaces underperforming class slots and overloaded coaches in real time.
**Business value:** Optimise scheduling to reduce empty slots (revenue leak) and prevent coach burnout (staff turnover cost ~€8K per coach replacement).
**Feasibility:** High. Booking data feeds a simple aggregation layer; n8n can trigger Slack/email alerts when utilisation drops below threshold.
**KPI impact:** 10–15% improvement in class fill rate = €30–60K incremental annual revenue per studio.

---

### O3 – Personalised Member Engagement
**What:** AI generates personalised workout suggestions, challenge invites, and re-engagement messages based on member history and goals.
**Business value:** Members who receive relevant communication are 2–3× more likely to renew (fitness industry benchmark).
**Feasibility:** Medium. Requires CRM integration and member profile data. LLM-generated message variants + send-time optimisation via n8n.
**KPI impact:** +5–8% renewal rate on at-risk segment.

---

### O4 – Demand Forecasting for Staffing
**What:** Predict class attendance 2–4 weeks ahead by combining historical bookings, seasonality, and local event data.
**Business value:** Right-size staffing — avoid paying coaches for empty classes or turning members away from full ones.
**Feasibility:** Medium. Time-series model (Prophet or simple ARIMA) on booking history; retrainable monthly.
**KPI impact:** 8–12% reduction in idle staff hours.

---

### O5 – AI Transparency Dashboard for Management
**What:** LangSmith-style monitoring layer showing what the AI recommended, why, and what happened — visible to non-technical management.
**Business value:** Directly addresses Chleo's concern about AI opacity. Builds internal trust and supports GDPR accountability obligations.
**Feasibility:** High. LangSmith + simple audit log in existing BI tool.
**KPI impact:** Faster AI adoption internally; reduced compliance risk.

---

## 2. Risk Register

### R1 – Data Privacy & GDPR Compliance
**Risk:** Processing biometric and location data (heart rate, GPS) without explicit consent or proper data minimisation violates GDPR Article 9.
**Likelihood:** High — fitness data qualifies as health data (special category).
**Impact:** Fines up to €20M or 4% of annual turnover; reputational damage.
**Mitigation:**
- Anonymise / pseudonymise member IDs before model training
- Obtain explicit opt-in for AI-driven personalisation
- Appoint a Data Protection Officer if processing at scale
- Keep raw GPS/biometric data out of the AI pipeline entirely (aggregate only)

---

### R2 – Model Bias & Unfair Treatment
**Risk:** Churn model may systematically under-serve or over-target certain demographic groups (e.g. older members, part-time users), leading to unfair retention offers.
**Likelihood:** Medium.
**Impact:** Member complaints, reputational risk, potential discrimination claims.
**Mitigation:**
- Audit model outputs by age group, contract type, and gender before deployment
- Use fairness metrics (equal opportunity, demographic parity) during evaluation
- Human review gate before any automated outreach

---

### R3 – Staff Resistance & Change Management
**Risk:** Coaches and front-desk staff may distrust or ignore AI recommendations, reducing ROI; or over-rely on them, reducing personal judgment.
**Likelihood:** High — common in service businesses adopting AI for the first time.
**Impact:** Low adoption, wasted investment, potential employee relations issues.
**Mitigation:**
- Frame AI as "coach's assistant", not replacement
- Involve coaches in defining the KPIs the model optimises for
- Provide short training sessions; show the LangSmith transparency dashboard to build trust

---

### R4 – Data Quality & Coverage Gaps
**Risk:** Incomplete check-in logs, inconsistent class records, or missing member profiles produce unreliable model outputs ("garbage in, garbage out").
**Likelihood:** Medium-High for a chain that has grown organically across 50–200 locations.
**Impact:** Low-confidence predictions surface as high-confidence; wrong interventions sent to members.
**Mitigation:**
- Data audit before model training (completeness, consistency checks)
- Confidence scores displayed alongside every AI recommendation
- Fallback rules for members with insufficient history (<4 weeks)

---

### R5 – Vendor & API Lock-in
**Risk:** Over-reliance on a single LLM provider (OpenAI / Anthropic) for personalisation or insight generation creates cost and continuity risk.
**Likelihood:** Low-Medium.
**Impact:** Cost spikes if pricing changes; service interruption if API goes down.
**Mitigation:**
- Abstract LLM calls behind a provider-agnostic interface
- Use open-weight models (Mistral, LLaMA) for non-sensitive batch tasks
- Cap monthly API spend; monitor via LangSmith token usage tracking

---

### R6 – Regulatory Uncertainty in Health AI
**Risk:** EU AI Act classifies some health-adjacent AI applications as high-risk, requiring conformity assessments and human oversight obligations.
**Likelihood:** Medium (Act applies from 2026 for most systems).
**Impact:** Compliance costs; potential need to pause or redesign certain features.
**Mitigation:**
- Scope initial AI use cases to "low-risk" category (business analytics, scheduling)
- Document model purpose, training data, and decision logic now — easier to comply later
- Monitor EU AI Act implementation timeline

---

## 3. Opportunity vs Risk Matrix

```
         HIGH IMPACT
              │
    O1 Churn  │  O3 Personalisation
    O2 Coach  │  O4 Forecasting
    O5 Transp.│
──────────────┼──────────────────────
   LOW EFFORT │  HIGH EFFORT
              │
    R1 GDPR   │  R6 AI Act
    R3 Staff  │  R2 Bias
              │  R4 Data quality
              │
         LOW IMPACT
```

**Priority order for MVP:**
1. O1 Dropout prediction + O5 Transparency layer — highest ROI, buildable in 2 days
2. O2 Coach utilisation dashboard — adds immediate operational value
3. O3/O4 — Phase 2 after data quality (R4) is addressed

---

## 4. Summary for Chleo

| | Opportunity | Estimated annual value |
|---|---|---|
| Reduce churn 60% → 45% | Dropout prediction (O1) | ~€72K / studio |
| Fill empty class slots +10% | Utilisation balancing (O2) | ~€45K / studio |
| Improve renewal rate +6% | Personalisation (O3) | ~€30K / studio |
| **Total (conservative)** | | **~€147K / studio** |

**Top 3 risks to manage first:** GDPR compliance (R1), staff buy-in (R3), data quality (R4).
All are solvable within the first 90 days with the right process — none require delaying the project.
