from quart import jsonify
from quart_openapi import Resource
from varpivo import app
from varpivo.recipe import CookBook


# api = OpenApiView(app=blueprint, title="Var:Pivo API", doc="/documentation", version=API_VERSION)
@app.route("/recipe")
class RecipeList(Resource):
    async def get(self):
        '''Retrieve all available recipes

        This docstring will show up as the description and short-description
        for the openapi docs for this route.
        '''
        return jsonify(list(map(lambda recipe: recipe.cookbook_entry, CookBook().recipes.values())))


# noinspection PyUnresolvedReferences
@app.route('/recipe/<rid>')
class Recipe(Resource):
    async def get(self, rid):
        try:
            return jsonify(CookBook()[rid].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), 404

    async def post(self, rid):
        try:
            # TODO - skontrolovat ci uz nahodou neni nejaky vybraty
            # TODO - vybrat :)
            return jsonify(CookBook()[rid].steps)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), 404
