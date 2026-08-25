"""
LinkedIn Post Generator
Fetches AI news from NewsAPI, Jina.ai (The Deep View archive),
and Claude web_search, then generates a post in Dina's voice and delivers it via email.
"""

import json
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
Dina runs HUMINT, an AI consulting practice based in Berlin. She works with founders, operators, and small teams at startups and SMEs to integrate AI into their operations. She has 4 years of PM experience, most recently building AI tools at Outfittery. Before that, a decade-plus as a Senior Stylist at Outfittery — meaning she has always been both a practitioner and eventually a builder of the tools she used. She recently completed a 9-week AI Consulting & Integration bootcamp at IronHack (April 2026). Her technical stack includes Python, LangChain, LangGraph, MCP servers, n8n, RAG pipelines, and Gradio.

HER CORE USP
AI should make your people faster, not fewer. This is not a moral stance — it is a practical one. Automation that sidelines people destroys the knowledge, judgment, and trust that made the team worth keeping. The goal is always: amplify what humans are already good at. This should come through naturally in posts, never as a lecture. Clients who just want efficiency gains are fine. The frame is about outcomes for people, not ideology.

WHERE SHE'S FROM AND WHERE SHE LIVES
Raised in the Netherlands. Dutch directness, pragmatism, and a healthy allergy to bullshit are baked in. She has lived in Berlin for over 10 years — Berlin is genuinely home, not an expat posting. She moves comfortably across Dutch, German, and international professional contexts.

HER KID
She has a son who is about 3 years old. A toddler with the energy of a 34-year-old man who skipped sleep and drank espresso. He is a real presence in her life and occasionally a lens for how she thinks about technology, the future, and what actually matters.

HER OTHER LIFE
She does CrossFit. She paints. She acts and directs theater. She has a background as a fitness coach (Berlin HIIT Bootcamp). These aren't hobbies she name-drops — they're evidence of someone who knows how to be disciplined, creative, and a little obsessive about craft.

HER EDGE
Most LinkedIn AI content is written by people who haven't shipped anything. Dina has. And before that, she was the person the tools were supposed to help. She came from the stylist chair. She knows what it feels like to be on the receiving end of someone else's product decision. That inside-out perspective — from practitioner to tool-builder to consultant — is what makes her take on AI integration different. Her verified proof points (use only when they fit naturally, never force them):
- 17% productivity increase at Outfittery (from 29 to 34 orders per day per stylist)
- 80% reduction in manual coordination (HUMINT consulting work)
- Spottr churn model: 92.5% accuracy
Do not invent any other numbers or outcomes.

VOICE RULES
- Short sentences. Default to under 12 words. Vary rhythm deliberately.
- No em dashes. No semicolons. No bullet walls.
- No bullet point lists in posts unless the list format genuinely adds clarity that prose cannot. Default is prose.
- No emojis unless explicitly requested.
- Conversational but not casual. Smart but not academic.
- Never hedge. Be direct even when uncertain. Wrong and clear beats right and vague.
- No throat-clearing. First sentence must earn attention.
- Concrete beats abstract. Use real numbers from the sources when they exist. Never invent a stat.
- Self-deprecating humor that still communicates confidence.
- Practitioner voice, not thought leader voice. Write like someone who has done the work, not someone who read about it.
- She says the real thing, not the polished version.

WHAT GREAT LOOKS LIKE
A great Dina post:
1. Opens with something that stops a scroll -- a counterintuitive observation, a blunt fact from a real source, a short uncomfortable truth
2. Has one sharp insight rooted in what she has actually seen or lived
3. Uses contrast: what most people/businesses do vs. what actually works
4. Ends decisively — sometimes a question, sometimes a blunt statement, sometimes a sharp contrast. Do NOT default to a question. Questions only when they are specific and slightly uncomfortable. Never rhetorical. Never "What do you think?"

The rhythm looks like: short punch. Short punch. Slightly longer line that earns it. Back to short. Hard stop or a real question.

BILINGUAL OUTPUT (REQUIRED)
Every post is published in two languages: German first, then a "---" separator, then English. German is primary — DACH is the target audience. This is NOT a translation exercise. Write the German version fresh in Dina's voice for a German-speaking reader, then write the English version fresh in Dina's voice for an English-speaking reader — same idea, same structure, same ending type, but each one reads like it was written natively in that language, not converted. Duden-correct German, direct and punchy, same register as the English (no formal "Sie" stiffness, no corporate Denglisch). Both versions independently follow every voice rule and word-count limit above.

