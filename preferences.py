from dataclasses import dataclass
from typing import Any, Iterable, Protocol

from create_recipes import IngredientId, Recipe


class DietaryPreference(Protocol):
    """Protocol used for dietary preferences.

    It's basically a "cost" function: return high number to restrict a given
    menu candidate.
    """

    def __call__(self, recipes: Iterable[Recipe]) -> float: ...


class RestrictIngredient(DietaryPreference):
    ingredient_id: IngredientId

    def __init__(self, ingredient_id: IngredientId):
        self.ingredient_id = ingredient_id

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        for recipe in recipes:
            if recipe.contains(self.ingredient_id):
                return float("inf")
        return 0


class MacroPreferences(DietaryPreference):
    carbohydrates: float
    proteins: float
    fats: float

    def __init__(self, carbohydrates: float, proteins: float, fats: float):
        self.carbohydrates = carbohydrates
        self.proteins = proteins
        self.fats = fats

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        (total_carbohydrates, total_proteins, total_fats) = 0.0, 0.0, 0.0
        for recipe in recipes:
            (carbohydrates, proteins, fats) = recipe.macros_per_serving()
            total_carbohydrates += carbohydrates
            total_proteins += proteins
            total_fats += fats
        return (
            abs(self.carbohydrates - total_carbohydrates)
            + abs(self.proteins - total_proteins)
            + abs(self.fats - total_fats)
        )


class KilocaloriesPreferences(DietaryPreference):
    kilocalories: float

    def __init__(self, kilocalories: float):
        self.kilocalories = kilocalories

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        total_kilocalories = sum(
            recipe.kilocalories_per_serving() for recipe in recipes
        )
        return abs(self.kilocalories - total_kilocalories)


class DietaryPreferenceCombination(DietaryPreference):
    preferences: list[DietaryPreference]

    def __init__(self, preferences: list[DietaryPreference]):
        self.preferences = preferences

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        return sum(p(recipes) for p in self.preferences)


@dataclass
class DietaryPreferenceDTO:
    type_: str
    parameters: dict[str, Any]


def create_preferences(
    preferences: Iterable[DietaryPreferenceDTO],
) -> DietaryPreferenceCombination:
    preferences_: list[DietaryPreference] = []
    for preference in preferences:
        match preference.type_:
            case "restrict-ingredient":
                preferences_.append(RestrictIngredient(**preference.parameters))
            case "macro-preferences":
                preferences_.append(MacroPreferences(**preference.parameters))
            case "kilocalories-preferences":
                preferences_.append(KilocaloriesPreferences(**preference.parameters))
            case _:
                raise ValueError
    return DietaryPreferenceCombination(preferences_)
