from typing import Dict

from pybeerxml.parser import Parser
import glob

from pybeerxml import recipe

from varpivo.config.config import RECIPES_DIR
from os.path import basename


class Recipe(recipe.Recipe):

    def __init__(self, id: str, recipe: recipe.Recipe):
        self.id = id
        self.recipe = recipe

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
                id = file + str(index)
                # noinspection PyTypeChecker
                self.recipes[id] = Recipe(id=basename(file), recipe=recipe)

    def __getitem__(self, item):
        return self.recipes[item]
