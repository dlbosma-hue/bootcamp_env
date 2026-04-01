# Use Case Definition
### Spottr

---

## 1. Business Problem

Boutique fitness studios operate on tight margins with structurally high member turnover. The fitness industry reports annual churn rates of 50–60% for boutique studios (IHRSA European Market Report). The critical insight is that churn is almost never sudden — members disengage gradually over 4–6 weeks before cancelling. Visit frequency drops. Coaching sessions get skipped. Activity goes quiet. Then they cancel.

Studio owners and coaches rarely have the time or tooling to spot these patterns early across their full member base. They rely on intuition, personal relationships, and memory — which works at 30 members and breaks at 150. By the time someone notices a member has gone quiet, the decision to leave has often already been made.

**The result is preventable revenue loss at scale.** A member paying €120/month who churns after 5 months represents €1,440 in lost lifetime value. Replacing them costs approximately 5× more than retaining them would have (acquisition cost: marketing, promotions, onboarding). At a studio of 150 members with 55% annual churn, this is roughly €118,800 in annual revenue lost to churn that could partially be prevented with earlier intervention.

The problem is not that coaches don't care — they do. The problem is that they have no systematic way to see who is slipping before it is too late.

---

## 2. Company Profile

**Industry:** Boutique fitness — a distinct segment of the fitness industry characterised by specialised formats (yoga, Pilates, CrossFit, HIIT, personal training), small group or individual sessions, premium pricing, and high member-coach relationship intensity.

**Target company size:**
- 80–250 direct members (members with direct billing relationships — not Urban Sports Club / Gympass pass holders, who have different retention economics)
- 1–3 locations
- 2–8 coaches or instructors on staff
- Annual revenue: €150,000–€600,000
- No in-house data or technology team

**Current state — what these studios typically have today:**
- A gym management system (e.g. Mindbody, Gymdesk, Magicline) that stores attendance and membership data but provides no predictive analytics
- No formal churn monitoring process — retention is managed reactively
- Coaches who know their regulars well but have no visibility on members they see less frequently
- No structured outreach process for at-risk members — contact happens when something breaks, not before
- GDPR obligations they are aware of but not confident they are fully meeting

**What they do not have:**
- A data analyst or business intelligence function
- Budget for enterprise retention software (€500–2,000/month SaaS tools are out of reach)
- Time to build or manage complex tooling

---

## 3. The AI-Powered Solution

### Core system — churn prediction for all members

A scheduled AI pipeline ingests visit data, pseudonymises member identities, calculates a churn risk score for every member using a logistic regression model, and delivers a natural language briefing to all coaches and the studio owner each week via email.

The AI's role is to **summarise, not instruct.** The briefing tells a coach what the data shows in plain language. The coach decides whether and how to reach out. This keeps the human relationship at the centre.

**Why a trained model rather than simple rules:**
An earlier version of this system used fixed thresholds: flag a member if they haven't visited in 21 days and average fewer than 1 session per week. This approach has a fundamental limitation — it treats all members with the same inactivity pattern identically. A member who joined last month on a rolling contract going quiet is a very different situation from a long-term member of 3 years who missed 3 weeks due to a holiday.

The logistic regression model was trained on 4,000 gym members with real churn outcomes (`gym_churn_us.csv` — binary churn labels, held-out test set). This is separate from the 150-member demo population used in the dashboard and weekly email, which is derived from Endomondo workout data and used purely to demonstrate the system at boutique gym scale. It learned to weight combinations of signals — visit recency, session frequency, tenure, contract type — in proportion to how predictive they actually were in real cancellation data. The result is a churn *probability* per member (e.g. 0.81) rather than a binary flag, which means coaches can see not just who is at risk but how urgently each person needs attention. The model also has a documented retraining path: after 6–8 weeks of real studio data, it is retrained on that studio's actual churn outcomes and improves over time.

**Data inputs:**
- Member visit frequency and recency
- Class attendance history
- Membership tier and tenure
- Member survey responses (event-triggered — see below)

**Output:**

