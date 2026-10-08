"""
Shared recipe filters for every source (Gyna, Chefkoch, Kitchen Stories, LECKER).

Matching is on word starts, so "Reis" does not trigger "eis" and "Hähnchenfilet" does
not trigger "filet". Only name + ingredients are checked, not the cooking steps.
"""
import re

# Red meat, offal, pork products, shellfish and raw fish (household rules)
_EXCLUDED_STEMS = (
    "rindfleisch", "rinder", "rinds", "rind", "kalb", "schwein", "lamm", "hirsch", "wildschwein",
    "wildfleisch", "speck", "bacon", "pancetta", "schinken", "prosciutto", "salami", "chorizo",
    "mortadella", "hackfleisch", "gehacktes", "hack", "mett", "steak", "rumpsteak", "entrecote",
    "schnitzel", "schmorbraten", "braten", "bratwurst", "würstchen", "wiener", "leberkäse",
    "innereien", "niere", "pastete", "garnele", "shrimp", "scampi", "krabbe", "hummer",
    "muschel", "tintenfisch", "sushi", "sashimi", "tatar",
)
# Matched anywhere in a word: liver and sausage in any compound ("Hähnchenleber", "Bratwurst")
_EXCLUDED_ANYWHERE = ("leber", "wurst")

_DESSERT_STEMS = (
    "kuchen", "torte", "tarte", "muffin", "keks", "brownie", "dessert", "eiscreme",
    "tiramisu", "pudding", "mousse", "panna cotta", "cheesecake", "cupcake", "crumble",
    "strudel", "waffel", "plätzchen", "schoko", "nutella", "süße", "riegel", "pancake",
    "crêpe", "milchreis", "grießbrei", "kompott", "smoothie", "cocktail", "marmelade",
    "eis", "saft", "shake",
)
# Savory dishes whose names contain a dessert word
_SAVORY_EXCEPTIONS = ("reibekuchen", "kartoffelkuchen", "gemüsekuchen", "herzhafte", "herzhafter")

# Protein sources that make a recipe count as "high protein"
_PROTEIN_STEMS = (
    "ei", "eier", "rührei", "spiegelei", "linse", "kichererbse", "bohne", "bohnen", "edamame",
    "tofu", "tempeh", "seitan", "quark", "skyr", "hüttenkäse", "joghurt", "parmesan", "feta", "halloumi",
    "hähnchen", "hühnchen", "huhn", "pute", "putenbrust", "lachs",
    "kabeljau", "seelachs", "forelle", "thunfisch", "fisch", "zander", "dorsch",
)


def _pattern(stems: tuple[str, ...], anywhere: bool = False) -> re.Pattern:
    alt = "|".join(re.escape(s) for s in sorted(stems, key=len, reverse=True))
    return re.compile(rf"(?:{alt})" if anywhere else rf"(?<![a-zäöüß])(?:{alt})")


_EXCLUDED_RE = _pattern(_EXCLUDED_STEMS)
_EXCLUDED_ANY_RE = _pattern(_EXCLUDED_ANYWHERE, anywhere=True)
# Short or ambiguous words ("eis", "hack", "ei", "rind") must be whole words
_WHOLE_WORD_ONLY = {"eis", "hack", "ei", "rind", "mett", "wiener", "saft", "shake"}
_DESSERT_RE = _pattern(tuple(s for s in _DESSERT_STEMS if s not in _WHOLE_WORD_ONLY), anywhere=True)


def _text(recipe: dict) -> str:
    return (recipe.get("name", "") + " " + " ".join(str(i) for i in recipe.get("ingredients", []))).lower()


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zäöüß]+", text))


def exclusion_reason(recipe: dict) -> str | None:
    """Why a recipe is rejected (red meat, offal, shellfish, dessert), or None if it is fine."""
    text = _text(recipe)
    tokens = _tokens(text)
    whole = tokens & _WHOLE_WORD_ONLY
    if whole & {"hack", "rind", "mett", "wiener"}:
        return f"fleisch: {sorted(whole)[0]}"
    if m := _EXCLUDED_RE.search(" ".join(t for t in tokens if t not in _WHOLE_WORD_ONLY)):
        return f"fleisch/schalentier: {m.group(0)}"
    if m := _EXCLUDED_ANY_RE.search(text):
        return f"innereien/wurst: {m.group(0)}"
    name_tokens = _tokens(recipe.get("name", "").lower())
    if name_tokens & {"eis", "saft", "shake"}:
        return "dessert/getraenk"
    name = recipe.get("name", "").lower()
    for ok in _SAVORY_EXCEPTIONS:
        name = name.replace(ok, "")
    if m := _DESSERT_RE.search(name):
        return f"dessert: {m.group(0)}"
    return None


def protein_sources(recipe: dict) -> set[str]:
    tokens = _tokens(_text(recipe))
    hits = set()
    for stem in _PROTEIN_STEMS:
        if stem in {"ei", "eier"}:
            if tokens & {"ei", "eier"}:
                hits.add("ei")
        elif any(t.startswith(stem) or t.endswith(stem) for t in tokens):
            hits.add(stem)
    return hits


def is_high_protein(recipe: dict) -> bool:
    return bool(protein_sources(recipe))


def is_allowed(recipe: dict) -> bool:
    """No red meat / offal / shellfish / dessert, and at least one real protein source."""
    return exclusion_reason(recipe) is None and is_high_protein(recipe)
