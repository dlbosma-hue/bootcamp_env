"""
mock_server.py
Lightweight mock FastAPI server for N8N smoke testing (Day 2).
Returns a hardcoded ResearchResponse — no LLM calls, no API keys needed.
Replace with `python run.py` in Day 4 to use the live LangGraph agent.
"""
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Media Diversity Watch — Mock Server (Day 2 smoke test)")

class AnalyseRequest(BaseModel):
    company: str
    focus: str = "all"

@app.get("/")
def health():
    return {"status": "ok", "mode": "mock", "date": date.today().isoformat()}

@app.post("/research")
def mock_research(request: AnalyseRequest):
    company = request.company or "Test Outlet"
    return {
        "status": "success",
        "company": company,
        "report_text": f"# {company}: Media Inclusivity Report\n\n**Date:** {date.today().strftime('%d %B %Y')}\n\nThis is a mock report generated for N8N smoke testing.\n\n## 9. Inclusivity Score\n\n| Community | Score (1-10) | Justification |\n|---|---|---|\n| Women | 6/10 | Mock score |\n| LGBTQ+ | 5/10 | Mock score |\n| Race | 5/10 | Mock score |\n| Disability | 4/10 | Mock score |\n| **Overall Average** | **5/10** | |\n\n## 8. Areas of Concern and Harm Flags\n- ⚠️ Mock harm flag for smoke test\n",
        "summary": f"{company} scores 5.0/10 in this mock smoke test. Plumbing confirmed — swap mock_server.py for run.py in Day 4.",
        "report_path": f"reports/mock_{company.lower().replace(' ', '_')}_{date.today().isoformat()}.md",
        "overall_score": 5.0,
        "harm_flags": ["Mock harm flag for smoke test"],
        "community_scores": {"Women": 6.0, "LGBTQ+": 5.0, "Race": 5.0, "Disability": 4.0},
        "date": date.today().isoformat(),
    }

if __name__ == "__main__":
    import uvicorn
    print("\nMock server running at http://localhost:8000")
    print("N8N should call POST http://localhost:8000/research")
    print("Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
