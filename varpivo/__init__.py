from quart_openapi import Pint

app = Pint(__name__, title="var:pivo API")
app.config['SERVER_NAME'] = "127.0.0.1:5000"
@app.route('/')
async def hello():
    return 'hello'

from varpivo.api import recipe
from quart_openapi import OpenApiView


nieco = OpenApiView(app)
