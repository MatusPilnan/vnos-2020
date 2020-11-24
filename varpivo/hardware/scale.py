from random import random

try:
    from RPi import GPIO
    # noinspection PyPackageRequirements
    from hx711 import HX711
except ModuleNotFoundError:
    emulate = True
    print('No modules for scale found. Using emulated scale.')


class Scale:
    __instance = None

    @staticmethod
    def get_instance():
        if Scale.__instance is None:
            if emulate:
                EmulatedScale()
            else:
                Scale()

        return Scale.__instance

    def __init__(self) -> None:
        super().__init__()
        if Scale.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Scale.__instance = self

    @property
    def weight(self):
        raise NotImplementedError


class EmulatedScale(Scale):

    @property
    def weight(self):
        return random() * 100
