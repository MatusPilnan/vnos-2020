import glob
import os
import shelve
from os.path import basename, exists
from typing import Dict, List

from pybeerxml import recipe
from pybeerxml.parser import Parser

from varpivo import event_observers
from varpivo.config.config import RECIPES_DIR
from varpivo.steps import *
from varpivo.utils import prepare_recipe_files


class Recipe(recipe.Recipe):

    def __init__(self, id: str, recipe: recipe.Recipe):
        self.id = id
        self.recipe = recipe
        steps: List[Step] = []
        self.ingredients = []
        self.steps: Dict[str, Step] = {}

        mash_fermentable_count = 0
        after_boil_fermentables = []
        for fermentable in recipe.fermentables:
            self.ingredients.append(Fermentable(fermentable).to_dict())
            if not fermentable.add_after_boil:
                mash_fermentable_count += 1
                steps.append(WeighIngredient(grams=int(fermentable.amount * 1000), ingredient=fermentable.name,
                                             dependencies=[]))
            else:
                step = WeighIngredient(grams=int(fermentable.amount * 1000),
                                       ingredient=fermentable.name,
                                       dependencies=[])
                steps.append(step)
                after_boil_fermentables.append(Step(name=f'Add {fermentable.name}',
                                                    description=
                                                    f'Add {fermentable.amount:.2f} kg of {fermentable.name}',
                                                    duration=2,
                                                    dependencies=[step]))

        recipe.hops.sort(key=(lambda h: h.time), reverse=True)
        hop_boil_addition_deps = []
        for hop in recipe.hops:
            self.ingredients.append(Hop(hop).to_dict())
            if hop.use == 'Boil':
                step = WeighIngredient(grams=int(hop.amount * 1000), ingredient=hop.name, dependencies=[])
                steps.append(step)
                hop_boil_addition_deps.append(step)

        for i, ms in enumerate(recipe.mash.steps):
            if i == 0:
                steps.append(AddWater(amount=int(ms.infuse_amount), dependencies=[]))
            else:
                steps.append(AddWater(amount=int(ms.infuse_amount), dependencies=[steps[-1]]))
            steps.append(SetTemperature(target=int(ms.step_temp), dependencies=[steps[-1]]))
            if i == 0:
                steps.append(Step(name='Add malts', description='Add the malts', duration=5,
                                  dependencies=steps[:mash_fermentable_count] + [steps[-1]]))
            steps.append(KeepTemperature(name=ms.name, duration=int(ms.step_time), dependencies=[steps[-1]]))

        steps.append(Step(name='Mashout', description='Take the mash out of the kettle', duration=2,
                          dependencies=[steps[-1]]))
        steps.append(SetTemperature(target=100, dependencies=[steps[-1]]))

        miscs = []
        for misc in recipe.miscs:
            self.ingredients.append(Misc(misc).to_dict())
            if misc.use == 'Boil':
                miscs.append(misc)

        miscs.sort(key=(lambda m: m.time), reverse=True)

        remaining_boil_time = int(recipe.boil_time)
        dep = steps[-1]
        for i, hop in enumerate(recipe.hops):
            if hop.use == 'Boil':
                while len(miscs) > 0 and miscs[0].time > hop.time:
                    if miscs[0].time != remaining_boil_time:
                        steps.append(KeepTemperature(name='Boil',
                                                     duration=int(remaining_boil_time - miscs[0].time),
                                                     dependencies=[steps[-1]]))
                        dep = [steps[-1]]
                    steps.append(AddMisc(name=miscs[0].name, amount=miscs[0].amount,
                                         misc_type=miscs[0].type, dependencies=dep))
                    remaining_boil_time = miscs[0].time
                    miscs.pop(0)

                if miscs[0].time != remaining_boil_time:
                    steps.append(KeepTemperature(name='Boil',
                                                 duration=int(remaining_boil_time - hop.time),
                                                 dependencies=[steps[-1]]))
                    dep = [steps[-1]]
                steps.append(AddHop(name=hop.name, grams=int(hop.amount * 1000),
                                    dependencies=dep + [hop_boil_addition_deps[i]]))
                remaining_boil_time = hop.time

        if remaining_boil_time > 0:
            steps.append(KeepTemperature(name='Boil',
                                         duration=int(remaining_boil_time),
                                         dependencies=[steps[-1]]))
        last_boil_step = len(steps) - 1
        for step in after_boil_fermentables:
            step.dependencies.append(steps[last_boil_step])
            steps.append(step)

        for step in steps:
            self.steps[step.id] = step

    @property
    def cookbook_entry(self):
        # noinspection PyUnresolvedReferences
        return {"name": self.recipe.name, "id": self.id,
                "style": {"name": self.recipe.style.name, "type": self.recipe.style.type},
                "ingredients": self.ingredients}

    @property
    def steps_list(self):
        # TODO nejake rozumne zoradovanie - ak to nechceme riesit na FE
        return self.steps.values()

    def to_checkpoint(self):
        return self


