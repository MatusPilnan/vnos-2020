import asyncio
import logging
from typing import List, Union

from varpivo.config import config
from varpivo.utils.sounds import Note


class Buzzer:
    __instance = None

    @staticmethod
    def get_instance():
        if Buzzer.__instance is None:
            try:
                Buzzer.__instance = Buzzer()
            except ModuleNotFoundError:
                Buzzer.__instance = EmulatedBuzzer()

        return Buzzer.__instance

    def __init__(self) -> None:
        import RPi.GPIO as GPIO
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.BUZZER_GPIO, GPIO.OUT)
        self.buzzer = GPIO.PWM(config.BUZZER_GPIO, 1000)

    async def buzz(self, pattern_miliseconds: Union[List[int], int]):
        if isinstance(pattern_miliseconds, int):
            pattern_miliseconds = [pattern_miliseconds]

        self.buzzer.ChangeFrequency(1000)
        for beep in pattern_miliseconds:
            self.buzzer.start()
            await asyncio.sleep(beep / 1000)
            self.buzzer.stop()
            await asyncio.sleep(config.BUZZER_DELAY)

    async def play_melody(self, song: List[Note]):
        for note in song:
            if note.frequency > 0:
                self.buzzer.ChangeFrequency(note.frequency)
                self.buzzer.start(50)
                await asyncio.sleep(note.duration / 1000)
                self.buzzer.stop()
            else:
                await asyncio.sleep(note.duration / 1000)


class EmulatedBuzzer(Buzzer):

    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        logging.getLogger('quart.app').info('Using emulated buzzer')

    async def buzz(self, pattern_miliseconds: Union[List[int], int]):
        logging.getLogger('quart.app').debug(f'Buzzing pattern requested: {pattern_miliseconds}')

    async def play_melody(self, song: List[Note]):
        logging.getLogger('quart.app').debug(f'Melody requested: {song}')