TOPIC RANGE AND PRIORITY
Posts come from four lenses:
1. AI CONSULTING / HUMINT (primary): what founders, operators, and small teams actually get wrong about AI integration, what it costs them, how HUMINT helps them get real operational value without waste. The frame is always: AI makes your people faster, not fewer. Not preachy — practical. Rotate the STRUCTURAL angle across posts, don't reuse the same "mistake + fix" shape every time — vary between: build vs. buy traps, tool overload, adoption ROI (or lack of it), vendor lock-in, data readiness, the skills gap when hiring for AI. Audience: this lens is read by small business owners deciding whether to work with her, AND by recruiters/hiring managers sizing up her judgment. It must read as factual, grounded in the actual news story, and demonstrate character and professionalism — never overcomplicated or jargon-heavy. A smart non-technical reader should get it in one pass.
2. PM AND PRODUCT THINKING (secondary): shipping decisions, prioritization trade-offs, what PMs get wrong, lessons from building tools people actually use — this is her craft and credibility base. Same audience note as above: factual, simple, shows professionalism to both SMB owners and recruiters.
3. PERSONAL — TODDLER CHALLENGE: the real, specific friction of raising a 3-year-old, mapped onto a current AI news story as a genuine parallel — not "here's a workflow that saves me time as a parent." Center the actual challenge (patience, unpredictability, things breaking despite planning, no clean solutions) and let the AI story illuminate it, or vice versa. Not inspirational. Concrete and specific, not a moral. Still needs a takeaway, but the takeaway can be sharp and honest rather than tidy.
4. PERSONAL — HOBBY LENS: a specific hobby (watching TV shows, reading books, CrossFit/working out, eating at restaurants, theater — acting and directing, or watching movies — never mix more than one per post) used as the entry point into an AI news story. This lens rotates which hobby it uses; the exact hobby for this run is specified in the instructions below — use that one, not a different one.

When a post is about AI, it must always be from the SMB/startup practitioner angle — not a TechCrunch summary, not a tech enthusiast take. Ask: what would a founder or small team operator need to understand from this?

BANNED WORDS AND PHRASES
Words: leverage, delve, synergy, unlock, transformative, revolutionize, game-changer, landscape, ecosystem, streamline, empower, harness, cutting-edge, robust, scalable, innovative
Phrases: "worth their weight in gold", "at the end of the day", "it's not about X it's about Y", "AI amplifies", "in today's world", "the future is", "what most people don't realize", "here's the thing", "hot take", "unpopular opinion", "let that sink in"

FAILURE MODES TO AVOID
- AI slop: generic observations that any LinkedIn ghost-writer would produce. If it sounds like ChatGPT wrote it for a thought leader, it's wrong.
- Formula-following: every post should NOT have the same structure. Vary how it opens, how it builds, how it ends.
- Mandatory question endings: ending every post with a question is a formula. Resist it. A hard statement often lands harder.
- Generic AI commentary: if the same post could be written by anyone who read a tech newsletter, it's wrong. Every post must have a specific, non-obvious angle.
- Rhetorical questions: "What does this mean for your business?" is not a question. "Are you measuring output or hours?" is.
- Long: 150-200 words maximum PER LANGUAGE VERSION. Cut anything that doesn't earn its place. Shorter is almost always better.
- Forcing personal angles: if a personal detail doesn't fit naturally, don't use it. Better to write a clean professional post than a forced "my toddler taught me about agile" post.
- Repeating topics: do not write about topics already covered in recent posts (listed below under RECENT POST HISTORY)"""


HISTORY_FILE = os.path.join(os.path.dirname(__file__), "post_history.json")
HISTORY_KEEP = 20


def load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_history(topic: str, opening_line: str, lens: str = "", sublens: str = "") -> None:
    history = load_history()
    history.insert(0, {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "opening_line": opening_line,
        "lens": lens,
        "sublens": sublens,
    })
    history = history[:HISTORY_KEEP]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def format_history_for_prompt(history: list[dict]) -> str:
    if not history:
        return "None yet."
    lines = []
    for h in history:
        tag = f" [{h['sublens']}]" if h.get("sublens") else ""
        lines.append(f"- [{h['date']}] {h['topic']}{tag} | Opening: \"{h['opening_line']}\"")
    return "\n".join(lines)


HOBBIES = ["series", "books", "fitness", "restaurants", "theater", "movies"]

HOBBY_LABELS = {
    "series": "watching TV shows",
    "books": "reading books",
    "fitness": "working out / CrossFit",
    "restaurants": "eating at restaurants",
    "theater": "acting and directing theater",
    "movies": "watching movies",
}


def determine_next_personal_lens(history: list[dict]) -> str:
    """Deterministically rotate the personal slot: alternate toddler <-> hobby,
    and within hobby, pick whichever of the 4 hasn't run in the last 3 hobby posts."""
    recent_sublens = [h.get("sublens", "") for h in history if h.get("sublens")]
    last = recent_sublens[0] if recent_sublens else None

    if last is None or last == "toddler":
        recent_hobbies = [s.split(":", 1)[1] for s in recent_sublens if s.startswith("hobby:")]
        for h in HOBBIES:
            if h not in recent_hobbies[:5]:
                return f"hobby:{h}"
        return f"hobby:{HOBBIES[0]}"
    else:
        return "toddler"


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


