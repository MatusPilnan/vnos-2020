import asyncio

from varpivo.hardware.display import Display
from varpivo.ui.screens import *


class UserInterface:
    __instance = None

    @staticmethod
    def get_instance():
        if UserInterface.__instance is None:
            UserInterface.__instance = UserInterface()

        return UserInterface.__instance

    def __init__(self):
        self.screens = [SummaryScreen(), NetworkScreen(), SecurityScreen()]
        self._current_screen = 0
        Display.get_instance().show(StartupScreen())

    @property
    def current_screen(self):
        return self.screens[self._current_screen]

    @current_screen.setter
    def current_screen(self, val):
        SystemInfo.remove_observer(self.update_screen)
        if val < 0:
            val += len(self.screens)

        val = val % len(self.screens)
        self._current_screen = val
        self.update_screen()
        SystemInfo.add_observer(self.update_screen, self.current_screen.observed_properties)

    def update_screen(self):
        self.current_screen.redraw()
        Display.get_instance().show(self.current_screen)

    @staticmethod
    async def cycle_screens():
        while True:
            UserInterface.next_screen()
            await asyncio.sleep(config.SCREEN_CYCLE_INTERVAL)

    @staticmethod
    def next_screen():
        UserInterface.get_instance().current_screen = UserInterface.get_instance()._current_screen + 1

    @staticmethod
    def previous_screen():
        UserInterface.get_instance().current_screen = UserInterface.get_instance()._current_screen - 1
