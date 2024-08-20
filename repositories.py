import json
from typing import Any

from create_recipes import (
    Ingredient,
    IngredientId,
    MacroNutrients,
    Recipe,
    RecipeId,
    IngredientRepository,
    RecipeRepository,
)
from create_menu import Menu, MenuId, MenuRepository


def create_ingredient(ingredient_info: dict[str, Any]) -> Ingredient:
    return Ingredient(
        id=ingredient_info["id"],
        macronutrients=MacroNutrients(
            carbohydrates=ingredient_info["macronutrients"]["carbohydrates"],
            proteins=ingredient_info["macronutrients"]["proteins"],
            fats=ingredient_info["macronutrients"]["fats"],
        ),
        kilocalories=ingredient_info["kilocalories"],
    )


def create_recipe(recipe_info: dict[str, Any]) -> Recipe:
    return Recipe(
        id=recipe_info["id"],
        name=recipe_info["name"],
        yield_=recipe_info["yield"],
        ingredients=[
            (i[0], create_ingredient(i[1])) for i in recipe_info["ingredients"]
        ],
    )


class InMemoryIngredientRepository(IngredientRepository):
    def __init__(self, ingredients: list[dict[str, Any]]):
        self.ingredients = {i["id"]: create_ingredient(i) for i in ingredients}

    @staticmethod
    def from_file(path: str) -> "InMemoryIngredientRepository":
        with open(path) as f:
            ingredients = json.loads(f.read())
        return InMemoryIngredientRepository(ingredients)

    def find(self, ingredient_id: IngredientId) -> Ingredient | None:
        return self.ingredients.get(ingredient_id)


class InMemoryRecipeRepository(RecipeRepository):
    def __init__(self, recipes: list[dict[str, Any]]):
        self.recipes = {i["id"]: create_recipe(i) for i in recipes}

    @staticmethod
    def from_file(path: str) -> "InMemoryRecipeRepository":
        with open(path) as f:
            recipes = json.loads(f.read())
        return InMemoryRecipeRepository(recipes)

    def find(self, recipe_id: RecipeId) -> Recipe | None:
        return self.recipes.get(str(recipe_id))

    def all(self) -> list[Recipe]:
        return list(self.recipes.values())

    def add(self, recipe: Recipe):
        self.recipes[str(recipe.id)] = recipe


class InMemoryMenuRepository(MenuRepository):
    def __init__(self):
        self.menus = {}

    def find(self, menu_id: MenuId) -> Menu | None:
        return self.menus.get(str(menu_id))

    def add(self, menu: Menu):
        self.menus[str(menu.id)] = menu
