import logging

from PIL import Image, ImageDraw, ImageFont

from varpivo.config import config
from varpivo.info.system_info import SystemInfo


class Screen:
    observed_properties = [SystemInfo.ANY]

    def __init__(self, dimensions=(128, 64)):
        self.image = Image.new(mode='1', size=dimensions)
        self.rect = [(0, 0), self.image.size]

    def redraw(self):
        pass

    def up(self):
        pass

    def down(self):
        pass

    def action(self):
        pass


class SummaryScreen(Screen):
    observed_properties = [SystemInfo.TEMPERATURE, SystemInfo.HEATING, SystemInfo.WEIGHT]

    def redraw(self):
        draw = ImageDraw.Draw(self.image)

        info = SystemInfo.get_instance()
        message = f'Temperature: {info.temperature}°C\n' \
                  f'Heater {"on" if info.heating else "off"}\n' \
                  f'Weight: {info.weight} g'

        draw.rectangle(self.rect, outline="black", fill="black")
        draw.text((5, 15), message, fill="white")


class NetworkScreen(Screen):
    observed_properties = [SystemInfo.ADDRESSES]

    def redraw(self):
        draw = ImageDraw.Draw(self.image)

        message = 'IP Addresses:\n' + '\n'.join(SystemInfo.get_instance().addresses)
        draw.rectangle(self.rect, outline="black", fill="black")
        draw.text((5, 5), message, fill="white")


class SecurityScreen(Screen):
    observed_properties = [SystemInfo.BREW_SESSION_CODE]

    def __init__(self):
        super().__init__()
        try:
            self.font = ImageFont.truetype(config.SECURITY_CODE_FONT_FILE, 30)
        except OSError:
            self.font = None
            logging.getLogger('quart.app').info('Could not load security code font.')

    def redraw(self):
        draw = ImageDraw.Draw(self.image)

        draw.rectangle(self.rect, outline="black", fill="black")
        draw.text((5, 5), "Brew session code:", fill="white")
        draw.text((5, 25), f"{SystemInfo.get_instance().brew_session_code}", fill="white", font=self.font)


class StartupScreen(Screen):

    def __init__(self):
        super().__init__()
        with Image.open('varpivo.jpg') as img:
            position = ((self.image.width - img.width) // 2, (self.image.height - img.height) // 2)
            self.image.paste(img, position)

    def redraw(self):
        pass

