FORBIDDEN_INGREDIENTS = [
    "roher fisch", "sushi", "sashimi", "ceviche", "tatar", "carpaccio",
    "roher lachs", "geräucherter lachs", "räucherlachs",
    "weichkäse", "brie", "camembert", "roquefort", "gorgonzola", "feta",
    "rohmilch", "unpasteurisiert",
    "rohes ei", "rohe eier", "mayonnaise selbstgemacht",
    "leber", "leberpastete", "leberaufstrich",
    "alkohol", "wein zum trinken",
]

WARNING_INGREDIENTS = [
    "thunfisch",  # high mercury — limit
    "schwertfisch", "haifisch", "königsmakrele",
    "aufschnitt", "wurst", "salami",  # listeria risk if not heated
]


def validate_recipe(recipe: dict) -> dict:
    """
    Checks a recipe dict for pregnancy-unsafe ingredients.
    Returns the recipe with added keys:
      - pregnancy_safe: bool
      - pregnancy_warnings: list of warning strings
    """
    ingredients_text = " ".join(
        str(i).lower() for i in recipe.get("ingredients", [])
    )
    name_text = recipe.get("name", "").lower()
    full_text = ingredients_text + " " + name_text

    issues = [f for f in FORBIDDEN_INGREDIENTS if f in full_text]
    warnings = [w for w in WARNING_INGREDIENTS if w in full_text]

    recipe["pregnancy_safe"] = len(issues) == 0
    recipe["pregnancy_warnings"] = issues + [f"Achtung: {w}" for w in warnings]
    return recipe


def filter_safe_recipes(recipes: list[dict]) -> list[dict]:
    validated = [validate_recipe(r) for r in recipes]
    return [r for r in validated if r["pregnancy_safe"]]
