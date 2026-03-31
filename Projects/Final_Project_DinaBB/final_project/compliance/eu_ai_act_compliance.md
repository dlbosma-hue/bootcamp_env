# EU AI Act Compliance Documentation
### Spottr

---

## 2.1 Risk Classification

**Classification Decision: LIMITED RISK (Article 50)**

| Element | Decision |
|---|---|
| Risk Classification | LIMITED RISK |
| High-Risk System? | No |
| Unacceptable-Risk System? | No |
| EU AI Act Article Applicable | Article 50 (Transparency Obligations) |
| Conformity Assessment Required? | No (notified body review not required) |
| Mandatory CAB Certification? | No |

---

## 2.2 Classification Reasoning (Step-by-Step)

### Step 1: Unacceptable Risk Check (Article 5)

| Criterion | Applies? | Justification |
|---|---|---|
| (a) Subliminal manipulation | No | System generates plain-language behavioral alerts. Text is explicit, not subliminal. No sensory manipulation. |
| (b) Exploitation of vulnerabilities | No | System targets coaches (professionals, not vulnerable individuals). Coaches exercise independent judgment before any member contact. Members have opt-out right. |
| (c) Real-time biometric surveillance | No | System does not perform biometric surveillance. Uses voluntary visit records and optional Fitbit data with explicit consent. No public authority involvement. |
| (d) Social scoring by public authorities | No | System is operated by a private consultant for a private studio. No public authority involved. No legal consequences for members. Classification is advisory only. |

**Verdict: ✓ NONE APPLY — System is NOT unacceptable risk.**

---

### Step 2: High-Risk Classification Check (Annex III)

| Annex III Category | Criterion | Applies? | Justification |
|---|---|---|---|
| 4(a) – Employment/HR | Evaluating employees affecting employment terms | No | Coaches use system voluntarily as a decision-support tool. System does not evaluate coach performance or make employment decisions. |
| 4(b) – Employment/HR | Automated recruitment or job applicant evaluation | No | Not applicable. |
| 4(c) – Access to Essential Services | Determining eligibility for essential services | No | Fitness membership is a commercial service, not an essential service as defined by the EU AI Act. |
| 4(d) – Biometric Categorisation | Categorising individuals based on biometric identifiers | No | System does not categorise individuals by biometric data. Visit frequency and recency are behavioral signals. Even when Fitbit data is used with consent, only aggregated activity minutes are processed. No biometric categorization occurs. |
| 4(e) – Biometric Safety Evaluation | Assessing biometric safety or health risk | No | System does not assess health risk or safety. Does not predict medical outcomes or prescribe interventions. |
| 3(a) – Law Enforcement | Predicting criminal behavior | No | Not applicable. |
| 3(c) – Migration/Border Control | Assessing illegal entry risk | No | Not applicable. |
| 3(d) – Administration of Justice | Predicting recidivism | No | Not applicable. |
| 3(e) – Access to Goods/Services | Determining creditworthiness or insurance eligibility | No | System does not make final decisions on service access. Classification is advisory. Coach decision is final. |
| 2(a) – Education | Evaluating students or educational track placement | No | Not applicable. |

**Verdict: ✓ NO ANNEX III CATEGORY APPLIES — System is NOT high-risk.**

---

### Step 3: Transparency Trigger Check (Article 50)

| Aspect | Detail | Triggers Transparency? |
|---|---|---|
| System Output | Classifies gym members as low, medium, or high dropout risk | Yes |
| Individual Effect | Classification may lead to coach contact and retention outreach | Yes, but... |
| Degree of Autonomy | All decisions remain with human coaches. System produces recommendations only. | Effect is advisory, not determinative. |
| Member Awareness | Members informed in privacy notice. Can opt out at any time. | Yes |
| **Transparency Obligation Triggered?** | **Yes, Article 50 applies.** | **Yes** |

---

### Step 4: Final Classification

```
Classification: LIMITED RISK
Primary Obligation: Article 50 (Transparency)

Reasoning:
  ✓ Does not meet unacceptable risk criteria (Article 5)
  ✓ Does not meet high-risk criteria (Annex III)
  ✓ Generates outputs affecting individuals, but decisions remain with humans
  ✓ Transparency and human-in-the-loop design satisfies Article 50
```

---

## 2.3 Article 50 Mandatory Requirements

