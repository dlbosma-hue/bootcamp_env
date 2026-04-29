"""
Scores recipes on prenatal nutrition value (0–10).
A score of 5–7 is ideal: good nutrients without being a "superfood salad".
Scores are added as metadata so the meal planner can balance the week.
"""

# Ingredients that are great for prenatal nutrition
PRENATAL_BOOSTERS = {
    # folate / iron / calcium
    "spinach": 2, "lentil": 2, "chickpea": 2, "black bean": 2, "kidney bean": 2,
    "kale": 2, "broccoli": 2, "edamame": 2, "asparagus": 2, "avocado": 1,
    # omega-3 / protein
    "salmon": 2, "sardine": 2, "walnut": 1, "chia": 1, "flaxseed": 1,
    "egg": 1, "greek yogurt": 1, "cottage cheese": 1, "tofu": 1, "tempeh": 1,
    # vitamin D / calcium
    "fortified": 1, "almond milk": 1, "oat": 1,
    # iron helpers
    "pumpkin seed": 1, "sunflower seed": 1, "quinoa": 1,
}

# Ingredients to flag — not blocked, just lower the score
PRENATAL_FLAGS = {
    "liver": -3,       # excess vitamin A risk
    "alcohol": -3, "wine": -2, "beer": -2,
    "raw egg": -2, "mayonnaise": -1,
    "tuna": -1, "swordfish": -2, "king mackerel": -2,  # mercury
    "raw fish": -2, "sashimi": -2, "sushi": -2,
    "brie": -1, "camembert": -1, "roquefort": -1, "gorgonzola": -1,  # soft cheeses
    "unpasteurized": -2,
    "deli meat": -1, "hot dog": -1,
}


def score_recipe(recipe: dict) -> dict:
    text = " ".join([
        recipe.get("name", ""),
        " ".join(str(i) for i in recipe.get("ingredients", [])),
        " ".join(recipe.get("steps", [])),
    ]).lower()

    score = 5  # neutral baseline
    notes = []

    for ingredient, pts in PRENATAL_BOOSTERS.items():
        if ingredient in text:
            score += pts
            notes.append(f"+{pts} {ingredient}")

    for ingredient, pts in PRENATAL_FLAGS.items():
        if ingredient in text:
            score += pts  # pts are negative
            notes.append(f"{pts} {ingredient}")

    recipe["prenatal_score"] = max(0, min(10, score))
    recipe["prenatal_notes"] = notes
    return recipe


def score_recipes(recipes: list[dict]) -> list[dict]:
    return [score_recipe(r) for r in recipes]
