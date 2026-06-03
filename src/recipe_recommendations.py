"""Daily recipe recommendations with links back to source sites."""

from datetime import datetime


FASTING_RECIPES = [
    {
        "title": "Stewed Chickpeas (Revithkia)",
        "source": "Aphrodite's Kitchen",
        "url": "https://afroditeskitchen.com/recipe/spicy-chickpeas-spicy-revithkia/",
        "summary": "A Cypriot fasting dish built around chickpeas, tomato, herbs, and slow oven cooking.",
        "category": "Fasting recipe",
    },
    {
        "title": "Coconut Curry Lentils",
        "source": "Aphrodite's Kitchen",
        "url": "https://afroditeskitchen.com/recipe_category/lent-recipes/",
        "summary": "A vegan lentil idea from the fasting recipe collection; use the source page for the full recipe.",
        "category": "Fasting recipe",
    },
    {
        "title": "Lemon Rocket Penne",
        "source": "Aphrodite's Kitchen",
        "url": "https://afroditeskitchen.com/recipe_category/lent-recipes/",
        "summary": "A light pasta idea with lemon and rocket from the fasting recipe collection.",
        "category": "Fasting recipe",
    },
    {
        "title": "Carrot-Ginger Soup",
        "source": "Aphrodite's Kitchen",
        "url": "https://afroditeskitchen.com/recipe_category/lent-recipes/",
        "summary": "A warming soup option from the fasting recipe collection.",
        "category": "Fasting recipe",
    },
]

ANCIENT_RECIPES = [
    {
        "title": "Stoic Lentil Soup",
        "source": "Tasting History",
        "url": "https://www.tastinghistory.com/recipes/stoiclentilsoup",
        "summary": "A Greece/Rome ancient-inspired lentil soup connected with Stoic simplicity.",
        "category": "Ancient recipe",
    },
    {
        "title": "Roman Honey Glazed Mushrooms",
        "source": "Tasting History",
        "url": "https://www.tastinghistory.com/recipes/romanmushrooms",
        "summary": "An ancient Roman mushroom dish using honey, pepper, herbs, and savory sauce.",
        "category": "Ancient recipe",
    },
    {
        "title": "Savillum (Roman Cheesecake)",
        "source": "Tasting History",
        "url": "https://www.tastinghistory.com/recipes/savillum",
        "summary": "A Roman cheesecake sweetened with honey and finished with poppy seeds.",
        "category": "Ancient recipe",
    },
    {
        "title": "Roman Stuffed Dates",
        "source": "Tasting History",
        "url": "https://www.tastinghistory.com/recipes/romanstuffeddates",
        "summary": "Ancient Roman-style dates stuffed with nuts and cooked with honey.",
        "category": "Ancient recipe",
    },
]


def build_daily_recipes(date_text):
    """Return one fasting and one ancient recipe recommendation for a date."""
    date = datetime.strptime(str(date_text), "%Y-%m-%d").date()
    day_index = date.timetuple().tm_yday - 1
    return {
        "fasting": _select(FASTING_RECIPES, day_index),
        "ancient": _select(ANCIENT_RECIPES, day_index + date.year),
        "notice": (
            "Recipe text is not republished here. Follow the source links for the full recipes."
        ),
    }


def _select(items, index):
    item = dict(items[index % len(items)])
    item["review_required"] = True
    return item
