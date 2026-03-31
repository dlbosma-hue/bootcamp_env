# ROI and Risk Assessment
### Spottr

---

## 1.1 Cost Estimates

### Upfront Costs (One-Time)

| Item | Cost (EUR) | Notes |
|---|---|---|
| System setup, configuration, data pipeline | 2,000 | Includes initial integration with gym management system, pipeline configuration, and dashboard setup |
| Coach training and onboarding | Included in setup | One session, 1–2 hours. Covers: reading the weekly email, using the dashboard, wearable consent process. |
| Retention dashboard (Plotly) | Included in setup | Installed on studio computer. Coaches access via browser at localhost:8050. Shows member risk overview and priority contact list. Phase 2: hosted on Railway so accessible from any device via URL (add ~€5–7/month). |
| Infrastructure at pilot scale | 0 | All components use free tiers: n8n Cloud free, Plotly Dash local |
| **Total Upfront** | **2,000** | Pilot studio only — see billing model below |

**What the €2,000 actually is:**
There are no significant cash costs at POC scale — n8n, Plotly, and scikit-learn all run on free tiers or local hardware. The €2,000 setup fee covers consultant time (20–25 hours at €80–100/hour) to adapt and configure the system for a specific studio:

| Task | Hours |
|---|---|
| Data pipeline config (CSV format per gym management system) | 4 |
| n8n workflow setup, consent gate, testing | 4 |
| Plotly dashboard install and customisation | 2 |
| Model retraining preparation | 3 |
| Coach onboarding session (1–2 hours) + materials | 2 |
| Compliance documents (DPA, privacy notice) | 3 |
| End-to-end testing and debugging | 4 |
| POC debrief and outcome report | 3 |
| **Total** | **25 hours** |

**Billing model by studio:**
- **Pilot studio (Phase 1):** €2,000 one-time setup. No subscription during the 90-day POC. If Stage 1 and Stage 2 pass, subscription begins post-debrief (€149–399/month depending on size).
- **Subsequent studios (Phase 2+):** €500–1,000 setup (onboarding is faster with a proven system) + subscription from Day 1.
- **At scale (Phase 3):** Setup fee reduces as onboarding becomes automated. Recurring subscription is the primary revenue stream.

*Assumption: Costs are for a single boutique fitness studio managed by a solo consultant using shared infrastructure on free/low-cost tiers.*

### Ongoing Costs (Monthly, Pilot Scale)

| Item | Cost (EUR/month) | Details |
|---|---|---|
| Churn prediction model (scikit-learn) | **€0** | Logistic regression runs locally on the studio computer. No API, no cloud inference, no per-call fee. Scoring 150 members takes under 1 second. Cost increases only if deployed to a hosted server (Phase 2: ~€5–7/month on Railway hobby tier). |
| OpenAI API (GPT-4o-mini) | ~0.60 | **1 batched call per weekly email** × ~1,000 tokens avg × 4.3 weeks/month. €0.15 per call. (Previous Project 5 architecture used 12 sequential calls at ~€1.80/month — replaced with single batched prompt in this system.) |
| n8n Cloud | ~20 | Shared across studios at pilot scale; scales linearly with studio count |
| **Total Ongoing** | **~20.60/month** | ~4 EUR per studio at 5-studio pilot |

**Cost Scaling:**
- **Phase 1 (1 studio):** ~21 EUR/month total shared infrastructure.
- **Phase 2 (3–5 studios):** Add Railway hosting for dashboard (~7 EUR/month). Per-studio cost drops to ~5–6 EUR/month.
- **Phase 3 (10+ studios):** n8n Pro tier required (~100 EUR/month at 50k+ executions). Per-studio marginal cost approaches ~0.60 EUR/month (OpenAI only). Gym management API fees may apply per studio if direct API integration is used (Mindbody: ~50 EUR/studio/month — offset by removing manual CSV step).

**Cost tracking:** Token count is tracked via OpenAI API response metadata. Alert fires if tokens per briefing exceed 8,000.

**Cost Structure Assumptions:**
- OpenAI API: GPT-4o-mini at USD 0.00015 per input token, USD 0.0006 per output token. Single batched call per weekly run containing all flagged members in one prompt.
- scikit-learn model: Runs on local hardware. No inference cost at POC scale. Railway hosting (~€5–7/month) is a Phase 2 cost once the scoring API needs to be accessible to n8n over the internet.
- n8n Cloud: Free tier for <1,000 executions/month; first paid tier at 20 EUR/month for 10,000 executions/month

