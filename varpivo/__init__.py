import asyncio
from asyncio import Queue
from functools import wraps

from quart import websocket, jsonify, make_response, render_template, request
from quart_cors import cors
from quart_openapi import Pint
from swagger_ui import quart_api_doc

from main import loop
from varpivo.config import config
from varpivo.hardware.buttons import Buttons
from varpivo.hardware.display import Display
from varpivo.hardware.heater import Heater
from varpivo.hardware.scale import Scale
from varpivo.hardware.thermometer import Thermometer
from varpivo.info.nfc import NFCTagEmulator
from varpivo.info.system_info import SystemInfo
from varpivo.logging import setup_logger, log_reader, stream_log_reader
from varpivo.security.security import Security
from varpivo.ui import UserInterface
from varpivo.utils import Event
from varpivo.utils.network import ServerSentEvent
from varpivo.utils.sounds import Songs

UserInterface.get_instance()

app = Pint(__name__, title="Var:Pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"
app = cors(app, allow_origin='*')
setup_logger(app.logger)
Security.get_instance()


@app.route('/')
async def hello():
    app.logger.info('Hello!')
    return 'hello'


async def ws_observer(event):
    if event.event_type[0] == Event.WS:
        await broadcast(event.payload)


connected_websockets = set()
event_queue = Queue(loop=loop)
Buttons.get_instance()
event_observers = {ws_observer, Scale.calibration_observer, Security.security_observer, UserInterface.event_observer}


def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        queue = asyncio.Queue()
        connected_websockets.add(queue)
        try:
            return await func(queue, *args, **kwargs)
        except Exception as e:
            app.logger.exception(e)
        finally:
            connected_websockets.remove(queue)

    return wrapper


@app.websocket('/tap')
@collect_websocket
async def ws(queue):
    _, message = await SystemInfo.weight_to_keg()
    await websocket.send(message)
    _, _, message = await SystemInfo.temperature_to_keg()
    await websocket.send(message)
    while True:
        data = await queue.get()
        await websocket.send(data)


async def broadcast(message):
    for queue in connected_websockets:
        await queue.put(message)


async def send_weight(**kwargs):
    weight, message = await SystemInfo.weight_to_keg()
    await broadcast(message)


async def send_temperature(**kwargs):
    temperature, heating, message = await SystemInfo.temperature_to_keg()
    await broadcast(message)


async def observe():
    while True:
        event = await event_queue.get()
        for observer in event_observers:
            await observer(event)


@app.after_serving
async def shutdown():
    app.logger.info('Cleaning up...')
    await NFCTagEmulator.get_instance().stop()
    try:
        # noinspection PyUnresolvedReferences
        from RPi import GPIO
        GPIO.cleanup()
    except ModuleNotFoundError:
        app.logger.info("Or maybe not...")


from varpivo.api import recipe
from quart_openapi import OpenApiView

SystemInfo.add_observer(send_temperature, [SystemInfo.TEMPERATURE, SystemInfo.HEATING])
SystemInfo.add_observer(send_weight, [SystemInfo.WEIGHT])

asyncio.ensure_future(SystemInfo.collect_info())
asyncio.ensure_future(observe())
asyncio.ensure_future(UserInterface.cycle_screens())
asyncio.ensure_future(NFCTagEmulator.get_instance().run_nfc_tag_emulator())


@app.route('/logs')
async def logs():
    if 'text/event-stream' == request.accept_mimetypes.best:
        response = await make_response(stream_log_reader(app.logger), {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked',
        })
        response.timeout = None
        return response
    else:
        return await render_template('logstream.html', lines=log_reader(encode=False))


@app.route('/api/doc/swagger.json')
async def swagger():
    return jsonify(app.__schema__)


nieco = OpenApiView(app)

quart_api_doc(app, config_url='http://127.0.0.1:5000/openapi.json', url_prefix='/api/doc', title="Var:Pivo API")
