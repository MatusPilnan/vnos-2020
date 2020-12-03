class Display:
    __instance = None

    @staticmethod
    def get_instance():
        if Display.__instance is None:
            try:
                Display.__instance = Display()
            except ModuleNotFoundError:
                Display.__instance = EmulatedDisplay()

        return Display.__instance

    def __init__(self):
        from luma.core.interface.serial import i2c
        from luma.oled.device import sh1106

        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        self._temperature = -1
        self._weight = -1
        self._heating = False

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, val):
        self._temperature = val
        self.show()

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, val):
        self._weight = max(val, 0)
        self.show()

    @property
    def heating(self):
        return self._heating

    @heating.setter
    def heating(self, val):
        self._heating = val
        self.show()

    def show(self, message=None):
        from luma.core.render import canvas

        if not message:
            message = ''
            if self.temperature > -1:
                message += f'Temperature: {self.temperature}°C\n'
            message += f'Heater {"on" if self._heating else "off"}\n'
            if self.weight > -1:
                message += f'Weight: {self.weight} g'

        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            draw.text((5, 15), message, fill="white")


class EmulatedDisplay(Display):

    # noinspection PyMissingConstructor
    def __init__(self):
        print('No display detected.')

    def show(self, **kwargs):
        pass
