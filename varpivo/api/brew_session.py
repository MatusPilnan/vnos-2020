from http import HTTPStatus

from quart import jsonify, request
from quart_openapi import Resource, PintBlueprint

from varpivo.api.models import *
from varpivo.config import config
from varpivo.cooking.cookbook import CookBook
from varpivo.security.security import Security, brew_session_code_required
from varpivo.steps import step_to_dict

app = PintBlueprint('brew_session', __name__)


@app.route("/status")
class BrewStatus(Resource):
    @app.response(HTTPStatus(HTTPStatus.OK), description='OK',
                  validator=app.create_validator('brew_session', brew_session_model))
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @app.doc(tags=['Brew session status'])
    async def get(self):
        """Get currently selected recipe with steps"""
        if not CookBook.get_instance().selected_recipe:
            return jsonify({"error": 'No recipe selected'}), HTTPStatus.FAILED_DEPENDENCY
        recipe = CookBook.get_instance().selected_recipe
        return jsonify({"recipe": recipe.cookbook_entry, "steps": list(map(step_to_dict, recipe.steps_list)),
                        "boil_started_at": CookBook.get_instance().selected_recipe.boil_started_at,
                        "bs_code_valid": Security.check_code(request.headers.get(config.BREW_SESSION_CODE_HEADER))})

    @app.doc(tags=['Brew session status'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def delete(self):
        """Reset state - unselect any selected recipe"""
        CookBook.get_instance().unselect_recipe()
        return jsonify({})
