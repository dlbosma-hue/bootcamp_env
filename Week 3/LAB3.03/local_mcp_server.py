"""
local_mcp_server.py
A minimal MCP server (stdio transport) that exposes AI reference content
as MCP resources. Used in LAB3.03 Step 6 to demonstrate multi-server setup
with real resource access alongside the langchain-docs HTTP server.
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource

app = Server("local-resources")

_RESOURCES = {
    "local://ai-concepts/rag": Resource(
        uri="local://ai-concepts/rag",
        name="RAG Overview",
        description="Retrieval-Augmented Generation: how it works and key components",
        mimeType="text/plain",
    ),
    "local://ai-concepts/agents": Resource(
        uri="local://ai-concepts/agents",
        name="AI Agents Overview",
        description="How AI agents work: the ReAct loop and LangChain components",
        mimeType="text/plain",
    ),
    "local://ai-concepts/mcp": Resource(
        uri="local://ai-concepts/mcp",
        name="MCP Protocol Overview",
        description="Model Context Protocol: tools, resources, and prompts explained",
        mimeType="text/plain",
    ),
}

_CONTENT = {
    "local://ai-concepts/rag": """\
Retrieval-Augmented Generation (RAG)
=====================================
RAG enhances LLM responses by retrieving relevant context from a knowledge base
before generating an answer, reducing hallucinations and grounding answers in data.

Key components:
  1. Document Loader  – ingests source documents (PDFs, web pages, databases)
  2. Text Splitter    – chunks documents into manageable pieces
  3. Embeddings       – converts text to dense vectors for similarity search
  4. Vector Store     – stores and retrieves document embeddings (e.g. FAISS, Chroma)
  5. Retriever        – finds the most relevant chunks for a given query
  6. LLM              – generates the final answer using retrieved context

LangChain RAG example:
  from langchain_community.vectorstores import FAISS
  from langchain_openai import OpenAIEmbeddings
  from langchain.chains import RetrievalQA

  vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
  qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
  answer = qa_chain.invoke({"query": "What is LangChain?"})
""",
    "local://ai-concepts/agents": """\
AI Agents
=========
An agent lets an LLM decide which tools to call, in what order, to complete a task.

ReAct pattern (Reason + Act):
  1. Think   – the LLM reasons about what to do next
  2. Act     – it calls a tool with arguments
  3. Observe – it reads the tool result
  4. Repeat until the task is done or a final answer is produced

LangChain agent components:
  - LLM            : the reasoning engine (e.g. gpt-4o-mini)
  - Tools          : functions the agent can call (search, calculator, APIs, MCP)
  - Memory         : conversation history / scratchpad
  - Agent Executor : orchestrates the think-act-observe loop

Quick start:
  from langchain.agents import create_react_agent, AgentExecutor
  from langchain_core.tools import tool

  @tool
  def add(a: int, b: int) -> int:
      "Add two numbers."
      return a + b

  agent = create_react_agent(llm, tools=[add], prompt=prompt)
  executor = AgentExecutor(agent=agent, tools=[add])
  executor.invoke({"input": "What is 3 + 5?"})
""",
    "local://ai-concepts/mcp": """\
Model Context Protocol (MCP)
=============================
MCP is an open standard that lets AI agents connect to external systems
using a single consistent protocol — like a USB-C port for AI integrations.

Three capability types a server can expose:
  • Tools      – functions the AI can call  (e.g. search_docs, send_email)
  • Resources  – read-only data for context (e.g. files, database rows, this file!)
  • Prompts    – reusable prompt templates stored server-side

Transport options:
  • stdio  – subprocess via stdin/stdout (local servers, like this one)
  • http   – streamable HTTP (remote servers, like langchain-docs)
  • sse    – Server-Sent Events (legacy remote servers)

Note: Not all servers implement all three capabilities.
  langchain-docs exposes Tools only.
  This local server exposes Resources only.
  A full-featured server can expose all three.

LangChain integration:
  from langchain_mcp_adapters.client import MultiServerMCPClient
  client = MultiServerMCPClient({
      "remote": {"transport": "http", "url": "https://example.com/mcp"},
      "local":  {"transport": "stdio", "command": "python", "args": ["server.py"]},
  })
  tools     = await client.get_tools()      # merged from all servers
  resources = await client.get_resources()  # merged from all servers
""",
}


@app.list_tools()
async def list_tools():
    # This server exposes resources only, not tools.
    # Returning an empty list lets MultiServerMCPClient call get_tools()
    # across all servers without hitting "Method not found".
    return []


@app.list_resources()
async def list_resources():
    return list(_RESOURCES.values())


@app.read_resource()
async def read_resource(uri):
    # Pydantic may normalise the URI (e.g. add a trailing slash), so strip it.
    uri_str = str(uri).rstrip("/")
    if uri_str in _CONTENT:
        # Return a plain string — the mcp library wraps it in TextContent internally.
        return _CONTENT[uri_str]
    raise ValueError(f"Unknown resource URI: {uri_str!r}. Available: {list(_CONTENT.keys())}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