**Cost Reduction vs prior architecture (Green Tech):**
- Batching LLM calls from 12 sequential (Project 5) to 1 batched (this system): ~92% reduction in OpenAI cost per briefing (€1.80 → €0.15)
- ML model runs locally at zero marginal cost — no inference API needed at POC scale
- n8n trigger weekly instead of daily: 80% reduction in workflow executions

---

## 1.2 Business Value Estimate

### Quantified Benefits (Per Studio, Per Year)

| Metric | Value | Basis |
|---|---|---|
| Revenue at risk | 90,000–120,000 EUR | IHRSA blended benchmark: 60% churn × 100 direct members × 1,500 EUR LTV (upper end). Conservative boutique case: 40% churn × 100 members × 1,000 EUR LTV = 40,000 EUR at risk. POC establishes studio-specific baseline. |
| Target churn reduction | 15 percentage points | Conservative: retain 1-in-3 at-risk members (20 of 60 churners) |
| Retained revenue | 30,000 EUR | 20 members × 1,500 EUR LTV |
| Coach time saved | 2 hours/week | Automated alerts eliminate manual member screening |
| Coach time value | 2,600 EUR/year | 2 hrs/week × 52 weeks × 25 EUR/hour (estimated coach rate) |
| **Total Annual Benefit** | **32,600 EUR** | Retained revenue + time savings |

**Business Value Assumptions:**
- Member LTV (1,500 EUR): Upper-end estimate based on IHRSA European benchmark (100–150 EUR/month × 12 months). Boutique-specific data suggests 10-month average tenure is more realistic, placing conservative LTV at 1,000 EUR. The POC will establish a studio-specific baseline in Weeks 1–4 to replace this estimate with real data.
- Churn Rate (60%): IHRSA blended industry average — includes budget chains with 70–80% churn. Boutique studios with strong community typically report 30–45%. 40% is used as the boutique-realistic figure in the conservative case below. The 60% figure is used in the base case as a worst-case bound. POC Week 1–4 establishes the studio's actual baseline before any benefit claims are made.
- Intervention Success (33%): Provisional estimate based on fitness retention literature (group exercise loyalty lift: ~20%; targeted outreach: 15–30%). No single published study establishes a precise figure for coach-led outreach in boutique studios. The POC Stage 2 (Weeks 7–12) is designed specifically to measure this from real contacted vs. non-contacted outcomes. All projections below should be treated as pre-POC estimates, not guarantees.
- Coach Hourly Rate (25 EUR): Market estimate for boutique fitness coaches in Germany. Range 20–35 EUR/hour depending on seniority.

**Sensitivity Analysis:**

| Case | Intervention success | Churn assumption | LTV | Annual benefit | ROI (12 months) |
|---|---|---|---|---|---|
| Conservative | 20% | 40% boutique | 1,000 EUR | ~11,000 EUR | ~304% |
| Base | 33% | 60% blended | 1,500 EUR | 32,600 EUR | ~1,099% |
| Upside | 50% | 60% blended | 1,500 EUR | 47,600 EUR | ~1,652% |

*All figures are projections. The conservative case uses boutique-specific churn (40%) and LTV (1,000 EUR) — this is the number to defend in a sceptical conversation. The base and upside cases use IHRSA blended benchmarks and should be presented as "validated in POC" rather than assumed.*

---

## 1.3 ROI Calculation

### Simple ROI Formula
```
ROI (%) = [(Net Benefit − Total Cost) / Total Cost] × 100

Net Benefit = Annual Retained Revenue + Coach Time Savings
Total Cost = Upfront Cost + (Monthly Ongoing Cost × 12 months for year 1)
```

### ROI Results

| Metric | 12-Month Horizon | 36-Month Horizon |
|---|---|---|
| Year 1 Total Cost | 2,720 EUR | 2,720 EUR (Year 1 only) |
| Year 2 Total Cost | — | 696 EUR |
| Year 3 Total Cost | — | 696 EUR |
| Cumulative 36-Month Cost | — | 4,112 EUR |
| Annual Benefit (Year 1–3) | 32,600 EUR | 32,600 EUR (stable) |
| Net Benefit (12 months) | 29,880 EUR | — |
| Net Benefit (36 months) | — | 93,788 EUR |
| **ROI (12 months)** | **1,099%** | — |
| **ROI (36 months)** | — | **2,282%** |

### Break-Even Analysis

| Metric | Value |
|---|---|
| Annual Benefit | 32,600 EUR |
| Year 1 Total Cost | 2,720 EUR |
| Break-Even Point | 33 days |
| Months to Positive ROI | 1.1 months |