class CookBook:
    __instance = None
    selected_recipe = None

    CHECKPOINT_FILE = os.path.join("shelf", "shelf.page")

    @staticmethod
    def get_instance():
        if CookBook.__instance is None:
            CookBook()

        return CookBook.__instance

    @staticmethod
    async def step_observer(event: Event):
        if event.event_type[0] == Event.STEP:
            CookBook.get_instance().save_checkpoint()
            await event_queue.put(Event(Event.WS, payload=event.payload.to_keg()))

    def __init__(self) -> None:
        super().__init__()
        if CookBook.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CookBook.__instance = self

        event_observers.add(CookBook.step_observer)
        self.check_checkpoint()
        parser = Parser()
        path = RECIPES_DIR
        prepare_recipe_files(glob.glob(f"{path}/*.xml"))
        self.recipes: Dict[Recipe] = {}
        for file in glob.glob(f"{path}/*.xml"):
            for index, recipe in enumerate(parser.parse(xml_file=file)):
                id = basename(file) + str(index)
                # noinspection PyTypeChecker
                self.recipes[id] = Recipe(id=id, recipe=recipe)

    def select_recipe(self, recipeId):
        if self.selected_recipe:
            return False
        self.selected_recipe = self[recipeId]
        return True

    def __getitem__(self, item) -> Recipe:
        return self.recipes[item]

    def check_checkpoint(self):
        if not exists(self.CHECKPOINT_FILE):
            return
        checkpoint = shelve.open(self.CHECKPOINT_FILE)
        self.checkpoint = {"recipe": checkpoint["recipe"], "time": checkpoint["time"]}
        checkpoint.close()

    def load_checkpoint(self):
        if self.checkpoint:
            self.selected_recipe = self.checkpoint["recipe"]
            return True
        return False

    def save_checkpoint(self):
        if self.selected_recipe:
            checkpoint = shelve.open(self.CHECKPOINT_FILE)
            checkpoint["recipe"] = self.selected_recipe.to_checkpoint()
            checkpoint["time"] = time()
            checkpoint.close()
            return True
        return False


class Ingredient:
    def __init__(self, name: str, amount: float, unit: str) -> None:
        self.name = name
        self.amount = amount
        self.unit = unit

    def to_dict(self):
        return {"name": self.name, "amount": self.amount, "unit": self.unit}


class Fermentable(Ingredient):
    def __init__(self, fermentable: recipe.Fermentable) -> None:
        super().__init__(name=fermentable.name, amount=fermentable.amount, unit='kg')


class Hop(Ingredient):
    def __init__(self, hop: recipe.Hop) -> None:
        super().__init__(name=hop.name, amount=hop.amount * 1000, unit='g')


class Misc(Ingredient):
    def __init__(self, misc: recipe.Misc) -> None:
        super().__init__(name=misc.name, amount=misc.amount, unit='units')
