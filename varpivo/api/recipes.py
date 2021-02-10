from http import HTTPStatus

from quart import jsonify
from quart_openapi import Resource, PintBlueprint

from varpivo.api.models import *
from varpivo.config import config
from varpivo.cooking.cookbook import CookBook
from varpivo.security.security import brew_session_code_required
from varpivo.steps import step_to_dict

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


recipe_step = app.create_validator('recipe_step', step_model)
recipe_steps = app.create_validator('recipe_steps', recipe_steps_model)


@app.param("recipeId", "Recipe ID", "path", required=True)
@app.route('/recipe/<' + 'recipeId>')
class Recipe(Resource):
    @app.doc(tags=['Recipes'])
    @app.response(HTTPStatus(HTTPStatus.NOT_FOUND), "Recipe not found")
    @app.response(HTTPStatus(HTTPStatus.OK), description="Returns a signle recipe",
                  validator=app.create_validator('recipe', recipe_model))
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


@app.param("stepId", "Step ID", "path", required=True)
@app.route('/step/<' + 'stepId>')
class StepStart(Resource):
    @app.response(HTTPStatus(HTTPStatus.OK), description="", validator=recipe_step)
    @app.doc(tags=['Recipe steps'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def post(self, stepId):
        """Start specified step"""
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        try:
            step = CookBook.get_instance().selected_recipe.steps[stepId]
        except IndexError:
            return jsonify({"error": 'Step not found'}), HTTPStatus.NOT_FOUND
        if not step.available:
            return jsonify({"error": 'Step not yet available'}), HTTPStatus.FAILED_DEPENDENCY
        await step.start()
        return jsonify(step_to_dict(step))

    @app.response(HTTPStatus(HTTPStatus.OK), description="", validator=recipe_step)
    @app.doc(tags=['Recipe steps'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def delete(self, stepId):
        """Finish specified step"""
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        try:
            step = CookBook.get_instance().selected_recipe.steps[stepId]
        except IndexError:
            return jsonify({"error": 'Step not found'}), HTTPStatus.NOT_FOUND

        if not step.started:
            return jsonify({"error": 'Step not in progress'}), HTTPStatus.FAILED_DEPENDENCY
        if not step.finished:
            await step.stop()
        return jsonify(step_to_dict(step))