| Channel | Frequency | Content | Recipients |
|---|---|---|---|
| Weekly email report | Monday 07:00 | Full member risk overview, survey responses from the week, natural language coaching context per flagged member | All coaches + studio owner (individual email per recipient, full studio view) |
| Monthly survey summary | 1st of each month | Aggregated satisfaction scores, NPS, goal progress breakdown, every feedback quote from the past month | Studio owner |
| Plotly dashboard | Always-on | Studio-level retention trends, segment breakdowns | Studio owner |

**Weekly email — coaching context section:**
For each flagged member, the AI generates a short natural language paragraph (under 80 words) describing what the data shows and what context might be useful before the coach reaches out. This is background for the coach's own judgment — not a script, not an instruction. The coach decides whether and how to act.

**Technical stack:** Python (scikit-learn) · n8n workflow automation · OpenAI GPT-4o-mini · Plotly Dash for visualisation · Email (SMTP via n8n) for delivery · Tally.so for member surveys

**Member survey — event-triggered, not scheduled:**
A short 3-question survey is sent to members when one of two attendance signals drops below a configured threshold:

- **Class-level trigger:** A specific class drops in attendance versus its rolling 4-week average (e.g., a class normally at 10 attendees drops to 6 for 2 consecutive sessions). Survey sent to recent attendees of that class.
- **Studio-level trigger:** Total daily check-ins across the studio fall below a threshold vs the prior 4-week average (e.g., >20% drop week-on-week). Survey sent to all active members.

To prevent survey fatigue, no member receives a survey more than once every 5 weeks, regardless of how many triggers fire.

Survey questions (3 maximum):
1. How have you been finding your sessions lately? (1–5 stars)
2. Is there anything making it harder to come in regularly? (optional free text)
3. Would you like your coach to check in with you this week? (Yes / No)

Responses are tagged to the member's pseudonymous ID and surfaced in that week's weekly email report alongside the member's risk score. They are not processed by the AI model directly — they provide qualitative context the coach reads, not an additional model feature.

**GDPR note:** Survey participation is voluntary. Legal basis is legitimate interest (Article 6(1)(f)) — operational feedback on service quality. No sensitive data is collected. Responses are stored for 90 days and included in erasure requests. Members can opt out of survey contact at any time.

**Customisable thresholds — set per studio:**
Every studio defines churn differently. Before deployment, the following parameters are agreed jointly with the studio owner and stored as configuration values:

| Parameter | Default | Studio-defined |
|---|---|---|
| Days inactive = high risk | 21 days | Agreed at onboarding |
| Visit drop threshold | 50% vs prior 4-week avg | Agreed at onboarding |
| Class attendance drop trigger | 30% below 4-week avg for 2 sessions | Agreed at onboarding |
| Studio-wide check-in drop trigger | >20% drop week-on-week | Agreed at onboarding |
| Survey cooldown per member | 5 weeks | Agreed at onboarding |
| Briefing delivery time | 07:00 | Agreed at onboarding |
| Members shown in briefing | Top 10 by risk score | Agreed at onboarding |

---

### Coaching add-on — private coaching retention

Many boutique studios offer private or semi-private coaching programmes. These clients have a higher LTV (€200–400/month) and a distinct churn pattern: they may maintain general membership while quietly disengaging from coaching sessions — detectable weeks before they cancel.

The coaching add-on extends the core system with three additional data signals, each collected under explicit informed consent:

**Signal 1 — Coaching session check-in** (required for coaching module)
Attendance at every scheduled coaching session is recorded. The system tracks attendance rate, consecutive missed sessions, and days since last check-in. This is the primary early-warning signal for coaching churn.

**Signal 2 — General studio attendance** (optional)
The client's existing visit data feeds into their coaching profile. This distinguishes between full disengagement (stop coming entirely) and coaching-specific drop-off (still attending classes, skipping sessions) — two different interventions.

**Signal 3a — Wearable workout session data** (optional, explicit Article 9 consent)
Manually-initiated workout sessions from connected wearables (Fitbit, Garmin). Session type, duration, calories, in-session heart rate. Pulled only for sessions the member actively starts on their device.

