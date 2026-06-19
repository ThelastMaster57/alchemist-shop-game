# Dummy potions.py module for testing

INGREDIENTS = ["dragonsblood", "ironbark", "moonflower", "glowmoss", "mistdew", "voidash"]

POTIONS = {
    "Health Potion": {
        "recipe": ["dragonsblood", "mistdew"]
    },
    "Speed Potion": {
        "recipe": ["moonflower", "glowmoss"]
    },
    "Strength Potion": {
        "recipe": ["ironbark", "voidash"]
    }
}

def check_recipe(ingredients):
    """Returns the potion name if ingredients match a recipe, else None.
    Supports both lists and dictionaries of counts.
    """
    if isinstance(ingredients, dict):
        flat_list = []
        for ing, count in ingredients.items():
            flat_list.extend([ing] * count)
        ingredients = flat_list

    s_ingredients = sorted(ingredients)
    for name, data in POTIONS.items():
        recipe = data["recipe"] if isinstance(data, dict) and "recipe" in data else data
        if sorted(recipe) == s_ingredients:
            return name
    return None