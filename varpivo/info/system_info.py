import asyncio
import json
from typing import List

from varpivo.hardware.heater import Heater
from varpivo.hardware.scale import Scale
from varpivo.hardware.thermometer import Thermometer


class SystemInfo:
    __instance = None
    ANY = -1
    TEMPERATURE = 0
    WEIGHT = 1
    HEATING = 2
    ADDRESSES = 3

    @staticmethod
    def get_instance():
        if SystemInfo.__instance is None:
            SystemInfo.__instance = SystemInfo()

        return SystemInfo.__instance

    def __init__(self):
        self.observers: List[SystemInfoObserver] = []
        self.changed_properties = set()
        self._temperature = None
        self._heating = None
        self._weight = None
        self._addresses = None

    @staticmethod
    def add_observer(observer, properties: List[int] = None):
        if not properties:
            properties = [SystemInfo.ANY]
        SystemInfo.get_instance().observers.append(SystemInfoObserver(observer, properties))

    @staticmethod
    async def collect_info():
        instance = SystemInfo.get_instance()
        while True:
            instance.changed_properties = {SystemInfo.ANY}
            instance.temperature = round(await Thermometer.get_instance().temperature)
            instance.weight = int(await Scale.get_instance().weight)
            instance.heating = Heater.get_instance().heat
            for observer in instance.observers:
                if instance.changed_properties.union(observer.observed_properties):
                    await observer.func()
            await asyncio.sleep(0.5)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, val):
        if self._temperature != val:
            self._temperature = val
            self.changed_properties.add(SystemInfo.TEMPERATURE)

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, val):
        new_value = max(val, 0)
        if new_value != self._weight:
            self._weight = new_value
            self.changed_properties.add(SystemInfo.WEIGHT)

    @property
    def heating(self):
        return self._heating

    @heating.setter
    def heating(self, val):
        if self._heating != val:
            self._heating = val
            self.changed_properties.add(SystemInfo.HEATING)

    @staticmethod
    async def temperature_to_keg():
        instance = SystemInfo.get_instance()
        temperature = instance.temperature
        heating = instance.heating
        message = json.dumps({"payload": json.dumps({"temperature": temperature, "heating": heating}),
                              "content": "temperature"})
        return temperature, heating, message

    @staticmethod
    async def weight_to_keg():
        weight = SystemInfo.get_instance().weight
        return weight, json.dumps({"payload": json.dumps(weight), "content": "weight"})


class SystemInfoObserver:
    def __init__(self, func, observed_properties: List[int]) -> None:
        self.observed_properties = set(list(observed_properties))
        self.func = func
