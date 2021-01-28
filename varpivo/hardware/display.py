from varpivo.config import config


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
        # noinspection PyUnresolvedReferences
        from luma.core.interface.serial import i2c
        # noinspection PyUnresolvedReferences
        from luma.oled.device import sh1106

        serial = i2c(port=config.DISPLAY_I2C_PORT, address=config.DISPLAY_I2C_ADDRESS)
        self.device = sh1106(serial)

    @property
    def dimensions(self):
        return self.device.width, self.device.height

    def show(self, screen):
        self.device.display(screen.image)


class EmulatedDisplay(Display):

    # noinspection PyMissingConstructor
    def __init__(self):
        print('No display detected.')

    def show(self, **kwargs):
        pass


