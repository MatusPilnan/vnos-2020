import logging

from varpivo.config import config


class Button:
    def __init__(self, pin, name=None) -> None:
        if not name:
            name = f'GPIO-{pin}'
        self.name = name
        self.pin = pin
        self.callbacks = {lambda: logging.getLogger('quart.app').debug(f'Pressed {name} button')}
        # noinspection PyUnresolvedReferences
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=Buttons.execute_callbacks, bouncetime=500)


class Buttons:
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"
    UP = "UP"
    DOWN = "DOWN"
    ACTION = "ACTION"

    __instance = None
    __button_pins = None
    generic_callbacks = set()

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
        Buttons.__button_pins = {
            config.BUTTON_NEXT_GPIO: Button(config.BUTTON_NEXT_GPIO, Buttons.NEXT),
            config.BUTTON_PREV_GPIO: Button(config.BUTTON_PREV_GPIO, Buttons.PREVIOUS)
        }

    @staticmethod
    def execute_callbacks(pin):
        button = Buttons.__button_pins[pin]
        for callback in Buttons.generic_callbacks:
            callback(button.name)
        for callback in button.callbacks:
            callback()


class EmulatedButtons(Buttons):
    # noinspection PyMissingConstructor
    def __init__(self):
        logging.getLogger('quart.app').info('Using emulated buttons.')