| Requirement | How This System Addresses It |
|---|---|
| Transparency to humans using the system | ✓ Every weekly email report includes behavioral triggers per member (e.g., "Days inactive: 21, Avg interval: 7 days"). ✓ n8n execution log accessible to consultant: full prompt and output recorded per run. ✓ Report includes confidence intervals and data quality notes. |
| Information to data subjects (members) | ✓ Privacy notice states AI tool is used to analyze attendance and flag engagement drops. ✓ Wearable consent form explicitly lists what data is used and why. ✓ Members informed of right to object to AI-driven analysis. |
| Human oversight: decisions NOT automated | ✓ System generates recommendations; coaches make final contact decisions. ✓ No automated member notifications. ✓ No autonomous membership changes, refunds, or access changes. |
| Accuracy and robustness | ✓ Logistic regression model trained on 4,000 labelled gym members (gym_churn_us.csv): 92.5% accuracy, 0.977 ROC-AUC on held-out test set. ✓ Output quality reviewed manually via n8n execution log after each run. ✓ Members with < 4 weeks of data excluded. ✓ Confidence scores accompany every classification. |
| Audit trail and accountability | ✓ n8n execution log records every prompt, AI output, and timestamp. ✓ DPA assigns data controller role to studio owner, processor role to consultant. ✓ GDPR processing register maintained per Article 30. |
| Cybersecurity | ✓ Member IDs pseudonymized before pipeline entry. ✓ API keys stored in .env files, never version-controlled. ✓ Fitbit OAuth tokens transmitted directly from Fitbit to local script.  |

---

## 2.4 Conformity Assessment Summary (Article 48)

| Section | Detail |
|---|---|
| System Name | AI Early Warning System – Member Churn Prediction |
| Provider | Dina Bosma, AI Consultant |
| Deployer | Boutique fitness studio (owner-operator) |
| System Version | 1.0 (Pilot) |
| Deployment Date | March 2026 |
| User (Data Controller) | Studio Owner / Manager |
| Scope | Boutique fitness studios, 50–200 direct members, EU-based (Berlin initial pilot) |

### What This System Does

**Objective:** Identify gym members at high risk of membership cancellation within a 4–6 week window, enabling coaching teams to intervene proactively.

**Inputs:**
- Member visit history (attendance dates, session frequency)
- Optional wearable data (Fitbit active minutes, if member consents)

**Processing:**
- Logistic regression model calculates churn risk score per member
- GPT-4o-mini (via n8n) generates coaching briefings from member risk data
- n8n workflow delivers weekly email report to coaching team and studio owner

**Outputs:**
- Weekly email report: full member risk ranking, estimated revenue at risk, behavioral signals, coaching context per flagged member
- Monthly retention briefing: studio-level churn trends, segmented risk breakdown
- n8n execution logs: full prompt and GPT-4o-mini output recorded per weekly run

### Why This System Is Limited Risk

| Factor | Assessment |
|---|---|
| No Autonomous Decisions | Coaches review every alert and decide independently. System is advisory only. |
| Human Oversight Built-In | Contact decision, message content, and follow-up timing are all human-controlled. |
| Transparent Recommendations | Every alert shows specific behavioral signals. Coaches understand the reasoning. |
| Member Consent & Rights | Wearable data processed only with explicit opt-in. Members can opt out entirely. |
| Data Minimisation | Only visit history and optional aggregated wearable metrics used. No raw biometric data stored. |
| No Annex III Criterion Met | System does not evaluate employment, determine essential service eligibility, or perform biometric surveillance. |

### Applicable Obligations

| Article | Obligation | How Addressed |
|---|---|---|
| Article 50 | System outputs must be interpretable to humans | ✓ Behavioral signals shown in every alert. n8n execution log reviewed for quality. Coach training provided. |
| Article 50 | Information must be provided to data subjects | ✓ Privacy notice + wearable consent form explain AI use in plain language. Right to object honored. |
| Article 50 | Humans must remain in control | ✓ No autonomous decisions. Coaches decide who to contact and how. |
| Article 5 | System must not be unacceptable risk | ✓ No subliminal manipulation, exploitation, biometric surveillance, or social scoring. |
| General | Documented classification reasoning | ✓ This conformity assessment provides step-by-step reasoning (Section 2.2). |

### Identified Gaps & Resolution Plan

| Gap | Status | Resolution |
|---|---|---|
| Token-level energy measurement | Not yet implemented | Read token count from OpenAI API response in n8n after each run. Log to a simple CSV. Target: < 8,000 tokens/briefing. Phase 2 option: add LangSmith for structured multi-studio token tracking. |
| Wearable consent gate production testing | Designed, not yet tested with real Fitbit data | Test with 3–5 real members (Phase 2). Confirm OAuth flow works, tokens stored securely. |
| Model retraining on real studio data | Planned after 6–8 weeks pilot | Collect studio check-in data. Retrain logistic regression. Validate accuracy ≥ 80%. |
| Multi-studio user management | Not applicable at Phase 1 | Phase 3 requires role-based access control. Design: `studio_id`-based isolation, separate email recipient lists per studio. |

---

## 2.5 Technical Documentation Outline

