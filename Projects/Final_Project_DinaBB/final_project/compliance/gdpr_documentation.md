# GDPR Compliance Documentation
### Spottr

---

## 3.1 Personal Data Flow Map

### Data Inventory

| Data Type | Source | Identifier | Where It Goes | Processed By | Stored Where | Deletion Timeline |
|---|---|---|---|---|---|---|
| Member visit history (dates, times, session count) | Gym booking system CSV export | Member ID (e.g., M_001) replaces name | Data pipeline → Logistic regression → GPT-4o-mini briefing (via n8n) | Dina (data processor) | Local filesystem (.csv) | 30 days after membership end |
| Wearable activity data (active minutes, session metadata) | Fitbit API (OAuth 2.0, consent-gated) | Member ID (pseudonymized) | Consent gate check (n8n) → If consent true: local script → model feature input | Dina (data processor) | Local filesystem only; never sent to OpenAI or third parties | 48 hours after consent withdrawal |
| n8n workflow execution logs | n8n Cloud automation | None (operational logs) | n8n infrastructure | n8n (subprocessor) | n8n Cloud EU region | 3 months (default retention) |
| Weekly email report (member risk list, revenue at risk, behavioral signals, coaching context) | n8n → SMTP | Member IDs only (not names) | Coach and studio owner inboxes | n8n (subprocessor, EU region) | Email provider per studio's chosen mail service | Per studio's email retention policy |
| Fitbit OAuth credentials (tokens, refresh tokens) | Fitbit authentication flow | None (credentials, not data) | Local .env file (encrypted at rest) | Dina (data processor) | Local filesystem only | 30 days after member withdraws consent OR 90-day rotation cycle |

### Key Design Principles

**Pseudonymization:** Member names never entered into data pipeline. Only generated IDs (M_001, M_002) used in model training and LLM context.

**Minimization:** Only fields needed for churn prediction extracted. Payment details, emergency contacts, training goals never ingested.

**Consent Gating:** Wearable data access blocked at n8n workflow level until member has explicitly given consent.

**EU Data Residency:** n8n is configured to EU region. OpenAI processes only aggregated non-personal prompt data (US-hosted, SCCs apply). Email delivery via n8n SMTP uses EU-hosted infrastructure.

---

## 3.2 Processing Register (Article 30 GDPR)

*Studio Name: [To be completed at deployment]*
*Studio Location: Berlin, Germany (pilot)*
*Data Controller: Studio Owner / Manager*
*Data Processor: Dina Bosma, AI Consultant*
*DPA Reference: See data_processing_agreement_template.md*

---

### Activity 1: Churn Risk Classification

| Element | Detail |
|---|---|
| Purpose | Identify gym members at high risk of cancellation within 4–6 weeks; enable coaches to intervene proactively |
| Legal Basis | **Legitimate Interests (Article 6(1)(f) GDPR):** Studio has legitimate business interest in retaining members and preventing revenue loss. Processing is proportionate and not overridden by data subject interests. Balancing test: Risk is low (recommendations only, no autonomous decisions). Data minimization applied. |
| Data Categories | Member visit history (dates, session frequency, recency). Pseudonymized member IDs. No names in pipeline. |
| Data Subjects | Current gym members and recently lapsed members (past 30 days) |
| Recipients | Coaches and studio owner (via weekly email report). |
| Retention Period | Visit history retained for duration of active membership + 30 days after membership end. Then deleted. |
| Sub-Processors | OpenAI (GPT-4o-mini LLM inference, US, SCCs apply). n8n (workflow automation, EU region). |
| Data Subject Rights | Access (✓ CSV export on request), Erasure (✓ 30-day deletion timeline), Rectification (✓ corrected in source system, pipeline re-run within 48 hours), Portability (✓ CSV export format), Objection (✓ member can exclude themselves from AI analysis at any time). |

---

### Activity 2: Wearable Activity Data Enhancement (Optional Coaching Add-On)

