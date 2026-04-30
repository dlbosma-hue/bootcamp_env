import re
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_QUERIES = [
    ("https://www.chefkoch.de/rs/s0g53o3/Vegetarisch/Rezepte.html", "Mittagessen"),
    ("https://www.chefkoch.de/suche.html?query=H%C3%A4hnchen+Pfanne+schnell+gesund", "Abendessen"),
    ("https://www.chefkoch.de/suche.html?query=Lachs+Ofenrezept+schnell", "Abendessen"),
    ("https://www.chefkoch.de/suche.html?query=vegetarisch+Salat+schnell+Mittagessen", "Mittagessen"),
]

FORBIDDEN_WORDS = {
    # red meat
    "rind", "schwein", "speck", "wurst", "salsiccia", "hack", "hirsch", "wild", "lamm", "schinken",
    "steak", "schnitzel", "braten", "filet",
    # desserts / baked goods — not meals
    "kuchen", "torte", "tarte", "streusel", "muffin", "keks", "brownie", "dessert", "eis", "tiramisu",
}


def _is_allowed(recipe: dict) -> bool:
    text = (recipe["name"] + " ".join(recipe["ingredients"])).lower()
    return not any(w in text for w in FORBIDDEN_WORDS)

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


def scrape_web_recipes(n: int = TARGET) -> list[dict]:
    recipes = []
    seen_names = set()

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
