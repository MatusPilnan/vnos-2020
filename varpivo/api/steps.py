from http import HTTPStatus

from quart import jsonify
from quart_openapi import Resource, PintBlueprint

from varpivo.api.models import *
from varpivo.config import config
from varpivo.cooking.cookbook import CookBook
from varpivo.security.security import brew_session_code_required
from varpivo.steps import step_to_dict

app = PintBlueprint('steps', __name__)

recipe_step = app.create_validator('recipe_step', step_model)


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
