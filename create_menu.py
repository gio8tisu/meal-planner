from dataclasses import dataclass
from typing import TypeAlias, Protocol
from itertools import combinations_with_replacement
from uuid import UUID, uuid4

from create_recipes import Recipe, RecipeRepository
from preferences import DietaryPreference, DietaryPreferenceDTO, create_preferences


MenuId: TypeAlias = UUID


@dataclass
class Menu:
    id: MenuId
    meals: list[Recipe]


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


class MenuRepository(Protocol):
    def find(self, menu_id: MenuId) -> Menu | None: ...

    def add(self, menu: Menu): ...


class DietaryPreferenceNotValid(Exception):
    pass


class MenuNotFound(Exception):
    pass


class CannotCreateMenu(Exception):
    pass


class GetMenuUseCase:
    def __init__(self, menu_repository: MenuRepository):
        self.menu_repository = menu_repository

    def __call__(self, menu_id: MenuId) -> Menu:
        menu = self.menu_repository.find(menu_id)
        if menu is None:
            raise MenuNotFound()
        return menu


class CreateMenuUseCase:
    def __init__(
        self, recipe_repository: RecipeRepository, menu_repository: MenuRepository
    ):
        self.recipe_repository = recipe_repository
        self.menu_repository = menu_repository

    def __call__(self, size: int, preferences_spec: list[DietaryPreferenceDTO]) -> Menu:
        recipes = self.recipe_repository.all()
        try:
            preferences = create_preferences(preferences_spec)
        except (ValueError, TypeError):
            raise DietaryPreferenceNotValid()
        try:
            meals = select_recipes_brute_force(recipes, size, preferences)
        except ValueError:
            raise CannotCreateMenu()
        menu = Menu(id=uuid4(), meals=meals)
        self.menu_repository.add(menu)
        return menu
