# newsapi_tool.py
# Tool 3: NewsAPI Search - What Critics and Journalists Say
#
# Part of the Media Diversity Watch autonomous research agent.
# Searches recent news articles to find what journalists, researchers,
# and critics are saying about a media outlet's diversity and
# inclusion practices.
#
# Requires NEWSAPI_KEY in .env (free tier: 100 requests/day).

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()


@tool
def search_newsapi(query: str) -> str:
    """
    Search recent news articles about a media company's diversity and
    inclusion practices, newsroom composition, editorial decisions,
    or representation controversies. Use this to find what journalists,
    researchers, and critics say about the outlet's inclusivity record.
    Returns top 5 most relevant articles from the last 30 days.
    """
    api_key = os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
    if not api_key:
        return (
            "NewsAPI key not configured. "
            "Add NEWSAPI_KEY=your_key to the .env file."
        )

    try:
        from newsapi import NewsApiClient

        client = NewsApiClient(api_key=api_key)
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        response = client.get_everything(
            q=query,
            language="en",
            sort_by="relevancy",
            from_param=from_date,
            page_size=5,
        )

        articles = response.get("articles", [])
        total = response.get("totalResults", 0)

        if not articles:
            return f"No recent news articles found for: '{query}'"

        lines = [
            f"NEWS SEARCH: '{query}'",
            f"Total results available: {total} (showing top {len(articles)})",
            "",
        ]

        for i, article in enumerate(articles, 1):
            title = article.get("title") or "No title"
            source = article.get("source", {}).get("name", "Unknown source")
            description = article.get("description") or ""
            url = article.get("url") or ""
            published = (article.get("publishedAt") or "")[:10]

            lines.append(f"{i}. [{source}] {title}")
            lines.append(f"   Published: {published}")
            if description:
                lines.append(f"   {description[:200]}")
            lines.append(f"   URL: {url}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"NewsAPI search failed: {e}"
