import unittest

from preferences import (
    RestrictIngredient,
    MacroPreferences,
    KilocaloriesPreferences,
    DietaryPreferenceCombination,
    create_preferences,
    DietaryPreferenceDTO,
)
from create_menu import Recipe
from create_recipes import Ingredient, IngredientId, RecipeId, MacroNutrients


test_ingredient = Ingredient(
    id="forbid",
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


class RestrictIngredientTestCase(unittest.TestCase):
    def test_allowed_returns_0(self):
        id = IngredientId("allow")
        menu = [test_recipe]

        preference = RestrictIngredient(id)
        cost = preference(menu)

        self.assertEqual(cost, 0)

    def test_forbidden_returns_infinite(self):
        id = IngredientId("forbid")
        menu = [test_recipe]

        preference = RestrictIngredient(id)
        cost = preference(menu)

        self.assertEqual(cost, float("inf"))


class MacroPreferencesTestCase(unittest.TestCase):
    def test_lower_carbs(self):
        target_carbs = 100
        menu = [test_recipe]

        preference = MacroPreferences(target_carbs, 0, 0)
        cost = preference(menu)

        # We are `target_carbs` short, that's the cost.
        self.assertEqual(cost, target_carbs)

    def test_higher_carbs(self):
        target_carbs = 30
        bread = Ingredient(
            id="bread",
            macronutrients=MacroNutrients(
                carbohydrates=100,
                proteins=0,
                fats=0,
            ),
            kilocalories=0,
        )
        test_recipe = Recipe(
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(100, bread)],
            yield_=1,
        )
        menu = [test_recipe]

        preference = MacroPreferences(target_carbs, 0, 0)
        cost = preference(menu)

        # We are 70 carbs over, that's the cost.
        self.assertEqual(cost, 70)

    def test_sums_recipes(self):
        target_carbs = 100
        target_proteins = 50
        bread = Ingredient(
            id="bread",
            macronutrients=MacroNutrients(
                carbohydrates=100,
                proteins=0,
                fats=0,
            ),
            kilocalories=0,
        )
        chicken = Ingredient(
            id="chicken",
            macronutrients=MacroNutrients(
                carbohydrates=50,
                proteins=target_proteins,
                fats=0,
            ),
            kilocalories=0,
        )
        bread_recipe = Recipe(
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(100, bread)],
            yield_=1,
        )
        chicken_recipe = Recipe(
            id=RecipeId("23456781234567812345678123456781"),
            name="test",
            ingredients=[(100, chicken)],
            yield_=1,
        )
        menu = [bread_recipe, chicken_recipe]

        preference = MacroPreferences(target_carbs, target_proteins, 0)
        cost = preference(menu)

        # We are spot-on on protein and 50 carbs over, that's the cost.
        self.assertEqual(cost, 50)


class KilocaloriesPreferencesTestCase(unittest.TestCase):
    def test_lower(self):
        target = 100
        menu = [test_recipe]

        preference = KilocaloriesPreferences(target)
        cost = preference(menu)

        # We are `target` short, that's the cost.
        self.assertEqual(cost, target)

    def test_higher_carbs(self):
        target = 30
        bread = Ingredient(
            id="bread",
            macronutrients=MacroNutrients(
                carbohydrates=100,
                proteins=0,
                fats=0,
            ),
            kilocalories=100,
        )
        test_recipe = Recipe(
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(100, bread)],
            yield_=1,
        )
        menu = [test_recipe]

        preference = KilocaloriesPreferences(target)
        cost = preference(menu)

        # We are 70 over, that's the cost.
        self.assertEqual(cost, 70)

    def test_sums_recipes(self):
        target = 100
        bread = Ingredient(
            id="bread",
            macronutrients=MacroNutrients(
                carbohydrates=100,
                proteins=0,
                fats=0,
            ),
            kilocalories=100,
        )
        chicken = Ingredient(
            id="chicken",
            macronutrients=MacroNutrients(
                carbohydrates=50,
                proteins=100,
                fats=0,
            ),
            kilocalories=50,
        )
        bread_recipe = Recipe(
            id=RecipeId("12345678123456781234567812345678"),
            name="bread",
            ingredients=[(100, bread)],
            yield_=1,
        )
        chicken_recipe = Recipe(
            id=RecipeId("23456781234567812345678123456781"),
            name="chicken",
            ingredients=[(100, chicken)],
            yield_=1,
        )
        menu = [bread_recipe, chicken_recipe]

        preference = KilocaloriesPreferences(target)
        cost = preference(menu)

        # We are 50 kcal over (from chicken).
        self.assertEqual(cost, 50)


class PreferencesCombinationTestCase(unittest.TestCase):
    def test_empty(self):
        preference = DietaryPreferenceCombination([])
        cost = preference([])

        self.assertEqual(cost, 0)

    def test_sums(self):
        preference = DietaryPreferenceCombination(
            [
                lambda x: 1,
                lambda x: 2,
            ]
        )
        cost = preference([])

        # Sum of 1 and 2.
        self.assertEqual(cost, 3)


class CreatePreferencesTestCase(unittest.TestCase):
    def test_invalid_type(self):
        preference = DietaryPreferenceDTO(
            type_="invalid",
            parameters={},
        )
        self.assertRaises(ValueError, create_preferences, [preference])

    def test_restrict_ingredient_invalid_params(self):
        preference = DietaryPreferenceDTO(
            type_="restrict-ingredient",
            parameters={"ingredient": 0},
        )

        self.assertRaises(TypeError, create_preferences, [preference])

    def test_restrict_ingredient(self):
        preference = DietaryPreferenceDTO(
            type_="restrict-ingredient",
            parameters={"ingredient_id": 0},
        )

        preferences = create_preferences([preference])

        expected_preference = RestrictIngredient(ingredient_id=0)
        self.assertEqual(preferences([]), expected_preference([]))

    def test_macro_preferences(self):
        preference = DietaryPreferenceDTO(
            type_="macro-preferences",
            parameters={
                "carbohydrates": 0,
                "proteins": 0,
                "fats": 0,
            },
        )

        preferences = create_preferences([preference])

        expected_preference = MacroPreferences(
            carbohydrates=0,
            proteins=0,
            fats=0,
        )
        self.assertEqual(preferences([]), expected_preference([]))

    def test_kilocalories_preferences(self):
        preference = DietaryPreferenceDTO(
            type_="kilocalories-preferences",
            parameters={"kilocalories": 0},
        )

        preferences = create_preferences([preference])

        expected_preference = KilocaloriesPreferences(kilocalories=0)
        self.assertEqual(preferences([]), expected_preference([]))
