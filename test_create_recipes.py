from unittest import TestCase, mock

from create_recipes import (
    RecipeNotFound,
    IngredientNotFound,
    IngredientRepository,
    Recipe,
    RecipeId,
    RecipeRepository,
    CreateRecipeUseCase,
    GetRecipeUseCase,
    RecipeDTO,
    Ingredient,
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

class RecipeTestCase(TestCase):
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
                # Ingredient nutrients are defined per 100 grams.
                carbohydrates=10,
                proteins=10,
                fats=10,
            ),
            kilocalories=0,
        )
        test_recipe = Recipe(
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(200, test_ingredient)],
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
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(100, test_ingredient)],
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
        # Ingredient Kilocalories are defined per 100 grams.
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
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(200, test_ingredient)],
            yield_=1,
        )

        kilocalories = test_recipe.kilocalories_per_serving()

        self.assertEqual(kilocalories, 20)

    def test_recipe_kilocalories_per_serving_divides_by_yield(self):
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
            id=RecipeId("12345678123456781234567812345678"),
            name="test",
            ingredients=[(100, test_ingredient)],
            yield_=2,
        )

        kilocalories = test_recipe.kilocalories_per_serving()
        self.assertEqual(kilocalories, 5)


class TestGetRecipeUseCase(TestCase):
    def test_non_existing_recipe_id(self):
        mock_recipe_repo = mock.create_autospec(RecipeRepository)
        mock_recipe_repo.find.return_value = None

        use_case = GetRecipeUseCase(mock_recipe_repo)
        self.assertRaises(
            RecipeNotFound, use_case, "34516e5e-2d08-43a8-a640-3c8bede481fb"
        )

    def test_happy_path(self):
        pass


class TestCreateRecipeUseCase(TestCase):
    def test_happy_path(self):
        new_recipe = RecipeDTO(
            name="My super recipe",
            ingredients=[(100, "eggplant")],
            yield_=2,
        )
        eggplant = Ingredient(
            id="eggplant",
            macronutrients=(1, 2, 3),
            kilocalories=100,
        )
        mock_recipe_repo = mock.create_autospec(RecipeRepository)
        mock_ingredient_repo = mock.create_autospec(IngredientRepository)
        mock_ingredient_repo.find.return_value = eggplant

        use_case = CreateRecipeUseCase(mock_recipe_repo, mock_ingredient_repo)
        with mock.patch("create_recipes.uuid4", return_value="1234"):
            use_case(new_recipe)

        mock_recipe_repo.add.assert_called_with(
            Recipe(
                id="1234",
                name="My super recipe",
                ingredients=[
                    (100, eggplant),
                ],
                yield_=2,
            )
        )

    def test_non_existing_ingredient_id(self):
        new_recipe = RecipeDTO(
            name="My super recipe",
            ingredients=[(100, "eggplant")],
            yield_=2,
        )
        mock_recipe_repo = mock.create_autospec(RecipeRepository)
        mock_ingredient_repo = mock.create_autospec(IngredientRepository)
        mock_ingredient_repo.find.return_value = None

        use_case = CreateRecipeUseCase(mock_recipe_repo, mock_ingredient_repo)
        self.assertRaises(IngredientNotFound, use_case, new_recipe)
