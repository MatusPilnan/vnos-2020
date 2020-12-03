import asyncio
import os

from varpivo import Thermometer
from varpivo.hardware.heater import Heater


class Kettle:
    __instance = None
    observing_steps = set()
    target_temperature = 0

    CHECKPOINT_FILE = os.path.join("shelf", "shelf.kettle")

    @staticmethod
    def get_instance():
        if Kettle.__instance is None:
            Kettle.__instance = Kettle()

        return Kettle.__instance

    def __init__(self) -> None:
        # TODO: save status
        asyncio.ensure_future(self.work())

    def __del__(self):
        Heater.get_instance().heat = False

    async def work(self):
        from varpivo.recipe import CookBook
        while True:
            temp = Thermometer.get_instance().temperature
            Heater.get_instance().heat = self.target_temperature > temp
            steps = set(self.observing_steps)
            if not CookBook.get_instance().selected_recipe:
                self.target_temperature = 0
                del Kettle.__instance
                return
            for observer in steps:
                await CookBook.get_instance().selected_recipe.steps[observer].observe_kettle(temp)
            await asyncio.sleep(1)
