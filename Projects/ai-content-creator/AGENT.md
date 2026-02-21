# AI Content Creator - Agent Context

## Project Structure
- `src/` - Python source code
- `knowledge_base/primary/` - Brand guidelines, product specs, past content
- `knowledge_base/secondary/` - Market trends, competitor analysis
- `config/vscode_agent.json` - Agent configuration
- `templates/` - Prompt templates

## Key Files
- [src/main.py](src/main.py) - Entry point
- [src/content_pipeline.py](src/content_pipeline.py) - Pipeline orchestration
- [src/llm_integration.py](src/llm_integration.py) - LLM API wrapper
- [config/vscode_agent.json](config/vscode_agent.json) - Configuration

## Environment
- Python virtual environment in `venv/`
- API keys in `.env` file
- Dependencies in `requirements.txt`
