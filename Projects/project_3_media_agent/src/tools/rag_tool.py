# rag_tool.py
# Tool 1: Knowledge Base Search - Research Benchmarks via RAG
#
# Part of the Media Diversity Watch autonomous research agent.
# Wraps the Pinecone RAG pipeline as a LangChain tool so the
# ReAct agent can query our curated knowledge base for industry
# standards, evidence-based criteria, and inclusivity benchmarks.
#
# The knowledge base contains 18 curated documents across 4 angles.

from langchain.tools import tool


@tool
def rag_query_tool(query: str, angle: str = "") -> str:
    """
    Search the Media Diversity Watch knowledge base for research benchmarks,
    industry standards, and evidence-based criteria for evaluating media
    inclusivity. Use this to answer questions like:
      - 'What is good byline diversity for women in news?'
      - 'What language is considered harmful toward LGBTQ+ communities?'
      - 'What do industry standards say about sourcing diversity?'
    The optional 'angle' parameter filters results to a specific research area.
    Valid values: bylines_and_story_selection, portrayal_in_content,
    sourcing_diversity, language_and_framing. Leave blank to search all angles.
    """
    from src.rag_pipeline import rag_query

    angle_filter = angle.strip() if angle.strip() else None

    try:
        results = rag_query(query, top_k=3, angle_filter=angle_filter)
    except Exception as e:
        return f"Knowledge base query failed: {e}"

    if not results:
        return f"No knowledge base results found for: '{query}'"

    lines = [
        f"KNOWLEDGE BASE: '{query}'",
        f"Angle filter: {angle_filter or 'all angles'}",
        f"Retrieved {len(results)} relevant benchmark(s):",
        "",
    ]

    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] Relevance: {r['score']:.3f} | Angle: {r['angle']}")
        lines.append(r["text"])
        lines.append("")

    return "\n".join(lines)
