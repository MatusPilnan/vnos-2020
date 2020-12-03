import json
from http import HTTPStatus

from quart import jsonify, request
from quart_openapi import Resource

from varpivo import app, Scale, event_queue
from varpivo.api.models import recipe_model, step_model, ws_message_model, recipe_list_model, recipe_steps_model, \
    brew_session_model, ws_temperature_model
from varpivo.recipe import CookBook
from varpivo.steps import Step
from varpivo.utils import Event


@app.route("/recipe")
class RecipeList(Resource):
    @app.response(HTTPStatus.OK, description="", validator=app.create_validator('recipe_list', recipe_list_model))
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

    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.OK, description="Returns a signle recipe",
                  validator=app.create_validator('recipe', recipe_model))
    async def get(self, recipeId):
        try:
            return jsonify(CookBook.get_instance()[recipeId].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND

    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.CONFLICT, "Recipe already selected")
    @app.response(HTTPStatus.OK, description="",
                  validator=recipe_steps)
    async def post(self, recipeId):

        try:
            if CookBook.get_instance().select_recipe(recipeId):
                return jsonify({"steps": list(map(step_to_dict, CookBook.get_instance()[recipeId].steps_list))})
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
            step = CookBook.get_instance().selected_recipe.steps[stepId]
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
            step = CookBook.get_instance().selected_recipe.steps[stepId]
        except IndexError:
            return jsonify({"error": 'Step not found'}), HTTPStatus.NOT_FOUND

        if not step.started:
            return jsonify({"error": 'Step not in progress'}), HTTPStatus.FAILED_DEPENDENCY
        if not step.finished:
            await step.stop()
        return jsonify(step_to_dict(step))


@app.route("/status")
class BrewStatus(Resource):
    @app.response(HTTPStatus.OK, description='OK', validator=app.create_validator('brew_session', brew_session_model))
    async def get(self):
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        recipe = CookBook.get_instance().selected_recipe
        return jsonify({"recipe": recipe.cookbook_entry, "steps": list(map(step_to_dict, recipe.steps_list))})

    @app.response(HTTPStatus.OK, description='OK', validator=app.create_validator('brew_session', brew_session_model))
    async def delete(self):
        """Reset state - unselect any selected recipe"""
        CookBook.get_instance().selected_recipe = None
        return jsonify({"recipe": None, "steps": []})


@app.route("/scale")
class ScaleRes(Resource):
    @app.param('grams', description='Real weight used for calibration', required=True, schema={"type": "integer"})
    async def patch(self):
        """Start scale calibration"""
        weight = request.args['grams']
        Scale.get_instance().start_calibration(int(weight))
        await event_queue.put(Event(Event.WS, payload=json.dumps({"content": "calibration", "payload": "ready"})))
        return jsonify({}), HTTPStatus.NO_CONTENT

    async def put(self):
        """Find scale reference units, after weight was PUT on the scale"""
        if not Scale.get_instance().calibrating:
            return jsonify({"error": 'Calibration not started'}), HTTPStatus.FAILED_DEPENDENCY
        await event_queue.put(Event(Event.CALIBRATION_READY, payload=None))
        return jsonify({}), HTTPStatus.NO_CONTENT

    async def delete(self):
        """Tare the scale"""
        Scale.get_instance().tare()
        return jsonify({}), HTTPStatus.NO_CONTENT


@app.route("/brizolit/je/cesta/neprestrelna/vesta")
class WebSocketKeg(Resource):
    @app.response(HTTPStatus.OK, description="Tatrofkaaaaaa", validator=app.create_validator('wskeg', ws_message_model))
    def get(self):
        return jsonify({""}, HTTPStatus.IM_A_TEAPOT)

    @app.response(HTTPStatus.OK, description="ZonickaaaAAA",
                  validator=app.create_validator('temperature', ws_temperature_model))
    def post(self):
        return jsonify({""}, HTTPStatus.IM_A_TEAPOT)
