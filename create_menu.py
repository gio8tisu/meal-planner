from dataclasses import dataclass
from typing import Callable, TypeAlias, Protocol, NamedTuple
from itertools import combinations_with_replacement


class MacroNutrients(NamedTuple):
    carbohydrates: float
    proteins: float
    fats: float


IngredientId: TypeAlias = str


@dataclass
class Ingredient:
    """Holds information about ingredient.

    In this context we simply care about name, calories and macros.

    Properties:
    - macronutrients: amount macronutrients per gram.
    - kilocalories: amount of kilocalories per gram.
    """
    id: IngredientId
    macronutrients: MacroNutrients
    kilocalories: float


@dataclass
class Recipe:
    """Holds information about recipe.

    In this context we simply care about list of ingredients and quantities.

    Properties:
    - ingredients: list of (quantity, ingredient) tuples the recipe calls for.
    - yields_: number servings the recipe provides.
    """
    ingredients: list[tuple[float, Ingredient]]
    yield_: int

    def contains(self, ingredient: Ingredient | IngredientId) -> bool:
        ingredient_id = ingredient if isinstance(ingredient, IngredientId) else ingredient.id
        return any([i[1].id == ingredient_id for i in self.ingredients])

    def macros_per_serving(self) -> MacroNutrients:
        (
            total_carbohydrate,
            total_protein,
            total_fat
        ) = 0, 0, 0
        for weight, ingredient in self.ingredients:
            carbohydrates, proteins, fats = ingredient.macronutrients
            total_carbohydrate += weight * carbohydrates
            total_protein += weight * proteins
            total_fat += weight * fats
        return MacroNutrients(
            total_carbohydrate / self.yield_,
            total_protein / self.yield_,
            total_fat / self.yield_
        )

    def kilocalories_per_serving(self) -> float:
        total_kilocalories = sum(
            w * i.kilocalories for w, i in self.ingredients
        )
        return total_kilocalories / self.yield_


Menu: TypeAlias = list[Recipe]


class DietaryPreference(Protocol):
    """Protocol used for dietary preferences.

    It's basically a "cost" function: return high number to restrict a given
    menu candidate.
    """
    def __call__(self, menu: Menu) -> float:
        ...


def create_menu_brute_force(
    recipes: Menu, size: int, preferences: Callable[[Menu], float] | None = None
) -> Menu:
    """Returns list of meals from preferences.

    Tests all combinations (with replacement) and returns the one that best
    fits preferences.

    In case there's a draw, return first tested combination (which depends on
    original ordering).

    Args:
    - recipes: List of possible recipes.
    - preferences: Returned list of meals should satisfy this preferences.
    - size: number of meals the menu should return.
    """
    if size < 1 or len(recipes) == 0:
        raise ValueError
    if preferences is None:
        preferences = lambda recipe: 0
    return min(combinations_with_replacement(recipes, size), key=preferences)