| Element | Detail |
|---|---|
| Purpose | Optional enhancement of churn risk classification using wearable workout data. Members can choose to share Fitbit data for more accurate activity signals. |
| Legal Basis | **Explicit Consent (Article 9(2)(a) GDPR).** Wearable data includes heart rate information, which qualifies as health data under Article 9 (special category). Legitimate interest is insufficient for Article 9 data. Only valid basis is prior, explicit opt-in consent from data subject. Consent is separate from visit history consent and can be withdrawn independently. |
| Data Categories | Wearable activity: active minutes, session start/end times, session type, calories burned, heart rate (average and peak during session only). **Explicitly excluded:** Resting heart rate, sleep data, GPS/location, health condition data, medical history. |
| Data Subjects | Members who have explicitly given wearable consent via coaching intake form. Consent is granular and documented. |
| Recipients | None outside the studio. Data stays local. Fitbit API called from local script only; data never forwarded to OpenAI or other services. |
| Retention Period | Wearable data retained only while member is actively enrolled AND has given consent. Deleted within 48 hours of consent withdrawal. After programme end, deleted within 30 days. |
| Sub-Processors | Fitbit (data source, OAuth flow, US-based). No other subprocessors access wearable data. |
| Data Subject Rights | Access (✓ local script exports wearable history on request), Erasure (✓ 48-hour deletion timeline per Article 17(1)), Withdraw Consent (✓ member can opt out at any time via studio staff), Objection (✓ member can request no wearable processing). |

---

### Activity 3: AI Output Logging (n8n Execution Log)

| Element | Detail |
|---|---|
| Purpose | Audit trail for every GPT-4o-mini call — records the full prompt sent and the coaching briefing returned. Used to review output quality and investigate any complaints. |
| Legal Basis | **Legitimate Interests (Article 6(1)(f) GDPR):** Proportionate operational logging. Logs contain aggregated prompt text only — no individual member names. |
| Data Categories | Prompt text (member IDs + behavioural signals), LLM output (coaching briefing text), token count, timestamp, execution status. |
| Data Subjects | Not directly applicable. Logs are operational. Member IDs appear in prompt context but are pseudonymous. |
| Recipients | Dina (consultant, for system maintenance and quality review). |
| Retention Period | n8n execution logs retained for 3 months (n8n Cloud default). |
| Sub-Processors | n8n (EU region). OpenAI (US-based, SCCs apply). |
| Data Subject Rights | Not directly applicable. Available for review on request in anonymised form. |

> **Phase 2 note:** LangSmith (LangChain Inc.) is an optional observability platform that can be added in Phase 2 to provide structured quality scoring across multiple studios. It is not active in Phase 1. If added, it would be listed as a subprocessor (EU endpoint available) and this activity register would be updated accordingly.

---

### Activity 4: Member Survey Response Processing

| Element | Detail |
|---|---|
| Purpose | Collect optional member feedback when engagement drops are detected. Responses are used to give coaches context before outreach — not for automated decisions. |
| Legal Basis | **Legitimate Interests (Article 6(1)(f) GDPR):** Studio has legitimate interest in understanding why members are disengaging. Survey participation is optional and members are not penalised for not responding. Balancing test: low risk (data used only for coaching context, not automated action). |
| Trigger | Event-based: survey sent when class attendance drops >30% for 2+ consecutive sessions, or studio-wide check-in volume drops >20% vs prior 7-day average. Maximum once per member per 5-week rolling window. |
| Data Categories | Member ID (pseudonymous), survey rating (1–5 numeric), optional free-text response, whether member has requested a coach check-in (boolean). No names collected. Free-text field is open input — members may choose to share personal context; this is voluntary and not solicited. |
| Data Subjects | Active members who meet the engagement-drop trigger criteria and have not received a survey in the past 5 weeks. |
| Recipients | Coaches and studio owner (via weekly email report — survey responses surfaced alongside member risk score). No third-party recipients. |
| Retention Period | Survey responses retained for 90 days. Included in weekly report cycle during that period. Deleted on rolling 90-day basis. |
| Sub-Processors | Tally.so (survey form provider, EU-based). n8n (webhook receiver and log writer, EU region). |
| Data Subject Rights | Access (✓ response data available on request), Erasure (✓ deleted from survey_responses.csv and weekly report within 48 hours of request), Objection (✓ member can opt out of future surveys at any time by contacting studio staff — flag set in survey_sent_log.csv). |

---

## 3.3 Data Protection Impact Assessment (DPIA)
### Wearable Activity Data Processing via Fitbit API

