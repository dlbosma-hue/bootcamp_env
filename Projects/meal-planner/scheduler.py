import random
import schedule
import time
from datetime import datetime
from gyna_scraper import scrape_gyna_recipes
from recipe_fetcher import fetch_recipes
from prenatal_scorer import score_recipes
from meal_planner import build_meal_plan
from email_renderer import render_email, send_email

# Meal plan needs 28 slots (7 days × 4). Send 40 to give GPT-4o some choice.
RECIPES_TO_SEND = 40


def select_recipes(scored: list[dict], n: int = RECIPES_TO_SEND) -> list[dict]:
    """
    Pick a balanced subset: mix of meal types, cuisines, and prenatal scores.
    Filters to ≤45 min prep first, then samples proportionally by meal type.
    """
    quick = [r for r in scored if r.get("prep_time_minutes", 99) <= 45]
    if len(quick) < n:
        quick = scored  # fallback if not enough quick recipes

    # Sort by prenatal score descending, then shuffle within score bands
    # to ensure variety across weeks
    quick.sort(key=lambda r: r.get("prenatal_score", 5), reverse=True)

    # Take top 60% by score, randomise the rest for variety
    top = quick[:int(len(quick) * 0.6)]
    rest = quick[int(len(quick) * 0.6):]
    random.shuffle(rest)
    pool = top + rest

    # Sample proportionally by meal type to ensure balanced week
    by_type = {}
    for r in pool:
        t = r.get("meal_type", "Mittagessen")
        by_type.setdefault(t, []).append(r)

    selected = []
    targets = {
        "Mittagessen": 16,
        "Abendessen": 16,
        "Frühstück": 4,
        "Snack": 4,
    }
    for meal_type, count in targets.items():
        bucket = by_type.get(meal_type, [])
        selected.extend(bucket[:count])

    # Fill remainder if any bucket was short
    needed = n - len(selected)
    used_names = {r["name"] for r in selected}
    extras = [r for r in pool if r["name"] not in used_names]
    selected.extend(extras[:needed])

    return selected[:n]


def run_meal_planner():
    print(f"[{datetime.now()}] Starte Wochenplan-Generierung...")

    print("  → Rezepte aus Gyna-Cache laden...")
    gyna_recipes = scrape_gyna_recipes(use_cache=True)
    print(f"  → {len(gyna_recipes)} Gyna-Rezepte geladen.")

    print("  → Neue Rezepte von deutschen Websites abrufen...")
    try:
        web_recipes = fetch_recipes()
        print(f"  → {len(web_recipes)} Web-Rezepte abgerufen.")
    except Exception as e:
        print(f"  → Web-Rezepte fehlgeschlagen ({e}), fahre nur mit Gyna fort.")
        web_recipes = []

    all_recipes = gyna_recipes + web_recipes
    print(f"  → {len(all_recipes)} Rezepte gesamt. Pränatal-Score berechnen...")
    scored_recipes = score_recipes(all_recipes)

    selected = select_recipes(scored_recipes)
    print(f"  → {len(selected)} Rezepte ausgewählt für GPT-4o.")

    print("  → Wochenplan erstellen...")
    plan_data = build_meal_plan(selected)

    print("  → E-Mail rendern und senden...")
    html = render_email(plan_data)
    send_email(html)

    print(f"[{datetime.now()}] Fertig!")


schedule.every().sunday.at("18:00").do(run_meal_planner)

if __name__ == "__main__":
    print("Mahlzeitenplaner gestartet. Warte auf Sonntag 18:00 Uhr...")
    print("Zum sofortigen Testen: Strg+C drücken und 'run_meal_planner()' direkt aufrufen.")
    while True:
        schedule.run_pending()
        time.sleep(60)
