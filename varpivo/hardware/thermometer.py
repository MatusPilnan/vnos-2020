from random import random


class Thermometer:
    __instance = None

    @staticmethod
    def get_instance():
        if Thermometer.__instance is None:
            try:
                from w1thermsensor import W1ThermSensor, NoSensorFoundError
                Thermometer()
            except ModuleNotFoundError:
                EmulatedThermometer()
            except NoSensorFoundError as e:
                print(e)
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
            self.sensor = W1ThermSensor()

    @property
    def temperature(self):
        return self.sensor.get_temperature()


class EmulatedThermometer(Thermometer):
    def init_sensor(self):
        print('Using emulated thermometer!')

    @property
    def temperature(self):
        return random() * 100
