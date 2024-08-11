from dataclasses import dataclass
from typing import Callable, TypeAlias, Protocol
from itertools import combinations_with_replacement


IngredientId: TypeAlias = str


@dataclass
class Ingredient:
    """Holds information about ingredient.

    In this context we simply care about name, calories and macros.

    Properties:
    - carbohydrates: amount of carbohydrates per gram.
    - proteins: amount of proteins per gram.
    - fats: amount of fats per gram.
    - kilocalories: amount of kilocalories per gram.
    """
    id: IngredientId
    carbohydrates: float
    proteins: float
    fats: float
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

    def contains(self, ingredient: Ingredient):
        return any([i[1] == ingredient for i in self.ingredients])


Menu: TypeAlias = list[Recipe]


class DietaryPreference(Protocol):
    """Protocol used for dietary preferences.

    It's basically a "cost" function: return high number to restrict a given
    menu candidate.
    """
    def __call__(self, menu: Menu) -> float:
        ...


def create_menu_brute_force(
    recipes: Menu, preferences: Callable[[Menu], float], size: int
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
    return min(combinations_with_replacement(recipes, size), key=preferences)
