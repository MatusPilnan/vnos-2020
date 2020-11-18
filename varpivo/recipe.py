from typing import Dict, List

from pybeerxml.parser import Parser
import glob

from pybeerxml import recipe

from varpivo.config.config import RECIPES_DIR
from os.path import basename


class Recipe(recipe.Recipe):

    def __init__(self, id: str, recipe: recipe.Recipe):
        self.id = id
        self.recipe = recipe
        self.steps: List[Step] = []

        for fermentable in recipe.fermentables:
            if not fermentable.add_after_boil:
                self.steps.append(WeighIngredient(grams=int(fermentable.amount * 1000), ingredient=fermentable.name,
                                                  dependencies=[]))
        recipe.hops.sort(key=(lambda h: h.time), reverse=True)
        hop_boil_addition_deps = []
        for hop in recipe.hops:
            if hop.use == 'Boil':
                step = WeighIngredient(grams=int(hop.amount), ingredient=hop.name, dependencies=[])
                self.steps.append(step)
                hop_boil_addition_deps.append(step)

        for i, ms in enumerate(recipe.mash.steps):
            if i == 0:
                self.steps.append(AddWater(amount=int(ms.infuse_amount), dependencies=[]))
            else:
                self.steps.append(AddWater(amount=int(ms.infuse_amount), dependencies=[self.steps[-1]]))
            self.steps.append(SetTemperature(target=int(ms.step_temp), dependencies=[self.steps[-1]]))
            if i == 0:
                self.steps.append(Step(name='Add malts', description='Add the malts', duration=5,
                                       dependencies=self.steps[:len(recipe.fermentables)]))
            self.steps.append(KeepTemperature(name=ms.name, duration=int(ms.step_time)))

        self.steps.append(Step(name='Mashout', description='Take the mash out of the kettle', duration=2,
                               dependencies=self.steps[-1]))
        self.steps.append(SetTemperature(target=100, dependencies=[self.steps[-1]]))

        remaining_boil_time = int(recipe.boil_time)
        for i, hop in enumerate(recipe.hops):
            if hop.use == 'Boil':
                self.steps.append(KeepTemperature(name='Boil', duration=int(remaining_boil_time - hop.time),
                                                  dependencies=[self.steps[-1]]))
                self.steps.append(AddHop(name=hop.name, grams=int(hop.amount),
                                         dependencies=[self.steps[-1], hop_boil_addition_deps[i]]))
                remaining_boil_time = hop.time


    @property
    def cookbook_entry(self):
        return {"name": self.recipe.name, "id": self.id,
                "style": {"name": self.recipe.style.name, "type": self.recipe.style.type}}


class CookBook:
    def __init__(self) -> None:
        super().__init__()
        parser = Parser()
        path = RECIPES_DIR
        self.recipes: Dict[Recipe] = {}
        for file in glob.glob(f"{path}/*.xml"):
            for index, recipe in enumerate(parser.parse(xml_file=file)):
                id = basename(file) + str(index)
                # noinspection PyTypeChecker
                self.recipes[id] = Recipe(id=id, recipe=recipe)

    def __getitem__(self, item) -> Recipe:
        return self.recipes[item]


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
