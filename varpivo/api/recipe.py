from http import HTTPStatus

from quart import jsonify
from quart_openapi import Resource
from quart_openapi.cors import crossdomain

from varpivo import app
from varpivo.api.models import recipe_model, step_model, ws_message_model, recipe_list_model, recipe_steps_model
from varpivo.recipe import CookBook
from varpivo.steps import Step


@app.route("/recipe")
class RecipeList(Resource):
    @app.response(HTTPStatus.OK, description="", validator=app.create_validator('recipe_list', recipe_list_model))
    @crossdomain("*")
    async def get(self):
        '''Retrieve all available recipes

        This docstring will show up as the description and short-description
        for the openapi docs for this route.
        '''
        return jsonify(
            {"recipes": list(map(lambda recipe: recipe.cookbook_entry, CookBook.get_instance().recipes.values()))})


def step_to_dict(step: Step):
    return step.to_dict()


recipe_step = app.create_validator('recipe_step', step_model)
recipe_steps = app.create_validator('recipe_steps', recipe_steps_model)


# noinspection PyUnresolvedReferences,PyPep8Naming
@app.param("recipeId", "Recipe ID", "path", required=True)
@app.route('/recipe/<recipeId>')
class Recipe(Resource):

    @crossdomain("*")
    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.OK, description="Returns a signle recipe",
                  validator=app.create_validator('recipe', recipe_model))
    async def get(self, recipeId):
        try:
            return jsonify(CookBook.get_instance()[recipeId].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND

    @crossdomain("*")
    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.CONFLICT, "Recipe already selected")
    @app.response(HTTPStatus.OK, description="",
                  validator=recipe_steps)
    async def post(self, recipeId):

        try:
            if not CookBook.get_instance().selected_recipe:
                CookBook.get_instance().selected_recipe = CookBook.get_instance()[recipeId]
                return jsonify({"steps": list(map(step_to_dict, CookBook.get_instance()[recipeId].steps))})
            else:
                return jsonify({"error": 'Recipe already selected'}), HTTPStatus.CONFLICT
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND


# noinspection PyUnresolvedReferences,PyPep8Naming
@app.param("stepId", "Step ID", "path", required=True)
@app.route('/step/<stepId>')
class StepStart(Resource):
    @app.response(HTTPStatus.OK, description="", validator=recipe_step)
    async def post(self, stepId):
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        try:
            step = CookBook.get_instance().selected_recipe.steps[int(stepId)]
        except IndexError:
            return jsonify({"error": 'Step not found'}), HTTPStatus.NOT_FOUND
        if not step.available:
            return jsonify({"error": 'Step not yet available'}), HTTPStatus.FAILED_DEPENDENCY
        await step.start()
        return jsonify(step_to_dict(step))

    @app.response(HTTPStatus.OK, description="", validator=recipe_step)
    async def delete(self, stepId):
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        try:
            step = CookBook.get_instance().selected_recipe.steps[int(stepId)]
        except IndexError:
            return jsonify({"error": 'Step not found'}), HTTPStatus.NOT_FOUND

        if not step.started:
            return jsonify({"error": 'Step not in progress'}), HTTPStatus.FAILED_DEPENDENCY
        await step.stop()
        return jsonify(step_to_dict(step))


@app.route("/brizolit/je/cesta/neprestrelna/vesta")
class WebSocketKeg(Resource):
    @app.response(HTTPStatus.OK, description="Tatrofkaaaaaa", validator=app.create_validator('wskeg', ws_message_model))
    def get(self):
        return jsonify({""}, HTTPStatus.IM_A_TEAPOT)
