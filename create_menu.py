from dataclasses import dataclass
from typing import TypeAlias, Protocol, Iterable
from itertools import combinations_with_replacement
from uuid import UUID

from create_recipes import Recipe, RecipeRepository


MenuId: TypeAlias = UUID


@dataclass
class Menu:
    id: MenuId
    meals: list[Recipe]


class DietaryPreference(Protocol):
    """Protocol used for dietary preferences.

    It's basically a "cost" function: return high number to restrict a given
    menu candidate.
    """

    def __call__(self, recipes: Iterable[Recipe]) -> float: ...


def select_recipes_brute_force(
    recipes: list[Recipe], size: int, preferences: DietaryPreference | None = None
) -> list[Recipe]:
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
    return list(
        min(
            combinations_with_replacement(recipes, size),
            key=preferences or (lambda recipe: 0),
        )
    )
