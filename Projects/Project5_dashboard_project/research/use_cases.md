# Use Case Proposals: European Medium Fitness / Health Tech Chain

## Client Profile

- Sector: Fitness / Health Tech  
- Geography: Europe (EU‑based operator)  
- Company size: Medium – approx. 50–100 studios, 200+ coaches.  
- Core business model: Subscription and class‑based memberships with recurring revenue; strong dependence on retention and coach relationships.

Average membership fees in Europe often sit in the ~€30–€70 per month range depending on country and positioning, which means each retained member has a meaningful yearly value. Chleo’s main concern is that AI is a “black box” and she cannot see how it makes decisions about her members. The use cases below are chosen to both deliver financial value and showcase transparency.

---

## Use Case 1: Member Dropout Prediction (Early Warning System)

**Goal**  
Identify members at high risk of cancelling 2–4 weeks before they actually quit, so coaches can intervene proactively.

**Why it matters for a European medium chain**  
- Assume a typical studio with 100 active members paying around €50 per month (~€600 per year) and an effective lifetime value in the €1,500–€2,000 range when members stay engaged.  
- If roughly 60% of members disengage within the first 6–12 months, the lost lifetime value quickly reaches €90,000–€120,000 per year per 100‑member studio.  
- For a 50‑studio chain, even a modest 20–30% reduction in churn translates into hundreds of thousands of euros in retained revenue annually.

**Data used**  
- Behavioural workout data (sessions per week, gaps between workouts, intensity, variability) from Endomondo‑like datasets or integrated trackers.  
- Optional member metadata from churn datasets (membership type, contract length, demographics as available).

**AI component**  
- A logistic regression or similarly interpretable model that outputs a dropout risk score (0–100) per member.  
- Features: consistency, intensity, engagement/variety, recovery patterns, derived from large historical workout datasets.

**Value / KPI impact**  
- KPIs: churn rate, retention rate, revenue at risk, and retained revenue in euro terms.  
- Example framing for Chleo:
  - “If we prevent 20 of 60 expected dropouts per 100 members, at an LTV of ~€1,500 each, that’s ~€30,000 in retained value per studio per year.”  
  - “At a system cost around €299 per month (~€3,588 per year), payback is measured in weeks, not years.”

**Transparency angle**  
- Use LangSmith to log each risk prediction and show the input features and reasoning path.  
- In the demo, you can open an individual member trace and explain: “Here is why this member was flagged as high‑risk.”

---

## Use Case 2: Coach Workload Balancing and Prioritisation

**Goal**  
Provide coaches and regional managers with a clear view of which coaches are overloaded and which high‑risk members need immediate attention.

**Why it matters for a European medium chain**  
- With 200+ coaches across multiple countries or regions, it is difficult to see who has too many at‑risk clients and who has spare capacity.  
- Overloaded coaches may miss warning signs, while underutilised coaches could focus on outreach or follow‑up programmes.

**Data used**  
- Output from Use Case 1 (member‑level risk scores).  
- Coach‑member assignment data (which coach manages which members).  
- Operational metrics: number of clients per coach, average risk score per coach, number of overdue follow‑ups.

**AI / analytics component**  
- Aggregations and rules such as:
  - Flag coaches with more than a threshold number of “high‑risk” members.  
  - Highlight studios or regions where total risk load is above normal and may need additional staffing.

**Value / KPI impact**  
- Faster response to at‑risk members through better workload distribution.  
- Improved coach experience and retention by avoiding chronic overload and making expectations transparent.

**Transparency angle**  
- Dashboards clearly show how individual risk scores roll up to coach‑ and studio‑level metrics.  
- Thresholds (“overloaded”, “normal load”) can be defined in business terms, not hidden inside a model.

---

## Use Case 3: Class Scheduling and Capacity Optimisation

**Goal**  
Optimise class schedules and capacity (time slots, class types, locations) using attendance and engagement data, rather than intuition alone.

**Why it matters for a European medium chain**  
- With 50–100 studios in different cities or countries, local class demand patterns vary strongly.  
- Poor scheduling can leave daytime classes half‑empty while evening classes have waitlists, limiting revenue growth and member satisfaction.

**Data used**  
- Class attendance logs: date/time, location, class type, instructor, capacity, occupancy rate, waitlists.  
- Member behaviour patterns from Use Case 1 (e.g., at‑risk members who stopped attending a particular class or time).

**AI / analytics component**  
- Descriptive analytics to identify:
  - Underperforming time slots with consistently low occupancy.  
  - High‑demand classes and times with persistent waitlists.  
