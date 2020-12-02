from varpivo.config.config import HEATER_RELAY_GPIO


class Heater(object):
    __instance = None
    observers = []
    target_temperature = 0

    @staticmethod
    def get_instance():
        if Heater.__instance is None:
            try:
                Heater.__instance = Heater()
            except ModuleNotFoundError:
                Heater.__instance = EmulatedHeater()

        return Heater.__instance

    def __init__(self):
        import RPi.GPIO as GPIO
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(HEATER_RELAY_GPIO, GPIO.OUT)
        self._heat = False

    @property
    def heat(self):
        return self._heat

    @heat.setter
    def heat(self, val):
        """Heater turns ON on LOW, turns OFF on HIGH"""
        import RPi.GPIO as GPIO
        if val:
            GPIO.output(HEATER_RELAY_GPIO, GPIO.LOW)
        else:
            GPIO.output(HEATER_RELAY_GPIO, GPIO.HIGH)
        self._heat = val


class EmulatedHeater(Heater):

    # noinspection PyMissingConstructor
    def __init__(self):
        print('Using emulated heater!')
        pass

    @property
    def heat(self):
        return self._heat

    @heat.setter
    def heat(self, val):
        self._heat = val
        pass
