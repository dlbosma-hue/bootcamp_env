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
# Target outlets: Al Jazeera English, The Guardian, NPR, New York Times

import os
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
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception:
        return ""


def _analyse_guardian_api(n: int = 30) -> str:
    """
    Fetch The Guardian's latest articles via the Open Platform API.
    Returns full body text, bylines, and section names — far richer than RSS.
    Used automatically when company is The Guardian.
    """
    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        return None  # fall through to RSS

    try:
        resp = requests.get(
            "https://content.guardianapis.com/search",
            params={
                "api-key": api_key,
                "show-fields": "bodyText,byline,trailText",
                "show-tags": "keyword",
                "page-size": n,
                "order-by": "newest",
            },
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("response", {}).get("results", [])
    except Exception:
        return None

    if not results:
        return None

    articles = []
    for r in results:
        fields = r.get("fields", {})
        body = fields.get("bodyText", fields.get("trailText", ""))
        articles.append({
            "title":       r.get("webTitle", "No title"),
            "author":      fields.get("byline", "Unknown"),
            "description": body[:800],  # first 800 chars of full article body
            "category":    r.get("sectionName", "Uncategorised"),
            "url":         r.get("webUrl", ""),
            "published":   r.get("webPublicationDate", "Unknown date"),
        })

    # Byline analysis
    known_authors = [a["author"] for a in articles if a["author"] != "Unknown"]
    unique_authors = list(set(known_authors))
    unknown_count = sum(1 for a in articles if a["author"] == "Unknown")

    # Community coverage scan
    community_hits = {c: [] for c in INCLUSIVITY_KEYWORDS}
    for article in articles:
        full_text = (article["title"] + " " + article["description"]).lower()
        for community, keywords in INCLUSIVITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in full_text:
                    community_hits[community].append({
                        "keyword": keyword,
                        "title": article["title"],
                        "url": article["url"],
                    })
                    break

    # Language flag scan
    language_flags = []
    for article in articles:
        full_text = (article["title"] + " " + article["description"]).lower()
        for phrase in PROBLEMATIC_LANGUAGE:
            if phrase in full_text:
                language_flags.append({"phrase": phrase, "title": article["title"], "url": article["url"]})

    lines = [
        "PRIMARY SOURCE ANALYSIS: The Guardian (Guardian Open Platform API)",
        "Source: content.guardianapis.com — full article body text",
        f"Articles analysed: {len(articles)}",
        "",
        "=== BYLINE ANALYSIS ===",
        f"Known authors: {len(known_authors)} | Unknown/missing bylines: {unknown_count}",
        f"Unique author names: {len(unique_authors)}",
        f"Names found: {', '.join(unique_authors[:15]) if unique_authors else 'None detected'}",
        "",
        "=== COMMUNITY COVERAGE ===",
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
        if language_flags else "No problematic language detected in headlines or article text.",
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


# RSS feed URLs for our 4 monitored outlets
RSS_FEEDS = {
    "al jazeera":         "https://www.aljazeera.com/xml/rss/all.xml",
    "al jazeera english": "https://www.aljazeera.com/xml/rss/all.xml",
    "the guardian":       "https://www.theguardian.com/world/rss",
    "guardian":           "https://www.theguardian.com/world/rss",
    "npr":                "https://feeds.npr.org/1001/rss.xml",  # fallback if multi-feed fails
    "new york times":     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "nyt":                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
}

# NPR publishes multiple limited-article feeds (~10 each).
# Combine topic feeds to reach a sample size comparable to other outlets.
_NPR_FEEDS = [
    "https://feeds.npr.org/1001/rss.xml",    # News / Top Stories
    "https://feeds.npr.org/1003/rss.xml",    # Politics
    "https://feeds.npr.org/1008/rss.xml",    # Business
    "https://feeds.npr.org/1025/rss.xml",    # Race
    "https://feeds.npr.org/2101254/rss.xml", # Health
]


def _fetch_npr_combined(n: int = 30) -> list:
    """
    Fetch from multiple NPR topic feeds and return up to n unique entries.
    Deduplicates by article URL so no story appears twice.
    Returns raw feedparser entry objects — identical interface to feed.entries.
    """
    seen_urls: set = set()
    combined: list = []
    for feed_url in _NPR_FEEDS:
        if len(combined) >= n:
            break
        try:
            print(f"[RSS/NPR] Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                entry_url = getattr(entry, "link", "")
                if entry_url and entry_url not in seen_urls:
                    seen_urls.add(entry_url)
                    combined.append(entry)
                    if len(combined) >= n:
                        break
        except Exception as e:
            print(f"[RSS/NPR] Failed {feed_url}: {e}")
            continue
    print(f"[RSS/NPR] Combined: {len(combined)} unique articles from {len(_NPR_FEEDS)} feeds")
    return combined[:n]

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
    Always call this tool when researching any of our 4 monitored outlets.
    """

    # Route Guardian requests through the Open Platform API for full article text
    company_key = company.lower().strip()
    if "guardian" in company_key:
        guardian_result = _analyse_guardian_api()
        if guardian_result:
            return guardian_result
        # fall through to RSS if API key missing or call fails

    # Route NPR through multi-feed combiner (individual feeds return ~10 articles each)
    if "npr" in company_key:
        raw_entries = _fetch_npr_combined(n=30)
        if not raw_entries:
            return "Could not retrieve any NPR RSS feeds after trying all configured sources."
        feed_url = f"NPR combined ({len(_NPR_FEEDS)} topic feeds)"
    else:
        # Find the feed URL for this company
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

        raw_entries = feed.entries[:30]

    # Parse articles (up to 30 from whatever source was used above)
    articles = []
    for entry in raw_entries:
        author = getattr(entry, "author", getattr(entry, "dc_creator", "Unknown"))
        # Prefer content:encoded (full article) over summary (teaser)
        if hasattr(entry, "content") and entry.content:
            description = entry.content[0].get("value", "")[:800]
        else:
            description = getattr(entry, "summary", getattr(entry, "description", ""))
        url = getattr(entry, "link", "")

        # If still thin (<150 chars), try fetching the article URL directly
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
