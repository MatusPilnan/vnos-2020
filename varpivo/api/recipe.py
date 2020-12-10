import json
from http import HTTPStatus

from quart import jsonify, request
from quart_openapi import Resource

from varpivo import app, Scale, event_queue
from varpivo.api.models import recipe_model, step_model, ws_message_model, recipe_list_model, recipe_steps_model, \
    brew_session_model, ws_temperature_model
from varpivo.cooking.cookbook import CookBook
from varpivo.steps import Step
from varpivo.utils import Event


@app.route("/recipe")
class RecipeList(Resource):
    @app.response(HTTPStatus.OK, description="", validator=app.create_validator('recipe_list', recipe_list_model))
    @app.doc(tags=['Recipes'])
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
    @app.doc(tags=['Recipes'])
    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.OK, description="Returns a signle recipe",
                  validator=app.create_validator('recipe', recipe_model))
    async def get(self, recipeId):
        """Get single recipe"""
        try:
            return jsonify(CookBook.get_instance()[recipeId].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), HTTPStatus.NOT_FOUND

    @app.doc(tags=['Recipes'])
    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.CONFLICT, "Recipe already selected")
    @app.response(HTTPStatus.OK, description="",
                  validator=recipe_steps)
    async def post(self, recipeId):
        """Select recipe and start brew session"""
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
    @app.doc(tags=['Recipe steps'])
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

    @app.response(HTTPStatus.OK, description="", validator=recipe_step)
    @app.doc(tags=['Recipe steps'])
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


@app.route("/status")
class BrewStatus(Resource):
    @app.response(HTTPStatus.OK, description='OK', validator=app.create_validator('brew_session', brew_session_model))
    @app.doc(tags=['Brew session status'])
    async def get(self):
        """Get currently selected recipe with steps"""
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        recipe = CookBook.get_instance().selected_recipe
        return jsonify({"recipe": recipe.cookbook_entry, "steps": list(map(step_to_dict, recipe.steps_list)),
                        "boil_started_at": CookBook.get_instance().selected_recipe.boil_started_at})

    @app.doc(tags=['Brew session status'])
    async def delete(self):
        """Reset state - unselect any selected recipe"""
        CookBook.get_instance().unselect_recipe()
        return jsonify({})


@app.route("/scale")
class ScaleRes(Resource):
    @app.param('grams', description='Real weight used for calibration', required=True, schema={"type": "integer"})
    @app.doc(tags=['Scale'])
    async def patch(self):
        """Start scale calibration"""
        weight = request.args['grams']
        Scale.get_instance().start_calibration(int(weight))
        await event_queue.put(Event(Event.WS, payload=json.dumps({"content": "calibration", "payload": "ready"})))
        return jsonify({}), HTTPStatus.NO_CONTENT

    @app.doc(tags=['Scale'])
    async def put(self):
        """Find scale reference units, after weight was PUT on the scale"""
        if not Scale.get_instance().calibrating:
            return jsonify({"error": 'Calibration not started'}), HTTPStatus.FAILED_DEPENDENCY
        await event_queue.put(Event(Event.CALIBRATION_READY, payload=None))
        return jsonify({}), HTTPStatus.NO_CONTENT

    @app.doc(tags=['Scale'])
    async def delete(self):
        """Tare the scale"""
        Scale.get_instance().tare()
        return jsonify({}), HTTPStatus.NO_CONTENT


@app.route("/brizolit/je/cesta/neprestrelna/vesta")
class WebSocketKeg(Resource):
    @app.response(HTTPStatus.OK, description="Tatrofkaaaaaa", validator=app.create_validator('wskeg', ws_message_model))
    @app.doc(tags=['WS'])
    def get(self):
        """Resource format for WS messages"""
        return jsonify({""}, HTTPStatus.IM_A_TEAPOT)

    @app.response(HTTPStatus.OK, description="ZonickaaaAAA",
                  validator=app.create_validator('temperature', ws_temperature_model))
    @app.doc(tags=['WS'])
    def post(self):
        """Format of WS message with temperature"""
        return jsonify({""}, HTTPStatus.IM_A_TEAPOT)
