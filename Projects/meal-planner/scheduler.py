import schedule
import time
from datetime import datetime
from recipe_fetcher import fetch_recipes
from pregnancy_validator import filter_safe_recipes
from meal_planner import build_meal_plan
from email_renderer import render_email, send_email


def run_meal_planner():
    print(f"[{datetime.now()}] Starte Wochenplan-Generierung...")

    print("  → Rezepte abrufen...")
    raw_recipes = fetch_recipes()

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
