ingredient_model = {
    "type": "object",
    "title": "Ingredient",
    "required": ["name", "amount", "unit"],
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
        },
        "boil_time": {
            "type": "number"
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
        "id": {
            "type": "string"
        },
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
        },
        "kind": {
            "type": "string",
            "default": "generic"
        },
        "target": {
            "type": "number"
        }
    },
    "required": ["name", "available", "description", "id", "kind"]
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

ws_temperature_model = {
    "type": "object",
    "title": "Temperature",
    "required": ["temperature", "heating"],
    "properties": {
        "temperature": {
            "type": "number"
        },
        "heating": {
            "type": "boolean"
        }
    }
}

step_list_property = {
    'type': 'array',
    'items': step_model
}

recipe_steps_model = {
    "type": "object",
    "title": "StepsList",
    "required": ["steps"],
    "properties": {
        "steps": step_list_property
    }
}

brew_session_model = {
    "type": "object",
    "title": "BrewSession",
    "required": ["steps", "recipe"],
    "properties": {
        "steps": step_list_property,
        "recipe": recipe_model,
        "boil_started_at": {
            "type": "number"
        }
    }
}

message_model = {
    "type": "object",
    "title": "Message",
    "required": ["message"],
    "properties": {
        "message": {
            "type": "string"
        }
    }
}
