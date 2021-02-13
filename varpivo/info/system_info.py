import asyncio
import json
import logging
from typing import List

import httpx

from varpivo.hardware.heater import Heater
from varpivo.hardware.scale import Scale
from varpivo.hardware.thermometer import Thermometer
from varpivo.security.security import Security
from varpivo.utils.network import get_local_ip, get_public_ip, Ngrok


class SystemInfo:
    __instance = None
    ANY = -1
    TEMPERATURE = 0
    WEIGHT = 1
    HEATING = 2
    ADDRESSES = 3
    BREW_SESSION_CODE = 4

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
        self.addresses = [f'127.0.0.1']
        self.ip_timed_out = False

    @staticmethod
    def add_observer(observer, properties: List[int] = None):
        if not properties:
            properties = [SystemInfo.ANY]

        if not isinstance(properties, list):
            properties = [properties]
        SystemInfo.get_instance().observers.append(SystemInfoObserver(observer, properties))

    @staticmethod
    def remove_observer(func):
        SystemInfo.get_instance().observers = [x for x in SystemInfo.get_instance().observers if x.func != func]

    @staticmethod
    async def collect_info():
        instance = SystemInfo.get_instance()
        ngrok_address = Ngrok.get_address()
        if ngrok_address is not None:
            instance.addresses.append(ngrok_address)
        await instance.resolve_ip_addresses()
        await instance.notify_observers()
        while True:
            instance.changed_properties = set()
            instance.temperature = round(await Thermometer.get_instance().temperature)
            instance.weight = int(await (await Scale.get_instance()).weight)
            instance.heating = Heater.get_instance().heat
            if instance.ip_timed_out:
                await instance.resolve_ip_addresses(timeout=5)

            await instance.notify_observers()
            await asyncio.sleep(0.5)

    async def notify_observers(self):
        if len(self.changed_properties) > 0:
            self.changed_properties.add(SystemInfo.ANY)

        for observer in self.observers:
            if observer.func and self.changed_properties.intersection(observer.observed_properties):
                if asyncio.iscoroutinefunction(observer.func):
                    await observer.func(changed=self.changed_properties)
                else:
                    observer.func(changed=self.changed_properties)

    async def resolve_ip_addresses(self, timeout=5):
        self.addresses.append(get_local_ip())
        try:
            self.addresses.append(await get_public_ip(timeout))
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            logging.getLogger('quart.app').warning('Public IP retrieval timed out.')
            self.ip_timed_out = True
        self.changed_properties.add(SystemInfo.ADDRESSES)

    @property
    def brew_session_code(self):
        return Security.get_instance().brew_session_code

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
