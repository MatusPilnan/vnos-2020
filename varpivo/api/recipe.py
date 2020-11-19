from quart import jsonify
from quart_openapi import Resource
from varpivo import app
from varpivo.recipe import CookBook
from http import HTTPStatus

from varpivo.steps import Step

recipe_list_properties = {
    'name': {
        'type': 'string'
    },
    'id': {
        'type': 'string'
    },
    'style': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'type': {'type': 'string'}
        }
    }
}
recipe_list = app.create_validator('recipe_list', {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': recipe_list_properties
    },
})


# api = OpenApiView(app=blueprint, title="Var:Pivo API", doc="/documentation", version=API_VERSION)
@app.route("/recipe")
class RecipeList(Resource):
    @app.response(HTTPStatus.OK, description="", validator=recipe_list)
    async def get(self):
        '''Retrieve all available recipes

        This docstring will show up as the description and short-description
        for the openapi docs for this route.
        '''
        return jsonify(list(map(lambda recipe: recipe.cookbook_entry, CookBook().recipes.values())))


def step_to_dict(step: Step):
    return {"started": step.started,
            "finished": step.finished,
            "progress": step.progress,
            "estimation": step.estimation,
            "description": step.description,
            "duration": step.duration,
            "name": step.name,
            "available": step.available}


recipe_list = app.create_validator('recipe_steps', {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            "started": {
                "type": "string"
            },
            "finished": {
                "type": "string"
            },
            "progress": {
                "type": "string"
            },
            "estimation": {
                "type": "integer"
            },
            "description": {
                "type": "string"
            },
            "duration_mins": {
                "type": "integer"
            },
            "name": {
                "type": "string"
            },
            "available": {
                "type": "boolean"
            }
        }
    },
})


# noinspection PyUnresolvedReferences
@app.param("recipe_id", "Recipe ID", "path", required=True)
@app.route('/recipe/<recipe_id>')
class Recipe(Resource):

    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.OK, description="",
                  validator=app.create_validator('recipe', {"type": "object", "properties": recipe_list_properties}))
    async def get(self, recipe_id):
        try:
            return jsonify(CookBook()[recipe_id].cookbook_entry)
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), 404

    @app.response(HTTPStatus.NOT_FOUND, "Recipe not found")
    @app.response(HTTPStatus.CONFLICT, "Recipe already selected")
    @app.response(HTTPStatus.OK, description="",
                  validator=app.create_validator('recipe', {"type": "object", "properties": recipe_list_properties}))
    async def post(self, recipe_id):
        try:
            # TODO - skontrolovat ci uz nahodou neni nejaky vybraty
            # TODO - vybrat :)
            return jsonify(list(map(step_to_dict, CookBook()[recipe_id].steps)))
        except KeyError:
            return jsonify({"error": 'Recipe not found'}), 404
