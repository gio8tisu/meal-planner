from unittest import TestCase, mock

from create_recipes import RecipeNotFound, IngredientNotFound, IngredientRepository, Recipe, RecipeRepository, CreateRecipeUseCase, GetRecipeUseCase, RecipeDTO, Ingredient


class TestGetRecipeUseCase(TestCase):
    def test_non_existing_recipe_id(self):
        mock_recipe_repo = mock.create_autospec(RecipeRepository)
        mock_recipe_repo.find.return_value = None

        use_case = GetRecipeUseCase(mock_recipe_repo)
        self.assertRaises(RecipeNotFound, use_case, "34516e5e-2d08-43a8-a640-3c8bede481fb")

    def test_happy_path(self):
        pass

class TestCreateRecipeUseCase(TestCase):
    def test_happy_path(self):
        new_recipe = RecipeDTO(
            name="My super recipe",
            ingredients=[
                (100, "eggplant")
            ],
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
            ingredients=[
                (100, "eggplant")
            ],
            yield_=2,
        )
        mock_recipe_repo = mock.create_autospec(RecipeRepository)
        mock_ingredient_repo = mock.create_autospec(IngredientRepository)
        mock_ingredient_repo.find.return_value = None

        use_case = CreateRecipeUseCase(mock_recipe_repo, mock_ingredient_repo)
        self.assertRaises(IngredientNotFound, use_case, new_recipe)
