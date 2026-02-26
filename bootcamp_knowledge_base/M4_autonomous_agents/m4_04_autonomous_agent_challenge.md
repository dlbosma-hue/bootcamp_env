# LAB M4.04 - Autonomous Agent Challenge (Project Plan)

## Use Case
ADD-Friendly Study Assistant Agent. An autonomous agent that answers questions from bootcamp course materials using RAG, provides source citations, and delivers structured summaries to support students with ADD.

## The Problem Being Solved
Students with ADD struggle with:
- Re-reading large documents without retaining information
- No easy way to ask a document a direct question
- Losing track of which topics have been studied
- Getting overwhelmed when content is not broken into small pieces

## Technology Stack Selected
- Core LLM: OpenAI GPT-4
- Embeddings: text-embedding-ada-002
- Vector Database: Pinecone (already configured)
- Agent Framework: LangChain with RAG
- Document types: PDF and Markdown
- Orchestration: none for MVP (on-demand only)

## Technology Selection Framework Answers
- Needs external knowledge: Yes - requires RAG
- Needs file access: Yes - requires LangChain tools
- Multi-step reasoning: Yes - LangGraph considered for v2
- Business system integration: No - n8n not needed for MVP
- Autonomous operation: No - student triggers manually

## MVP Scope (What Is Included)
- Answer questions from course documents using RAG
- Support PDF and Markdown files
- Return source citation with every answer
- Summarize any topic in 3 to 5 bullet points on request
- Basic conversation memory within a single session

## Out of Scope for MVP
- Cross-session topic tracking
- Quiz generation
- Flashcard export
- Multi-language support
- Mobile app
- Calendar integration

## MVP Success Metrics
- 90% answer accuracy from loaded documents
- 100% citation rate (every answer has a source)
- Under 10 seconds response time

## Key Risks
- Hallucination: mitigated by "answer only from context" instruction in prompt
- High API costs: mitigated by caching common questions
- Poor chunking quality: mitigated by testing retrieval before connecting LLM

## Implementation Phases
- Phase 1 (1-2 days): Pinecone setup, document ingestion pipeline, chunking tests
- Phase 2 (2-3 days): LangChain RAG chain, citation output, session memory, summarization
- Phase 3 (1-2 days): Testing with real bootcamp documents, accuracy evaluation
- Phase 4 (1 day): Deployment as local tool, user guide

## Scoping Lesson Applied
Key question from the lesson: "What is the smallest scope that still brings value?"
Answer: just answer questions from documents with citations. Everything else is v2.
