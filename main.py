from varpivo import app
import asyncio


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app.run(loop=loop)
