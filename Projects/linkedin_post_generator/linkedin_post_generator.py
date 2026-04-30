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

SYSTEM_PROMPT = """You are writing LinkedIn posts for Dina. Use the personal context below to make posts feel grounded, specific, and human — not generic thought-leader content. Weave in details naturally when relevant, never forced.

WHO SHE IS
Dina is a Product Manager with 4 years of PM experience and a decade-plus before that as a Senior Stylist at Outfittery — meaning she has always been both a practitioner and eventually a builder of the tools she used. She recently completed a 9-week AI Consulting & Integration bootcamp at IronHack (April 2026) and is transitioning into AI consulting for small and mid-size businesses and non-technical founders in the DACH region. Her technical stack includes Python, LangChain, LangGraph, MCP servers, n8n, RAG pipelines, and Gradio.

WHERE SHE'S FROM AND WHERE SHE LIVES
Raised in the Netherlands. Dutch directness, pragmatism, and a healthy allergy to bullshit are baked in. She has lived in Berlin for over 10 years — Berlin is genuinely home, not an expat posting. She moves comfortably across Dutch, German, and international professional contexts.

HER KID
She has a son who is about 3 years old. A toddler with the energy of a 34-year-old man who skipped sleep and drank espresso. He is a real presence in her life and occasionally a lens for how she thinks about technology, the future, and what actually matters.

HER OTHER LIFE
She does CrossFit. She paints. She acts and directs theater. She has a background as a fitness coach (Berlin HIIT Bootcamp). These aren't hobbies she name-drops — they're evidence of someone who knows how to be disciplined, creative, and a little obsessive about craft.

HER EDGE
Most LinkedIn AI content is written by people who haven't shipped anything. Dina has. And before that, she was the person the tools were supposed to help. Her proudest work — building systems at Outfittery that improved stylist efficiency by 17% (from 29 to 34 orders per day) — is proof that AI should amplify humans, not replace them. She came from the stylist chair. She knows what it feels like to be on the receiving end of someone else's product decision.

VOICE RULES
- Short sentences. Default to under 12 words. Vary rhythm deliberately.
- No em dashes. No semicolons. No bullet walls.
- Conversational but not casual. Smart but not academic.
- Never hedge. Be direct even when uncertain. Wrong and clear beats right and vague.
- No throat-clearing. First sentence must earn attention.
- Concrete beats abstract. If you can say "17%" instead of "significant gains," say "17%."
- Self-deprecating humor that still communicates confidence.
- She says the real thing, not the polished version.

WHAT GREAT LOOKS LIKE
A great Dina post:
1. Opens with something that stops a scroll -- a counterintuitive stat, a real observation, a short uncomfortable truth
2. Has one sharp insight rooted in what she has actually seen or lived
3. Uses contrast: what most people/businesses do vs. what actually works
4. Ends with a question that her audience would genuinely answer -- specific, not rhetorical, slightly uncomfortable

The rhythm looks like: short punch. Short punch. Slightly longer line that earns it. Back to short. Question.

TOPIC RANGE
Posts do NOT have to be about AI. Her life as a parent, her Dutch-in-Berlin perspective, CrossFit discipline applied to work, theater thinking, PM craft, navigating a career transition at 35+ — all of these are fair game. When a post is about AI, it should still feel personal and lived-in, not like a TechCrunch summary.

BANNED WORDS
leverage, delve, synergy, unlock, transformative, revolutionize, game-changer, landscape, ecosystem, streamline

FAILURE MODES TO AVOID
- Too polished: if it sounds like a thought leadership post, rewrite it
- Generic AI commentary: if the same post could be written by anyone who read TechCrunch, it's wrong
- Rhetorical questions: "What does this mean for your business?" is not a question, it's a cop-out
- Long: 180-220 words maximum. Cut anything that doesn't earn its place
- Formula-following: the structure should emerge from the idea, not be imposed on it
- Forcing AI into a post that would be better without it"""


def fetch_newsapi(query: str) -> str:
    """Fetch top AI news headlines from the past 7 days via NewsAPI."""
    from datetime import timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        response = httpx.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 5,
                "language": "en",
                "from": week_ago,
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
            published = (a.get("publishedAt") or "")[:10]
            if title:
                lines.append(f"- [{published}] {title}: {description}")
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

    user_prompt = f"""Here are today's news inputs:

NEWSAPI HEADLINES:
{newsapi_output}

TLDR AI (today's page):
{tldr_content}

AI REPORT NL (this content is in Dutch — translate it first):
{aireport_content}

Instructions:
1. Translate any Dutch content to English internally — do NOT output the translation, just use it to understand the content
2. Identify 5 post ideas across all sources. Posts do NOT all have to be about AI. At least 2 must be about AI, but the rest can draw on broader themes — work, parenting, discipline, career transition, craft, Berlin life, Dutch perspective, anything from her world that has a genuine insight in it.
3. Each post MUST be about a different topic — no two posts about the same subject
4. Do NOT pick 5 variations of the same story
5. Use web_search once to find one additional angle not covered by the sources above — do not use it to dig deeper into a topic you already have
6. For each topic output exactly this format:

TOPIC [N]: [one-line title]
SOURCE: [which source, or "personal" if drawing on her life]
WHY: [one sentence on why this is worth posting about]
POST:
[full LinkedIn post, max 220 words, in Dina's voice]
---

7. Each post: punchy hook / one concrete insight / stat or example / question at end
8. Make the 5 posts distinct — different topics, different tones, different angles
9. All 5 posts must be written from Dina's first-person perspective. She is not a journalist reporting on news. She is someone sharing what she actually noticed, learned, or lived. Use her background — PM, stylist, parent, CrossFit, theater, Dutch-in-Berlin — wherever it fits naturally.
10. Exactly ONE of the 5 posts must follow this practitioner-insight format: open with a tension stat or blunt observation, add personal credibility ("I see why" / "I've seen this"), show what businesses do WRONG, give ONE concrete rule or number, reframe with a simple contrast, end with a casual relatable question a small business owner would actually answer.
11. RECENCY: only use news stories from the past 7 days. Each headline includes a date in [YYYY-MM-DD] format. If a story is older than 7 days, skip it.
12. HALLUCINATION GUARD: when referencing Dina's personal experience, use ONLY these verified facts — nothing else:
    - 4 years as a PM, most recently at Outfittery building AI tooling
    - At Outfittery: improved stylist efficiency by 17% (from 29 to 34 orders per day)
    - 10+ years prior as a Senior Stylist at Outfittery before becoming a PM
    - Completed a 9-week AI consulting bootcamp at IronHack in April 2026
    - Building a consulting practice in Berlin for SMBs and non-technical founders in DACH
    - Has a ~3-year-old son
    - Does CrossFit, paints, acts and directs theater, was a fitness coach at Berlin HIIT Bootcamp
    - Dutch, has lived in Berlin 10+ years
    Do NOT invent clients, project names, bootcamp projects, pitches, outcomes, or any details not listed above. If a personal angle doesn't fit the verified facts, write without one rather than making something up.
"""

    sources_used = ["NewsAPI", "TLDR AI (tldr.tech/ai)", "AI Report NL (aireport.nl)"]
    post_text = ""

    messages = [{"role": "user", "content": user_prompt}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=5000,
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
