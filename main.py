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
    MacroNutrients,
)
from create_menu import (
    Menu,
    MenuId,
    GetMenuUseCase,
    CreateMenuUseCase,
    MenuNotFound,
    CannotCreateMenu,
    DietaryPreferenceDTO,
    DietaryPreferenceNotValid,
)
from repositories import (
    InMemoryRecipeRepository,
    InMemoryMenuRepository,
    InMemoryIngredientRepository,
)

app = FastAPI()

recipe_repo = InMemoryRecipeRepository.from_file("data/recipes.json")
ingredient_repo = InMemoryIngredientRepository.from_file("data/ingredients.json")
menu_repo = InMemoryMenuRepository()
get_recipe = GetRecipeUseCase(recipe_repo)
create_recipe = CreateRecipeUseCase(recipe_repo, ingredient_repo)
get_menu = GetMenuUseCase(menu_repo)
create_menu = CreateMenuUseCase(recipe_repo, menu_repo)


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


class MenuResponse(BaseModel):
    id: MenuId
    meals: list[RecipeResponse]

    @staticmethod
    def from_menu(menu: Menu) -> "MenuResponse":
        meals = [RecipeResponse.from_recipe(r) for r in menu.meals]
        return MenuResponse(id=menu.id, meals=meals)


class MenuRequest(BaseModel):
    size: int = 7
    preferences: list[DietaryPreferenceDTO] = []


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
        return JSONResponse(
            status_code=404, content={"message": "Ingredient not found"}
        )


@app.get(
    "/menus/{menu_id}",
    response_model=MenuResponse,
    responses={404: {"model": Message}},
)
async def get_menu_endpoint(menu_id: MenuId):
    try:
        menu = get_menu(menu_id)
        return MenuResponse.from_menu(menu)
    except MenuNotFound:
        return JSONResponse(status_code=404, content={"message": "Menu not found"})


@app.post("/menus", response_model=MenuResponse, responses={404: {"model": Message}})
async def create_menu_endpoint(menu_request: MenuRequest):
    try:
        menu = create_menu(menu_request.size, menu_request.preferences)
        return MenuResponse.from_menu(menu)
    except DietaryPreferenceNotValid:
        return JSONResponse(
            status_code=400,
            content={"message": "Provided dietary preference is not valid"},
        )
    except CannotCreateMenu:
        return JSONResponse(status_code=500, content={"message": "Cannot create menu"})
