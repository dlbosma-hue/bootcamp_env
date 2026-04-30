import os
import json
import time
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GYNA_EMAIL = os.getenv("GYNA_EMAIL")
GYNA_PASSWORD = os.getenv("GYNA_PASSWORD")
GYNA_RECIPES_URL = "https://gyna.co/recipes/list"
GYNA_LOGIN_URL = "https://gyna.co/log_in"
CACHE_FILE = os.path.join(os.path.dirname(__file__), "gyna_recipes_cache.json")


def _login(page):
    page.goto(GYNA_LOGIN_URL, wait_until="networkidle")
    time.sleep(2)
    page.fill('#email-input', GYNA_EMAIL)
    page.fill('#user_password', GYNA_PASSWORD)
    page.click('button[type="submit"]')
    time.sleep(5)
    if "log_in" in page.url:
        raise RuntimeError("Gyna login failed — check GYNA_EMAIL and GYNA_PASSWORD in .env")


def _parse_prep_time(text: str) -> int:
    match = re.search(r"Prep time[:\s]+(\d+)\s*minutes?", text, re.I)
    cook_match = re.search(r"Cook time[:\s]+(\d+)\s*minutes?", text, re.I)
    prep = int(match.group(1)) if match else 0
    cook = int(cook_match.group(1)) if cook_match else 0
    return prep + cook or 30


def _scrape_recipe_detail(page, url: str) -> dict | None:
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        time.sleep(1)

        # Title
        title_el = page.query_selector("[class*='title']")
        name = title_el.inner_text().strip() if title_el else ""
        if not name:
            return None

        # Prep + cook time from body text
        body_text = page.inner_text("body")
        prep_time = _parse_prep_time(body_text)

        # Fertility benefits — paragraph after "Vorteile für die Fruchtbarkeit" h2
        fertility_benefits = ""
        fertility_match = re.search(
            r"Vorteile f.r die Fruchtbarkeit\s*\n(.+?)(?=\nZutaten|\nIngredients|\Z)",
            body_text, re.DOTALL
        )
        if fertility_match:
            fertility_benefits = fertility_match.group(1).strip()

        # Ingredients: <ul> contains <li> items
        ul = page.query_selector("ul")
        ingredients = []
        if ul:
            ingredients = [li.inner_text().strip() for li in ul.query_selector_all("li") if li.inner_text().strip()]

        # Steps: <ol> contains <li> items
        ol = page.query_selector("ol")
        steps = []
        if ol:
            steps = [li.inner_text().strip() for li in ol.query_selector_all("li") if li.inner_text().strip()]

        if not ingredients:
            return None

        # Detect meal type from name/content
        meal_type = _detect_meal_type(name, body_text)

        # Detect cuisine from tags (text between title and ingredients)
        cuisine = _detect_cuisine(body_text)

        return {
            "name": name,
            "source_url": url,
            "cuisine": cuisine,
            "meal_type": meal_type,
            "prep_time_minutes": prep_time,
            "ingredients": ingredients,
            "steps": steps,
            "fertility_benefits": fertility_benefits,
            "calories_per_adult": 0,
            "protein_per_adult_g": 0,
            "child_adaptation": None,
            "expensive_ingredients": [],
        }
    except PlaywrightTimeoutError:
        print(f"  Timeout on {url}, skipping.")
        return None


def _detect_meal_type(name: str, body: str) -> str:
    name_lower = name.lower()
    body_lower = body.lower()
    breakfast_kw = ["breakfast", "pancake", "oatmeal", "porridge", "smoothie", "granola", "muffin", "waffle", "pudding", "chia"]
    snack_kw = ["cookie", "ball", "snack", "bite", "bar", "cracker", "dip", "pesto", "sauce"]
    dinner_kw = ["soup", "stew", "curry", "roast", "casserole", "bake", "dinner", "skillet", "stir", "pasta", "risotto", "lentil"]
    if any(k in name_lower for k in breakfast_kw):
        return "Frühstück"
    if any(k in name_lower for k in snack_kw):
        return "Snack"
    if any(k in name_lower for k in dinner_kw):
        return "Abendessen"
    return "Mittagessen"


def _detect_cuisine(body: str) -> str:
    body_lower = body.lower()
    if any(k in body_lower for k in ["asian", "thai", "chinese", "japanese", "korean", "soy sauce", "miso", "tofu stir"]):
        return "Asiatisch"
    if any(k in body_lower for k in ["mediterranean", "greek", "feta", "hummus", "tzatziki"]):
        return "Mediterran"
    if any(k in body_lower for k in ["mexican", "taco", "burrito", "salsa", "guacamole", "avocado"]):
        return "Mexikanisch"
    if any(k in body_lower for k in ["indian", "curry", "masala", "tikka", "dal", "dahl", "lentil"]):
        return "Orientalisch"
    return "International"


def scrape_gyna_recipes(use_cache: bool = True) -> list[dict]:
    if use_cache and os.path.exists(CACHE_FILE):
        print(f"  → Lade Rezepte aus Cache ({CACHE_FILE})")
        with open(CACHE_FILE) as f:
            return json.load(f)

    recipes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        print("  → Anmelden bei Gyna...")
        _login(page)
        print("  → Angemeldet. Rezeptliste laden...")

        page.goto(GYNA_RECIPES_URL, wait_until="networkidle", timeout=20000)
        time.sleep(2)

        # Scroll to load all lazy-loaded recipes
        for _ in range(15):
            page.keyboard.press("End")
            time.sleep(0.6)

        # Collect all recipe detail links (pattern: /recipes/123-slug)
        recipe_links = set()
        for el in page.query_selector_all("a[href]"):
            href = el.get_attribute("href") or ""
            if re.match(r"^/recipes/\d+-", href):
                recipe_links.add(f"https://gyna.co{href}")

        print(f"  → {len(recipe_links)} Rezept-Links gefunden.")

        for i, url in enumerate(sorted(recipe_links), 1):
            print(f"  → [{i}/{len(recipe_links)}] {url.split('/')[-1]}")
            recipe = _scrape_recipe_detail(page, url)
            if recipe:
                recipes.append(recipe)

        browser.close()

    print(f"  → {len(recipes)} Rezepte erfolgreich gescrapt.")

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    print(f"  → Cache gespeichert: {CACHE_FILE}")

    return recipes


if __name__ == "__main__":
    results = scrape_gyna_recipes(use_cache=False)
    print(f"\nFertig: {len(results)} Rezepte")
    if results:
        print("Beispiel:", json.dumps(results[0], ensure_ascii=False, indent=2))
