import socket

import httpx

from varpivo.config import config


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return f'{ip}'


async def get_public_ip():
    async with httpx.AsyncClient() as client:
        ip = (await client.get('https://api.ipify.org')).text
        return f'{ip}:{config.PUBLIC_PORT}'
