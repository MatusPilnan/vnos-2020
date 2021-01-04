import asyncio
import logging

from varpivo.config import config
from varpivo.info.system_info import SystemInfo


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

        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        self.screens = [SummaryScreen(self.device), NetworkScreen(self.device)]
        self._current_screen = 0
        StartupScreen(self.device).show()
        self.screens[self._current_screen].observe_sys_info()

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, val):
        self.screens[self._current_screen].stop_observing()
        if val < 0:
            val += len(self.screens)

        val = val % len(self.screens)
        self._current_screen = val
        self.screens[self._current_screen].show()
        self.screens[self._current_screen].observe_sys_info()

    @staticmethod
    async def cycle_screens():
        while True:
            Display.next_screen()
            await asyncio.sleep(config.DISPLAY_CYCLE_INTERVAL)

    @staticmethod
    def next_screen():
        Display.get_instance().current_screen += 1

    @staticmethod
    def previous_screen():
        Display.get_instance().current_screen -= 1


class EmulatedDisplay(Display):

    # noinspection PyMissingConstructor
    def __init__(self):
        print('No display detected.')

    def show(self, **kwargs):
        pass


class Screen:
    observed_properties = [SystemInfo.ANY]

    def __init__(self, display=None):
        self.display = display

    def observe_sys_info(self):
        SystemInfo.add_observer(self.show, self.observed_properties)

    def stop_observing(self):
        SystemInfo.remove_observer(self.show)

    def show(self):
        pass


class SummaryScreen(Screen):
    observed_properties = [SystemInfo.TEMPERATURE, SystemInfo.HEATING, SystemInfo.WEIGHT]

    def show(self):
        # noinspection PyUnresolvedReferences
        from luma.core.render import canvas

        info = SystemInfo.get_instance()
        message = f'Temperature: {info.temperature}°C\n' \
                  f'Heater {"on" if info.heating else "off"}\n' \
                  f'Weight: {info.weight} g'

        with canvas(self.display) as draw:
            draw.rectangle(self.display.bounding_box, outline="black", fill="black")
            draw.text((5, 15), message, fill="white")


class NetworkScreen(Screen):
    observed_properties = [SystemInfo.ADDRESSES]

    def show(self):
        # noinspection PyUnresolvedReferences
        from luma.core.render import canvas

        message = 'IP Addresses:\n' + '\n'.join(SystemInfo.get_instance().addresses)

        with canvas(self.display) as draw:
            draw.rectangle(self.display.bounding_box, outline="black", fill="black")
            draw.text((5, 5), message, fill="white")


class StartupScreen(Screen):
    def show(self):
        # noinspection PyBroadException
        try:
            # noinspection PyUnresolvedReferences
            from PIL import Image

            with Image.open('varpivo.jpg') as img:
                background = Image.new(mode='1', size=(self.display.width, self.display.height))
                position = ((self.display.width - img.width) // 2, (self.display.height - img.height) // 2)
                background.paste(img, position)
                self.display.display(background)
        except Exception:
            logging.getLogger('quart.app').info('Not showing splashscreen')
