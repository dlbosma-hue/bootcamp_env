import json
import re
import time
import random
import urllib.request
from recipe_filters import is_allowed
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_QUERIES = [
    ("https://www.chefkoch.de/rs/s0g53o3/Vegetarisch/Rezepte.html", "Mittagessen"),
    ("https://www.chefkoch.de/suche.html?query=H%C3%A4hnchen+Pfanne+schnell+gesund", "Abendessen"),
    ("https://www.chefkoch.de/suche.html?query=Lachs+Ofenrezept+schnell", "Abendessen"),
    ("https://www.chefkoch.de/suche.html?query=vegetarisch+Salat+schnell+Mittagessen", "Mittagessen"),
]

def _is_allowed(recipe: dict) -> bool:
    # No red meat / offal / shellfish / desserts, and a real protein source (see recipe_filters)
    return is_allowed(recipe)


TARGET = 10


def _accept_cookies(page):
    for sel in [
        "button[data-testid='uc-accept-all-button']",
        "button:has-text('Alle akzeptieren')",
        "button:has-text('Akzeptieren')",
        "#onetrust-accept-btn-handler",
    ]:
        try:
            btn = page.query_selector(sel)
            if btn:
                btn.click()
                time.sleep(1)
                return
        except Exception:
            pass


def _parse_time(body: str) -> int:
    match = re.search(r"Arbeitszeit\s*\n?\s*(\d+)\s*Min", body)
    total = re.search(r"Gesamtzeit\s*\n?\s*(\d+)\s*Min", body)
    if match:
        return int(match.group(1))
    if total:
        return int(total.group(1))
    return 30


def _parse_steps(body: str) -> list[str]:
    idx = body.find("Zubereitung")
    if idx < 0:
        return []
    section = body[idx + len("Zubereitung"):idx + 3000]
    steps = re.split(r"\n\d+\n", section)
    result = [s.strip() for s in steps if len(s.strip()) > 20]
    return result[:12]


def _scrape_recipe(page, url: str, default_meal_type: str) -> dict | None:
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        time.sleep(1)
        _accept_cookies(page)

        title = page.query_selector("h1")
        name = title.inner_text().strip() if title else ""
        if not name:
            return None

        body = page.inner_text("body")
        prep_time = _parse_time(body)

        # Ingredients: each tr[class*='ingredient'] contains qty + name
        ingredients = []
        for row in page.query_selector_all("tr[class*='ingredient']"):
            text = re.sub(r'\s+', ' ', row.inner_text().strip())
            if text and len(text) > 1:
                ingredients.append(text)

        if not ingredients:
            return None

        steps = _parse_steps(body)
        clean_url = url.split("#")[0].split("?ck_")[0]

        return {
            "name": name,
            "source_url": clean_url,
            "meal_type": default_meal_type,
            "prep_time_minutes": prep_time,
            "ingredients": ingredients,
            "steps": steps,
            "fertility_benefits": "",
            "calories_per_adult": 0,
            "protein_per_adult_g": 0,
            "child_adaptation": None,
            "expensive_ingredients": [],
            "source": "web",
        }
    except PlaywrightTimeoutError:
        return None


def _get_recipe_links(page, search_url: str) -> list[str]:
    try:
        page.goto(search_url, wait_until="networkidle", timeout=15000)
        time.sleep(1)
        _accept_cookies(page)
        links = set()
        for el in page.query_selector_all("a[href*='/rezepte/']"):
            href = el.get_attribute("href") or ""
            if re.match(r"https://www\.chefkoch\.de/rezepte/\d+/", href):
                links.add(href.split("#")[0].split("?ck_")[0])
        return list(links)
    except PlaywrightTimeoutError:
        return []


UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
KS_SITEMAP_INDEX = "https://www.kitchenstories.com/sitemap_index.xml"
MAX_TIME_MIN = 35
LUNCH_HINTS = ("salat", "suppe", "bowl", "wrap", "sandwich", "eintopf", "brot")
NON_MEAL_HINTS = ("dessert", "backen", "kuchen", "getränk", "drink", "cocktail", "frühstück")


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=20).read().decode("utf8", "ignore")


