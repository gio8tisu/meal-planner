import unittest
from unittest import mock

from create_menu import create_menu_brute_force, Ingredient, Recipe, MacroNutrients


test_ingredient = Ingredient(
    id="Test",
    macronutrients=MacroNutrients(
        carbohydrates=0,
        proteins=0,
        fats=0,
    ),
    kilocalories=0,
)
test_recipe = Recipe(
    ingredients=[
        (1, test_ingredient)
    ],
    yield_=1,
)


class RecipeTestCase(unittest.TestCase):
    def test_recipe_contains_ingredient(self):
        self.assertTrue(test_recipe.contains(test_ingredient))

    def test_recipe_contains_ingredient_id(self):
        self.assertTrue(test_recipe.contains(test_ingredient.id))

    def test_recipe_macros_per_serving_empty(self):
        macros = test_recipe.macros_per_serving()

        self.assertEqual(macros.carbohydrates, 0)
        self.assertEqual(macros.proteins, 0)
        self.assertEqual(macros.fats, 0)

    def test_recipe_macros_per_serving_multiplies_by_weight(self):
        test_ingredient = Ingredient(
            id="Test",
            macronutrients=MacroNutrients(
                carbohydrates=10,
                proteins=10,
                fats=10,
            ),
            kilocalories=0,
        )
        test_recipe = Recipe(
            ingredients=[
                (2, test_ingredient)
            ],
            yield_=1,
        )

        macros = test_recipe.macros_per_serving()

        self.assertEqual(macros.carbohydrates, 20)
        self.assertEqual(macros.proteins, 20)
        self.assertEqual(macros.fats, 20)

    def test_recipe_macros_per_serving_divides_by_yield(self):
        test_ingredient = Ingredient(
            id="Test",
            macronutrients=MacroNutrients(
                carbohydrates=10,
                proteins=10,
                fats=10,
            ),
            kilocalories=0,
        )
        test_recipe = Recipe(
            ingredients=[
                (1, test_ingredient)
            ],
            yield_=2,
        )

        macros = test_recipe.macros_per_serving()

        self.assertEqual(macros.carbohydrates, 5)
        self.assertEqual(macros.proteins, 5)
        self.assertEqual(macros.fats, 5)

    def test_recipe_kilocalories_per_serving_empty(self):
        kilocalories = test_recipe.kilocalories_per_serving()

        self.assertEqual(kilocalories, 0)

    def test_recipe_kilocalories_per_serving_multiplies_by_weight(self):
        test_ingredient = Ingredient(
            id="Test",
            macronutrients=MacroNutrients(
                carbohydrates=0,
                proteins=0,
                fats=0,
            ),
            kilocalories=10,
        )
        test_recipe = Recipe(
            ingredients=[
                (2, test_ingredient)
            ],
            yield_=1,
        )

        kilocalories = test_recipe.kilocalories_per_serving()

        self.assertEqual(kilocalories, 20)

    def test_recipe_macros_per_serving_divides_by_yield(self):
        test_ingredient = Ingredient(
            id="Test",
            macronutrients=MacroNutrients(
                carbohydrates=0,
                proteins=0,
                fats=0,
            ),
            kilocalories=10,
        )
        test_recipe = Recipe(
            ingredients=[
                (1, test_ingredient)
            ],
            yield_=2,
        )

        kilocalories = test_recipe.kilocalories_per_serving()
        self.assertEqual(kilocalories, 5)


class BruteForceTestCase(unittest.TestCase):
    def test_invalid_size_raises_error(self):
        recipes = [test_recipe]
        preferences = lambda menu: 0
        size = 0

        self.assertRaises(ValueError, create_menu_brute_force, recipes, preferences, size)

    def test_empty_recipes_raises_error(self):
        recipes = []
        preferences = lambda menu: 0
        size = 1

        self.assertRaises(ValueError, create_menu_brute_force, recipes, preferences, size)

    def test_single_recipe_size_1(self):
        recipes = [test_recipe]
        preferences = lambda menu: 0
        size = 1

        menu = create_menu_brute_force(recipes, preferences, size)

        self.assertEqual(len(menu), 1)
        self.assertEqual(menu[0], test_recipe)

    def test_single_recipe_size_3(self):
        recipes = [test_recipe]
        preferences = lambda menu: 0
        size = 3

        menu = create_menu_brute_force(recipes, preferences, size)

        self.assertEqual(len(menu), 3)
        self.assertEqual(menu[0], test_recipe)
        self.assertEqual(menu[1], test_recipe)
        self.assertEqual(menu[2], test_recipe)

    def test_2_recipes_size_3(self):
        recipes = [
            Recipe(
                ingredients=[
                    (1, test_ingredient)
                ],
                yield_=1,
            ),
            Recipe(
                ingredients=[
                    (1, test_ingredient),
                    (2, test_ingredient),
                ],
                yield_=1,
            ),
        ]
        preferences = lambda menu: 0
        size = 3

        menu = create_menu_brute_force(recipes, preferences, size)

        self.assertEqual(len(menu), 3)
        for recipe in menu:
            self.assertTrue(recipe in recipes)

    def test_ingredient_preferences(self):
        allowed_ingredient = Ingredient(
            id="Allowed",
            macronutrients=MacroNutrients(
                carbohydrates=10,
                proteins=10,
                fats=10,
            ),
            kilocalories=10,
        )
        forbidden_ingredient = Ingredient(
            id="Forbidden",
            macronutrients=MacroNutrients(
                carbohydrates=10,
                proteins=10,
                fats=10,
            ),
            kilocalories=10,
        )
        def forbid_ingredient(menu):
            for recipe in menu:
                if recipe.contains(forbidden_ingredient):
                    return float("inf")
            return 0
        # Having forbidden recipe first, forces it to be checked first.
        recipes = [
            # Forbidden.
            Recipe(
                ingredients=[(1, forbidden_ingredient)],
                yield_=1,
            ),
            # Allowed.
            Recipe(
                ingredients=[(1, allowed_ingredient)],
                yield_=1,
            ),
        ]

        menu = create_menu_brute_force(recipes, forbid_ingredient, 1)

        self.assertEqual(len(menu), 1)
        self.assertTrue(menu[0] == recipes[1])
