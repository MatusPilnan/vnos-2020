class Step:

    started = None
    finished = None
    progress = None
    estimation = None

    def __init__(self, name: str, description: str, duration: int, dependencies=None) -> None:
        super().__init__()
        if dependencies is None:
            dependencies = []
        self.description = description
        self.duration = duration
        self.name = name
        self.dependendies = dependencies

    @property
    def available(self):
        for dependency in self.dependendies:
            if not dependency.finished:
                return False
        return not self.started


class AddWater(Step):

    def __init__(self, amount: int, dependencies=None) -> None:
        super().__init__(name=f'Add water: {amount:.2f} L', description=f'Add {amount:.2f} L water for infusion.',
                         duration=2 + amount//2, dependencies=dependencies)


class SetTemperature(Step):

    def __init__(self, target: int, dependencies=None) -> None:
        super().__init__(name=f'Heat water: {target:.2f} C', description=f'Heat water to {target:.2f}°C.',
                         duration=target//2, dependencies=dependencies)
        self.target = target


class WeighIngredient(Step):

    def __init__(self, ingredient: str, grams: int, dependencies=None) -> None:
        super().__init__(f'Weight {ingredient}: {grams}g', description=f'Weight {grams} grams of {ingredient}.', duration=3, dependencies=dependencies)
        self.grams = grams


class KeepTemperature(Step):

    def __init__(self, name: str, duration: int, dependencies=None) -> None:
        super().__init__(name=name, description=f"Keep temperature for {duration} minutes.", duration=duration, dependencies=dependencies)


class AddHop(Step):

    def __init__(self, name: str, grams: int, dependencies=None)-> None:
        super().__init__(name=f'Add hops: {name}', description=f'Add {grams} gramsof {name} hops.', duration=1, dependencies=dependencies)
