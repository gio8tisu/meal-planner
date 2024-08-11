import unittest

from create_menu import create_menu_brute_force, Ingredient, IngredientId, Recipe, MacroNutrients
from preferences import RestrictIngredient, MacroPreferences, KilocaloriesPreferences


bread = Ingredient(
    id="bread",
    macronutrients=MacroNutrients(
        carbohydrates=2,
        proteins=1,
        fats=0.5,
    ),
    kilocalories=1,
)
chicken = Ingredient(
    id="chicken",
    macronutrients=MacroNutrients(
        carbohydrates=0,
        proteins=1,
        fats=0.1,
    ),
    kilocalories=1.5,
)
lettuce = Ingredient(
    id="lettuce",
    macronutrients=MacroNutrients(
        carbohydrates=0.1,
        proteins=0.2,
        fats=0,
    ),
    kilocalories=0.1,
)
ground_beef = Ingredient(
    id="ground_beef",
    macronutrients=MacroNutrients(
        carbohydrates=0,
        proteins=1,
        fats=1,
    ),
    kilocalories=3,
)

salad_recipe = Recipe(
    ingredients=[
        (100, lettuce),
        (10, bread),
        (20, chicken),
    ],
    yield_=2,
)
chicken_sandwich_recipe = Recipe(
    ingredients=[
        (30, lettuce),
        (70, bread),
        (150, chicken),
    ],
    yield_=1,
)
hamburger_recipe = Recipe(
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
            [salad_recipe, chicken_sandwich_recipe, hamburger_recipe],
            7
        )

    def test_create_menu_with_alergen(self):
        preference = RestrictIngredient(IngredientId("ground_beef"))
        menu = create_menu_brute_force(
            [hamburger_recipe, chicken_sandwich_recipe, salad_recipe],
            7,
            preference
        )

        self.assertNotIn(hamburger_recipe, menu)

    def test_create_menu_diet(self):
        preference = KilocaloriesPreferences(100)
        menu = create_menu_brute_force(
            [hamburger_recipe, chicken_sandwich_recipe, salad_recipe],
            1,
            preference
        )

        self.assertEqual(salad_recipe, menu[0])

    def test_create_menu_fit(self):
        preference = MacroPreferences(
            carbohydrates=1000,
            proteins=2000,
            fats=100,
        )
        menu = create_menu_brute_force(
            [hamburger_recipe, salad_recipe, chicken_sandwich_recipe],
            7,
            preference
        )

        self.assertIn(chicken_sandwich_recipe, menu)
        self.assertNotIn(hamburger_recipe, menu)
