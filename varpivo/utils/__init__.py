def vypicuj(picung=None):
    raise RuntimeError(picung)


def prepare_recipe_files(recipe_files):
    for file in recipe_files:
        with open(file) as f:
            content = f.read()

        content = content.replace('>true<', '>1<').replace('>TRUE<', '>1<')
        content = content.replace('>false<', '>0<').replace('>FALSE<', '>0<')

        with open(file, 'w') as f:
            f.write(content)


class Event:
    STEP = "STEP"
    WS = "WS"

    def __init__(self, event_type, payload) -> None:
        super().__init__()
        self.event_type = event_type,
        self.payload = payload