*Base case: The system pays for itself within ~33 days and generates positive return on every subsequent month of operation. Conservative case (boutique-realistic inputs): break-even at approximately 90 days — within the 90-day POC window. All ROI figures are projections based on pre-POC benchmarks. The POC debrief at Week 13 replaces these estimates with studio-specific outcomes.*

---

## 1.4 Risk Assessment Matrix

### Framework

**Likelihood (L) & Impact (I) Scales (1–5):**
- L1/I1: Almost never / Negligible
- L2/I2: Unlikely / Minor
- L3/I3: Possible / Moderate
- L4/I4: Likely / Severe
- L5/I5: Almost certain / Catastrophic

**Risk Level (L × I):**
- Green (1–5): Low risk, monitor
- Amber (6–11): Medium risk, mitigation required
- Red (12–25): High risk, mandatory controls

---

### REGULATORY RISKS

| Risk | L | I | Level | Mitigation Strategy |
|---|---|---|---|---|
| GDPR non-compliance: wearable data processing | 3 | 5 | **15 (Red)** | ✓ Consent Gate: Explicit opt-in required before any Fitbit data is accessed. Wearable consent stored as `consent_wearable` boolean. ✓ Technical Enforcement: n8n workflow blocks Fitbit API call if `consent_wearable = false`. ✓ Audit Trail: n8n execution logs record every workflow run and data access event. ✓ Withdrawal: Member withdraws consent → local data deleted within 48 hours, n8n execution logs purged within 30 days. |
| EU AI Act classification challenge | 2 | 4 | **8 (Amber)** | ✓ Classification: System classified as Limited Risk (Article 50 transparency only). Step-by-step reasoning documented. ✓ Human-in-the-Loop: All outputs are recommendations; no autonomous decisions made. ✓ Audit Trail: n8n execution logs provide workflow-level audit trail. Quality gate enforced: scores > 0.70 required before delivery. ✓ Transparency Label: Members informed in privacy notice. |
| Data breach during wearable OAuth token storage | 2 | 4 | **8 (Amber)** | ✓ Token Management: Fitbit OAuth tokens stored in local .env files only. Never committed to version control. ✓ No Third-Party Transmission: Tokens never forwarded to OpenAI or n8n. ✓ Immediate Revocation: Studio owner revokes Fitbit token via Fitbit dashboard if breach detected. ✓ Quarterly Rotation: Tokens rotated every 90 days. |

---

### TECHNICAL RISKS

| Risk | L | I | Level | Mitigation Strategy |
|---|---|---|---|---|
| Model bias against low-frequency members | 3 | 3 | **9 (Amber)** | ✓ Data Threshold: Members with < 4 weeks of check-in history excluded from risk predictions. Flagged as "Insufficient Data" separately. ✓ Explicit Filtering: Feature engineering excludes members with < 8 total sessions. ✓ Human Review: Bottom quartile of visit frequency requires coach manual review. ✓ Monitoring: Feature distribution reviewed manually at each weekly run; alerts if low-frequency cohort proportion changes by > 10%. |
| LLM hallucination in insight generation | 2 | 3 | **6 (Amber)** | ✓ Temperature Control: GPT-4o-mini set to temperature = 0 (deterministic). ✓ Output Review: n8n execution log shows full prompt and GPT-4o-mini response after every run — coach can flag poor outputs. ✓ Scope Limitation: LLM only processes aggregated statistical summaries. Never given raw member names or personal details. ✓ Fact-Check Protocol: Insights cross-checked against source CSV data before delivery. |
| Data quality gaps from gym CSV export | 4 | 3 | **12 (Red)** | ✓ Pre-Pipeline Audit: Data quality check run before first briefing: validates date formats, membership ID consistency, no negative session counts. ✓ Data Exclusion: Members with inconsistent data flagged and excluded from predictions. ✓ Confidence Scoring: Every risk label accompanied by a confidence score (0.0–1.0). High-risk with confidence <0.60 requires coach verification. ✓ Incremental Validation: Weekly data audit after first 4 weeks. |
| Model degradation on new studio data | 3 | 4 | **12 (Red)** | ✓ Retraining Schedule: Requires retraining on real studio data after 6–8 weeks of pilot data collection. ✓ Validation Protocol: New model validated on hold-out test set (20% of studio data). Accuracy must remain ≥ 80%. ✓ Fallback: If new model accuracy < 80%, system reverts to the baseline model trained on gym_churn_us.csv (4,000 labelled members, 92.5% accuracy). ✓ Monitoring: Accuracy re-evaluated monthly via manual review of n8n execution logs and member outcome data. |
| API rate limits or service outages | 2 | 3 | **6 (Amber)** | ✓ Error Handling: n8n workflow configured with exponential backoff (retry up to 3 times, 5s–30s intervals). ✓ Fallback Alert: If OpenAI API fails, n8n sends manual alert to studio owner. ✓ Queue Mechanism: n8n workflow retries failed OpenAI calls on next scheduled run. ✓ SLA Monitoring: Weekly report on uptime; SLA target ≥ 99% for scheduled runs. |

