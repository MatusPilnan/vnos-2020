from http import HTTPStatus
from typing import Dict

from quart import jsonify, request
from quart_openapi import Resource, PintBlueprint

from varpivo.api.external import BrewersFriend
from varpivo.api.models import *
from varpivo.cooking.cookbook import CookBook
from varpivo.steps import step_to_dict
from varpivo.utils.librarian import check_recipe_file_existence

app = PintBlueprint('recipes', __name__)


@app.route("/recipe")
class RecipeList(Resource):
    @app.response(HTTPStatus(HTTPStatus.OK), description="",
                  validator=app.create_validator('recipe_list', recipe_list_model))
    @app.doc(tags=['Recipes'])
    async def get(self):
        '''Retrieve all available recipes

        This docstring will show up as the description and short-description
        for the openapi docs for this route.
        '''
        return jsonify(
            {"recipes": list(map(lambda recipe: recipe.cookbook_entry, CookBook.get_instance().recipes.values()))})


recipe_steps = app.create_validator('recipe_steps', recipe_steps_model)
recipe = app.create_validator('recipe', recipe_model)


@app.param("recipeId", "Recipe ID", "path", required=True)
@app.route('/recipe/<' + 'recipeId>')
class Recipe(Resource):
    @app.doc(tags=['Recipes'])
    @app.response(HTTPStatus(HTTPStatus.NOT_FOUND), "Recipe not found")
    @app.response(HTTPStatus(HTTPStatus.OK), description="Returns a single recipe",
                  validator=recipe)
    async def get(self, recipeId):
        """Get single recipe"""
        try:
            return jsonify(CookBook.get_instance()[recipeId].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND

    @app.doc(tags=['Recipes'])
    @app.response(HTTPStatus(HTTPStatus.NOT_FOUND), "Recipe not found")
    @app.response(HTTPStatus(HTTPStatus.CONFLICT), "Recipe already selected")
    @app.response(HTTPStatus(HTTPStatus.OK), description="",
                  validator=recipe_steps)
    async def post(self, recipeId):
        """Select recipe and start brew session"""
        try:
            if await CookBook.get_instance().select_recipe(recipeId):
                return jsonify({"steps": list(map(step_to_dict, CookBook.get_instance()[recipeId].steps_list))})
            else:
                return jsonify({"error": 'Recipe already selected'}), HTTPStatus.CONFLICT
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND


@app.route('/recipe/brewers_friend')
class BrewersFriendRecipe(Resource):
    @app.doc(tags=['Recipes'])
    @app.expect(app.create_validator('brewers_friend', brewers_friend_request_model))
    @app.response(HTTPStatus(HTTPStatus.OK), "Recipe imported successfully", recipe)
    @app.response(HTTPStatus(HTTPStatus.NOT_FOUND), "Recipe not found on Brewer's Friend")
    @app.response(HTTPStatus(HTTPStatus.CONFLICT), "Recipe already exists and neither 'replace' nor 'add' were set")
    @app.response(HTTPStatus(HTTPStatus.FORBIDDEN), "Recipe is not accessible on Brewer's Friend, possibly because "
                                                    "it's private")
    @app.response(HTTPStatus(HTTPStatus.BAD_REQUEST), "None of recipe ID or Brewer's friend URL provided")
    async def post(self):
        """Import a recipe from Brewer's Friend"""
        req: Dict = await request.json
        brewers_friend_id = req.setdefault("id", None)
        brewers_friend_url = req.setdefault('url', None)
        replace = req.setdefault('replace', False)
        add = req.setdefault('add', False)
        recipe_id = f'brewers_friend_{brewers_friend_id}'
        if check_recipe_file_existence(recipe_id) and not (replace or add):
            return jsonify({"error": 'Recipe already exists'}), HTTPStatus.CONFLICT
        try:
            beerxml, recipe_id = await BrewersFriend.get_beerxml_recipe(brewers_friend_id, brewers_friend_url)
        except (FileNotFoundError, IndexError):
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND
        except PermissionError:
            return jsonify({"error": 'Recipe not accessible'}), HTTPStatus.FORBIDDEN
        except ValueError:
            return jsonify({"error": "No URL or ID specified"}), HTTPStatus.BAD_REQUEST
        try:
            new_recipe = CookBook.get_instance().add_recipe_from_beerxml(beerxml, recipe_id, replace=replace, add=add)
        except FileExistsError:
            return jsonify({"error": 'Recipe already exists'}), HTTPStatus.CONFLICT

        return jsonify(new_recipe.cookbook_entry)
