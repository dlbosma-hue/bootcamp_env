import json
import random
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

EXTRAS_PER_WEEK = 2

SHOPPING_LIST_PROMPT = """
Du erhältst einen Wochenplan (7 Tage, je 1 Abendessen "dinner") und die Rezepte dazu.

Erstelle 2 Einkaufslisten:
- shopping_list_1: alle Zutaten der Abendessen von Montag, Dienstag, Mittwoch, Donnerstag
- shopping_list_2: alle Zutaten der Abendessen von Freitag, Samstag, Sonntag

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
    if len(quick) < 15:
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


def _key(name: str) -> str:
    return " ".join(str(name).lower().split())


def _deduplicate_plan(plan_data: dict, all_recipes: list[dict]) -> dict:
    """Make the 7 dinners + 2 extras unique and valid; fill bad slots from the unused pool."""
    meal_plan = plan_data.get("meal_plan", [])
    extras = list(plan_data.get("extras", []))[:EXTRAS_PER_WEEK]
    extras += [""] * (EXTRAS_PER_WEEK - len(extras))
    pool = [r for r in all_recipes if isinstance(r, dict) and r.get("name")]
    pool_names = {r["name"] for r in pool}

    # Every slot is (kind, index): a dinner of a day, or an extra
    slots = [("dinner", i) for i in range(len(meal_plan))] + [("extra", i) for i in range(len(extras))]

    def get(kind, i):
        return meal_plan[i].get("dinner", "") if kind == "dinner" else extras[i]

    def put(kind, i, name):
        if kind == "dinner":
            meal_plan[i]["dinner"] = name
        else:
            extras[i] = name

    seen: set[str] = set()
    bad_slots = []
    for kind, i in slots:
        name = get(kind, i)
        # Empty, repeated, or invented (not in the pool) names are all replaced
        if not name or _key(name) in seen or name not in pool_names:
            bad_slots.append((kind, i))
        else:
            seen.add(_key(name))

    unused = [r for r in pool if _key(r["name"]) not in seen]
    random.shuffle(unused)
    for kind, i in bad_slots:
        if not unused:
            print(f"  ! Kein unbenutztes Rezept mehr fuer Slot {kind} {i + 1}.")
            break
        replacement = unused.pop()
        put(kind, i, replacement["name"])
        seen.add(_key(replacement["name"]))

    # Rebuild recipes in plan order: the AI's version (with its estimates) if present, else the pool's
    ai_by_key = {_key(r.get("name", "")): r for r in plan_data.get("recipes", []) if isinstance(r, dict)}
    pool_by_key = {_key(r["name"]): r for r in pool}
    final_recipes = []
    for kind, i in slots:
        name = get(kind, i)
        recipe = ai_by_key.get(_key(name)) or pool_by_key.get(_key(name))
        if recipe:
            final_recipes.append(recipe)

    plan_data["meal_plan"] = meal_plan
    plan_data["extras"] = [e for e in extras if e]
    plan_data["recipes"] = final_recipes
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
