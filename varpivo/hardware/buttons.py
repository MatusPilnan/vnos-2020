import asyncio
import logging

from varpivo.config import config


class Button:
    def __init__(self, pin, name=None) -> None:
        if not name:
            name = f'GPIO-{pin}'
        self.pin = pin
        self.callbacks = {lambda: logging.getLogger('quart.app').debug(f'Pressed {name} button')}
        self.pressed = False


class Buttons:
    __instance = None
    __button_pins = {
        config.BUTTON_NEXT_GPIO: Button(config.BUTTON_NEXT_GPIO, 'NEXT'),
        config.BUTTON_PREV_GPIO: Button(config.BUTTON_NEXT_GPIO, 'PREVIOUS')
    }

    @staticmethod
    def get_instance():
        if Buttons.__instance is None:
            try:
                # noinspection PyUnresolvedReferences
                import RPi.GPIO as GPIO
                Buttons.__instance = Buttons()

            except ModuleNotFoundError:
                Buttons.__instance = EmulatedButtons()

        return Buttons.__instance

    def __init__(self):
        # noinspection PyUnresolvedReferences
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)

    async def listen_for_buttons(self):
        # noinspection PyUnresolvedReferences
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in Buttons.__button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while True:
            for button in Buttons.__button_pins.values():
                if GPIO.input(button.pin):
                    if not button.pressed:
                        button.pressed = True
                        for callback in button.callbacks:
                            callback()
                else:
                    button.pressed = False

            await asyncio.sleep(0.1)

    @staticmethod
    def add_callback(func, button_gpio):
        Buttons.__button_pins[button_gpio].callbacks.add(func)


class EmulatedButtons(Buttons):
    # noinspection PyMissingConstructor
    def __init__(self):
        logging.getLogger('quart.app').info('Using emulated buttons.')

    async def listen_for_buttons(self):
        while True:
            await asyncio.sleep(120)
