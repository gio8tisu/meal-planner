import unittest

from create_menu import (
    select_recipes_brute_force,
)
from create_recipes import (
    Recipe,
    Ingredient,
    RecipeId,
    MacroNutrients,
)


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
    id=RecipeId("12345678123456781234567812345678"),
    name="test",
    ingredients=[(1, test_ingredient)],
    yield_=1,
)


class BruteForceTestCase(unittest.TestCase):
    def test_invalid_size_raises_error(self):
        recipes = [test_recipe]
        size = 0

        self.assertRaises(ValueError, select_recipes_brute_force, recipes, size)

    def test_empty_recipes_raises_error(self):
        recipes = []
        size = 1

        self.assertRaises(ValueError, select_recipes_brute_force, recipes, size)

    def test_single_recipe_size_1(self):
        recipes = [test_recipe]
        size = 1

        menu = select_recipes_brute_force(recipes, size)

        self.assertEqual(len(menu), 1)
        self.assertEqual(menu[0], test_recipe)

    def test_single_recipe_size_3(self):
        recipes = [test_recipe]
        size = 3

        menu = select_recipes_brute_force(recipes, size)

        self.assertEqual(len(menu), 3)
        self.assertEqual(menu[0], test_recipe)
        self.assertEqual(menu[1], test_recipe)
        self.assertEqual(menu[2], test_recipe)

    def test_2_recipes_size_3(self):
        recipes = [
            Recipe(
                id=RecipeId("12345678123456781234567812345678"),
                name="test",
                ingredients=[(1, test_ingredient)],
                yield_=1,
            ),
            Recipe(
                id=RecipeId("23456781234567812345678123456781"),
                name="test",
                ingredients=[
                    (1, test_ingredient),
                    (2, test_ingredient),
                ],
                yield_=1,
            ),
        ]
        size = 3

        menu = select_recipes_brute_force(recipes, size)

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
                id=RecipeId("12345678123456781234567812345678"),
                name="forbidden recipe",
                ingredients=[(1, forbidden_ingredient)],
                yield_=1,
            ),
            # Allowed.
            Recipe(
                id=RecipeId("23456781234567812345678123456781"),
                name="allowed recipe",
                ingredients=[(1, allowed_ingredient)],
                yield_=1,
            ),
        ]

        menu = select_recipes_brute_force(recipes, 1, forbid_ingredient)

        self.assertEqual(len(menu), 1)
        self.assertTrue(menu[0] == recipes[1])
