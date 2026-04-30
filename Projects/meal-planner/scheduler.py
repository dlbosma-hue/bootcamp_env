import random
import schedule
import time
from datetime import datetime
from gyna_scraper import scrape_gyna_recipes
from web_scraper import scrape_web_recipes
from prenatal_scorer import score_recipes
from meal_planner import build_meal_plan, build_shopping_lists
from email_renderer import render_email, send_email

GYNA_PER_WEEK = 10
WEB_PER_WEEK = 10


def _pick_gyna(scored: list[dict], n: int) -> list[dict]:
    """Randomly pick n recipes from Gyna, balanced between lunch and dinner."""
    lunches = [r for r in scored if r.get("meal_type") == "Mittagessen"]
    dinners = [r for r in scored if r.get("meal_type") == "Abendessen"]
    random.shuffle(lunches)
    random.shuffle(dinners)
    half = n // 2
    selected = lunches[:half] + dinners[:n - half]
    random.shuffle(selected)
    return selected


def run_meal_planner():
    print(f"[{datetime.now()}] Starte Wochenplan-Generierung...")

    print("  → Gyna-Rezepte laden und bewerten...")
    gyna_recipes = scrape_gyna_recipes(use_cache=True)
    gyna_scored = score_recipes(gyna_recipes)
    gyna_selected = _pick_gyna(gyna_scored, GYNA_PER_WEEK)
    print(f"  → {len(gyna_selected)} Gyna-Rezepte ausgewaehlt.")

    print("  → Echte Rezepte von chefkoch.de scrapen...")
    try:
        web_recipes = scrape_web_recipes(WEB_PER_WEEK)
        web_scored = score_recipes(web_recipes)
        print(f"  → {len(web_scored)} Web-Rezepte gescrapt.")
    except Exception as e:
        print(f"  → Web-Scraping fehlgeschlagen ({e}), fahre nur mit Gyna fort.")
        web_scored = []

    selected = gyna_selected + web_scored
    print(f"  → {len(selected)} Rezepte gesamt ({len(gyna_selected)} Gyna + {len(web_scored)} Web).")

    print("  → Wochenplan erstellen...")
    plan_data = build_meal_plan(selected)

    print("  → Einkaufslisten erstellen...")
    shopping = build_shopping_lists(plan_data.get("meal_plan", []), plan_data.get("recipes", []))
    plan_data.update(shopping)

    print("  → E-Mail rendern und senden...")
    html = render_email(plan_data)
    print(f"  → HTML generiert ({len(html)} Zeichen). Sende E-Mail...")
    send_email(html)

    print(f"[{datetime.now()}] Fertig!")


schedule.every().sunday.at("18:00").do(run_meal_planner)

if __name__ == "__main__":
    print("Mahlzeitenplaner gestartet. Warte auf Sonntag 18:00 Uhr...")
    while True:
        schedule.run_pending()
        time.sleep(60)
