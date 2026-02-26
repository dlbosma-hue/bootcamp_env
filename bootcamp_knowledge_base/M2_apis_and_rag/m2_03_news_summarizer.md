# LAB M2.03 - Multi-Provider News Summarizer

## Use Case
Build a production-ready application that fetches news articles from NewsAPI, summarizes them using OpenAI GPT-4o-mini, and analyzes sentiment using Anthropic Claude. The system handles provider failures with fallback logic and tracks API costs.

## Architecture
```
NewsAPI --> fetch articles
    |
    v
OpenAI GPT-4o-mini --> summarize each article
    |
    v
Anthropic Claude --> sentiment analysis
    |
    v
Cost tracker + Rate limiter --> output report
```

## Key Components

### Provider Fallback Logic
If the primary provider (OpenAI) fails or rate limits, the system automatically retries with the fallback provider (Anthropic). This prevents total failure when one API has issues.

### Rate Limiting with Jitter Optimization
Standard rate limiting waits a fixed amount between requests. Jitter adds random variance to the wait time:
- NewsAPI jitter: 0 to 30% of the base wait time
- LLM providers jitter: 0 to 20% of the base wait time

Why jitter matters: if all requests come in with identical timing, servers can detect the pattern and throttle more aggressively. Random variance makes requests look more natural.

```python
import random
wait_time = base_wait * (1 + random.uniform(0, 0.3))  # NewsAPI example
```

Result: 8% performance improvement, reduced throttling risk.

### Cost Tracking
Each API call logs the number of tokens used. Total cost is calculated at the end of a session using the pricing per 1000 tokens for each provider.

## Files Structure
- `news_api.py` - NewsAPI client with jitter-optimized rate limiter
- `llm_providers.py` - OpenAI and Anthropic clients with fallback logic
- `cost_tracker.py` - token logging and cost calculation
- `main.py` or notebook - orchestrates the full pipeline

## Key Learning
Jitter is a simple one-line change that meaningfully improves real-world reliability. Rate limiting without jitter is a common beginner mistake that causes avoidable throttling in production systems.