*Full documentation to be completed before scaling beyond the pilot phase.*

**1. System Description and Intended Purpose**
- Objective: Identify churn-at-risk members 4–6 weeks before cancellation
- Intended users: Studio coaches (decision-makers), studio owner (oversight)
- Out-of-scope: Automated member contact, membership changes, pricing decisions

**2. Scope, Use Context, and Boundaries**
- Applicable: Direct-membership boutique fitness studios (50–200 members), EU-based
- Not applicable: Studios with > 30% Urban Sports Club / Gympass members
- Not applicable: Recruitment, employment decisions, law enforcement

**3. Training Data Documentation**

Two datasets are used for two distinct purposes — they are not the same data:

| Dataset | Purpose | Size | Churn labels |
|---|---|---|---|
| `gym_churn_us.csv` | Model training | 4,000 labelled gym members | Real binary labels (churned / retained) |
| Endomondo (167,783 sessions) → `demo_members.csv` | Demo member population | 150 members (boutique studio scale) | None — used for scoring only |

The model is trained exclusively on `gym_churn_us.csv`. The Endomondo-derived dataset is used to demonstrate the system with realistic member profiles when no real studio data is available. It is replaced with a real studio CSV export at go-live.

- Synthetic recency applied to demo data (dates shifted to current timeline so distribution looks live)
- Plan: Retrain on real studio data after 6–8 weeks pilot

**4. Model Architecture**
- Algorithm: Logistic regression (binary classification: churn vs. retain)
- Input features: Age, Lifetime (tenure), Contract_period, Month_to_end_contract, Avg_class_frequency_total, Avg_class_frequency_current_month, Avg_additional_charges_total, Near_Location, Partner, Promo_friends, Phone, Group_visits, gender
- Output: churn_probability (0–1), mapped to risk tier (HIGH ≥ 0.65 / MEDIUM 0.35–0.64 / LOW < 0.35)

**5. Validation Results**
- Accuracy: **92.5%** on held-out test set (20% of gym_churn_us.csv, stratified, random_state=42)
- Precision: 88.0% | Recall: 83.0% | F1: 85.4% | ROC-AUC: **0.977**
- Strongest retention signals: current-month class frequency, membership tenure
- Retraining on real studio data required after 6–8 weeks — minimum threshold ≥ 80% accuracy

**6. LLM Component Specification**
- Model: GPT-4o-mini
- Temperature: 0 (deterministic)
- Quality evaluation: manual review of n8n execution log output after each run
- Minimum threshold: 0.70 for production delivery

**7. Human Oversight Design**
- Decision boundary: Coaches receive alerts; coaches decide on outreach
- Fallback: if coaching note appears off-topic or generic, coach flags it and consultant reviews the prompt
- Confidence interval: Every risk classification includes confidence score (0–1)
- Coach training: Mandatory onboarding; coaches treat AI output as starting point, not final truth

**8. Logging & Audit Trail Architecture**
- n8n execution log: records every prompt, AI output, token count, and timestamp per run
- n8n: Logs workflow execution (trigger time, API calls, success/failure)
- Wearable consent gate: Logs every consent_check with timestamp
- Retention: Logs retained 12 months; older logs archived

**9. Known Limitations & Failure Modes**
- Model trained on 2015 data; may not reflect current fitness trends
- Performance not validated on members with < 4 weeks history
- LLM can hallucinate if context block includes ambiguous aggregates (mitigated by temperature=0)
- API rate limits can delay alerts by up to 48 hours

**10. Update and Retraining Procedure**
- Retraining trigger: After 6–8 weeks real studio data OR quarterly accuracy review shows > 5% drift
- Validation: New model tested on hold-out studio data; accuracy must ≥ 80%
- If validation fails: Continue previous model; flag studio for manual review

**11. GDPR Alignment Summary**
- Legal basis: Legitimate interest (visit history), explicit consent (wearable data)
- Data minimization: Only fields needed for churn prediction extracted
- Retention: Visit history deleted 30 days after membership end; wearable data deleted on consent withdrawal
- Data subject rights: Access, rectification, erasure, portability supported

**12. Green Software Assessment & Energy Proxy Measurement**
- Legacy baseline (Project 5 architecture): 7,800 tokens/briefing (12 sequential calls), 260 n8n executions/year per studio
- Current system: ~1,000 tokens/briefing (1 batched call), 52 n8n executions/year (weekly trigger) — 87% token reduction already achieved
- Monitoring: token count logged from OpenAI API response in n8n after each run. Alert if tokens/briefing exceed 8,000.
- Phase 2 option: LangSmith can be added for structured token tracking across multiple studios
- Carbon intensity: EU West ~0.2 kgCO2/kWh. Batching + EU routing = ~60% carbon reduction per briefing
