class Heater(object):
    __instance = None
    observers = []
    target_temperature = 0

    @staticmethod
    def get_instance():
        if Heater.__instance is None:
            Heater.__instance = Heater()

        return Heater.__instance

    def __init__(self):
        self._heat = False

    @property
    def heat(self):
        return self._heat

    @heat.setter
    def heat(self, val):
        self._heat = val
        pass  # TODO: turn on/off heating element
