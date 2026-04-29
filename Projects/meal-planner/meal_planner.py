import json
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def _summarise(recipes: list[dict]) -> list[dict]:
    return [
        {
            "name": r["name"],
            "meal_type": r.get("meal_type"),
            "cuisine": r.get("cuisine"),
            "prep_time_minutes": r.get("prep_time_minutes"),
            "prenatal_score": r.get("prenatal_score"),
            "ingredients": r.get("ingredients", [])[:5],  # first 5 only for context
        }
        for r in recipes
    ]


def build_meal_plan(recipes: list[dict]) -> dict:
    recipes_json = json.dumps(_summarise(recipes), ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Hier sind die gefetchten Rezepte. Erstelle daraus den Wochenplan:\n\n{recipes_json}",
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