def _recipe_jsonld(html: str) -> dict | None:
    for m in re.finditer(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        for item in data if isinstance(data, list) else data.get("@graph", [data]):
            kind = item.get("@type")
            if kind == "Recipe" or (isinstance(kind, list) and "Recipe" in kind):
                return item
    return None


def _iso_minutes(value) -> int | None:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?", value or "")
    if not m or not any(m.groups()):
        return None
    d, h, mi = (int(g or 0) for g in m.groups())
    return d * 1440 + h * 60 + mi


def _jsonld_steps(instructions) -> list[str]:
    steps = []
    for s in instructions if isinstance(instructions, list) else [instructions]:
        if isinstance(s, dict):
            s = s.get("text") or " ".join(
                i.get("text", "") for i in s.get("itemListElement", []) if isinstance(i, dict)
            )
        if isinstance(s, str) and len(s.strip()) > 10:
            steps.append(re.sub(r"<[^>]+>", "", s).strip())
    return steps[:12]


def _recipe_from_jsonld(ld: dict, url: str, source: str) -> dict | None:
    name = (ld.get("name") or "").strip()
    ingredients = [i.strip() for i in ld.get("recipeIngredient", []) if isinstance(i, str)]
    minutes = _iso_minutes(ld.get("totalTime")) or _iso_minutes(ld.get("prepTime"))
    if not name or not ingredients or minutes is None:
        return None

    category = ld.get("recipeCategory") or ""
    keywords = ld.get("keywords") or ""
    meta = " ".join(category if isinstance(category, list) else [category]).lower()
    meta += " " + (" ".join(keywords) if isinstance(keywords, list) else keywords).lower()
    if any(w in meta for w in NON_MEAL_HINTS):
        return None

    is_lunch = any(w in (name + meta).lower() for w in LUNCH_HINTS)
    return {
        "name": name,
        "source_url": url,
        "meal_type": "Mittagessen" if is_lunch else "Abendessen",
        "prep_time_minutes": minutes,
        "ingredients": ingredients,
        "steps": _jsonld_steps(ld.get("recipeInstructions", [])),
        "fertility_benefits": "",
        "calories_per_adult": 0,
        "protein_per_adult_g": 0,
        "child_adaptation": None,
        "expensive_ingredients": [],
        "source": source,
    }


def _scrape_kitchenstories(n: int, seen_names: set) -> list[dict]:
    """Sample random recipe pages from the Kitchen Stories sitemap (schema.org JSON-LD)."""
    sitemaps = [s for s in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", _fetch(KS_SITEMAP_INDEX))
                if "post-sitemap" in s]
    # Several files: a few of them are mostly articles, so one bad pick must not empty the source
    urls = []
    for sitemap in random.sample(sitemaps, min(3, len(sitemaps))):
        urls += [u for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", _fetch(sitemap))
                 if not u.endswith(".xml")]
    random.shuffle(urls)

    recipes = []
    for url in urls[:n * 15]:  # many sitemap entries are articles, not recipes
        if len(recipes) >= n:
            break
        try:
            ld = _recipe_jsonld(_fetch(url))
        except Exception:
            continue
        recipe = _recipe_from_jsonld(ld, url, "web") if ld else None
        if (recipe and recipe["name"] not in seen_names
                and recipe["prep_time_minutes"] <= MAX_TIME_MIN and _is_allowed(recipe)):
            seen_names.add(recipe["name"])
            recipes.append(recipe)
            print(f"    ✓ [Kitchen Stories] {recipe['name']} ({recipe['prep_time_minutes']} Min)")
        time.sleep(0.5)
    return recipes


LECKER_HUBS = [
    "rezepte/schnelle-rezepte", "rezepte/vegetarische-rezepte", "rezepte/fisch",
    "rezepte/gefluegel", "rezepte/pasta", "rezepte/gesunde-rezepte",
]


def _scrape_lecker(n: int, seen_names: set) -> list[dict]:
    """LECKER blocks plain HTTP clients, so use the browser; recipes come from JSON-LD."""
    recipes = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(user_agent=UA["User-Agent"]).new_page()
        try:
            hubs = random.sample(LECKER_HUBS, len(LECKER_HUBS))
            links: list[str] = []
            for hub in hubs[:3]:
                try:
                    page.goto(f"https://www.lecker.de/{hub}", wait_until="domcontentloaded", timeout=25000)
                    time.sleep(1.5)
                except PlaywrightTimeoutError:
                    continue
                for a in page.query_selector_all("a[href]"):
                    href = (a.get_attribute("href") or "").split("#")[0]
                    if re.search(r"-\d{5,}\.html$", href):
                        links.append(href if href.startswith("http") else "https://www.lecker.de" + href)
            links = list(dict.fromkeys(links))
            random.shuffle(links)

            for url in links[:n * 6]:  # some links are articles, not recipes
                if len(recipes) >= n:
                    break
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    time.sleep(1)
                    ld = _recipe_jsonld(page.content())
                except PlaywrightTimeoutError:
                    continue
                recipe = _recipe_from_jsonld(ld, url, "web") if ld else None
                if recipe:
                    recipe["name"] = re.sub(r"\s+Rezept$", "", recipe["name"])
                if (recipe and recipe["name"] not in seen_names
                        and recipe["prep_time_minutes"] <= MAX_TIME_MIN and _is_allowed(recipe)):
                    seen_names.add(recipe["name"])
                    recipes.append(recipe)
                    print(f"    ✓ [LECKER] {recipe['name']} ({recipe['prep_time_minutes']} Min)")
        finally:
            browser.close()
    return recipes


def scrape_web_recipes(n: int = TARGET) -> list[dict]:
    recipes = []
    seen_names = set()

    # Each source is isolated so one failing site cannot break the weekly run
    share = n // 3
    for label, scrape in (("Kitchen Stories", _scrape_kitchenstories), ("LECKER", _scrape_lecker)):
        try:
            recipes += scrape(share, seen_names)
        except Exception as e:
            print(f"  → {label} fehlgeschlagen ({e}).")
    # Chefkoch below fills up to the total n (and covers for any source that failed)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        for search_url, meal_type in SEARCH_QUERIES:
            if len(recipes) >= n:
                break

            print(f"  → Suche: {search_url.split('?')[0].split('/')[-1]}")
            links = _get_recipe_links(page, search_url)
            random.shuffle(links)
            print(f"    {len(links)} Links gefunden.")

            for url in links:
                if len(recipes) >= n:
                    break
                recipe = _scrape_recipe(page, url, meal_type)
                if recipe and recipe["name"] not in seen_names:
                    if recipe["prep_time_minutes"] <= 40 and _is_allowed(recipe):
                        seen_names.add(recipe["name"])
                        recipes.append(recipe)
                        print(f"    ✓ {recipe['name']} ({recipe['prep_time_minutes']} Min)")

        browser.close()

    return recipes


if __name__ == "__main__":
    results = scrape_web_recipes()
    print(f"\n{len(results)} Rezepte gefunden:")
    for r in results:
        print(f"  {r['name']} ({r['prep_time_minutes']} Min) — {len(r['ingredients'])} Zutaten")
        if r['ingredients']:
            print(f"    Beispiel: {r['ingredients'][0]}")
