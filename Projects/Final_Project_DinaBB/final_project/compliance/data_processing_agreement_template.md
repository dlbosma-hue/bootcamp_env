# Data Processing Agreement (DPA)
### Spottr — DPA Template

---

**Between:**

**[STUDIO NAME]**, a business registered at [address], operating as [legal form], hereinafter referred to as the **"Controller"**

**and**

**Dina Bosma**, operating as an independent AI systems consultant, hereinafter referred to as the **"Processor"**

Together referred to as the **"Parties"**.

---

## 1. Subject Matter and Duration

**1.1** This Agreement governs the processing of personal data by the Processor on behalf of the Controller in connection with the delivery and operation of an AI-driven member retention and churn prediction system (the "System").

**1.2** The System includes:
- Automated ingestion and analysis of member visit and attendance data
- Machine learning models producing individual-level churn risk scores
- AI-generated retention briefings delivered to studio staff
- Optional integration with member wearable device data (Fitbit), subject to separate explicit consent

**1.3** This Agreement enters into force on the date of last signature below and remains in effect for the duration of the service engagement. It survives termination of the main service contract for the purposes of deletion and return of data obligations under clause 9.

---

## 2. Nature and Purpose of Processing

| Element | Detail |
|---|---|
| **Purpose** | Member retention analysis, churn risk prediction, generation of staff briefings |
| **Nature** | Automated analysis, scoring, report generation |
| **Categories of personal data** | Member names, membership IDs (pseudonymised in pipeline), visit frequency and recency, class attendance history, membership tier; where explicit consent is obtained: wearable workout session data (session type, duration, calories, in-session heart rate average and peak) — daily passive tracking data (steps, resting HR, sleep) is explicitly excluded |
| **Categories of data subjects** | Current and recently lapsed members of the Controller's studio |
| **Retention period** | Active while membership is live; deleted within 30 days of written erasure instruction or end of service |

---

## 3. Instructions and Compliance

**3.1** The Processor shall process personal data only on documented instructions from the Controller. These instructions are set out in this Agreement and any written instructions issued subsequently by the Controller.

**3.2** If the Processor believes any instruction infringes GDPR or applicable EU/national data protection law, the Processor shall immediately inform the Controller in writing. The Processor shall not be required to follow an instruction it reasonably believes to be unlawful.

**3.3** The Processor shall not use the Controller's member data for any purpose other than delivering the System as described in this Agreement.

---

## 4. Confidentiality

**4.1** The Processor shall ensure that all persons authorised to process the personal data under this Agreement are bound by appropriate confidentiality obligations.

**4.2** Access to personal data is limited to the Processor and, where applicable, designated subprocessors listed in Annex A. No other person shall have access without prior written consent from the Controller.

---

## 5. Technical and Organisational Security Measures

The Processor has implemented the following technical and organisational measures:

**Pseudonymisation:** Member names are replaced with generated IDs before data enters the AI pipeline. Mapping between names and IDs is held separately and access-controlled.

**Data minimisation:** Only the fields required for churn prediction are extracted from source data. Fields not required (e.g., payment details, emergency contacts) are never ingested.

**Access controls:** Pipeline infrastructure access is protected by API keys and environment variable management. Keys are never committed to version control.

**EU data residency:** n8n is configured to EU region. OpenAI processes only aggregated non-personal prompt data (US-hosted, SCCs apply).

**Consent gate:** Wearable data integration is technically disabled by default. It is activated per member only after the Processor receives written confirmation from the Controller that the member has provided explicit consent on the form set out in Annex B.

**Audit logging:** The Processor maintains a log of all data deletion actions (see clause 8).

---

## 6. Subprocessors

**6.1** The Controller grants the Processor general written authorisation to engage the subprocessors listed in Annex A for the purposes of delivering the System.

**6.2** The Processor shall notify the Controller in writing of any intended addition or replacement of a subprocessor at least **14 days** in advance. The Controller may object within that period on reasonable data protection grounds.

**6.3** The Processor shall impose data protection obligations on each subprocessor equivalent to those in this Agreement.

**Annex A — Current Subprocessors:**

