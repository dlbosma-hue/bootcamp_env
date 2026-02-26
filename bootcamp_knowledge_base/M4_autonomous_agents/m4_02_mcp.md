# LAB M4.02 - MCP (Model Context Protocol) Setup

## What is MCP?
MCP stands for Model Context Protocol. It gives an AI assistant (Claude, Cursor) the ability to reach outside its chat window and interact with real systems - like your file system, the web, or external APIs.

Without MCP: Claude can only work with text you paste into the chat.
With MCP: Claude can read files on your computer, list directories, create and edit files directly.

Think of MCP as giving your AI assistant hands to reach out and touch the real world.

## Two Config Locations (macOS)
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Code: `~/.claude/mcp-servers.json`

These are separate files. Claude Code manages its own config independently.

## The Config File Format
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourusername/bootcamp_env"
      ]
    }
  }
}
```

Key fields:
- `command`: always `npx` for Node.js-based MCP servers
- `args[0]`: `-y` means "yes, install if not found"
- `args[1]`: the npm package name of the MCP server
- `args[2]`: the directory path the server is allowed to access

## Setup Steps (macOS)
1. Verify Node.js is installed: `node --version`
2. Create the config folder if it does not exist: `mkdir -p ~/Library/Application\ Support/Claude/`
3. Create the config JSON file with the correct format
4. Restart Claude Desktop or Claude Code
5. Test by asking: "What MCP tools are available?"

## The 8 Filesystem Tools Available After Setup
- `read_file` - read contents of a file
- `write_file` - create or overwrite a file
- `list_directory` - list files in a folder
- `create_directory` - make a new folder
- `move_file` - rename or move a file
- `delete_file` - remove a file
- `search_files` - find files by name pattern
- `get_file_info` - get metadata about a file (size, modified date)

All tools are scoped to the directory specified in the config. Claude cannot access anything outside that path.

## MCP + LangChain Integration
```python
from langchain_mcp_adapters import MultiServerMCPClient

client = MultiServerMCPClient({
    "langchain-docs": {
        "url": "https://mcp.langchain.com/docs",
        "transport": "streamable_http"
    }
})

tools = await client.get_tools()
agent = create_react_agent(llm, tools)
```

## Troubleshooting Encountered
- Config folder did not exist on fresh macOS install - had to create it manually
- Claude Code created its own config at `~/.claude/mcp-servers.json` separate from Claude Desktop
- Python 3.14 required compatibility patches for `sniffio` and `anyio` libraries

## Key Learning
MCP is the bridge between AI assistants and real-world systems. The config file tells the AI: "here is what you are allowed to touch." Security is built in by scoping to a specific directory.
