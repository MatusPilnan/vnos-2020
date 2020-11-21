ingredient_model = {
    "type": "object",
    "title": "Ingredient",
    "required": ["name", "amount"],
    "properties": {
        "name": {
            "type": "string"
        },
        "unit": {
            "type": "string"
        },
        "amount": {
            "type": "number"
        }
    }
}

recipe_model = {
    'type': 'object',
    'title': 'Recipe',
    'properties': {
        'name': {
            'type': 'string'
        },
        'id': {
            'type': 'string',
        },
        'style': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'type': {'type': 'string'}
            },
            'required': ['name', 'type']
        },
        "ingredients": {
            "type": "array",
            "items": ingredient_model
        }
    },
    'required': ['id', 'style', 'name', 'ingredients']
}

recipe_list_model = {
    'title': 'RecipeList',
    'type': 'object',
    'properties': {
        'recipes': {
            'type': 'array',
            'items': recipe_model
        }
    },
    'required': ['recipes']
}

step_model = {
    'type': 'object',
    'title': 'RecipeStep',
    'properties': {
        "started": {
            "type": "number"
        },
        "finished": {
            "type": "number"
        },
        "progress": {
            "type": "number"
        },
        "estimation": {
            "type": "number"
        },
        "description": {
            "type": "string",
            "default": ""
        },
        "duration_mins": {
            "type": "number"
        },
        "name": {
            "type": "string"
        },
        "available": {
            "type": "boolean"
        }
    },
    "required": ["name", "available", "description"]
}

ws_message_model = {
    "type": "object",
    "title": "WSKeg",
    "required": ["payload", "content"],
    "properties": {
        "payload": {
            "type": "string"
        },
        "content": {
            "type": "string"
        }
    }
}

recipe_steps_model = {
    "type": "object",
    "title": "StepsList",
    "required": ["steps"],
    "properties": {
        "steps": {
            'type': 'array',
            'items': step_model
        }
    }
}
