import schedule
import time
from datetime import datetime
from gyna_scraper import scrape_gyna_recipes
from recipe_fetcher import fetch_recipes
from pregnancy_validator import filter_safe_recipes
from meal_planner import build_meal_plan
from email_renderer import render_email, send_email


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

    raw_recipes = gyna_recipes + web_recipes

    print(f"  → {len(raw_recipes)} Rezepte abgerufen. Schwangerschaftssicherheit prüfen...")
    safe_recipes = filter_safe_recipes(raw_recipes)
    print(f"  → {len(safe_recipes)} Rezepte sind schwangerschaftssicher.")

    print("  → Wochenplan erstellen...")
    plan_data = build_meal_plan(safe_recipes)

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
