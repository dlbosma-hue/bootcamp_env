"""
local_mcp_server_full.py

Full-featured MCP server (stdio transport) that exposes:
  - Tools   : estimate_tokens, chunk_text, format_prompt
  - Prompts : summarise_topic, explain_concept, compare_tools

Tools are LLM-dev utilities — tasks you'd commonly need when building
LangChain apps (token budgeting, RAG chunking, prompt templating).

Used in LAB3.03 Step 6b to demonstrate a server with Tools + Prompts,
complementing local_mcp_server.py (Resources only).

Three-server architecture:
  langchain-docs  → HTTP (remote) → Tools only  (docs search)
  local-resources → stdio (local) → Resources only  (AI concept notes)
  local-full      → stdio (local) → Tools + Prompts  ← this file
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    GetPromptResult,
)

app = Server("local-full")


# ── Tools ──────────────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="estimate_tokens",
            description=(
                "Estimate the number of GPT tokens in a text string. "
                "Uses the ~4 chars/token rule of thumb (English text)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to estimate tokens for"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="chunk_text",
            description=(
                "Split a text into overlapping chunks by character count. "
                "Useful for RAG document preparation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to split into chunks",
                    },
                    "chunk_size": {
                        "type": "number",
                        "description": "Max characters per chunk (default: 200)",
                    },
                    "overlap": {
                        "type": "number",
                        "description": "Overlap in characters between chunks (default: 20)",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="format_prompt",
            description=(
                "Fill a prompt template that uses {variable} placeholders. "
                "Pass the template string and variables as a JSON string. "
                'Example: template="Hello {name}!", variables=\'{"name": "Alice"}\''
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "description": "Prompt template with {variable} placeholders",
                    },
                    "variables": {
                        "type": "string",
                        "description": 'JSON string of key-value pairs, e.g. \'{"domain": "LangChain", "topic": "agents"}\'',
                    },
                },
                "required": ["template", "variables"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "estimate_tokens":
        text = str(arguments["text"])
        # ~4 characters per token is the standard GPT rule of thumb for English
        estimated = max(1, len(text) // 4)
        word_count = len(text.split())
        result = (
            f"Estimated tokens: ~{estimated}\n"
            f"(Based on {len(text)} characters, {word_count} words; "
            f"rule: 1 token ≈ 4 chars)"
        )

    elif name == "chunk_text":
        text       = str(arguments["text"])
        chunk_size = int(arguments.get("chunk_size", 200))
        overlap    = int(arguments.get("overlap", 20))

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            if start >= len(text):
                break

        lines = [f"Total chunks: {len(chunks)}\n"]
        for i, chunk in enumerate(chunks, 1):
            lines.append(f"Chunk {i} (chars {(i-1)*(chunk_size-overlap)}-{min(len(text), (i-1)*(chunk_size-overlap)+chunk_size)}):\n  {chunk!r}")
        result = "\n".join(lines)

    elif name == "format_prompt":
        import json
        template      = str(arguments["template"])
        variables_raw = arguments.get("variables", "{}")
        # Accept either a JSON string (expected) or a dict (fallback)
        if isinstance(variables_raw, dict):
            variables = variables_raw
        else:
            try:
                variables = json.loads(str(variables_raw))
            except (json.JSONDecodeError, ValueError):
                variables = {}
        try:
            result = template.format_map(variables)
        except KeyError as e:
            result = f"Error: missing variable {e} in template.\nTemplate: {template!r}\nProvided: {list(variables.keys())}"

    else:
        raise ValueError(f"Unknown tool: {name!r}")

    return [TextContent(type="text", text=result)]


# ── Prompts ────────────────────────────────────────────────────────────────

@app.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="summarise_topic",
            description="Generate a concise summary prompt for any AI/ML topic",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="The topic to summarise",
                    required=True,
                ),
                PromptArgument(
                    name="length",
                    description="Desired length: short | medium | detailed",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="explain_concept",
            description="Beginner-friendly explanation prompt for a concept",
            arguments=[
                PromptArgument(
                    name="concept",
                    description="The concept to explain",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="compare_tools",
            description="Structured side-by-side comparison prompt for two tools or frameworks",
            arguments=[
                PromptArgument(
                    name="tool_a",
                    description="First tool or framework",
                    required=True,
                ),
                PromptArgument(
                    name="tool_b",
                    description="Second tool or framework",
                    required=True,
                ),
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None):
    args = arguments or {}

    if name == "summarise_topic":
        topic  = args.get("topic", "the topic")
        length = args.get("length", "medium")
        text = (
            f"Please provide a {length} summary of {topic}. "
            "Focus on key concepts, practical applications, and why it matters. "
            "Use bullet points for clarity."
        )

    elif name == "explain_concept":
        concept = args.get("concept", "the concept")
        text = (
            f"Explain {concept} as if I am a beginner developer. "
            "Start with a simple real-world analogy, then explain it technically, "
            "then show a short code example."
        )

    elif name == "compare_tools":
        tool_a = args.get("tool_a", "Tool A")
        tool_b = args.get("tool_b", "Tool B")
        text = (
            f"Compare {tool_a} and {tool_b} side by side. "
            "Cover: purpose, strengths, weaknesses, when to use each, "
            "and a quick code example for both. Format as a table where possible."
        )

    else:
        raise ValueError(f"Unknown prompt: {name!r}")

    return GetPromptResult(
        description=f"Prompt: {name}",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ],
    )


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
