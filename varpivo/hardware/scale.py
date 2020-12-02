import asyncio
import json
from random import random
from statistics import mean

from varpivo.config.config import SCALE_CALIBRATION_FILE, SCALE_CALIBRATION_ERROR_THRESHOLD
from varpivo.utils import Event


class Scale:
    calibration_weight = None
    __instance = None
    calibrating = False

    @staticmethod
    def get_instance():
        if Scale.__instance is None:
            try:
                Scale()
            except ModuleNotFoundError:
                Scale.__instance = EmulatedScale()

        return Scale.__instance

    def __init__(self) -> None:
        super().__init__()
        # noinspection PyUnresolvedReferences
        from hx711 import HX711
        if Scale.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.hx = None
            self.init_sensor()
            Scale.__instance = self

    def init_sensor(self):
        if not self.hx:
            self.hx = HX711(5, 6)
            try:
                with open(SCALE_CALIBRATION_FILE) as f:
                    cal = json.load(f)
                    self.hx.set_reference_unit_A(cal['a'])
                    self.hx.set_reference_unit_B(cal['b'])
            except FileNotFoundError:
                print('Reference units for scale not found')
            self.hx.set_reading_format("MSB", "MSB")
            self.tare()

    @property
    async def weight(self):
        return self.hx.get_weight_A() + self.hx.get_weight_B()

    def start_calibration(self, grams):
        if self.calibrating:
            return False
        Scale.calibration_weight = grams
        self.calibrating = True
        self.tare()
        return True

    def tare(self):
        self.hx.tare_A()
        self.hx.tare_B()

    async def find_reference_units(self, grams):
        channels = 'ab'
        val = None
        old_val = None
        avg_error = grams
        values = {}
        reference_values = {}
        errors = []
        for c in channels:
            values[c] = []
        while avg_error > SCALE_CALIBRATION_ERROR_THRESHOLD:
            if val is not None:
                old_val = val
            val_a = self.hx.get_value_A(15)
            val_b = self.hx.get_value_B(15)
            val = val_a + val_b
            if 'a' in channels:
                values['a'].append(val_a)
            if 'b' in channels:
                values['b'].append(val_b)
            if old_val is not None:
                errors.append(abs(val - old_val))
                avg_error = mean(errors[-5:])

            self.hx.power_down()
            self.hx.power_up()
            await asyncio.sleep(0.1)

        for channel, channel_values in values.items():
            channel_values.sort()
            reference_values[channel] = (channel_values[len(channel_values) // 2] // (grams / len(channels)))

        if 'a' in channels:
            self.hx.set_reference_unit_A(reference_values['a'])
        if 'b' in channels:
            self.hx.set_reference_unit_B(reference_values['b'])

        with open(SCALE_CALIBRATION_FILE, 'w') as f:
            json.dump(reference_values, f)
        self.calibrating = False
        from varpivo import event_queue
        await event_queue.put(Event(Event.WS, payload=json.dumps({"content": "calibration", "payload": "done"})))

    @staticmethod
    async def calibration_observer(event):
        if event.event_type[0] == Event.CALIBRATION_READY:
            await Scale.get_instance().find_reference_units(Scale.calibration_weight)


class EmulatedScale(Scale):

    # noinspection PyMissingConstructor
    def __init__(self) -> None:
        pass

    def init_sensor(self):
        pass

    @property
    async def weight(self):
        return random() * 100

    def tare(self):
        pass

    async def start_calibration(self, grams):
        print('emulated calibration')

    async def find_reference_units(self, grams):
        pass
