import asyncio

loop = asyncio.get_event_loop()

if __name__ == "__main__":
    from varpivo import app

    app.run(loop=loop)
