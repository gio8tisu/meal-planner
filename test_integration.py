import unittest

from create_menu import (
    create_menu_brute_force,
    Ingredient,
    IngredientId,
    Recipe,
    RecipeId,
    MacroNutrients,
)
from preferences import RestrictIngredient, MacroPreferences, KilocaloriesPreferences


bread = Ingredient(
    id="bread",
    macronutrients=MacroNutrients(
        carbohydrates=200,
        proteins=100,
        fats=50,
    ),
    kilocalories=100,
)
chicken = Ingredient(
    id="chicken",
    macronutrients=MacroNutrients(
        carbohydrates=0,
        proteins=100,
        fats=10,
    ),
    kilocalories=150,
)
lettuce = Ingredient(
    id="lettuce",
    macronutrients=MacroNutrients(
        carbohydrates=10,
        proteins=20,
        fats=0,
    ),
    kilocalories=10,
)
ground_beef = Ingredient(
    id="ground_beef",
    macronutrients=MacroNutrients(
        carbohydrates=0,
        proteins=100,
        fats=100,
    ),
    kilocalories=300,
)

salad_recipe = Recipe(
    id=RecipeId("12345678123456781234567812345678"),
    name="Chicken salad",
    ingredients=[
        (100, lettuce),
        (10, bread),
        (20, chicken),
    ],
    yield_=2,
)
chicken_sandwich_recipe = Recipe(
    id=RecipeId("23456781234567812345678123456781"),
    name="Chicken sandwich",
    ingredients=[
        (30, lettuce),
        (70, bread),
        (150, chicken),
    ],
    yield_=1,
)
hamburger_recipe = Recipe(
    id=RecipeId("34567812345678123456781234567812"),
    name="Burger",
    ingredients=[
        (30, lettuce),
        (100, bread),
        (150, ground_beef),
    ],
    yield_=1,
)


class TestIntegration(unittest.TestCase):
    def test_create_menu_no_preferences(self):
        create_menu_brute_force(
            [salad_recipe, chicken_sandwich_recipe, hamburger_recipe], 7
        )

    def test_create_menu_with_alergen(self):
        preference = RestrictIngredient(IngredientId("ground_beef"))
        menu = create_menu_brute_force(
            [hamburger_recipe, chicken_sandwich_recipe, salad_recipe], 7, preference
        )

        self.assertNotIn(hamburger_recipe, menu)

    def test_create_menu_diet(self):
        preference = KilocaloriesPreferences(100)
        menu = create_menu_brute_force(
            [hamburger_recipe, chicken_sandwich_recipe, salad_recipe], 1, preference
        )

        self.assertEqual(salad_recipe, menu[0])

    def test_create_menu_fit(self):
        preference = MacroPreferences(
            carbohydrates=1000,
            proteins=2000,
            fats=100,
        )
        menu = create_menu_brute_force(
            [hamburger_recipe, salad_recipe, chicken_sandwich_recipe], 7, preference
        )

        self.assertIn(chicken_sandwich_recipe, menu)
        self.assertNotIn(hamburger_recipe, menu)
