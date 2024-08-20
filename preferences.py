from typing import Iterable

from create_menu import Recipe
from create_recipes import IngredientId


class RestrictIngredient:
    ingredient_id: IngredientId

    def __init__(self, ingredient_id: IngredientId):
        self.ingredient_id = ingredient_id

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        for recipe in recipes:
            if recipe.contains(self.ingredient_id):
                return float("inf")
        return 0


class MacroPreferences:
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


class KilocaloriesPreferences:
    kilocalories: float

    def __init__(self, kilocalories: float):
        self.kilocalories = kilocalories

    def __call__(self, recipes: Iterable[Recipe]) -> float:
        total_kilocalories = sum(recipe.kilocalories_per_serving() for recipe in recipes)
        return abs(self.kilocalories - total_kilocalories)
