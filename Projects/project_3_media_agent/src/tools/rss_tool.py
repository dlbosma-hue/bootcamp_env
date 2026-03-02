# rss_tool.py
# Tool 4: RSS Feed Analyser - Primary Source Evidence
#
# Part of the Media Diversity Watch autonomous research agent.
# Fetches articles directly from each outlet's RSS feed and
# analyses them for inclusivity signals.
#
# This is primary source evidence -- we read what the outlet
# actually publishes today, not what others say about them.
# No API key required. Completely free and legal.
#
# Target outlets: Al Jazeera English, The Guardian, CNN, New York Times

import re
import time

import feedparser
import requests
from langchain.tools import tool

_HEADERS = {"User-Agent": "MediaDiversityWatch/1.0 (research agent; contact@mediadiversitywatch.org)"}


def _fetch_article_text(url: str, max_chars: int = 600) -> str:
    """Fetch plain text from an article URL. Returns empty string on any failure."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=5)
        resp.raise_for_status()
        # Strip HTML tags and collapse whitespace
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception:
        return ""

# RSS feed URLs for our 4 monitored outlets
RSS_FEEDS = {
    "al jazeera":         "https://www.aljazeera.com/xml/rss/all.xml",
    "al jazeera english": "https://www.aljazeera.com/xml/rss/all.xml",
    "the guardian":       "https://www.theguardian.com/world/rss",
    "guardian":           "https://www.theguardian.com/world/rss",
    "cnn":                "http://rss.cnn.com/rss/edition.rss",
    "new york times":     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "nyt":                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
}

# Keywords organised by community for coverage scanning
INCLUSIVITY_KEYWORDS = {
    "women": [
        "women", "woman", "gender", "female", "feminist",
        "sexism", "maternity", "gender pay gap"
    ],
    "lgbtq": [
        "lgbtq", "gay", "lesbian", "transgender", "trans",
        "nonbinary", "queer", "pride", "same-sex"
    ],
    "race": [
        "race", "racial", "racism", "black", "asian",
        "hispanic", "latino", "diversity", "ethnicity",
        "minority", "indigenous"
    ],
    "disability": [
        "disability", "disabled", "wheelchair", "deaf",
        "blind", "neurodiversity", "autism", "accessibility"
    ]
}

# Language patterns that suggest non-inclusive framing
PROBLEMATIC_LANGUAGE = [
    "illegal alien", "illegal immigrant", "suffers from",
    "confined to wheelchair", "born a", "biological male",
    "biological female", "admits to being", "claims to be"
]


@tool
def analyse_rss_feed(company: str) -> str:
    """
    Fetch and analyse the RSS feed of a media company directly.
    Use this to get primary source evidence of what the company
    is actually publishing today. Returns byline analysis,
    community coverage counts, language flags, and article samples.
    Always call this tool when researching any of our 5 monitored outlets.
    """

    # Find the feed URL for this company
    company_key = company.lower().strip()
    feed_url = None
    for key, url in RSS_FEEDS.items():
        if key in company_key or company_key in key:
            feed_url = url
            break

    if not feed_url:
        return (
            f"No RSS feed configured for '{company}'. "
            f"Monitored outlets: {list(RSS_FEEDS.keys())}"
        )

    # Fetch with retry logic (up to 3 attempts)
    feed = None
    MAX_RETRIES = 3
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[RSS] Attempt {attempt}: fetching {feed_url}")
            feed = feedparser.parse(feed_url)
            if feed.entries:
                print(f"[RSS] Success: {len(feed.entries)} articles retrieved")
                break
            else:
                print(f"[RSS] Empty feed on attempt {attempt}")
        except Exception as e:
            print(f"[RSS] Error on attempt {attempt}: {e}")
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)

    if not feed or not feed.entries:
        return f"Could not retrieve RSS feed for '{company}' after {MAX_RETRIES} attempts."

    # Parse articles (last 30)
    articles = []
    for entry in feed.entries[:30]:
        author = getattr(entry, "author", getattr(entry, "dc_creator", "Unknown"))
        description = getattr(entry, "summary", getattr(entry, "description", ""))
        url = getattr(entry, "link", "")

        # If RSS summary is thin (<150 chars), fetch full article text
        if len(description) < 150 and url:
            fetched = _fetch_article_text(url)
            if fetched:
                description = fetched

        category = "Uncategorised"
        if hasattr(entry, "tags") and entry.tags:
            category = entry.tags[0].get("term", "Uncategorised")
        articles.append({
            "title":       getattr(entry, "title", "No title"),
            "author":      author,
            "description": description,
            "category":    category,
            "url":         url,
            "published":   getattr(entry, "published", "Unknown date")
        })

    # Byline analysis
    known_authors  = [a["author"] for a in articles if a["author"] != "Unknown"]
    unique_authors = list(set(known_authors))
    unknown_count  = sum(1 for a in articles if a["author"] == "Unknown")

    # Community coverage scan
    community_hits = {c: [] for c in INCLUSIVITY_KEYWORDS}
    for article in articles:
        full_text = (article["title"] + " " + article["description"]).lower()
        for community, keywords in INCLUSIVITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in full_text:
                    community_hits[community].append({
                        "keyword": keyword,
                        "title":   article["title"],
                        "url":     article["url"]
                    })
                    break  # one hit per article per community

    # Language flag scan
    language_flags = []
    for article in articles:
        full_text = (article["title"] + " " + article["description"]).lower()
        for phrase in PROBLEMATIC_LANGUAGE:
            if phrase in full_text:
                language_flags.append({
                    "phrase": phrase,
                    "title":  article["title"],
                    "url":    article["url"]
                })

    # Build result string
    lines = [
        f"PRIMARY SOURCE ANALYSIS: {company} RSS Feed",
        f"Source: {feed_url}",
        f"Articles analysed: {len(articles)}",
        "",
        "=== BYLINE ANALYSIS ===",
        f"Known authors: {len(known_authors)} | Unknown/missing bylines: {unknown_count}",
        f"Unique author names: {len(unique_authors)}",
        f"Names found: {', '.join(unique_authors[:15]) if unique_authors else 'None detected'}",
        "",
        "=== COMMUNITY COVERAGE ==="
    ]

    for community, hits in community_hits.items():
        lines.append(f"{community.upper()}: {len(hits)} articles mention this community")
        for h in hits[:3]:
            lines.append(f"  - {h['title']}")
            lines.append(f"    {h['url']}")

    lines += [
        "",
        "=== LANGUAGE FLAGS ===",
        f"{len(language_flags)} potentially non-inclusive terms detected"
        if language_flags else "No problematic language detected in headlines."
    ]
    for flag in language_flags[:5]:
        lines.append(f"  Term '{flag['phrase']}' found in: '{flag['title']}'")
        lines.append(f"  {flag['url']}")

    lines += ["", "=== MOST RECENT 5 ARTICLES ==="]
    for article in articles[:5]:
        lines.append(f"Title:    {article['title']}")
        lines.append(f"Author:   {article['author']} | {article['published']}")
        lines.append(f"Category: {article['category']}")
        lines.append(f"URL:      {article['url']}")
        lines.append("")

    return "\n".join(lines)
