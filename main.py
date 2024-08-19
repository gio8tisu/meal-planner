from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from create_recipes import (
    IngredientId,
    Recipe,
    RecipeDTO,
    RecipeId,
    CreateRecipeUseCase,
    GetRecipeUseCase,
    RecipeNotFound,
    IngredientNotFound,
)
from create_menu import MacroNutrients
from repositories import InMemoryRecipeRepository, InMemoryIngredientRepository

app = FastAPI()

recipe_repo = InMemoryRecipeRepository.from_file("data/recipes.json")
ingredient_repo = InMemoryIngredientRepository.from_file("data/ingredients.json")
get_recipe = GetRecipeUseCase(recipe_repo)
create_recipe = CreateRecipeUseCase(recipe_repo, ingredient_repo)


class Message(BaseModel):
    message: str


class RecipeResponse(BaseModel):
    id: RecipeId
    name: str
    ingredients: list[IngredientId]
    yield_: int
    macros_per_serving: MacroNutrients
    kilocalories_per_serving: float

    @staticmethod
    def from_recipe(recipe: Recipe) -> "RecipeResponse":
        return RecipeResponse(
            id=recipe.id,
            name=recipe.name,
            ingredients=[i.id for _, i in recipe.ingredients],
            yield_=recipe.yield_,
            macros_per_serving=recipe.macros_per_serving(),
            kilocalories_per_serving=recipe.kilocalories_per_serving(),
        )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse,
    responses={404: {"model": Message}},
)
async def get_recipe_endpoint(recipe_id: RecipeId):
    try:
        recipe = get_recipe(recipe_id)
        return RecipeResponse.from_recipe(recipe)
    except RecipeNotFound:
        return JSONResponse(status_code=404, content={"message": "Recipe not found"})


@app.post(
    "/recipes", response_model=RecipeResponse, responses={404: {"model": Message}}
)
async def create_recipe_endpoint(recipe_request: RecipeDTO):
    try:
        recipe = create_recipe(recipe_request)
        return RecipeResponse.from_recipe(recipe)
    except IngredientNotFound:
        return JSONResponse(status_code=404, content={"message": "Recipe not found"})
