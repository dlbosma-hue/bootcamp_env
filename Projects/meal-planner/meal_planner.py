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
            "fertility_benefits": r.get("fertility_benefits", ""),
            "ingredients": r.get("ingredients", []),
            "steps": r.get("steps", []),
        }
        for r in quick
    ]


def _deduplicate_plan(plan_data: dict, all_recipes: list[dict]) -> dict:
    """Replace any repeated recipes in the meal plan with unused ones from the pool."""
    meal_plan = plan_data.get("meal_plan", [])
    pool_by_name = {r["name"]: r for r in all_recipes if isinstance(r, dict)}

    seen_names: set[str] = set()
    duplicate_slots: list[tuple[int, str]] = []
    for i, day in enumerate(meal_plan):
        for slot in ("lunch", "dinner"):
            name = day.get(slot, "")
            if name in seen_names:
                duplicate_slots.append((i, slot))
            else:
                seen_names.add(name)

    if not duplicate_slots:
        return plan_data

    unused = [r for r in all_recipes if isinstance(r, dict) and r["name"] not in seen_names]

    for idx, (day_idx, slot) in enumerate(duplicate_slots):
        if idx >= len(unused):
            break
        replacement = unused[idx]
        meal_plan[day_idx][slot] = replacement["name"]
        seen_names.add(replacement["name"])

    # Rebuild recipes list from final meal_plan names
    final_names = []
    for day in meal_plan:
        for slot in ("lunch", "dinner"):
            name = day.get(slot, "")
            if name and name not in final_names:
                final_names.append(name)

    recipes_by_name = {r.get("name"): r for r in plan_data.get("recipes", []) if isinstance(r, dict)}
    recipes_by_name.update(pool_by_name)
    plan_data["meal_plan"] = meal_plan
    plan_data["recipes"] = [recipes_by_name[n] for n in final_names if n in recipes_by_name]
    return plan_data


def build_meal_plan(recipes: list[dict]) -> dict:
    summarised = _summarise(recipes)
    recipes_json = json.dumps(summarised, ensure_ascii=False, indent=2)

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

    plan_data = json.loads(response.choices[0].message.content)
    return _deduplicate_plan(plan_data, recipes)


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
