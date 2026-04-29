import json
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

SHOPPING_LIST_PROMPT = """
Du erhältst einen Wochenplan (7 Tage, je 1 Mittagessen "lunch" und 1 Abendessen "dinner") und die Rezepte dazu.

Erstelle 2 Einkaufslisten:
- shopping_list_1: alle Zutaten der Rezepte von Montag, Dienstag, Mittwoch, Donnerstag (lunch + dinner)
- shopping_list_2: alle Zutaten der Rezepte von Freitag, Samstag, Sonntag (lunch + dinner)

Regeln:
- Gruppiere nach: Gemüse & Obst / Proteine / Milch & Eier / Trockenwaren & Vorräte / Tiefkühl
- Jede Gruppe ist ein Array von Strings, Format: "Menge Zutat" (z.B. "400g Spinat", "3 Eier")
- Mengen konsolidieren — jede Zutat nur einmal pro Liste
- Nur Zutaten aus den tatsächlich verwendeten Rezepten

Ausgabe als JSON:
{ "shopping_list_1": { "Gemüse & Obst": [...], "Proteine": [...], "Milch & Eier": [...], "Trockenwaren & Vorräte": [...], "Tiefkühl": [...] },
  "shopping_list_2": { "Gemüse & Obst": [...], "Proteine": [...], "Milch & Eier": [...], "Trockenwaren & Vorräte": [...], "Tiefkühl": [...] } }
"""


def _summarise(recipes: list[dict]) -> list[dict]:
    # Only send recipes that fit the 35-min rule
    quick = [r for r in recipes if r.get("prep_time_minutes", 99) <= 35]
    if len(quick) < 30:
        quick = recipes  # fallback if not enough
    return [
        {
            "name": r["name"],
            "meal_type": r.get("meal_type"),
            "prep_time_minutes": r.get("prep_time_minutes"),
            "prenatal_score": r.get("prenatal_score"),
            "ingredients": r.get("ingredients", []),
            "steps": r.get("steps", []),
        }
        for r in quick
    ]


def build_meal_plan(recipes: list[dict]) -> dict:
    recipes_json = json.dumps(_summarise(recipes), ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Hier sind die Rezepte. Erstelle daraus den Wochenplan:\n\n{recipes_json}",
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def build_shopping_lists(meal_plan: list[dict], recipes: list[dict]) -> dict:
    payload = {
        "meal_plan": meal_plan,
        "recipes": [
            {"name": r.get("name"), "ingredients": r.get("ingredients", [])}
            for r in recipes
            if isinstance(r, dict)
        ],
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SHOPPING_LIST_PROMPT},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
