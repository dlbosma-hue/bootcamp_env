# wikipedia_tool.py
# Tool 2: Wikipedia Search - Company Background and Context
#
# Part of the Media Diversity Watch autonomous research agent.
# Searches Wikipedia for background information about media companies:
# ownership, editorial history, reach, notable controversies.
#
# Uses Wikipedia's free REST API — no API key required.

import requests
from langchain.tools import tool


@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for background information about a media company or topic.
    Use this to get company overview, ownership structure, editorial history,
    and organisational context. Especially useful for the Company Overview
    section of the inclusivity report. Always call this when researching
    any of our 5 monitored outlets.
    """
    try:
        # Step 1: Search for the best matching Wikipedia page
        search_resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            },
            timeout=10,
        )
        search_resp.raise_for_status()
        search_results = search_resp.json().get("query", {}).get("search", [])

        if not search_results:
            return f"No Wikipedia article found for: {query}"

        page_title = search_results[0]["title"]

        # Step 2: Fetch the plain-English summary of that page
        summary_resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(page_title)}",
            timeout=10,
        )
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()

        title = summary_data.get("title", page_title)
        extract = summary_data.get("extract", "No summary available.")[:900]
        page_url = (
            summary_data.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        )

        return (
            f"WIKIPEDIA: {title}\n"
            f"URL: {page_url}\n\n"
            f"{extract}"
        )

    except requests.RequestException as e:
        return f"Wikipedia search failed (network error): {e}"
    except Exception as e:
        return f"Wikipedia search error: {e}"
