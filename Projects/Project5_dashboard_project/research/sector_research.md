# Sector Research: Fitness / Health Tech (Europe)

## 1. Sector Overview

The European fitness sector is large and data-rich. Around 65,000 health and fitness clubs serve roughly 68 million members across Europe, generating €31–36 billion in revenue annually (EuropeActive / Deloitte). Post-COVID recovery has been strong, and boutique fitness — HIIT studios, cycling, strength training — is the fastest-growing segment.

Our client, Chleo, runs a European boutique fitness chain: studios of up to 200 members per location, premium pricing, and a coaching model where staff know every member by name. Boutique fitness — HIIT studios, cycling, strength training — is the fastest-growing segment of the European market and operates on a fundamentally different model to large commercial gyms. Margins depend on retention, and retention depends on personal relationships.

---

## 2. The Core Business Problem: Churn

Industry benchmarks (IHRSA) put annual churn at approximately 60% for the fitness sector. For a boutique studio with up to 200 premium members, that translates to €90,000–€120,000 in preventable lost revenue per year, based on a lifetime value of €1,500 or more per member.

Unlike large commercial gyms that quietly profit from inactive direct debits, boutique chains cannot absorb this loss silently. When a boutique member cancels, it is an active, conscious decision — and it was almost certainly preceded by weeks of visible disengagement that the coaching team had the opportunity to catch.

The pattern is predictable: members don't quit suddenly. They "quiet quit" — attendance drops gradually over weeks, coaches miss the signals, and by the time anyone notices, the decision is already made. The intervention window is roughly **4–6 weeks before cancellation**, and that's exactly what this system is designed to catch.

---

## 3. Data Sources

**Primary dataset: Endomondo Fitness Trajectories (Kaggle)**
~250K+ real workout sessions with user IDs, timestamps, sport types, and duration. Used to derive the consistency, intensity, and engagement metrics that correlate with dropout. This is the dataset underlying the model in the case study (logistic regression, strong predictive performance validated on European fitness data).

**Supporting dataset: Gym Customer Churn (Kaggle / "Model Fitness")**
Member-level attributes plus a real churn label — useful for validating heuristics and showing churn breakdowns by segment (age, contract type, visit frequency).

Both are publicly available, open-licensed, and realistic for a European fitness chain context.

---

## 4. Sector Trends and AI Opportunity

Three trends are driving AI relevance in European fitness right now:

**Wearables and continuous tracking** — Members increasingly use apps and devices (Apple Watch, Garmin, GPS running apps) to log workouts. This creates the kind of behavioural data streams that make dropout prediction possible.

**Hybrid and digital coaching** — Remote and online coaching means coaches can't rely on just seeing a member in person. Data has to fill that visibility gap.

**Subscription model pressure** — Recurring revenue makes retention disproportionately valuable. Reducing churn by even 10–15% has a bigger P&L impact than most new revenue initiatives for a mid-size chain.

The direct AI applications for Chleo:
- Early-warning dropout prediction (visit gaps, session frequency drops, consistency changes)
- Coach dashboards that surface risk across a full client list, not just the loudest members
- Scheduling and capacity optimisation based on attendance patterns

---

## 5. Why Transparency Matters Here

Chleo's main objection: **"AI is a black box — I don't know how it's making decisions about my members."**

This is a real and valid concern in fitness. Members share health-adjacent data (workout history, activity patterns), and coaches have personal relationships with them. An AI that flags someone without explanation erodes trust — with coaches and with members.

That's why this project is built with LangSmith monitoring from day one. Every AI recommendation is logged, every score is auditable, and the system is designed to explain itself — not just produce outputs. Coaches see *why* a member was flagged, not just that they were.

This also prepares the chain for GDPR accountability requirements and the incoming EU AI Act, which will require documented reasoning for AI systems that affect individuals.
