import asyncio

from varpivo import Thermometer
from varpivo.hardware.heater import Heater
from varpivo.utils.librarian import save_kettle, load_kettle


class Kettle:
    __instance = None
    observing_steps = set()
    _target_temperature = 0


    @staticmethod
    def get_instance():
        if Kettle.__instance is None:
            Kettle.__instance = Kettle()

        return Kettle.__instance

    def __init__(self) -> None:
        self.load_state()
        asyncio.ensure_future(self.work())

    def __del__(self):
        Heater.get_instance().heat = False

    @property
    def target_temperature(self):
        return self._target_temperature

    @target_temperature.setter
    def target_temperature(self, val):
        self._target_temperature = val
        save_kettle(self)

    def add_observing_step(self, step_id: str):
        self.observing_steps.add(step_id)
        save_kettle(self)

    def remove_observing_step(self, step_id: str):
        self.observing_steps.remove(step_id)
        save_kettle(self)

    async def work(self):
        from varpivo.cooking.cookbook import CookBook
        while True:
            temp = await Thermometer.get_instance().temperature
            Heater.get_instance().heat = self.target_temperature > temp
            steps = set(self.observing_steps)
            if not CookBook.get_instance().selected_recipe:
                self.target_temperature = 0
                del Kettle.__instance
                return
            for observer in steps:
                await CookBook.get_instance().selected_recipe.steps[observer].observe_kettle(temp)
            await asyncio.sleep(1)

    def load_state(self):
        checkpoint = load_kettle()
        if not checkpoint:
            return
        self._target_temperature = checkpoint['target_temperature']
        self.observing_steps = checkpoint['observing_steps']
