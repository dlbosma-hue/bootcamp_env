import json
from openai import OpenAI
from config import OPENAI_API_KEY, RECIPE_SOURCES, DIETARY_RULES, CUISINE_ROTATION

client = OpenAI(api_key=OPENAI_API_KEY)

FETCH_PROMPT = """
Suche auf den folgenden deutschen Rezept-Websites nach passenden Rezepten:
{sources}

Suchfilter:
- Zubereitungszeit: unter 30 Minuten
- Familienfreundlich
- Hoher Proteingehalt
- Vegetarisch ODER mit Geflügel ODER mit Fisch (kein Schalentier, kein roher Fisch)
- Kalorienarm oder ausgewogene Makros

Benötigte Küchenstile diese Woche: {cuisines}

Finde GENAU 30 verschiedene Rezepte — 15 Mittagessen und 15 Abendessen.
WICHTIG: Jedes Rezept muss einzigartig sein. Kein Rezept darf zweimal vorkommen.
Für jedes Rezept extrahiere:
- name: Rezeptname
- source_url: direkte URL zum Rezept
- cuisine: Küchenstil
- meal_type: "Mittagessen" oder "Abendessen"
- prep_time_minutes: Zubereitungszeit in Minuten
- ingredients: Liste mit Zutaten und Mengen (metrisch: g, ml, EL, TL)
- steps: Zubereitungsschritte als Liste
- calories_per_adult: geschätzte Kalorien pro Erwachsenenportion
- protein_per_adult_g: geschätztes Protein in Gramm pro Erwachsenenportion
- child_adaptation: Anpassung für 3-jähriges Kind (oder null)
- expensive_ingredients: Liste teurer Zutaten mit günstigeren Alternativen (oder leer)

Gib das Ergebnis als JSON-Array zurück.
"""


def fetch_recipes() -> list[dict]:
    sources_str = "\n".join(f"- {s}" for s in RECIPE_SOURCES)
    cuisines_str = ", ".join(CUISINE_ROTATION)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Ernährungsexperte der deutsche Rezepte recherchiert. Antworte ausschließlich mit validem JSON.",
            },
            {
                "role": "user",
                "content": FETCH_PROMPT.format(sources=sources_str, cuisines=cuisines_str),
            },
        ],
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)
    recipes = data.get("recipes", data) if isinstance(data, dict) else data
    if not isinstance(recipes, list):
        recipes = list(data.values())[0]
    return recipes
