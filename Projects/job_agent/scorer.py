import json
import os
import re

from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

_RESUME_TEXT: str | None = None
_ARBEITSZEUGNIS_TEXT: str | None = None

SCORE_PROMPT = """\
Here is a job posting to evaluate:

<job>
Title: {title}
Company: {company}
Location: {location}
Description: {description}
</job>

Score this job from 1 to 10 based on fit with the candidate's full profile above.

Scoring criteria:
- Seniority match: candidate is a senior IT leader (Head of IT / Director level since 2019).
  The Arbeitszeugnis confirms exceptional performance at that level. Penalise roles below it.
- Domain overlap: IT strategy, infrastructure, governance, ITIL, PMO, digital transformation,
  ISO 27001, agile, consulting. Weight heavily.
- Location (important):
  * Prefer: Berlin-based hybrid, Berlin-based remote-friendly, or fully remote anywhere in DE/EU.
  * Accept: Berlin on-site if the role is a strong domain match.
  * Penalise heavily (-3 points): roles outside Berlin with no remote option mentioned.
  * Penalise heavily (-3 points): roles where location is unclear and no Berlin/remote signal exists.
- Language: German-language roles are fine; candidate is native German speaker.

IMPORTANT RULES:
- Only use information explicitly stated in the resume or Arbeitszeugnis.
- Do not infer, assume, or hallucinate any experience, skill, or achievement
  for the candidate that is not explicitly written in the resume or Arbeitszeugnis.

Respond with valid JSON only, no extra text:
{{
  "score": <int 1-10>,
  "match_reason": "<one sentence, grounded only in documented facts>",
  "flag": "<'apply' | 'maybe' | 'skip'>"
}}
"""


def _load_resume() -> str:
    global _RESUME_TEXT
    if _RESUME_TEXT is None:
        env_val = os.environ.get("RESUME_TEXT")
        if env_val:
            _RESUME_TEXT = env_val
        else:
            path = os.path.join(os.path.dirname(__file__), "resume.md")
            with open(path) as f:
                _RESUME_TEXT = f.read()
    return _RESUME_TEXT


def _load_arbeitszeugnis() -> str:
    global _ARBEITSZEUGNIS_TEXT
    if _ARBEITSZEUGNIS_TEXT is None:
        env_val = os.environ.get("ARBEITSZEUGNIS_TEXT")
        if env_val:
            _ARBEITSZEUGNIS_TEXT = env_val
        else:
            path = os.path.join(os.path.dirname(__file__), "arbeitszeugnis.md")
            with open(path) as f:
                _ARBEITSZEUGNIS_TEXT = f.read()
    return _ARBEITSZEUGNIS_TEXT


def _build_system_prompt() -> str:
    resume = _load_resume()
    zeugnis = _load_arbeitszeugnis()
    return (
        "You are a senior recruiter evaluating job fit for a senior IT leader candidate.\n"
        "Only use information explicitly stated in the documents below. "
        "Do not infer, assume, or hallucinate any experience not written there.\n\n"
        f"<resume>\n{resume}\n</resume>\n\n"
        f"<arbeitszeugnis>\n{zeugnis}\n</arbeitszeugnis>"
    )


def score_job(job: dict) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=256,
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {
                "role": "user",
                "content": SCORE_PROMPT.format(
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    description=job["description"] or "No description available.",
                ),
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {"score": 0, "match_reason": "parse error", "flag": "skip"}


def score_jobs(jobs: list[dict]) -> list[dict]:
    scored = []
    for i, job in enumerate(jobs):
        print(f"[scorer] Scoring {i+1}/{len(jobs)}: {job['title']} @ {job['company']}")
        result = score_job(job)
        scored.append({**job, **result})
    return scored
