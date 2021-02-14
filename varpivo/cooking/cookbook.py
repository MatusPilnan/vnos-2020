import glob
import logging
import time
from os.path import basename
from shutil import rmtree
from typing import Dict

from varpivo.config.config import RECIPES_DIR, CHECKPOINT_DIR
from varpivo.cooking.recipe import Recipe, TestRecipe
from varpivo.kettle import Kettle
from varpivo.utils import prepare_recipe_files, EventQueue, Event, replace_boolean
from varpivo.utils.BeerXMLUnicodeParser import BeerXMLUnicodeParser
from varpivo.utils.librarian import get_selected_recipe, save_selected_recipe, save_beerxml, \
    check_recipe_file_existence, remove_recipe_file


class CookBook:
    __instance = None
    selected_recipe = None

    @staticmethod
    def get_instance():
        if CookBook.__instance is None:
            CookBook()

        return CookBook.__instance

    @staticmethod
    async def step_observer(event: Event):
        if event.event_type[0] == Event.STEP:
            await CookBook.get_instance().selected_recipe.step_event(event)
            CookBook.get_instance().save_checkpoint()
            brewing_finished = True
            for step in CookBook.get_instance().selected_recipe:
                if not step.finished:
                    brewing_finished = False
                    break

            await EventQueue.get_queue().put(Event(Event.WS, payload=event.payload.to_keg()))
            if brewing_finished:
                await EventQueue.get_queue().put(Event(Event.BREW_SESSION_FINISHED, None))
                CookBook.get_instance().unselect_recipe()

    def __init__(self) -> None:
        super().__init__()
        if CookBook.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CookBook.__instance = self

        EventQueue.event_observers.add(CookBook.step_observer)
        self.load_checkpoint()
        parser = BeerXMLUnicodeParser()
        path = RECIPES_DIR
        prepare_recipe_files(glob.glob(f"{path}/*.xml"))
        self.recipes: Dict[str, Recipe] = {}
        for file in glob.glob(f"{path}/*.xml"):
            try:
                for index, recipe in enumerate(parser.parse(xml_file=file)):
                    id = basename(file) + str(index)
                    # noinspection PyTypeChecker
                    self.recipes[id] = Recipe(id=id, recipe=recipe)
            except UnicodeDecodeError:
                logging.getLogger('quart.app').warning(f'Could not parse file: {file}')
        self.recipes['test-recipe'] = TestRecipe()

    async def select_recipe(self, recipeId):
        if self.selected_recipe:
            return False
        self.selected_recipe = self[recipeId]
        await EventQueue.get_queue().put(Event(Event.BREW_SESSION_STARTED, None))
        return True

    def unselect_recipe(self):
        if self.selected_recipe:
            for step in self.selected_recipe:
                step.reset()
            self.selected_recipe = None
        try:
            rmtree(CHECKPOINT_DIR)
        except FileNotFoundError:
            pass

    def __getitem__(self, item) -> Recipe:
        return self.recipes[item]

    def load_checkpoint(self):
        checkpoint = get_selected_recipe()
        if not checkpoint:
            return False
        if checkpoint:
            self.selected_recipe = checkpoint["recipe"]
            Kettle.get_instance()
            return True
        return False

    def save_checkpoint(self):
        if self.selected_recipe:
            save_selected_recipe(self.selected_recipe)
            return True
        return False

    def add_recipe_from_beerxml(self, beerxml, recipe_id, replace=False, add=False):
        beerxml = replace_boolean(beerxml)

        if check_recipe_file_existence(recipe_id):
            if add:
                recipe_id = f'{recipe_id}-{time.ctime()}'
            elif not replace:
                raise FileExistsError

        filename = recipe_id + '.xml'
        recipe_id = filename + '0'
        parser = BeerXMLUnicodeParser()
        recipes = parser.parse_from_string(beerxml)

        self.recipes[recipe_id] = Recipe(id=recipe_id, recipe=recipes[0])
        save_beerxml(filename, beerxml)
        return self.recipes[recipe_id]

    def remove_recipe(self, recipe_id: str):
        self.recipes.pop(recipe_id)
        filename = recipe_id.rstrip('0123456789')
        try:
            remove_recipe_file(filename)
        except FileNotFoundError:
            pass
