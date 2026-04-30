import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from config import OPENAI_MODEL, OPENAI_FILTER_MODEL, SCORE_THRESHOLDS, SCORING_WORKERS

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ── Scoring prompt ────────────────────────────────────────────────────────────

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
Title:       {title}
Company:     {company}
Location:    {location}
Description: {description}"""


# ── Core scoring function ─────────────────────────────────────────────────────

def _call_score(job: dict, context: dict, model: str) -> dict:
    system = _SYSTEM_PROMPT.format(**context)
    user = _USER_TEMPLATE.format(
        title=job["title"],
        company=job["company"],
        location=job["location"],
        description=job["description"][:3000],
    )
    try:
        resp = client.chat.completions.create(
            model=model,
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
        thresholds = SCORE_THRESHOLDS
        if score >= thresholds["apply"]:
            flag = "apply"
        elif score >= thresholds["maybe"]:
            flag = "maybe"
        else:
            flag = "skip"
        return {"score": score, "match_reason": result.get("match_reason", ""), "flag": flag}
    except Exception as e:
        print(f"  [scorer] error on '{job['title']}': {e}")
        return {"score": 0, "match_reason": str(e), "flag": "skip"}



# ── Two-pass parallel pipeline ────────────────────────────────────────────────

def score_all(jobs: list[dict], resume_text: str, reference_text: str, certification_text: str) -> list[dict]:
    """
    Pass 1: score all jobs with gpt-4o-mini in parallel (fast filter).
    Pass 2: re-score shortlist (score >= FILTER_PASS_THRESHOLD) with gpt-4o.
    Pass 3: generate cover letter opening for every "apply" job.
    """
    from config import FILTER_PASS_THRESHOLD

    context = dict(
        resume_text=resume_text,
        reference_text=reference_text,
        certification_text=certification_text,
    )

    # ── Pass 1: mini, parallel ────────────────────────────────────────────────
    print(f"  [scorer] pass 1 — {OPENAI_FILTER_MODEL}, {len(jobs)} jobs, {SCORING_WORKERS} workers")
    results = [None] * len(jobs)

    with ThreadPoolExecutor(max_workers=SCORING_WORKERS) as ex:
        future_map = {
            ex.submit(_call_score, job, context, OPENAI_FILTER_MODEL): i
            for i, job in enumerate(jobs)
        }
        for future in as_completed(future_map):
            results[future_map[future]] = future.result()

    scored = [{**job, **result} for job, result in zip(jobs, results)]

    # ── Pass 2: gpt-4o re-score shortlist ────────────────────────────────────
    shortlist = [j for j in scored if j["score"] >= FILTER_PASS_THRESHOLD]
    print(f"  [scorer] pass 2 — {OPENAI_MODEL}, {len(shortlist)} shortlisted jobs")

    with ThreadPoolExecutor(max_workers=max(1, SCORING_WORKERS // 2)) as ex:
        future_map = {
            ex.submit(_call_score, job, context, OPENAI_MODEL): job["id"]
            for job in shortlist
        }
        refined = {fid: fut.result() for fut, fid in
                   [(f, future_map[f]) for f in as_completed(future_map)]}

    for job in scored:
        if job["id"] in refined:
            job.update(refined[job["id"]])

    return scored
