import json
import uuid
from time import time

from varpivo.kettle import Kettle
from varpivo.utils import Event, EventQueue


class Step:
    started = None
    finished = None
    progress = None
    estimation = None
    kind = 'generic'
    manual = True
    target = None

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
        self.next_steps = list()

        for dependency in dependencies:
            dependency.next_steps.append(self)

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
                "available": self.available,
                "kind": self.kind,
                "target": self.target}

    def to_keg(self):
        return json.dumps({"payload": json.dumps(self.to_dict()), "content": "step"})

    async def start(self):
        self.started = time()
        await EventQueue.get_queue().put(Event(Event.STEP, payload=self))

    async def stop(self):
        self.finished = time()
        await EventQueue.get_queue().put(Event(Event.STEP, payload=self))
        for next_step in self.next_steps:
            if next_step.available:
                await EventQueue.get_queue().put(Event(Event.STEP_AUTOSTART, payload=next_step))
                await next_step.start()

    def reset(self):
        self.started = None
        self.finished = None


class AddWater(Step):
    kind = 'water'

    def __init__(self, amount: int, dependencies=None) -> None:
        super().__init__(name=f'Add water: {amount:.2f} L', description=f'Add {amount:.2f} L water for infusion.',
                         duration=2 + amount // 2, dependencies=dependencies)


class SetTemperature(Step):
    kind = 'set_temperature'
    manual = False

    def __init__(self, target: int, dependencies=None) -> None:
        super().__init__(name=f'Heat water: {target:.2f} C', description=f'Heat water to {target:.2f}°C.',
                         duration=target // 2, dependencies=dependencies)
        self.target = target

    async def start(self):
        Kettle.get_instance().target_temperature = self.target
        Kettle.get_instance().add_observing_step(self.id)
        await super().start()

    async def stop(self):
        Kettle.get_instance().remove_observing_step(self.id)
        return await super().stop()

    async def observe_kettle(self, temperature):
        if temperature >= self.target:
            await self.stop()
        else:
            if self.progress != temperature:
                self.progress = temperature / self.target
                await EventQueue.get_queue().put(Event(Event.STEP, payload=self))


class WeighIngredient(Step):
    kind = 'weight'

    def __init__(self, ingredient: str, grams: int, dependencies=None) -> None:
        super().__init__(f'Weight {ingredient}: {grams} g', description=f'Weight {grams} grams of {ingredient}.',
                         duration=3, dependencies=dependencies)
        self.target = grams


class KeepTemperature(Step):
    kind = 'keep_temperature'
    manual = False

    def __init__(self, name: str, duration: int, dependencies=None) -> None:
        super().__init__(name=name, description=f"Keep temperature for {duration} minutes.", duration=duration,
                         dependencies=dependencies)

    async def start(self):
        self.target = time() + self.duration * 60
        Kettle.get_instance().add_observing_step(self.id)
        await super().start()

    async def stop(self):
        Kettle.get_instance().remove_observing_step(self.id)
        return await super().stop()

    async def observe_kettle(self, temperature):
        if time() >= self.target:
            await self.stop()
        else:
            p = round((time() - self.started) / (self.target - self.started), 2)
            if self.progress != p:
                self.progress = p
                await EventQueue.get_queue().put(Event(Event.STEP, payload=self))

    def reset(self):
        super().reset()
        self.target = None


class Boil(KeepTemperature):
    pass


class AddHop(Step):
    kind = 'hop'

    def __init__(self, name: str, grams: int, dependencies=None) -> None:
        super().__init__(name=f'Add hops: {name}', description=f'Add {grams} grams of {name} hops.', duration=1,
                         dependencies=dependencies)


class AddMisc(Step):
    kind = 'misc'

    def __init__(self, name: str, amount: float, misc_type: str, dependencies=None) -> None:
        super().__init__(name=f'Add {name}', description=f'Add {amount:.2f} units of {name} ({misc_type})', duration=1,
                         dependencies=dependencies)


def step_to_dict(step: Step):
    return step.to_dict()
