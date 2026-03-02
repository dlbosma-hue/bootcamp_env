"""
media_agent.py
Autonomous Media Inclusivity Research Agent

Uses LangGraph's ReAct pattern to reason and act across 4 research tools,
investigating media companies for Media Diversity Watch across:
  - 4 evaluation angles (bylines, portrayal, sourcing, language)
  - 4 marginalised communities (women, LGBTQ+, race, disability)

ReAct loop: Thought → Action (tool call) → Observation → Thought → ...
until the agent has enough evidence to produce a full research summary.

Usage (from project root):
    python -c "from src.agents.media_agent import run_research; result = run_research('BBC'); print(result['final_analysis'])"
"""

from datetime import date

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.tools import analyse_rss_feed, rag_query_tool, search_newsapi, search_wikipedia

load_dotenv()

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# All 4 MCP-compatible tools bound to the agent
TOOLS = [analyse_rss_feed, rag_query_tool, search_newsapi, search_wikipedia]

# ---------------------------------------------------------------------------
# System prompt — instructs the ReAct agent on its role and research protocol
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an autonomous media inclusivity researcher for Media Diversity Watch,
a non-profit that holds major news outlets accountable for fair and inclusive coverage.

Your role is to conduct thorough, evidence-based investigations of media companies.
You must research EVERY assignment across four evaluation angles and four communities.

EVALUATION ANGLES:
1. Bylines and Story Selection — Who writes the stories? Are marginalised journalists
   assigned to diverse beats or confined to "minority" topics?
2. Portrayal Within Content — Are marginalised groups shown as full human beings
   (experts, leaders, protagonists) or only as victims, criminals, or statistics?
3. Sourcing Diversity — Who gets quoted as an authority? Do community members speak
   for themselves, or are outside "experts" used to speak about them?
4. Language and Framing — Is language inclusive and accurate? Does framing humanise
   or dehumanise marginalised communities?

COMMUNITIES TO EVALUATE:
- Women and gender equality
- LGBTQ+ communities
- Racial and ethnic minorities
- People with disabilities

RESEARCH PROTOCOL — you MUST call all four tools for every assignment:
1. analyse_rss_feed — Get today's primary source data: bylines, community coverage
   counts, and language flags directly from the outlet's published content.
2. rag_query_tool — Query the knowledge base for industry benchmarks and standards.
   Call this multiple times with different queries and angle filters.
3. search_newsapi — Find what journalists and critics say about this outlet's
   diversity and inclusion record.
4. search_wikipedia — Get company background: ownership, editorial history, reach.

Collect all evidence before drawing conclusions. Be specific — cite numbers,
percentages, and named examples from your tool results. Never fabricate data.
Flag any active harm patterns (dehumanising language, crime-framing of minorities,
erasure of community voices) with clear evidence."""


# ---------------------------------------------------------------------------
# Research prompt builder
# ---------------------------------------------------------------------------
def _build_research_prompt(company: str) -> str:
    return f"""Research {company} comprehensively for a Media Diversity Watch inclusivity audit.

Today's date: {date.today().isoformat()}

Follow this research sequence:

STEP 1 — Primary source evidence:
  analyse_rss_feed("{company}")

STEP 2 — Knowledge base benchmarks (call rag_query_tool at least 4 times):
  rag_query_tool("bylines diversity women journalists", "bylines_and_story_selection")
  rag_query_tool("how marginalised communities should be portrayed news", "portrayal_in_content")
  rag_query_tool("expert sourcing diversity standards journalism", "sourcing_diversity")
  rag_query_tool("inclusive language guidelines harmful terms media", "language_and_framing")

STEP 3 — Critic and journalist perspectives:
  search_newsapi("{company} newsroom diversity inclusion representation")

STEP 4 — Company background:
  search_wikipedia("{company} media company")

After gathering all evidence, write a comprehensive research summary that covers:
  • Bylines and Story Selection findings (with specific numbers from RSS analysis)
  • Portrayal Within Content findings (examples from articles)
  • Sourcing Diversity findings
  • Language and Framing findings (note any flagged terms)
  • Community-by-Community observations (Women / LGBTQ+ / Race / Disability)
  • Any harm flags or serious concerns
  • Preliminary scores for each community on a 1-10 scale with justification
    Scoring guide: 9-10 = industry leader; 7-8 = above average;
    5-6 = meets minimum standards; 3-4 = below average; 1-2 = serious concerns
  • Key strengths and actionable recommendations

Be thorough. A senior analyst will use your summary to write the final report."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_research(company: str) -> dict:
    """
    Run the full ReAct research pipeline for a media company.

    The LangGraph agent reasons through what tools to call, calls them,
    observes the results, and iterates until it has enough evidence to
    produce a full research summary.

    Args:
        company: Name of the media outlet (e.g. 'BBC', 'Guardian', 'CNN')

    Returns:
        dict with keys:
          company       — the name passed in
          messages      — full LangGraph message history (Thought/Action/Observation)
          final_analysis — the agent's final research summary (string)
          error         — error message if something failed, else None
    """
    print(f"\n{'='*60}")
    print(f"[AGENT] Starting research: {company}")
    print(f"[AGENT] Tools: {[t.name for t in TOOLS]}")
    print(f"{'='*60}\n")

    agent = create_react_agent(llm, TOOLS)

    try:
        result = agent.invoke(
            {
                "messages": [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=_build_research_prompt(company)),
                ]
            },
            config={"recursion_limit": 30},
        )

        # The final AI message is the last non-tool message
        final_analysis = ""
        for msg in reversed(result["messages"]):
            if (
                hasattr(msg, "content")
                and msg.content
                and not getattr(msg, "tool_calls", None)
                and msg.__class__.__name__ == "AIMessage"
            ):
                final_analysis = msg.content
                break

        total_messages = len(result["messages"])
        tool_calls = sum(
            1 for m in result["messages"]
            if getattr(m, "tool_calls", None)
        )
        print("\n[AGENT] Research complete.")
        print(f"[AGENT] Total messages: {total_messages} | Tool calls: {tool_calls}")

        return {
            "company": company,
            "messages": result["messages"],
            "final_analysis": final_analysis,
            "error": None,
        }

    except Exception as e:
        print(f"\n[AGENT] Error during research: {e}")
        return {
            "company": company,
            "messages": [],
            "final_analysis": "",
            "error": str(e),
        }
