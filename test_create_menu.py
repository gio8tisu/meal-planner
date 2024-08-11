import unittest
from unittest import mock

from create_menu import create_menu_brute_force, Ingredient, Recipe


test_ingredient = Ingredient(
    name="Test",
    carbohydrates=0,
    proteins=0,
    fats=0,
    kilocalories=0,
)
test_recipe = Recipe(
    ingredients=[
        (1, test_ingredient)
    ],
    yield_=1,
)


class RecipeTestCase(unittest.TestCase):
    def test_recipe_contains(self):
        self.assertTrue(test_recipe.contains(test_ingredient))


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
            name="Allowed",
            carbohydrates=10,
            proteins=10,
            fats=10,
            kilocalories=10,
        )
        forbidden_ingredient = Ingredient(
            name="Forbidden",
            carbohydrates=10,
            proteins=10,
            fats=10,
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
