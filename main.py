import argparse
import asyncio
import json
import os
import pathlib

from quart_openapi import Swagger

from varpivo.config import config

loop = asyncio.get_event_loop()

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Start Var:Pivo server')
    arg_parser.add_argument('-o', '--openapi', type=str, nargs='?', const='out/openapi.json',
                            help='Write OpenAPI specification to specified file and exit')

    args = arg_parser.parse_args()

    from varpivo import app

    if args.openapi:
        path = pathlib.Path(args.openapi)
        print(f'Storing OpenAPI specification to {args.openapi}...')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf8') as f:
            json.dump(Swagger(app).as_dict(), f, indent=2)
    else:
        app.run(loop=loop, port=config.PORT)
