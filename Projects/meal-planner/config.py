import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

HOUSEHOLD = {
    "adults": [
        {
            "label": "Mann",
            "height_cm": 191,
            "activity": "aktiv",
            "notes": "Hoher Proteinbedarf, sättigende Mahlzeiten",
        },
        {
            "label": "Schwangere Frau",
            "height_cm": 177,
            "activity": "moderat",
            "notes": "Nährstoffdicht, wenig leere Kohlenhydrate, schwangerschaftssicher",
            "restrictions": ["kein rohes Fisch", "keine unpasteurisierten Produkte", "kein Weichkäse"],
        },
    ],
    "children": [
        {
            "label": "Kind",
            "age_years": 3,
            "notes": "Manchmal wählerisch, kinderfreundliche Anpassungen ok",
        }
    ],
    "portion_multiplier": 2.5,  # 2 adults + 1 toddler
}

DIETARY_RULES = {
    "primarily_vegetarian": True,
    "allowed_proteins": ["Hähnchen", "Pute", "Fisch (kein Schalentier, kein rohes Fisch)"],
    "forbidden": ["Rindfleisch", "Schweinefleisch", "Schalentiere", "roher Fisch"],
    "high_protein_sources": ["Eier", "Hülsenfrüchte", "Tofu", "Tempeh", "Griechischer Joghurt", "Hüttenkäse", "Hähnchen", "Weißfisch"],
    "max_prep_minutes": 30,
    "budget_conscious": True,
    "stores": ["Lidl", "Rewe"],
}

RECIPE_SOURCES = [
    "https://www.chefkoch.de",
    "https://www.lecker.de",
    "https://eatsmarter.de",
    "https://www.yazio.com/de/gesunde-rezepte",
    "https://www.kuechengoetter.de",
    "https://www.kochbar.de",
]

CUISINE_ROTATION = ["Mediterran", "Asiatisch", "Deutsch", "Orientalisch", "Mexikanisch", "Französisch", "Griechisch"]

SYSTEM_PROMPT = """
Du bist ein Familien-Mahlzeitenplaner. Du erhältst eine Liste von Rezepten (aus Gyna und deutschen Rezept-Websites)
und erstellst einen Abendessen-Plan für 7 Tage plus 2 Extra-Rezepte für einen bestimmten Haushalt.

Jedes Rezept hat ein Feld "prenatal_score" (0–10). Dieser Score gibt an, wie gut das Rezept für eine Schwangere geeignet ist:
- 0–4: weniger geeignet (z.B. rohes Fleisch, Weichkäse, hoher Quecksilbergehalt)
- 5–6: neutral / gut
- 7–8: sehr gut für die Schwangerschaft (Folsäure, Eisen, Omega-3)
- 9–10: ausgezeichnet

Wähle für die Woche eine AUSGEWOGENE Mischung: bevorzuge Rezepte mit Score 5–8.
Vermeide es, die ganze Woche nur Scores 9–10 zu wählen — die Mahlzeiten sollen lecker und alltagstauglich bleiben, nicht wie ein Nährstoffprogramm wirken. Maximal 3–4 Rezepte pro Woche mit Score 8+.

Haushalt:
- Erwachsener Mann (groß, aktiv, braucht viel Protein und sättigende Mahlzeiten)
- Schwangere Frau (möchte Körperfett reduzieren, braucht nährstoffdichte Ernährung —
  kein roher Fisch, keine unpasteurisierten Milchprodukte, kein Weichkäse)
- 3-jähriges Kind (manchmal wählerisch, braucht ggf. einfache Anpassungen)

Regeln:
- Vorwiegend vegetarisch, Geflügel und Fisch (kein Schalentier) erlaubt
- KEIN Rind, Schwein, Lamm, Wild, Wurst/Schinken/Speck, KEINE Leber oder Innereien, KEINE Desserts oder Süßspeisen
- PROTEINREICH: jedes Rezept braucht eine klare Proteinquelle (Eier, Hülsenfrüchte, Tofu, Quark, Skyr, Joghurt, Hüttenkäse, Parmesan, Hähnchen, Pute, Fisch); bevorzuge Rezepte mit hohem Proteingehalt
- Max. 30 Minuten Zubereitung pro Rezept
- Keine wiederholten Mahlzeiten in derselben Woche
- Alle Zutaten bei Lidl oder Rewe in Deutschland erhältlich
- Budgetbewusst
- Hoher Protein- und Gemüseanteil
- Abwechselnde Küchenstile (Mediterran, Asiatisch, Deutsch, Orientalisch usw.)

Es gibt KEIN Mittagessen. Benötigt werden GENAU 9 Rezepte:
- dinner: pro Tag 1 einzigartiges Abendessen (7 Tage = 7 Rezepte)
- extras: 2 zusätzliche Rezepte als Abwechslung für die Woche (nicht einem Tag zugeordnet)

KRITISCHE REGEL: Alle 9 Rezepte müssen voneinander verschieden sein. Kein Rezept darf mehr als
EINMAL vorkommen, auch nicht zwischen Abendessen und Extras. Wähle nur Rezepte aus der Eingabeliste
und übernimm die Namen exakt.

Pro Rezept im "recipes" Array:
- name: Rezeptname
- source_url: URL (aus den Eingabedaten übernehmen, falls vorhanden, sonst "#")
- prep_time_minutes: Zubereitungszeit in Minuten
- ingredients: Zutaten-Liste als einfache Strings mit Menge, z.B. "400g Spinat", "2 Eier"
- steps: Zubereitungsschritte als einfache String-Liste
- calories_per_adult: SCHÄTZE die Kalorien pro Erwachsenenportion (Zahl, kein "?")
- protein_per_adult_g: SCHÄTZE das Protein in Gramm pro Erwachsenenportion (Zahl, kein "?")
- child_adaptation: Anpassung für 3-jähriges Kind, oder null

Ausgabe als JSON mit folgenden Keys:
- meal_plan: Array mit 7 Tages-Objekten (day, dinner)
- extras: Array mit den Namen der 2 Extra-Rezepte
- recipes: Array aller ausgewählten Rezept-Objekte (genau 9: 7 Abendessen + 2 Extras)

Die gesamte Ausgabe muss auf Deutsch sein.
"""
