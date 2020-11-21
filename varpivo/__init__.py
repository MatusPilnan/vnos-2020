import asyncio
import json
from functools import wraps

from quart import websocket
from quart_openapi import Pint

from varpivo.hardware.scale import Scale

app = Pint(__name__, title="var:pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"


@app.route('/')
async def hello():
    return 'hello'


connected_websockets = set()


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


from varpivo.api import recipe
from quart_openapi import OpenApiView

asyncio.ensure_future(send_weight())

nieco = OpenApiView(app)