| Subprocessor | Purpose | Location |
|---|---|---|
| OpenAI (via API) | LLM inference — GPT-4o-mini generates coaching briefings for flagged members | USA (SCCs apply) |
| n8n Cloud | Workflow automation, scheduling, and email delivery | EU region (binding requirement) |
| Fitbit (via OAuth API) | Wearable workout session data source — OAuth token exchange only; data returned to local pipeline | USA (SCCs apply) |
| Studio email provider (SMTP) | Weekly retention email delivery to coaches and studio owner | As configured per studio (EU provider preferred) |

*Where subprocessors are located outside the EEA, the Processor ensures appropriate transfer mechanisms (Standard Contractual Clauses or equivalent) are in place.*

---

## 7. Data Subject Rights

**7.1** Given the nature of the System, data subject rights requests (access, rectification, erasure, restriction, portability, objection) will be received by the Controller from their members.

**7.2** The Processor shall assist the Controller in fulfilling these requests insofar as the data is held within the Processor's pipeline, within the timescales set out below.

**7.3** Upon receipt of a written erasure instruction from the Controller (ongoing data subject request during the engagement), the Processor shall:
- Acknowledge receipt within **24 hours**
- Complete deletion from all pipeline components within **48 hours**
- Provide written deletion confirmation to the Controller within **72 hours**

This timeline applies to individual data subject erasure requests received during the active engagement. It is designed to allow the Controller to meet the statutory 30-day deadline with substantial headroom.

Note: Final data return or deletion on contract termination is governed by Clause 8.2 (10 business days). These are two distinct processes and timelines.

---

## 8. Deletion and Return of Data

**8.1** On termination of this Agreement, or at the Controller's written request, the Processor shall at the Controller's election either:
- Return all personal data to the Controller in a portable format, or
- Securely delete all personal data from all systems

**8.2** The Processor shall provide written certification that deletion is complete within **10 business days** of the termination date or deletion instruction.

**8.3** For ongoing erasure requests during the service, the Processor maintains a **Deletion Log** recording:
- Date erasure instruction was received
- Member pseudonym ID(s) affected
- Systems from which data was deleted (CSV files, n8n workflow execution history, cached briefing outputs, Fitbit OAuth tokens where applicable)
- Date deletion was completed and confirmed

**8.4** Aggregated, fully anonymised statistical outputs (e.g., studio-level churn rate summaries containing no individual identifiers) are not personal data and are not subject to deletion obligations.

---

## 9. Breach Notification

**9.1** The Processor shall notify the Controller without undue delay — and in any event within **24 hours** — upon becoming aware of a personal data breach affecting the Controller's member data.

**9.2** Notification shall include, to the extent available: the nature of the breach, categories and approximate number of data subjects affected, likely consequences, and measures taken or proposed to address it.

**9.3** The Controller is responsible for notifying the relevant supervisory authority (in Germany: the Berliner Beauftragte für Datenschutz und Informationsfreiheit) within 72 hours of becoming aware, as required by GDPR Article 33.

---

## 10. Audit and Demonstration of Compliance

**10.1** The Processor shall make available to the Controller all information reasonably necessary to demonstrate compliance with this Agreement.

**10.2** The Processor shall allow for and contribute to audits and inspections conducted by the Controller or a mandated auditor, with reasonable notice (minimum 14 days).

**10.3** The Processor shall maintain documentation of technical and organisational measures and deletion logs, and shall provide these to the Controller on request.

---

## 11. Governing Law and Jurisdiction

This Agreement is governed by the laws of the Federal Republic of Germany. Any disputes shall be subject to the exclusive jurisdiction of the courts of Berlin.

---

## 12. Signatures

**For the Controller:**

Name: ___________________________

Title: ___________________________

Date: ___________________________

Signature: ______________________

---

**For the Processor:**

Name: Dina Bosma

Date: ___________________________

Signature: ______________________

---

*This template is provided for operational use in the Spottr engagement. It is not a substitute for legal advice. Both parties should have the agreement reviewed by a qualified lawyer before execution if the data volumes or commercial stakes are significant.*
