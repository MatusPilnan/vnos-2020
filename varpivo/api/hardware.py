import json
from http import HTTPStatus

from quart import jsonify, request
from quart_openapi import PintBlueprint, Resource

from varpivo.config import config
from varpivo.hardware.scale import Scale
from varpivo.security.security import brew_session_code_required
from varpivo.utils import EventQueue, Event

app = PintBlueprint('hardware', __name__)


@app.route("/scale")
class ScaleRes(Resource):
    @app.param('grams', description='Real weight used for calibration', required=True, schema={"type": "integer"})
    @app.doc(tags=['Scale'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def patch(self):
        """Start scale calibration"""
        weight = request.args['grams']
        (await Scale.get_instance()).start_calibration(int(weight))
        await EventQueue.get_queue().put(
            Event(Event.WS, payload=json.dumps({"content": "calibration", "payload": "ready"})))
        return jsonify({}), HTTPStatus.NO_CONTENT

    @app.doc(tags=['Scale'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def put(self):
        """Find scale reference units, after weight was PUT on the scale"""
        if not (await Scale.get_instance()).calibrating:
            return jsonify({"error": 'Calibration not started'}), HTTPStatus.FAILED_DEPENDENCY
        await EventQueue.get_queue().put(Event(Event.CALIBRATION_READY, payload=None))
        return jsonify({}), HTTPStatus.NO_CONTENT

    @app.doc(tags=['Scale'])
    @app.param(config.BREW_SESSION_CODE_HEADER, 'Brew session code', _in='header')
    @brew_session_code_required
    async def delete(self):
        """Tare the scale"""
        (await Scale.get_instance()).tare()
        return jsonify({}), HTTPStatus.NO_CONTENT