*DPIA Date: March 2026*
*Assessor: Dina Bosma (Data Processor) + Studio Owner (Data Controller)*
*Review Date: Quarterly*

---

### 1. Description of Processing

**What is being processed?**

Members with active Fitbit devices can grant consent to share workout session data:
- Session start/end time and duration
- Workout type (strength, cardio, cycling, running, etc.)
- Active minutes during session
- Calories burned
- Heart rate during session (average and peak)

**Explicitly NOT processed:**
- Resting heart rate (passive monitoring)
- Sleep data
- Daily step count (passive tracking)
- GPS/location data
- Medical diagnoses or health conditions

**How is data accessed?**
1. Member authenticates with Fitbit account (OAuth 2.0 flow)
2. Fitbit API called from local Python script
3. Data fetched directly from Fitbit servers to local script
4. Data never sent to OpenAI or cloud databases
5. Data processed locally to extract activity signal

**What is the data used for?**
Supplementary feature in churn risk model (~10% of feature importance; visit history is primary). Proxy for workout activity between scheduled classes.

---

### 2. Necessity & Proportionality Assessment

**Is wearable data necessary for the core service?**

| Aspect | Assessment |
|---|---|
| Core model accuracy without wearable | 92.5% accuracy, 0.977 ROC-AUC (logistic regression trained on 4,000 labelled gym members) |
| Accuracy improvement with wearable | Estimated 1–3% (not yet validated in pilot) |
| Necessity verdict | **NO – Wearable data is NOT necessary.** System functions effectively with visit history alone. |
| Purpose | Enhancement only – provides additional context but is optional. |

**Is processing proportionate to the benefit?**

| Criterion | Assessment |
|---|---|
| Data minimization | ✓ YES. Only aggregated daily activity signals processed. No raw heart rate time series. |
| Scope limitation | ✓ YES. Wearable feature accounts for ~10% of model input. |
| Purpose limitation | ✓ YES. Data used solely for churn risk scoring. Not used for health coaching or other purposes. |
| Access control | ✓ YES. Data stays local; not transmitted to third parties. |
| Consent requirement | ✓ YES. Explicit opt-in required. Consent can be withdrawn independently. |
| Member benefit | ✓ YES. More accurate churn risk flagging → more targeted coach outreach. |

**Proportionality verdict: YES – Processing is proportionate.**

---

### 3. Risk Assessment

**Risk 1: Unauthorized Access to Fitbit OAuth Credentials**

- Likelihood: 2 | Impact: 4 | Level: **8 (Medium)**
- Mitigations: OAuth tokens in .env file, never version-controlled. Local filesystem encrypted at rest. 90-day token rotation. Immediate revocation procedure via Fitbit dashboard. Quarterly version control audit. n8n access log monitors for anomalies.
- Residual Risk: **Low**

**Risk 2: Inappropriate Contact During Illness/Injury**

- Likelihood: 2 | Impact: 3 | Level: **6 (Medium)**
- Mitigations: Human-in-the-loop — coach always reviews alert before contacting member. Coach training includes instruction to ask how member is doing, not pressure. Alert includes wearable activity trend for context. Member right to object honored immediately. Monthly retrospective collects coach feedback.
- Residual Risk: **Low**

**Risk 3: Fitbit Server Compromise (Third-Party)**

- Likelihood: 1 | Impact: 5 | Level: **5 (Low)**
- Mitigations: Out of scope of studio/consultant control. Only aggregated signals stored locally (raw data not cached). Notification procedure: if Fitbit breach reported, all wearable-consented members notified within 24 hours. DPA includes sub-processor breach notification requirement.
- Residual Risk: **Very Low (accepted as inherent risk of third-party integration)**

**Risk 4: Misuse of Wearable Data for Discriminatory Pricing**

- Likelihood: 2 | Impact: 4 | Level: **8 (Medium)**
- Mitigations: DPA explicitly prohibits using wearable data for pricing decisions, membership tier changes, or facility access restrictions. Wearable data stored separately from billing/membership database. Quarterly audit of access logs. Coach/owner training on ethical use. Member complaint mechanism to Berlin DPA.
- Residual Risk: **Low**

---

### 4. DPIA Conclusions

