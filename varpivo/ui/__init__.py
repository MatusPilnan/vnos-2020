import asyncio

from varpivo.hardware.buttons import Buttons
from varpivo.hardware.display import Display
from varpivo.ui.screens import *


class UserInterface:
    __instance = None
    screen_changed_manually = False

    @staticmethod
    def get_instance():
        if UserInterface.__instance is None:
            UserInterface.__instance = UserInterface()

        return UserInterface.__instance

    def __init__(self):
        self.screens = [SummaryScreen(), NetworkScreen(), SecurityScreen()]
        self._current_screen = 0
        Display.get_instance().show(StartupScreen())
        Buttons.generic_callbacks.add(UserInterface.button_observer)
        SystemInfo.add_observer(self.update_screen, [SystemInfo.ANY])

    @property
    def current_screen(self):
        return self.screens[self._current_screen]

    @current_screen.setter
    def current_screen(self, val):
        if val < 0:
            val += len(self.screens)

        val = val % len(self.screens)
        self._current_screen = val
        self.update_screen(changed=set(self.current_screen.observed_properties))

    def update_screen(self, changed=None):
        if changed and changed.intersection(self.current_screen.observed_properties):
            self.current_screen.redraw()
            Display.get_instance().show(self.current_screen)

    @staticmethod
    async def cycle_screens():
        while True:
            if not UserInterface.screen_changed_manually:
                UserInterface.next_screen()
            else:
                UserInterface.screen_changed_manually = False
            await asyncio.sleep(config.SCREEN_CYCLE_INTERVAL)

    @staticmethod
    def next_screen():
        UserInterface.get_instance().current_screen = UserInterface.get_instance()._current_screen + 1

    @staticmethod
    def previous_screen():
        UserInterface.get_instance().current_screen = UserInterface.get_instance()._current_screen - 1

    @staticmethod
    def button_observer(button_pressed):
        if button_pressed == Buttons.NEXT:
            UserInterface.next_screen()
            UserInterface.screen_changed_manually = True
        elif button_pressed == Buttons.PREVIOUS:
            UserInterface.previous_screen()
            UserInterface.screen_changed_manually = True
        elif button_pressed == Buttons.UP:
            UserInterface.get_instance().current_screen.up()
        elif button_pressed == Buttons.DOWN:
            UserInterface.get_instance().current_screen.down()
        elif button_pressed == Buttons.ACTION:
            UserInterface.get_instance().current_screen.action()
        else:
            logging.getLogger('quart.app').info(f'Unknown button pressed: {button_pressed}')
