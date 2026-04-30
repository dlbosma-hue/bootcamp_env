import re
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SEARCH_QUERIES = [
    ("https://www.chefkoch.de/rs/s0g53/Vegetarisch/Rezepte.html", "Mittagessen"),
    ("https://www.chefkoch.de/suche.html?query=H%C3%A4hnchen+schnell+gesund", "Abendessen"),
    ("https://www.chefkoch.de/suche.html?query=Lachs+schnell+gesund", "Mittagessen"),
    ("https://www.chefkoch.de/suche.html?query=vegetarisch+schnell+Abendessen", "Abendessen"),
]

TARGET = 7  # recipes to return


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
    # Numbered steps: lines starting with a digit
    steps = re.split(r"\n\d+\n", section)
    result = [s.strip() for s in steps if len(s.strip()) > 20]
    return result[:12]


def _scrape_recipe(page, url: str, default_meal_type: str) -> dict | None:
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        time.sleep(1)

        title = page.query_selector("h1")
        name = title.inner_text().strip() if title else ""
        if not name:
            return None

        body = page.inner_text("body")
        prep_time = _parse_time(body)

        # Ingredients from table rows: "300 g | Kichererbsen"
        ingredients = []
        rows = page.query_selector_all("table.ingredients tr")
        for row in rows:
            tds = row.query_selector_all("td")
            if len(tds) >= 2:
                qty = tds[0].inner_text().strip().replace('\n', ' ').replace('\t', ' ')
                qty = re.sub(r'\s+', ' ', qty).strip()
                name_td = tds[1].inner_text().strip().replace('\n', ' ').replace('\t', ' ')
                name_td = re.sub(r'\s+', ' ', name_td).strip()
                if name_td:
                    ingredients.append(f"{qty} {name_td}".strip())

        if not ingredients:
            return None

        steps = _parse_steps(body)

        # Clean URL (remove tracking hash)
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
        links = set()
        for el in page.query_selector_all("a[href*='/rezepte/']"):
            href = el.get_attribute("href") or ""
            # Only full recipe detail URLs (not category pages)
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

            print(f"  → Suche auf chefkoch.de: {search_url.split('?')[0].split('/')[-1]}")
            links = _get_recipe_links(page, search_url)
            random.shuffle(links)

            for url in links:
                if len(recipes) >= n:
                    break
                recipe = _scrape_recipe(page, url, meal_type)
                if recipe and recipe["name"] not in seen_names:
                    if recipe["prep_time_minutes"] <= 40:
                        seen_names.add(recipe["name"])
                        recipes.append(recipe)
                        print(f"    ✓ {recipe['name']} ({recipe['prep_time_minutes']} Min)")

        browser.close()

    return recipes


if __name__ == "__main__":
    import json
    results = scrape_web_recipes()
    print(f"\n{len(results)} Rezepte gefunden:")
    for r in results:
        print(f"  {r['name']} ({r['prep_time_minutes']} Min) — {len(r['ingredients'])} Zutaten")
