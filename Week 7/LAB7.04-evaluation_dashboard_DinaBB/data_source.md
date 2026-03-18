# Data Source Documentation

**Option chosen:** Option B — Generated sample evaluation data

The dataset was generated using `generate_evaluation_data.py`, which produces synthetic but realistic LLM evaluation scores across five categories (reasoning, knowledge, code, instruction_following, tool_calling) and four model versions (gpt-4, gpt-4-turbo, gpt-3.5-turbo, claude-3-opus) over a fixed 90-day window (2025-12-19 to 2026-03-18).

Score distributions are intentionally category-specific using beta distributions to simulate real-world evaluation patterns — for example, reasoning scores skew lower and more variable, while instruction_following scores skew higher — making the data meaningful for stakeholder communication and visual storytelling.