| Conclusion | Detail |
|---|---|
| Is processing necessary and proportionate? | Yes — wearable integration is an optional enhancement, not a core requirement. Scope, consent, and data minimization controls are in place. |
| Are risks adequately mitigated? | Yes — all identified risks are Medium or below after mitigation. No unmitigated high-level risks. |
| Can processing proceed? | **Yes, subject to:** (1) Explicit consent obtained before first data access; (2) DPA signed between studio and consultant; (3) Token storage and rotation procedures implemented; (4) DPIA reviewed quarterly and updated if processing scope changes. |
| Supervisory Authority Consultation Required? | No — residual risks are below the threshold requiring prior consultation under Article 36. |

---

## 3.4 Data Subject Rights — Implementation

| Right | Legal Basis | How Supported | Response Timeline |
|---|---|---|---|
| Right of Access (Article 15) | GDPR Art. 15 | Member requests access → studio exports member's CSV record from local filesystem → provided in readable format | 30 days |
| Right to Erasure (Article 17) | GDPR Art. 17 | Member requests deletion → studio instructs consultant → deleted from CSV, n8n execution logs, cached briefings, Fitbit OAuth tokens (if applicable) → written confirmation provided | 48 hours (execution), 72 hours (confirmation) |
| Right to Rectification (Article 16) | GDPR Art. 16 | Incorrect visit data corrected in source system → pipeline re-run within 48 hours to reflect correction | 48 hours |
| Right to Portability (Article 20) | GDPR Art. 20 — applies where processing is based on consent or contract | Member's data exported as CSV on request | 30 days |
| Right to Object (Article 21) | GDPR Art. 21 | Member can request exclusion from AI analysis at any time without membership penalty → flag set in pipeline, member excluded from next run | 24 hours |
| Right to Withdraw Consent (wearable only) | GDPR Art. 7(3) | Member informs studio staff → wearable consent flag set to false → wearable data deleted within 48 hours → confirmed in writing | 48 hours |

---

## 3.5 Third-Party Data Transfers

| Subprocessor | Location | Transfer Mechanism | Data Transferred | Safeguard |
|---|---|---|---|---|
| OpenAI | USA | Standard Contractual Clauses (SCCs) | Aggregated statistical summaries (no individual names or member IDs) | Temperature=0, scope-limited prompts. No PII transmitted. |
| n8n | EU region | GDPR-compliant EU hosting | Workflow execution logs (operational metadata only) | EU data residency. DPA with n8n in place. |
| Studio email provider (SMTP) | EU (configurable) | GDPR-compliant EU hosting (default) | Weekly email report containing member IDs and risk signals | Studio responsible for their email provider's DPA. n8n delivers via SMTP only — no third-party email marketing platform. |
| Fitbit (Alphabet) | USA | Standard Contractual Clauses (SCCs) | OAuth authentication flow only. Raw Fitbit data fetched to local script — not forwarded. | Data never leaves local environment after fetch. |

**Note on OpenAI transfer:** The LLM context block sent to OpenAI contains only aggregated cohort statistics (e.g., "22% of members show 3+ week inactivity gaps"). No individual member names, IDs, or personal details are included. The transfer therefore does not constitute a personal data transfer as defined under GDPR Article 44.


---

## 3.6 Privacy Notice Template

The studio's existing privacy notice must include the following paragraph. The studio writes this in their own voice — the text below is a template:

---

*"We use an automated data analysis tool to help our coaches support your membership. This tool analyses your visit frequency and attendance patterns to identify members who may benefit from additional coaching support. The analysis is performed by a machine learning model and reviewed by your coach before any contact is made — no automated decisions are taken without human review. The legal basis for this processing is our legitimate interest in supporting your fitness goals and retaining your membership (Article 6(1)(f) GDPR). You have the right to object to this processing at any time by contacting us at [studio email]. If you object, you will be excluded from the analysis and this will have no effect on your membership."*

---

**If wearable data is collected (optional, separate consent required):**

*"With your explicit consent, we may also use data from your fitness wearable device (such as Fitbit) to provide more personalised coaching support. This data is classified as health data under Article 9 GDPR and is only processed with your explicit written consent, which you may withdraw at any time. Withdrawal of consent will result in deletion of your wearable data within 48 hours and will have no effect on your membership or general coaching programme."*

---

*Both paragraphs are provided as templates. The studio is responsible for incorporating them into their existing privacy notice before the Spottr system goes live.*
