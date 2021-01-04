import asyncio
from asyncio import Queue
from functools import wraps

from quart import websocket, jsonify
from quart_cors import cors
from quart_openapi import Pint
from swagger_ui import quart_api_doc

from main import loop
from varpivo.hardware.display import Display
from varpivo.hardware.heater import Heater
from varpivo.hardware.scale import Scale
from varpivo.hardware.thermometer import Thermometer
from varpivo.info.system_info import SystemInfo
from varpivo.utils import Event

app = Pint(__name__, title="Var:Pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"
app = cors(app, allow_origin='*')


@app.route('/')
async def hello():
    return 'hello'


async def ws_observer(event):
    if event.event_type[0] == Event.WS:
        await broadcast(event.payload)


connected_websockets = set()
event_queue = Queue(loop=loop)
event_observers = {ws_observer, Scale.calibration_observer}


def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        queue = asyncio.Queue()
        connected_websockets.add(queue)
        try:
            return await func(queue, *args, **kwargs)
        except Exception as e:
            print(e)
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


async def send_weight():
    weight, message = await SystemInfo.weight_to_keg()
    await broadcast(message)


async def send_temperature():
    temperature, heating, message = await SystemInfo.temperature_to_keg()
    await broadcast(message)


async def observe():
    while True:
        event = await event_queue.get()
        for observer in event_observers:
            await observer(event)


@app.after_serving
async def shutdown():
    print('Cleaning up...')
    try:
        from RPi import GPIO
        GPIO.cleanup()
    except ModuleNotFoundError:
        print("Or maybe not...")


from varpivo.api import recipe
from quart_openapi import OpenApiView

SystemInfo.add_observer(send_temperature, [SystemInfo.TEMPERATURE, SystemInfo.HEATING])
SystemInfo.add_observer(send_weight, [SystemInfo.WEIGHT])

asyncio.ensure_future(SystemInfo.collect_info())
asyncio.ensure_future(observe())
asyncio.ensure_future(Display.cycle_screens())


@app.route('/api/doc/swagger.json')
async def swagger():
    return jsonify(app.__schema__)


nieco = OpenApiView(app)

quart_api_doc(app, config_url='http://127.0.0.1:5000/openapi.json', url_prefix='/api/doc', title="Var:Pivo API")
