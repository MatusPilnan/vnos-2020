import asyncio
import json
from asyncio import Queue
from functools import wraps

from RPi import GPIO
from quart import websocket
from quart_cors import cors
from quart_openapi import Pint

from main import loop
from varpivo.hardware.scale import Scale
from varpivo.hardware.thermometer import Thermometer
from varpivo.utils import Event

app = Pint(__name__, title="var:pivo API")
app.config['SERVER_NAME'] = "192.168.1.13:5000"
app = cors(app, allow_origin='*')


@app.route('/')
async def hello():
    return 'hello'


async def ws_observer(event):
    if event.event_type[0] == Event.WS:
        await broadcast(event.payload)


connected_websockets = set()
event_queue = Queue(loop=loop)
event_observers = {ws_observer}


def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected_websockets
        queue = asyncio.Queue()
        connected_websockets.add(queue)
        try:
            return await func(queue, *args, **kwargs)
        finally:
            connected_websockets.remove(queue)

    return wrapper


@app.websocket('/tap')
@collect_websocket
async def ws(queue):
    while True:
        data = await queue.get()
        await websocket.send(data)


async def broadcast(message):
    for queue in connected_websockets:
        await queue.put(message)


async def send_weight():
    while True:
        await broadcast(json.dumps({"payload": json.dumps(round(Scale.get_instance().weight, 2)), "content": "weight"}))
        await asyncio.sleep(0.5)


async def send_temperature():
    while True:
        await broadcast(json.dumps({"payload": json.dumps(round(Thermometer.get_instance().temperature, 2)),
                                    "content": "temperature"}))
        await asyncio.sleep(0.5)


async def observe():
    while True:
        event = await event_queue.get()
        for observer in event_observers:
            await observer(event)


from varpivo.api import recipe
from quart_openapi import OpenApiView

asyncio.ensure_future(send_weight())
asyncio.ensure_future(send_temperature())
asyncio.ensure_future(observe())

nieco = OpenApiView(app)
