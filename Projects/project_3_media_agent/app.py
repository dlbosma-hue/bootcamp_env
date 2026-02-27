"""
app.py
FastAPI Server for Media Diversity Watch Agent

Provides HTTP endpoints for N8N and other clients to trigger
a full inclusivity research report for a media company.

Run:
    uvicorn app:app --reload --port 8000

Endpoints:
    GET  /          → health check
    POST /research  → N8N-compatible endpoint (matches workflow field names)
    POST /analyse   → alias for /research
"""

import re
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Media Diversity Watch API",
    description="Autonomous media inclusivity research agent powered by LangGraph ReAct",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class AnalyseRequest(BaseModel):
    company: str
    focus: str = "all"  # optional focus community, passed through by N8N


class ResearchResponse(BaseModel):
    status: str
    company: str
    report_text: str        # full Markdown report — saved as Notion page body
    summary: str            # 1-2 sentence plain-text summary — Notion column
    report_path: str
    overall_score: float    # parsed from score table — Notion column
    harm_flags: list        # list of ⚠️ flagged concerns — Notion column
    community_scores: dict  # {Women: 6.0, LGBTQ+: 5.0, ...} — Notion column
    date: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_report_metrics(report: str) -> dict:
    """
    Extract structured metrics from the generated Markdown report.
    Parses the score table and harm flags so N8N can store them in Notion.
    """
    metrics: dict = {
        "overall_score": 5.0,
        "harm_flags": [],
        "community_scores": {},
    }

    # Parse score table rows: | Women | 7/10 | justification |
    score_pattern = r"\|\s*(Women|LGBTQ\+|Race|Disability|Overall Average)\s*\|\s*\**(\d+(?:\.\d+)?)/10\**"
    for community, score in re.findall(score_pattern, report, re.IGNORECASE):
        if "overall" in community.lower():
            metrics["overall_score"] = float(score)
        else:
            metrics["community_scores"][community] = float(score)

    # Parse harm flags: any bullet line containing ⚠️
    harm_lines = [
        line.strip().lstrip("-•⚠️ ").strip()
        for line in report.split("\n")
        if "⚠️" in line and line.strip()
    ]
    metrics["harm_flags"] = harm_lines

    return metrics


def _run_full_pipeline(company: str) -> ResearchResponse:
    """Shared logic used by both /research and /analyse endpoints."""
    from src.agents.media_agent import run_research
    from src.report_generator import generate_report, generate_summary, save_report

    research_result = run_research(company)

    if research_result.get("error"):
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {research_result['error']}",
        )

    if not research_result.get("final_analysis"):
        raise HTTPException(
            status_code=500,
            detail="Agent returned no analysis. Check server logs.",
        )

    report_md = generate_report(company, research_result["final_analysis"])
    report_path = save_report(company, report_md)
    metrics = _parse_report_metrics(report_md)
    summary = generate_summary(company, report_md, metrics["overall_score"])

    return ResearchResponse(
        status="success",
        company=company,
        report_text=report_md,
        summary=summary,
        report_path=str(report_path),
        overall_score=metrics["overall_score"],
        harm_flags=metrics["harm_flags"],
        community_scores=metrics["community_scores"],
        date=date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def health_check():
    """Health check — confirms the server is running."""
    return {
        "status": "ok",
        "service": "Media Diversity Watch Agent",
        "date": date.today().isoformat(),
    }


@app.post("/research", response_model=ResearchResponse)
def research_company(request: AnalyseRequest):
    """
    N8N-compatible endpoint. Triggers the full ReAct research pipeline
    and returns structured fields that the N8N workflow expects:
    report_text, overall_score, harm_flags, community_scores.

    Called by N8N HTTP Request node:
        POST http://localhost:8000/research
        {"company": "BBC", "focus": "all"}
    """
    company = request.company.strip()
    if not company:
        raise HTTPException(status_code=400, detail="Company name cannot be empty.")
    return _run_full_pipeline(company)


@app.post("/analyse", response_model=ResearchResponse)
def analyse_company(request: AnalyseRequest):
    """Alias for /research — same behaviour, kept for backwards compatibility."""
    company = request.company.strip()
    if not company:
        raise HTTPException(status_code=400, detail="Company name cannot be empty.")
    return _run_full_pipeline(company)
