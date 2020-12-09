from typing import Dict, List

from pybeerxml import recipe
from pybeerxml.style import Style

from varpivo.config.config import DEFAULT_MASH_STEP_TIME
from varpivo.cooking.ingredients import Fermentable, Hop, Misc, Ingredient
from varpivo.steps import *


class Recipe(recipe.Recipe):
    boil_started_at = None
    target_boil_duration = None

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
            if not ms.step_time:
                ms.step_time = DEFAULT_MASH_STEP_TIME
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
        dep = [steps[-1]]
        i = -1
        for hop in recipe.hops:
            if hop.use == 'Boil':
                i += 1
                while len(miscs) > 0 and miscs[0].time > hop.time:
                    if miscs[0].time != remaining_boil_time:
                        steps.append(Boil(name='Boil',
                                          duration=int(remaining_boil_time - miscs[0].time),
                                          dependencies=[steps[-1]]))
                        dep = [steps[-1]]
                    steps.append(AddMisc(name=miscs[0].name, amount=miscs[0].amount,
                                         misc_type=miscs[0].type, dependencies=dep))
                    remaining_boil_time = miscs[0].time
                    miscs.pop(0)

                if hop.time != remaining_boil_time and (not miscs or miscs[0].time != remaining_boil_time):
                    steps.append(Boil(name='Boil',
                                      duration=int(remaining_boil_time - hop.time),
                                      dependencies=[steps[-1]]))
                    dep = [steps[-1]]
                steps.append(AddHop(name=hop.name, grams=int(hop.amount * 1000),
                                    dependencies=dep + [hop_boil_addition_deps[i]]))
                remaining_boil_time = hop.time

        if remaining_boil_time > 0:
            steps.append(Boil(name='Boil',
                              duration=int(remaining_boil_time),
                              dependencies=[steps[-1]]))
        last_boil_step = len(steps) - 1
        for step in after_boil_fermentables:
            step.dependencies.append(steps[last_boil_step])
            steps.append(step)

        for step in steps:
            self.steps[step.id] = step
        self.target_boil_duration = self.recipe.boil_time

    @property
    def cookbook_entry(self):
        # noinspection PyUnresolvedReferences
        return {"name": self.recipe.name, "id": self.id,
                "style": {"name": self.recipe.style.name, "type": self.recipe.style.type},
                "ingredients": self.ingredients, "boil_time": self.target_boil_duration}

    @property
    def steps_list(self):
        # TODO nejake rozumne zoradovanie - ak to nechceme riesit na FE
        return self.steps.values()

    def to_checkpoint(self):
        return self

    def __iter__(self):
        for step in self.steps_list:
            yield step

    async def step_event(self, event):
        if self.boil_started_at is None and isinstance(event.payload, Boil):
            self.boil_started_at = int((time()) * 1000)
            await event_queue.put(Event(Event.WS, payload=json.dumps(
                {"content": "boil_started_at", "payload": json.dumps(self.boil_started_at)})))


class TestRecipe(Recipe):

    # noinspection PyMissingConstructor
    def __init__(self):
        self.id = 'test-recipe'
        self.recipe = recipe.Recipe()
        self.recipe.name = 'Testovací recep'
        self.recipe.style = Style()
        self.recipe.style.name = "Penne-tračný test"
        self.recipe.style.type = 'Testoviny'
        # noinspection PyListCreation
        steps: List[Step] = [
            WeighIngredient(ingredient='Penne Barilla (z Lidla)', grams=1000),
            AddWater(amount=3)
        ]

        steps.append(SetTemperature(target=69, dependencies=[steps[-1]]))
        steps.append(AddMisc(name='salt', misc_type='salt', amount=1, dependencies=[steps[-2]]))
        steps.append(KeepTemperature(name='Len tak nech vidia že môžeme', duration=3, dependencies=[steps[-1]]))
        steps.append(SetTemperature(target=100, dependencies=[steps[-1]]))
        steps.append(Step(name='Pridaj cestoviny', description='Šak to je asi jasné celkom', duration=1, dependencies=[
            steps[-3], steps[-1]
        ]))
        steps.append(Boil(name='Boil', duration=10, dependencies=[steps[-1]]))

        self.ingredients = [
            Ingredient('Salz', amount=1, unit='štipka').to_dict(),
            Ingredient('Penne Barilla (z Lidla)', amount=1000, unit='g').to_dict()
        ]
        self.steps: Dict[str, Step] = {}
        for step in steps:
            self.steps[step.id] = step
        self.target_boil_duration = 10
