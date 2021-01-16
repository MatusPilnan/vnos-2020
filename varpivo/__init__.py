import asyncio
import json
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
from varpivo.security.security import Security
from varpivo.utils import Event

app = Pint(__name__, title="Var:Pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"
app = cors(app, allow_origin='*')
app.logger.setLevel('INFO')
Security.get_instance()


@app.route('/')
async def hello():
    return 'hello'


async def ws_observer(event):
    if event.event_type[0] == Event.WS:
        await broadcast(event.payload)


connected_websockets = set()
event_queue = Queue(loop=loop)
event_observers = {ws_observer, Scale.calibration_observer, Security.security_observer}


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
    _, message = await weight_to_keg()
    await websocket.send(message)
    _, _, message = await temperature_to_keg()
    await websocket.send(message)
    while True:
        data = await queue.get()
        await websocket.send(data)


async def broadcast(message):
    for queue in connected_websockets:
        await queue.put(message)


async def send_weight():
    last_reading = None
    while True:
        weight, message = await weight_to_keg()
        if last_reading != weight:
            Display.get_instance().weight = weight
            await broadcast(message)
            last_reading = weight
        await asyncio.sleep(0.5)


async def weight_to_keg():
    weight = int(await Scale.get_instance().weight)
    return weight, json.dumps({"payload": json.dumps(weight), "content": "weight"})


async def send_temperature():
    last_reading = None
    while True:
        temperature, heating, message = await temperature_to_keg()
        if (temperature, heating) != last_reading:
            Display.get_instance().temperature = temperature
            Display.get_instance().heating = heating
            await broadcast(message)
            last_reading = (temperature, heating)
        await asyncio.sleep(0.5)


async def temperature_to_keg():
    temperature = round(await Thermometer.get_instance().temperature)
    heating = Heater.get_instance().heat
    message = json.dumps({"payload": json.dumps({"temperature": temperature, "heating": heating}),
                          "content": "temperature"})
    return temperature, heating, message


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

asyncio.ensure_future(send_weight())
asyncio.ensure_future(send_temperature())
asyncio.ensure_future(observe())


@app.route('/api/doc/swagger.json')
async def swagger():
    return jsonify(app.__schema__)


nieco = OpenApiView(app)

quart_api_doc(app, config_url='http://127.0.0.1:5000/openapi.json', url_prefix='/api/doc', title="Var:Pivo API")
