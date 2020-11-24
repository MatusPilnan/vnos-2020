from random import random

try:
    from w1thermsensor import W1ThermSensor
    from RPi import GPIO
except ModuleNotFoundError:
    emulate = True
    print('No modules for thermometer found. Using emulated thermometer.')


class Thermometer:
    __instance = None

    @staticmethod
    def get_instance():
        if Thermometer.__instance is None:
            if emulate:
                EmulatedThermometer()
            else:
                Thermometer()

        return Thermometer.__instance

    def __init__(self) -> None:
        super().__init__()
        if Thermometer.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Thermometer.__instance = self

    @property
    def temperature(self):
        raise NotImplementedError


class EmulatedThermometer(Thermometer):

    @property
    def temperature(self):
        return random() * 100