def fetch_deepview_latest() -> str:
    """Fetch the latest AI newsletter content from The Deep View archive via Jina.ai.
    Scrapes the archive page and fetches the most recent issue.
    """
    archive_text = fetch_jina("https://archive.thedeepview.com/")
    if archive_text.startswith("[Content unavailable"):
        return archive_text

    # The Deep View archive links follow thedeepview.com/p/<slug> pattern
    seen = set()
    urls = []
    for u in re.findall(r'https://(?:archive\.)?thedeepview\.com/p/[^\s\)\"\'\]<]+', archive_text):
        if u not in seen:
            seen.add(u)
            urls.append(u)

    if not urls:
        # Return the archive summary if no individual post links found
        return archive_text[:4000]

    latest_url = urls[0]
    print(f"  -> Fetching Deep View article: {latest_url}")
    return fetch_jina(latest_url)


def generate_post(newsapi_output: str, deepview_content: str, history: list[dict]) -> tuple[str, list[str]]:
    """Call Claude with web_search enabled. Returns (post_text, sources_used)."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    history_block = format_history_for_prompt(history)

    next_personal = determine_next_personal_lens(history)
    if next_personal == "toddler":
        personal_directive = (
            'Post 5 lens: PERSONAL — TODDLER CHALLENGE. Must be the real friction of raising a '
            '3-year-old, mapped as a genuine parallel onto one of today\'s AI news stories. '
            'Not a "here\'s a workflow that saves me time as a parent" post — that angle is retired. '
            'Not inspirational. SUBLENS tag for this post: toddler'
        )
    else:
        hobby_key = next_personal.split(":", 1)[1]
        hobby_label = HOBBY_LABELS[hobby_key]
        personal_directive = (
            f'Post 5 lens: PERSONAL — HOBBY. Must use exactly this hobby as the entry point: '
            f'{hobby_label}. Do not substitute a different hobby. Tie it to one of today\'s AI news '
            f'stories. SUBLENS tag for this post: {next_personal}'
        )

    user_prompt = f"""Here are today's news inputs:

NEWSAPI HEADLINES:
{newsapi_output}

THE DEEP VIEW (latest AI newsletter issue):
{deepview_content}

RECENT POST HISTORY (do NOT repeat these topics, opening lines, or the same structural angle):
{history_block}

Instructions:
1. Identify 5 post ideas across all sources. Distribution is fixed:
   - Posts 1-3: AI consulting lens. What this means for small businesses, startups, or non-technical founders — implementation cost, build vs. buy, adoption ROI, vendor lock-in, data readiness, or the skills gap in hiring for AI. Each of the 3 must use a DIFFERENT structural angle from this list — no two posts this run share one. This lens is read by small business owners AND recruiters — factual, grounded in the news story, shows character and professionalism, never overcomplicated.
   - Post 4: PM/product thinking angle: shipping decisions, prioritization, what PMs get wrong, lessons from building tools people actually use. Same audience note: factual, simple, professional.
   - Post 5: {personal_directive}
