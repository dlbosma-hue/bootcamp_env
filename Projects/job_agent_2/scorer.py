import json
import os

from openai import OpenAI

from config import OPENAI_MODEL, SCORE_THRESHOLDS

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

_SYSTEM_PROMPT = """\
You are a senior tech recruiter evaluating job fit for an AI Product Manager
who is also IronHack-certified in AI Consulting & Integration and actively
targeting both PM and AI consulting roles.

Here is the candidate's CV:
<resume>
{resume_text}
</resume>

Here is an interim employer reference letter (Zwischenzeugnis) from a major
European e-commerce platform, issued May 2025, confirming ongoing employment
and senior-level performance:
<reference_letter>
{reference_text}
</reference_letter>

Here is the candidate's professional certification context:
<certification>
{certification_text}
</certification>

Score this job 1-10 for fit. Consider the following:

SENIORITY
Mid-to-senior PM with 3+ years in AI/platform product roles at a European
e-commerce company. Reference letter independently confirms senior-level
performance. IronHack certification (400h+, completed April 2026) confirms
hands-on AI implementation capability at consulting level.

DOMAIN STRENGTHS — reward strong overlap:
- AI-assisted decision systems, workflow automation, assignment algorithms
- Internal platform products scaled to 200+ users
- OKR/KPI-driven product governance
- Cross-functional stakeholder alignment (ops, sales, engineering)
- API integrations, data model design, AI system validation
- RAG architectures, agentic AI, LLM evaluation, EU AI Act compliance
- Executive-level AI communication and consulting delivery

TECHNICAL SKILLS — strong plus if required by role:
- Python, LangChain, LangGraph, OpenAI API, n8n, prompt engineering
- RAG pipelines, agentic AI orchestration, multi-LLM APIs
- pandas, NumPy, scikit-learn, Tableau, Power BI
- Git/GitHub, JIRA, Confluence

HARD REQUIREMENTS — penalise heavily if not met:
- Role must be workable in English, German, or Dutch
- Location: Berlin on-site acceptable, hybrid preferred, fully remote fine;
  penalise roles with zero remote/hybrid flexibility
- Hours: penalise roles clearly requiring more than 38 hours per week
- Seniority: penalise junior roles or roles requiring 5+ years in a pure
  engineering function the candidate does not hold

Do not hallucinate candidate experience. Base the score only on what is
explicitly stated in the resume, reference letter, and certification above.

Respond with JSON only — no preamble, no markdown fences:
{{
  "score": <int 1-10>,
  "match_reason": "<one sentence explaining the primary fit or gap>",
  "flag": "<apply | maybe | skip>"
}}"""

_USER_TEMPLATE = """\
Here is a job posting:
<job>
Title:       {title}
Company:     {company}
Location:    {location}
Description: {description}
</job>"""


def score_job(job: dict, resume_text: str, reference_text: str, certification_text: str) -> dict:
    system = _SYSTEM_PROMPT.format(
        resume_text=resume_text,
        reference_text=reference_text,
        certification_text=certification_text,
    )
    user = _USER_TEMPLATE.format(
        title=job["title"],
        company=job["company"],
        location=job["location"],
        description=job["description"][:3000],
    )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
            temperature=0,
        )
        result = json.loads(resp.choices[0].message.content)
        score = int(result.get("score", 1))
        flag = result.get("flag", "skip")

        # Ensure flag is consistent with score
        thresholds = SCORE_THRESHOLDS
        if score >= thresholds["apply"]:
            flag = "apply"
        elif score >= thresholds["maybe"]:
            flag = "maybe"
        else:
            flag = "skip"

        return {
            "score": score,
            "match_reason": result.get("match_reason", ""),
            "flag": flag,
        }
    except Exception as e:
        print(f"  [scorer] error scoring '{job['title']}': {e}")
        return {"score": 0, "match_reason": str(e), "flag": "skip"}
