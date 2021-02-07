def vypicuj(picung=None):
    raise RuntimeError(picung)


def prepare_recipe_files(recipe_files):
    for file in recipe_files:
        with open(file, encoding='utf-8') as f:
            content = f.read()

        content = content.replace('>true<', '>1<').replace('>TRUE<', '>1<')
        content = content.replace('>false<', '>0<').replace('>FALSE<', '>0<')

        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)


class Event:
    CALIBRATION_READY = "CALIBRATION_READY"
    BREW_SESSION_STARTED = "BREW_SESSION_STARTED"
    BREW_SESSION_FINISHED = "BREW_SESSION_FINISHED"
    STEP = "STEP"
    STEP_AUTOSTART = "STEP_AUTOSTART"
    WS = "WS"
    BUTTON_PRESSED = "BUTTON_PRESSED"

    def __init__(self, event_type, payload) -> None:
        super().__init__()
        self.event_type = event_type,
        self.payload = payload
