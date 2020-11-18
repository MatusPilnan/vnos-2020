from actorio import Actor
from actorio._abc import IdentifierABC, MessageABC

from varpivo.hardware.heater import Heater
from varpivo.hardware.thermometer import Thermometer


class Kettle(Actor):


    def __init__(self, *args, identifier: IdentifierABC = None, **kwargs) -> None:
        super().__init__(*args, identifier=identifier, **kwargs)
        self.thermometer = Thermometer()
        self.heater = Heater()

    async def handle_message(self, message: MessageABC):
        return await super().handle_message(message)
