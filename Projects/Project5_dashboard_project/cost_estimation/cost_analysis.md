# Cost Estimation: AI Retention System for European Medium Fitness Chain

## 1. Scope and Assumptions

**Objective**  
Estimate the upfront and first‑year costs of an AI‑driven “Early Warning System” for member dropout, including dashboards, automation, and monitoring, for a European medium‑sized fitness chain (50–100 studios, ~200+ coaches).

**Business Assumptions (Europe)**  
- Average membership fee: €50 / month → €600 / year per member.  
- Effective client lifetime value (LTV): €1,500–€2,000 per retained member.  
- Baseline churn: ~60% of new members churn or become inactive within 6–12 months.  
- Baseline revenue loss per 100‑member studio: ≈€90,000–€120,000 per year.  

**System Impact (Conservative Scenario)**  
- Prevent 20 out of 60 early churners per 100 members.  
- Retained LTV: 20 × €1,500 = €30,000 per studio per year.  
- Target SaaS licence: €299 / month per studio → €3,588 per year.  

All costs below are expressed in euros and based on typical EU pricing and free tiers where possible.

---

## 2. One‑Time Setup Effort (Internal)

This section covers internal work effort (can be presented either as hours or as an internal cost estimate).

- **Data & Analytics setup**
  - Collect and clean historical attendance / workout data.
  - Build first version of the churn / risk model using Python (pandas, sklearn).
  - Create export for Tableau (CSV source, published to Tableau Public).
  - Effort: e.g., 40–60 hours of data & ML work.

- **Dashboard setup**
  - Design and build the “Retention & Risk” dashboard (5–7 key metrics).
  - Validate with 1–2 stakeholders, adjust visuals and filters.
  - Effort: e.g., 16–24 hours of BI work.

- **Automation and monitoring setup**
  - n8n workflow: daily job to fetch latest risk scores and send alerts (Slack/email).
  - LangSmith integration: log model calls and traces for transparency.
  - Basic error handling and logging.
  - Effort: e.g., 16–24 hours (automation + observability).

You can convert these hours to an internal cost if needed (e.g., 80–100 hours × €X/hour), but for the pitch, focus on: “Setup takes a few weeks of initial implementation work.”

---

## 3. Ongoing Tooling Costs (per Studio, per Year)

### 3.1 AI / LLM API

Assume you use a hosted LLM (OpenAI / Anthropic) for:

- Generating explanations / insights on top of numeric model outputs.  
- Summarising risk lists and suggested interventions.  

Example (you can adjust later):

- Average daily usage during pilot:
  - ~200 members scored per studio per day.
  - LLM prompts only for explanations (e.g., 20–50 members per day that are high‑risk).  
- API cost assumption:
  - Roughly €10–€30 per month per studio in LLM usage at pilot scale.
  - Annual estimate: **€120–€360 per studio**.

For the mini‑project, you can pick a single rounded number, e.g.:  

> “We assume ~€250 per year per studio in LLM usage at pilot scale.”

### 3.2 LangSmith (Monitoring)

LangSmith is used to:

- Log each AI call and trace.  
- Provide transparency dashboards.  

For the project, assume:

- Start on free tier for pilot.  
- Paid tier later (example placeholder): e.g., **€50–€100 per month** at scale.  

For the MVP pitch:

> “We assume LangSmith can run on a free or low‑cost tier during the pilot; any paid upgrade is included in the system licence.”

So you can effectively bundle this into the €299 / month licence.

### 3.3 n8n (Automation)

n8n is used to:

- Schedule daily risk checks.  
- Send alerts to Slack/Email when new high‑risk members appear.  

Assumption:

- Use n8n Cloud starter plan or small self‑hosted instance.  
- Effective cost per studio is very small because one instance can serve many studios.

For the pitch:

> “We include n8n automation costs in the platform fee; marginal cost per studio is negligible once the workflow is set up.”

### 3.4 BI Tool

- The dashboard is built in Tableau, published to Tableau Public for the pilot.
- For production, assume:
  - Existing Tableau licences, or
  - Tableau Creator (~€70/month) for whoever manages the workbook.

For simplicity:

> “We assume the client already has BI licences; if not, this is a separate standard BI cost (not specific to this AI project).”

---

## 4. Proposed Pricing Model (EU)

### 4.1 Licence per Studio

To keep it simple and aligned with the financial assumptions:

- **Licence**: €299 per month per studio.  
- **Annual cost per studio**: €3,588.  

This licence is intended to cover:

- AI model hosting and updates.  
- LLM usage for explanations (within reasonable limits).  
- LangSmith monitoring environment.  
- n8n workflows for alerts and integrations.  
- Access to the retention dashboard (via existing BI licences).

### 4.2 Example for 10 Studios (Pilot)

If Chleo starts with a 10‑studio pilot:

- Annual platform cost: 10 × €3,588 = **€35,880 per year**.  
- Conservative retained revenue:
  - Each studio: ~€30,000 retained per year (from prevented churn).  
  - 10 studios: ~€300,000 retained per year.  

Even after conservative assumptions and platform cost, pilot‑level ROI is strong.

---

## 5. ROI Illustration

For a single 100‑member studio:

- Baseline:
  - 60 members churn early.
  - LTV ~€1,500 each.
  - Lost value ≈ €90,000 per year.
