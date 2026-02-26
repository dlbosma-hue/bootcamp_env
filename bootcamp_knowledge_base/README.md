# Bootcamp Knowledge Base
## ADD-Friendly Study Assistant - Source Documents

This folder contains clean summary documents for every lab completed in the bootcamp.
These files are designed to be loaded into a Pinecone vector database and searched
by the ADD-Friendly Study Assistant Agent.

---

## Folder Structure

```
bootcamp_knowledge_base/
    README.md                          <-- this file
    M1_python_foundations/
        m1_01_homeguard.md
        m1_02_refactoring.md
        m1_05_07_api_and_audio.md
    M2_apis_and_rag/
        m2_01_prompt_engineering.md
        m2_03_news_summarizer.md
        m2_04_chunking_strategies.md
        rag_pipeline_and_dynamic_prompting.md
    M3_langchain/
        m3_01_langchain_agents.md
        m3_02_reranking.md
    M4_autonomous_agents/
        m4_01_langgraph.md
        m4_02_mcp.md
        m4_03_n8n.md
        project3_media_inclusivity_agent.md
        m4_04_autonomous_agent_challenge.md
```

---

## What Each File Covers

### Module 1 - Python Foundations
| File | Topics |
|---|---|
| m1_01_homeguard.md | Functions, classes, dictionaries, if/else logic, sensor data processing |
| m1_02_refactoring.md | Helper functions, Single Responsibility Principle, error handling, DRY |
| m1_05_07_api_and_audio.md | Base64 encoding, OpenAI vision API, Whisper transcription, audio chunking |

### Module 2 - APIs and RAG
| File | Topics |
|---|---|
| m2_01_prompt_engineering.md | v1/v2/v3 iteration, few-shot examples, Chain-of-Thought, format constraints |
| m2_03_news_summarizer.md | Multi-provider API, fallback logic, rate limiting, jitter optimization |
| m2_04_chunking_strategies.md | Fixed-size vs recursive chunking, chunk_size, chunk_overlap, podcast vs PDF |
| rag_pipeline_and_dynamic_prompting.md | Full RAG pipeline, embeddings, Pinecone, dynamic prompt templates |

### Module 3 - LangChain
| File | Topics |
|---|---|
| m3_01_langchain_agents.md | ReAct loop, @tool decorator, AgentExecutor, freeform vs structured |
| m3_02_reranking.md | Two-stage RAG, Cohere reranker, cosine similarity vs reranker scores |

### Module 4 - Autonomous Agents
| File | Topics |
|---|---|
| m4_01_langgraph.md | State, nodes, edges, conditional routing, Pydantic validation, Bloyce's Protocol |
| m4_02_mcp.md | MCP config files, filesystem tools, Claude Code vs Claude Desktop setup |
| m4_03_n8n.md | n8n nodes, Discord+Sheets workflow, Set node transforms, session IDs |
| project3_media_inclusivity_agent.md | Full autonomous agent, 4-angle framework, LangGraph+n8n architecture |
| m4_04_autonomous_agent_challenge.md | Project planning, technology selection framework, MVP scope, risk assessment |

---

## How to Load These Into Pinecone (Pipeline - coming next)

When the ingestion pipeline is ready, it will:
1. Walk through every folder in this directory
2. Read each .md file
3. Split into chunks using RecursiveCharacterTextSplitter
4. Generate embeddings with text-embedding-ada-002
5. Store each chunk in Pinecone with metadata:
   - source: filename
   - module: folder name
   - chunk_id: unique hash

Then the Study Assistant Agent can search across all of them with a single query.

---

## Total Documents: 13 files across 4 modules
