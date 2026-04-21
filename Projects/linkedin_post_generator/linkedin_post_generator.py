"""
LinkedIn Post Generator
Fetches AI news from NewsAPI, Jina.ai (TLDR + AIReport NL latest article),
and Claude web_search, then generates a post in Dina's voice and delivers it via email.
"""

import os
import re
import smtplib
import traceback
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import anthropic
import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NEWSAPI_KEY = os.environ["NEWSAPI_KEY"]
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]

SYSTEM_PROMPT = """You are writing LinkedIn content for Dina, a PM and AI consultant.

Context:
- Building a consulting practice targeting businesses and non-technical adults in the DACH region.
- 4 years PM experience, most recently building AI tools at Outfittery (17% stylist efficiency improvement).
- Fresh out of a 9-week AI consulting bootcamp (IronHack, 2026).
- PM-first, technical second. Don't overclaim technical depth.

Voice rules:
- Direct, punchy, zero fluff. Conversational, not corporate.
- Short sentences. No em dashes. Ever.
- Assume smart reader. No hand-holding.
- Concrete over abstract. Use metrics when possible.

LinkedIn post playbook:
- Punchy opener that stops the scroll.
- One concrete insight.
- End with a question.
- Max 220 words.

Never use: leverage, delve, synergy, unlock, transformative.
Never sound like everyone else on LinkedIn.

Known failure modes to avoid:
- Too polished — loses her voice. Keep it human.
- Hedging everything. Be wrong and clear, not right and vague.
- Making it longer than it needs to be. Cut it."""


def fetch_newsapi(query: str) -> str:
    """Fetch top AI news headlines from NewsAPI."""
    try:
        response = httpx.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
            },
            timeout=30,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])
        lines = []
        for a in articles:
            title = a.get("title", "").strip()
            description = (a.get("description") or "").strip()
            if title:
                lines.append(f"- {title}: {description}")
        return "\n".join(lines) if lines else "[No articles found]"
    except Exception as e:
        print(f"[WARN] NewsAPI fetch failed: {e}")
        return "[NewsAPI unavailable]"


def fetch_jina(url: str) -> str:
    """Fetch page content via Jina.ai reader (no API key required)."""
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = httpx.get(
            jina_url,
            headers={"Accept": "text/plain"},
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.text[:4000]
    except Exception as e:
        print(f"[WARN] Jina fetch failed for {url}: {e}")
        return f"[Content unavailable for {url}]"


def fetch_aireport_latest() -> str:
    """Fetch the latest article from AI Report NL via Jina.ai.
    Tries the RSS feed first (most reliable for recency), then falls back
    to scraping the archive page and picking the first non-featured article.
    """
    # Try RSS feed — Beehiiv newsletters expose /feed
    rss_text = fetch_jina("https://www.aireport.nl/feed")
    if not rss_text.startswith("[Content unavailable"):
        rss_urls = re.findall(r'https://www\.aireport\.nl/p/[^\s<\"\'\]]+', rss_text)
        if rss_urls:
            latest_url = rss_urls[0]
            print(f"  -> Fetching AI Report article (via RSS): {latest_url}")
            return fetch_jina(latest_url)

    # Fall back: scrape the archive page
    archive_text = fetch_jina("https://www.aireport.nl/archive")
    if archive_text.startswith("[Content unavailable"):
        return archive_text

    # Beehiiv post URLs follow /p/<slug> pattern — deduplicate, preserve order
    seen = set()
    urls = []
    for u in re.findall(r'https://www\.aireport\.nl/p/[^\s\)\"\'\]]+', archive_text):
        if u not in seen:
            seen.add(u)
            urls.append(u)

    if not urls:
        return archive_text

    # Beehiiv often pins a featured article at position 0. Try the second unique URL
    # first so we get a genuinely recent post, then fall back to the first.
    candidate_url = urls[1] if len(urls) > 1 else urls[0]
    print(f"  -> Fetching AI Report article (via archive): {candidate_url}")
    return fetch_jina(candidate_url)


def generate_post(newsapi_output: str, tldr_content: str, aireport_content: str) -> tuple[str, list[str]]:
    """Call Claude with web_search enabled. Returns (post_text, sources_used)."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = f"""Here are today's AI news inputs:

NEWSAPI HEADLINES:
{newsapi_output}

TLDR AI (today's page):
{tldr_content}

AI REPORT NL (this content is in Dutch — translate it first):
{aireport_content}

Instructions:
1. Translate any Dutch content to English internally — do NOT output the translation, just use it to understand the content
2. Identify the 3 most interesting AI topics across all sources
3. Each topic MUST come from a different company, product, or theme — no two posts about the same subject
4. Do NOT pick 3 variations of the same story
5. Use web_search once to find one additional angle not already covered by the sources above — do not use it to dig deeper into a topic you already have
6. For each topic output exactly this format:

TOPIC [N]: [one-line title]
SOURCE: [which source]
WHY: [one sentence on why this is worth posting about]
POST:
[full LinkedIn post, max 220 words, in Dina's voice]
---

7. Each post: punchy hook / one concrete insight / stat or example / question at end
8. Make the 3 posts distinct — different companies, different angles, different audiences if possible
"""

    sources_used = ["NewsAPI", "TLDR AI (tldr.tech/ai)", "AI Report NL (aireport.nl)"]
    post_text = ""

    messages = [{"role": "user", "content": user_prompt}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages,
        )

        for block in response.content:
            if hasattr(block, "text"):
                post_text += block.text

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "web_search":
                    sources_used.append(f"Claude web_search: {block.input.get('query', '')}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "",
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return post_text.strip(), sources_used


def send_email(post_text: str, sources: list[str]) -> None:
    """Send generated post via Gmail SMTP."""
    today = datetime.now().strftime("%A, %d %B %Y")
    source_list = "\n".join(f"  - {s}" for s in sources)

    body = f"""Hi Dina,

Here's your LinkedIn post for today:

---
{post_text}
---

Just copy, paste, and edit if needed. Takes 30 seconds.

Sources used today:
{source_list}
"""

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = f"Your LinkedIn post for {today}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    print(f"[OK] Email sent to {RECIPIENT_EMAIL}")


def main():
    print("[1/4] Fetching NewsAPI headlines...")
    newsapi_output = fetch_newsapi("artificial intelligence")

    print("[2/4] Fetching TLDR AI via Jina.ai...")
    tldr_content = fetch_jina("https://tldr.tech/ai")

    print("[3/4] Fetching AI Report NL latest article via Jina.ai...")
    aireport_content = fetch_aireport_latest()

    print("[4/4] Generating LinkedIn post with Claude...")
    post_text, sources = generate_post(newsapi_output, tldr_content, aireport_content)

    print("\n--- GENERATED POST ---")
    print(post_text)
    print("--- END POST ---\n")

    print("Sending email...")
    send_email(post_text, sources)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
