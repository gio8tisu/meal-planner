from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from create_menu import Ingredient, IngredientId, Recipe, RecipeId


@dataclass
class RecipeDTO:
    name: str
    ingredients: list[tuple[float, IngredientId]]
    yield_: int


class IngredientRepository(Protocol):
    def find(self, ingredient_id: IngredientId) -> Ingredient | None: ...


class RecipeRepository(Protocol):
    def find(self, recipe_id: RecipeId) -> Recipe | None: ...

    def add(self, recipe: Recipe): ...


class IngredientNotFound(Exception):
    pass


class RecipeNotFound(Exception):
    pass


class GetRecipeUseCase:
    def __init__(self, recipe_repository: RecipeRepository):
        self.recipe_repository = recipe_repository

    def __call__(self, recipe_id: RecipeId) -> Recipe:
        recipe = self.recipe_repository.find(recipe_id)
        if recipe is None:
            raise RecipeNotFound()
        return recipe


class CreateRecipeUseCase:
    def __init__(self, recipe_repository: RecipeRepository, ingredient_repository: IngredientRepository):
        self.recipe_repository = recipe_repository
        self.ingredient_repository = ingredient_repository

    def __call__(self, new_recipe: RecipeDTO) -> Recipe:
        ingredients = [
            (quantity, self.ingredient_repository.find(id))
            for quantity, id in new_recipe.ingredients
        ]
        if any(i[1] is None for i in ingredients):
            raise IngredientNotFound()
        recipe = Recipe(
            id=uuid4(),
            name=new_recipe.name,
            ingredients=ingredients,  # type: ignore
            yield_=new_recipe.yield_,
        )
        self.recipe_repository.add(recipe)
        return recipe
