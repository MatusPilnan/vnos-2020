import time

from RPi import GPIO
# noinspection PyPackageRequirements
from hx711 import HX711


def calibrate(grams, channels='ab'):
    try:
        real_weight = grams()
    except TypeError:
        real_weight = grams
    val = None
    old_val = None
    i = 1
    try:
        hx = HX711(5, 6)
        hx.set_reading_format("MSB", "MSB")
        hx.reset()
        hx.tare_A()
        hx.tare_B()
        print('Add weight now...')
        time.sleep(2)
        avg_error = real_weight
        values = {}
        reference_values = {}
        for c in channels:
            values[c] = []
        while avg_error > 0.8:
            if val is not None:
                old_val = val
            val_a = hx.get_weight_A(15)
            val_b = hx.get_weight_B(15)
            val = val_a + val_b
            if 'a' in channels:
                values['a'].append(val_a)
            if 'b' in channels:
                values['b'].append(val_b)
            if old_val is not None:
                avg_error = ((avg_error * i) + abs(val - old_val)) / (i + 1)
            print(f'{val:.2f} g, avg error: {avg_error}')

            hx.power_down()
            hx.power_up()
            i += 1
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

    for channel, channel_values in values.items():
        channel_values.sort()
        reference_values[channel] = (channel_values[len(channel_values) // 2] // (grams / len(channels)))

    return reference_values