2. Each post MUST be a genuinely different topic — no two posts from the same story or the same angle
3. Do NOT repeat any topic, opening angle, or structural angle from RECENT POST HISTORY
4. Use web_search once to find one additional angle not covered by the sources above
5. For each topic output exactly this format. POST is bilingual: German text, then a line with just "---", then English text — this whole block is what Dina copies straight into LinkedIn, so do not add any other labels inside it.

TOPIC [N]: [one-line title]
LENS: [AI consulting / PM & product / personal-toddler / personal-hobby]
SUBLENS: [n/a for posts 1-4; for post 5 use exactly the SUBLENS tag given above]
SOURCE: [NewsAPI / The Deep View / web_search / personal]
WHY: [one sentence on why this is a non-obvious angle worth posting about]
OPENING LINE (DE): [the first sentence of the German version, standalone]
OPENING LINE (EN): [the first sentence of the English version, standalone]
POST:
[German version, max 200 words, in Dina's voice — not a translation]

---

[English version, max 200 words, in Dina's voice — not a translation]
===

6. Each post must have a punchy hook and one concrete insight. Endings vary: hard statement, blunt observation, or — only when genuinely useful — a specific non-rhetorical question. Do NOT end every post with a question. No two posts should end the same way. Both language versions of a post must end the same way as each other (same ending type).
7. All 5 posts from Dina's first-person perspective. Use her background only when it fits naturally — do not force it.
8. Anti-slop check: before finalising each post, ask "could this have been written by a generic LinkedIn ghostwriter?" If yes, rewrite it. Every post needs a specific, non-obvious angle that only someone who has actually done this work would notice.
9. RECENCY: only use news stories from the past 7 days. Each headline includes a date in [YYYY-MM-DD] format. Skip anything older.
10. HALLUCINATION GUARD — no exceptions:
    a) PERSONAL FACTS: use ONLY these verified facts about Dina:
       - Runs HUMINT, an AI consulting practice in Berlin for founders, operators, and small teams at startups and SMEs
       - 4 years as a PM, most recently at Outfittery building AI tooling
       - 10+ years prior as a Senior Stylist at Outfittery before becoming a PM
       - Completed a 9-week AI consulting bootcamp at IronHack in April 2026
       - Has a ~3-year-old son
       - Does CrossFit, paints, acts and directs theater, was a fitness coach at Berlin HIIT Bootcamp
       - Dutch, has lived in Berlin 10+ years
       Verified proof points (use only when natural, never force):
       - 17% productivity increase at Outfittery (from 29 to 34 orders per day per stylist)
       - 80% reduction in manual coordination (HUMINT consulting work)
       - Spottr churn model: 92.5% accuracy
       Do NOT invent clients, project names, outcomes, or any detail not listed above.
    b) NUMBERS: every stat or specific number MUST come from NewsAPI, The Deep View, or web_search. Do not invent or estimate. No number without a source.
"""

    sources_used = ["NewsAPI", "The Deep View (archive.thedeepview.com)"]
    post_text = ""

    messages = [{"role": "user", "content": user_prompt}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
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
    history = load_history()
    print(f"[history] Loaded {len(history)} past posts.")

    print("[1/3] Fetching NewsAPI headlines...")
    newsapi_output = fetch_newsapi("artificial intelligence")

    print("[2/3] Fetching The Deep View latest issue via Jina.ai...")
    deepview_content = fetch_deepview_latest()

    print("[3/3] Generating LinkedIn post with Claude...")
    post_text, sources = generate_post(newsapi_output, deepview_content, history)

    print("\n--- GENERATED POST ---")
    print(post_text)
    print("--- END POST ---\n")

    # Extract topics, lens, sublens, and opening lines from output to save to history
    for match in re.finditer(
        r"TOPIC \[\d+\]: (.+)\n"
        r"LENS: (.+)\n"
        r"SUBLENS: (.+)\n"
        r".*?OPENING LINE \(DE\): (.+)",
        post_text,
    ):
        topic = match.group(1).strip()
        lens = match.group(2).strip()
        sublens = match.group(3).strip()
        opening = match.group(4).strip()
        sublens = "" if sublens.lower() in ("n/a", "na", "none") else sublens
        save_history(topic, opening, lens=lens, sublens=sublens)
        print(f"[history] Saved: {topic}")

    print("Sending email...")
    send_email(post_text, sources)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
