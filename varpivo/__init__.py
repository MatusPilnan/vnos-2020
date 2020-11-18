from quart_openapi import Pint

app = Pint(__name__)

@app.route('/')
async def hello():
    return 'hello'

from varpivo.api import recipe
from quart_openapi import OpenApiView


nieco = OpenApiView(app)
