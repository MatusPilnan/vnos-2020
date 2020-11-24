import json
import uuid
from time import time

from quart import jsonify

from varpivo import broadcast, event_queue
from varpivo.utils import Event


class Step:
    started = None
    finished = None
    progress = None
    estimation = None
    next_step = None

    def __init__(self, name: str, description: str, duration: int, dependencies=None) -> None:
        super().__init__()
        if dependencies is None:
            dependencies = []
        self.id = str(uuid.uuid4())
        self.description = description
        self.duration = duration
        self.estimation = duration
        self.name = name
        self.dependencies = list(dependencies)

        for dependency in dependencies:
            if not isinstance(dependency, WeighIngredient):
                dependency.next_step = self

    @property
    def available(self):
        for dependency in self.dependencies:
            if not dependency.finished:
                return False
        return not self.started

    def to_dict(self):
        return {"id": self.id,
                "started": self.started,
                "finished": self.finished,
                "progress": self.progress,
                "estimation": self.estimation,
                "description": self.description,
                "duration": self.duration,
                "name": self.name,
                "available": self.available}

    def to_keg(self):
        return json.dumps({"payload": json.dumps(self.to_dict()), "content": "step"})

    async def start(self):
        self.started = time()
        await event_queue.put(Event(Event.STEP, payload=self))

    async def stop(self):
        self.finished = time()
        await event_queue.put(Event(Event.STEP, payload=self))
        if self.next_step.available:
            await self.next_step.start()


class AddWater(Step):

    def __init__(self, amount: int, dependencies=None) -> None:
        super().__init__(name=f'Add water: {amount:.2f} L', description=f'Add {amount:.2f} L water for infusion.',
                         duration=2 + amount // 2, dependencies=dependencies)


class SetTemperature(Step):

    def __init__(self, target: int, dependencies=None) -> None:
        super().__init__(name=f'Heat water: {target:.2f} C', description=f'Heat water to {target:.2f}°C.',
                         duration=target // 2, dependencies=dependencies)
        self.target = target

    async def start(self):
        await super().start()


class WeighIngredient(Step):

    def __init__(self, ingredient: str, grams: int, dependencies=None) -> None:
        super().__init__(f'Weight {ingredient}: {grams} g', description=f'Weight {grams} grams of {ingredient}.',
                         duration=3, dependencies=dependencies)
        self.grams = grams

    async def stop(self):
        self.finished = time()
        await broadcast(jsonify(self.to_dict()))


class KeepTemperature(Step):

    def __init__(self, name: str, duration: int, dependencies=None) -> None:
        super().__init__(name=name, description=f"Keep temperature for {duration} minutes.", duration=duration,
                         dependencies=dependencies)

    async def start(self):
        await super().start()

    async def stop(self):
        await super().stop()


class AddHop(Step):

    def __init__(self, name: str, grams: int, dependencies=None) -> None:
        super().__init__(name=f'Add hops: {name}', description=f'Add {grams} grams of {name} hops.', duration=1,
                         dependencies=dependencies)


class AddMisc(Step):
    def __init__(self, name: str, amount: float, misc_type: str, dependencies=None) -> None:
        super().__init__(name=f'Add {name}', description=f'Add {amount:.2f} units of {name} ({misc_type})', duration=1,
                         dependencies=dependencies)
