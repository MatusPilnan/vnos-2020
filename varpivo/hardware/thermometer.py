import logging
from random import random


class Thermometer:
    __instance = None

    @staticmethod
    def get_instance():
        if Thermometer.__instance is None:
            try:
                from w1thermsensor import NoSensorFoundError, KernelModuleLoadError
                try:
                    from w1thermsensor import W1ThermSensor
                    Thermometer()
                except NoSensorFoundError as e:
                    logging.getLogger('quart.app').info(e)
                    EmulatedThermometer()
                except KernelModuleLoadError as e:
                    logging.getLogger('quart.app').info(e)
                    EmulatedThermometer()
            except ModuleNotFoundError:
                EmulatedThermometer()

        return Thermometer.__instance

    def __init__(self) -> None:
        super().__init__()
        if Thermometer.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.sensor = None
            self.init_sensor()
            Thermometer.__instance = self

    def init_sensor(self):
        if not self.sensor:
            from w1thermsensor import AsyncW1ThermSensor
            self.sensor = AsyncW1ThermSensor()

    @property
    async def temperature(self):
        return await self.sensor.get_temperature()


class EmulatedThermometer(Thermometer):
    def init_sensor(self):
        logging.getLogger('quart.app').info('Using emulated thermometer!')

    @property
    async def temperature(self):
        return random() * 100
