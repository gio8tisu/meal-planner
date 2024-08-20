from dataclasses import dataclass
from typing import TypeAlias, Protocol, NamedTuple
from uuid import UUID, uuid4


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
    - macronutrients: amount macronutrients per 100 gram.
    - kilocalories: amount of kilocalories per 100 gram.
    """

    id: IngredientId
    macronutrients: MacroNutrients
    kilocalories: float


RecipeId: TypeAlias = UUID


@dataclass
class Recipe:
    """Holds information about recipe.

    In this context we simply care about list of ingredients and quantities.

    Properties:
    - ingredients: list of (quantity, ingredient) tuples the recipe calls for.
    - yields_: number servings the recipe provides.
    """

    id: RecipeId
    name: str
    ingredients: list[tuple[float, Ingredient]]
    yield_: int

    def contains(self, ingredient: Ingredient | IngredientId) -> bool:
        ingredient_id = (
            ingredient if isinstance(ingredient, IngredientId) else ingredient.id
        )
        return any([i[1].id == ingredient_id for i in self.ingredients])

    def macros_per_serving(self) -> MacroNutrients:
        (total_carbohydrate, total_protein, total_fat) = 0.0, 0.0, 0.0
        for weight, ingredient in self.ingredients:
            carbohydrates, proteins, fats = ingredient.macronutrients
            total_carbohydrate += weight * carbohydrates / 100
            total_protein += weight * proteins / 100
            total_fat += weight * fats / 100
        return MacroNutrients(
            total_carbohydrate / self.yield_,
            total_protein / self.yield_,
            total_fat / self.yield_,
        )

    def kilocalories_per_serving(self) -> float:
        total_kilocalories = sum(w * i.kilocalories / 100 for w, i in self.ingredients)
        return total_kilocalories / self.yield_


@dataclass
class RecipeDTO:
    name: str
    ingredients: list[tuple[float, IngredientId]]
    yield_: int


class IngredientRepository(Protocol):
    def find(self, ingredient_id: IngredientId) -> Ingredient | None: ...


class RecipeRepository(Protocol):
    def find(self, recipe_id: RecipeId) -> Recipe | None: ...

    def all(self) -> list[Recipe]: ...

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
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        ingredient_repository: IngredientRepository,
    ):
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
