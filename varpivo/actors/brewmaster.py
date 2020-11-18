from actorio import Actor, Message

from varpivo.events.recipe import RecipeSelected
from varpivo.recipe import Recipe
from varpivo.utils import vypicuj


class BrewMaster(Actor):
    recipe: Recipe = None

    async def handle_message(self, message: Message):
        if isinstance(message, RecipeSelected):
            self.on_recipe_selected(message)

    def on_recipe_selected(self, message):
        if self.recipe:
            vypicuj("Recipe already selected")
        self.recipe = message.data

