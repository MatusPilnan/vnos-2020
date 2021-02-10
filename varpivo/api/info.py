from http import HTTPStatus

from quart import jsonify
from quart_openapi import PintBlueprint, Resource

from varpivo.api.models import *
from varpivo.config import config
from varpivo.security.security import brew_session_code_required

app = PintBlueprint('info', __name__)


@app.route('/discover-varpivo')
class Discover(Resource):
    @app.doc(tags=['Info'])
    @app.response(HTTPStatus(HTTPStatus.OK), description='', validator=app.create_validator('message', message_model))
    async def get(self):
        """Used to check if this is a Var:Pivo server, or to ping"""
        return jsonify({"message": "OK"})


@app.route('/auth')
class Auth(Resource):
    @app.doc(tags=['Info'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @app.response(HTTPStatus(HTTPStatus.OK), description='', validator=app.create_validator('message', message_model))
    @brew_session_code_required
    async def get(self):
        """Used to check if brew session key code is valid"""
        return jsonify({"message": "OK"})


@app.route("/brizolit/je/cesta/neprestrelna/vesta")
class WebSocketKeg(Resource):
    @app.response(HTTPStatus(HTTPStatus.OK), description="Tatrofkaaaaaa",
                  validator=app.create_validator('wskeg', ws_message_model))
    @app.doc(tags=['WS'])
    async def get(self):
        """Resource format for WS messages"""
        return jsonify({""}, 418)

    @app.response(HTTPStatus(HTTPStatus.OK), description="ZonickaaaAAA",
                  validator=app.create_validator('temperature', ws_temperature_model))
    @app.doc(tags=['WS'])
    async def post(self):
        """Format of WS message with temperature"""
        return jsonify({""}, 418)
