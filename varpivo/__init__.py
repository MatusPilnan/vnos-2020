import asyncio
from functools import wraps

from quart import websocket
from quart_openapi import Pint

app = Pint(__name__, title="var:pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"


@app.route('/')
async def hello():
    return 'hello'


global recipe

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
    print('Kokot')
    while True:
        data = await queue.get()
        print(data)
        await websocket.send(data)


async def broadcast(message):
    for queue in connected_websockets:
        print(message)
        await queue.put(message)


from varpivo.api import recipe
from quart_openapi import OpenApiView

nieco = OpenApiView(app)