- Simple scenario recommendations:
  - Shift low‑performing classes to better times.  
  - Add capacity or duplicate high‑demand formats in peak evening hours.

**Value / KPI impact**  
- Higher average class occupancy and revenue per class hour.  
- Better alignment between offering and actual European member behaviour in each city.

**Transparency angle**  
- All recommendations are backed by visible charts in the BI dashboard (occupancy per time slot, class, location).  
- AI is used to highlight patterns and suggest scenarios; final decisions remain with operations managers.

---

---

## Implementation Status (as of March 2026)

This section documents what was actually built during the 2-day sprint vs. what remains at concept/proposal level.

### Use Case 1 — Member Dropout Prediction: FULLY IMPLEMENTED

Everything described above was built and is live:

- **Data pipeline:** `data/prepare_fitness_user_metrics_from_json.py` processes 167,783 Endomondo workout sessions into `fitness_user_metrics.csv` (1,059 members, 12 columns including churn risk and revenue at risk).
- **Churn scoring:** Rule-based heuristic using `avg_sessions_per_week` and `days_since_last_workout` assigns each member a low / medium / high risk label. Result: 382 low, 447 medium, 230 high-risk members; €345,000 total revenue at risk.
- **Dashboard:** Interactive Plotly/Dash app (5 charts + KPI cards) and a published Tableau workbook — both loaded and running against live data.
- **Automated daily alert:** n8n workflow (live at dina2.app.n8n.cloud) runs every weekday at 08:00, filters high-risk members, and sends a Slack message to the coach channel with member list and revenue at risk.
- **AI insight layer:** LangChain agent (`agent/agent.py`) generates 12 business insights from the processed data, saved to `agent/insights_generated.json`.
- **Quality monitoring:** LangSmith evaluation (`langsmith/monitoring_setup.py`) runs LLM-as-judge scoring across 3 dimensions (relevance, actionability, clarity). Overall score: 0.911 / 1.0.

### Use Case 2 — Coach Workload Balancing: CONCEPT ONLY (not built)

This use case is fully scoped in the proposal above but was not implemented in the sprint. The primary reason is a data gap: the Endomondo dataset contains no coach assignment data. There is no field mapping members to coaches, no coach workload metrics, and no coach-level aggregations in the current pipeline.

What exists that partially supports this use case:
- The Plotly dashboard includes a filterable high-risk member table, which a coach could manually use to identify who needs outreach.
- The n8n daily alert lists members by days inactive — a coach receiving this alert effectively has a prioritised action list.

What would be needed to fully implement this in production:
- A coach–member assignment table from the gym management system.
- Coach-level aggregations (average risk score per coach, number of high-risk members per coach, follow-up logs).
- A coach-facing dashboard view separate from the management overview.

### Use Case 3 — Class Scheduling & Capacity Optimisation: CONCEPT ONLY (not built)

This use case is fully scoped in the proposal but was not implemented. The data required (class attendance logs, time slots, occupancy rates, waitlists) does not exist in either the Endomondo or gym_churn_us datasets.

What exists that partially supports this use case:
- The `sport` field in the Endomondo data shows which sport type each session was logged for (e.g. running, cycling, gym). The pipeline derives `sport_variety` per member.
- The dashboard shows sport variety by risk level, which gives a weak proxy for class engagement breadth.

What would be needed to fully implement this in production:
- Class-level attendance logs from the studio booking system (date, time, class type, instructor, capacity, occupancy).
- Time-slot analysis: occupancy rate by hour and day of week.
- Scenario modelling: simple rules or descriptive analytics to identify underperforming slots and high-demand classes.

---

## Fit with a European Medium‑Sized Chain

These three use cases are specifically scoped for a European medium‑sized fitness chain:

- They rely on data that the operator likely already has (attendance, basic workout data, membership info).  
- They assume realistic tooling: common EU‑friendly SaaS and cloud offerings, plus free or low‑cost tiers (LangSmith, n8n Cloud, LLM APIs).  
- They are modular and can be piloted in a subset of clubs in one country before scaling across the network.

Together, these use cases form a coherent narrative for Chleo:

1. See which members are at risk in the next few weeks, in euro terms.  
2. Show which coaches and studios need help to act on that risk.  
3. Align the schedule and capacity to how European members actually train.

Each step is backed by visible data, interpretable metrics, and monitoring via LangSmith to address her fear that “AI is a black box.”