**Signal 3b — Full daily activity data** (optional, explicit Article 9 consent, requires 3a)
Daily step count, active minutes, and resting heart rate. Provides a broader picture of training activity between sessions. Requires separate consent from 3a.

The consent gate in the n8n workflow technically enforces these tiers — wearable data is never accessed unless the corresponding consent flag is set from the coaching intake form.

---

## 4. Key Stakeholders and Their Interests

| Stakeholder | Role | Primary Interest |
|---|---|---|
| **Studio owner** | Data controller, decision-maker, buyer | Revenue protection, GDPR compliance, minimal operational overhead. Wants to know churn is being caught early without hiring someone to watch a spreadsheet. |
| **Coaches** | Primary system users | Timely, useful information that helps them have better conversations with members — without creating more admin work. Sceptical of tools that don't match how they work. |
| **Members** | Data subjects | Not feeling surveilled. Trusting that their data is used to support them, not to pressure or disadvantage them. Clear right to opt out at any time. |
| **Dina Bosma-Buczynska (consultant)** | Data processor, system operator | Delivering measurable retention outcomes. Building a replicable system that can be deployed across multiple studios. |
| **Legal / DPA** (if applicable) | Compliance oversight | GDPR Article 28 DPA in place before processing begins. EU AI Act classification documented. Clear data subject rights processes. |
| **Gym management software** (Mindbody, Gymdesk etc.) | Data source | System ingests exported data — no deep integration required at POC stage. Partnership potential at scale. |

---

## 5. Success Criteria

### What "this works" looks like at 90 days (POC)

| Criterion | Measure | Target |
|---|---|---|
| Coaches act on briefings | % of high-risk alerts where coach initiates outreach within 7 days | > 60% |
| Outreach changes outcomes | Churn rate for flagged + contacted members vs flagged + not contacted | Contacted members churn at measurably lower rate |
| Briefing quality | Coach self-reported usefulness ("Would you miss this briefing if it stopped?") | ≥ 2 of 3 coaches say yes |
| Model relevance | Do flagged members actually churn more than unflagged members? | Flagged cohort churn rate ≥ 2× unflagged cohort |
| Operational reliability | Briefing delivered without failure | ≥ 95% of scheduled runs succeed |
| GDPR compliance | No data subject complaints, DPA in place, deletion executed on request | Zero compliance incidents |

### What "this works" looks like at 12 months (commercial validation)

| Criterion | Measure | Target |
|---|---|---|
| Studio retention (our own churn) | % of POC studios that renew beyond initial term | ≥ 50% |
| Revenue per studio | Annual retained revenue attributable to AI-flagged outreach | ≥ €15,000 per studio (downside case) |
| Onboarding efficiency | Time from DPA signing to first live briefing | ≤ 5 working days |
| Model accuracy on real data | Accuracy on real studio hold-out set after retraining | ≥ 80% |
| Coaching add-on adoption | % of studios with coaching clients that activate the add-on | ≥ 40% |

### What failure looks like (and what to do with it)

A failed POC is not a wasted POC if the measurement framework is in place. If coaches read the briefings but don't change behaviour, the failure is in the briefing format or the outreach culture — not the model. If flagged members churn at the same rate as unflagged members, the failure is in the signal selection for this specific studio. Both outcomes are actionable. The 90-day joint debrief exists to make this decision clearly and honestly.

---

## Hypothesis

The system is built on two hypotheses that must be validated in sequence. Neither is assumed to be true before evidence is collected.

> **H1 — Prediction:** Behavioural signals in member visit data (frequency, recency, drop-off patterns) reliably predict which members will churn within the next 4–6 weeks.

> **H2 — Intervention:** When coaches receive AI-generated briefings identifying at-risk members and reach out based on those recommendations, those members retain at a measurably higher rate than at-risk members who were not contacted.

H2 is only testable if H1 holds. The 90-day POC is structured to test H1 first (Weeks 1–6), then H2 (Weeks 7–12). A failed H1 does not invalidate the project — it tells us which signals to recalibrate. A passed H1 and failed H2 tells us the intervention design needs work, not the model. Both are actionable findings.
