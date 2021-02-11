import logging
import socket
from typing import Optional

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


async def get_public_ip(timeout=5):
    async with httpx.AsyncClient(timeout=timeout) as client:
        ip = (await client.get('https://api.ipify.org')).text
        return f'{ip}:{config.PUBLIC_PORT}'


class ServerSentEvent:

    def __init__(
            self,
            data: str,
            *,
            event: Optional[str] = None,
            id: Optional[int] = None,
            retry: Optional[int] = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

    def encode(self) -> bytes:
        message = f"data: {self.data}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.id is not None:
            message = f"{message}\nid: {self.id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        message = f"{message}\r\n\r\n"
        return message.encode('utf-8')


class Ngrok:
    tunnel = None
    enabled = True

    @staticmethod
    def get_address():
        if Ngrok.enabled:
            if Ngrok.tunnel is None:
                from pyngrok import ngrok
                try:
                    Ngrok.tunnel = ngrok.connect()
                except Exception as e:
                    logging.getLogger('quart.app').warning(f'Unable to start Ngrok: {e}')
                    return None
            ngrok_address = Ngrok.tunnel.public_url
            if ngrok_address.startswith('http://'):
                ngrok_address = ngrok_address[len('http://'):]
            elif ngrok_address.startswith('https://'):
                ngrok_address = ngrok_address[len('https://'):]
            return ngrok_address
        else:
            logging.getLogger('quart.app').info(f'Ngrok is disabled')
        return None

