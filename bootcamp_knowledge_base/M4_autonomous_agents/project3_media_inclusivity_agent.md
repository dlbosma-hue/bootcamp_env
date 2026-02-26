# Project 3 - Autonomous Media Inclusivity Research Agent

## Use Case
Build an autonomous AI agent that researches media companies and evaluates them through an intersectional inclusivity lens. The agent examines how organizations represent and portray women, LGBTQ+ communities, racial and ethnic minorities, and people with disabilities.

## The 4-Angle Evaluation Framework
1. Representation in bylines and story selection - are diverse communities writing the stories, not just appearing in them?
2. Portrayal within content - do communities appear as experts and leaders, or only as victims and criminals?
3. Sourcing diversity - who is quoted as an authority? Is it always the same demographic?
4. Language and framing - does the language used signal bias in how communities are described?

## Architecture

```
n8n (entry point - receives company name from webhook or form)
    |
    v
Python script: LangGraph workflow
    |
    +-- Plan node: define research questions
    |
    +-- Research node: call 3 APIs (NewsAPI, Guardian API, Wikipedia)
    |
    +-- RAG node: search Pinecone for existing knowledge about the company
    |
    +-- Analysis node: score the company on each of the 4 angles
    |
    +-- Synthesize node: combine scores into an overall assessment
    |
    +-- Report node: generate final report
    |
    v
n8n (output - delivers report via Notion or email)
```

## The 3 Research Tools (MCP Tools via LangChain)
- NewsAPI - fetches recent articles published by or about the media company
- Guardian API - pulls Guardian coverage for cross-reference and sourcing analysis
- Wikipedia API - retrieves background info about company ownership and history

## RAG Setup
- Vector database: Pinecone
- Embeddings: OpenAI text-embedding-ada-002
- Knowledge base: pre-loaded with media inclusivity research papers and reports
- The RAG lookup happens in parallel with API research to add academic grounding

## Hallucination Prevention
Because the agent makes claims about real companies that could be academically problematic if wrong:
- All claims must cite a specific source (article title + URL or document name)
- The synthesis prompt instructs the LLM: "Only make assessments supported by retrieved evidence"
- A confidence score accompanies each claim (high / medium / low)

## LangGraph State
```python
class ResearchState(TypedDict):
    company_name: str
    research_questions: list
    raw_articles: list
    rag_results: list
    angle_scores: dict      # one score per angle (1-5)
    overall_assessment: str
    report: str
    sources: list
```

## n8n Role
- Entry: webhook receives company name from user
- Middle: calls the Python LangGraph script via Execute Command node or HTTP request
- Exit: takes the report string and posts it to Notion via the Notion node

## Key Learning
n8n and LangGraph serve different roles and work best together. LangGraph handles the AI reasoning and multi-step research logic. n8n handles the trigger, the routing, and delivering the output to a real destination. Trying to do the AI reasoning inside n8n directly would require many more nodes and be much harder to debug.