---

### ETHICAL RISKS

| Risk | L | I | Level | Mitigation Strategy |
|---|---|---|---|---|
| Algorithmic bias affecting retention decision | 2 | 4 | **8 (Amber)** | ✓ Fairness Check: Model validated for performance parity across membership tiers. Acceptable difference < 5% accuracy. ✓ Explainability: Every member classification includes specific behavioral signals. No opaque scoring. ✓ Coach Training: Coaches instructed to treat AI classification as a starting point, not a final decision. |
| Misuse of risk scores for discriminatory contact | 2 | 4 | **8 (Amber)** | ✓ Governance: DPA explicitly prohibits using AI scores for anything other than retention coaching. ✓ Code of Conduct: Coach onboarding includes GDPR-compliant contact guidelines. ✓ Audit Trail: Every contact action logged and audited quarterly. ✓ Member Complaint Process: Members can object to AI-driven analysis at any time. |
| Data subject unaware of AI use in coaching | 3 | 3 | **9 (Amber)** | ✓ Transparency Notice: Privacy notice states AI tool is used to monitor engagement. ✓ Consent Form: Wearable consent form explicitly describes which data is used and why. ✓ Accessible Language: Privacy notice in plain language, < 3 minute read. ✓ Right to Object: Members can request no AI analysis at any time; honored within 24 hours. |

---

### OPERATIONAL RISKS

| Risk | L | I | Level | Mitigation Strategy |
|---|---|---|---|---|
| Coach adoption failure | 3 | 4 | **12 (Red)** | ✓ Zero Friction Integration: Weekly report delivered by email. No new tool to learn. ✓ Explainability: Each alert shows why a member was flagged. ✓ Onboarding Session: Mandatory 1–2 hour training included in 2,000 EUR setup. ✓ Feedback Loop: Monthly retrospective with coaches; system adjusted based on input. |
| Urban Sports Club member dilution | 3 | 3 | **9 (Amber)** | ✓ Filtering Rule: System explicitly excludes studios where > 30% of members use USC or Gympass passes. ✓ Screening Question: Studio onboarding includes question about USC/Gympass percentage. ✓ Reporting: Monthly briefing includes scope indicator. |
| Multi-studio identity and data isolation failure | 2 | 4 | **8 (Amber)** | ✓ Studio ID Isolation: Each studio assigned a unique `studio_id` in n8n workflow. ✓ Separate LLM Context: n8n workflow processes one studio's summary per run — no cross-studio data in prompt. ✓ Email Isolation: Each studio has a dedicated email recipient list configured in n8n. ✓ Quarterly Data Audit: Studio manager confirms data isolation quarterly. |

---

### ENVIRONMENTAL RISKS

| Risk | L | I | Level | Mitigation Strategy |
|---|---|---|---|---|
| Energy cost scaling with studio count | 3 | 2 | **6 (Amber)** | ✓ Batched LLM Calls (Priority 1): Reduce 12 sequential calls to 1 batched call. ~80% reduction in input tokens per briefing. Planned for Phase 2. ✓ Weekly Trigger (Priority 2): Change n8n schedule from daily to weekly. ✓ Energy Proxy Metric: Token count tracked via OpenAI API response metadata logged in n8n. Alert if tokens/briefing > 8,000. ✓ Green Tech Report: Annual carbon footprint estimate published. |

---

## 1.5 Risk Summary

| Risk Category | Count | Red (High) | Amber (Medium) | Green (Low) |
|---|---|---|---|---|
| Regulatory | 3 | 1 | 2 | 0 |
| Technical | 4 | 2 | 2 | 0 |
| Ethical | 3 | 0 | 3 | 0 |
| Operational | 3 | 1 | 2 | 0 |
| Environmental | 1 | 0 | 1 | 0 |
| **TOTAL** | **14** | **4** | **10** | **0** |

**Conclusion:** The system carries 4 red-level risks, all with documented mitigation strategies in place or planned before Phase 2 pilot. The most critical risks (GDPR wearable processing, data quality, model drift, coach adoption) have controls either already operational or scheduled for near-term implementation. Residual risk is acceptable for a pilot deployment with a single studio and human oversight throughout.
