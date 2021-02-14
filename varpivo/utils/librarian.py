import os
import shelve
from glob import glob
from time import time

from varpivo.config.config import *


def get_checkpoint(file):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_location = os.path.join(CHECKPOINT_DIR, file)
    return shelve.open(checkpoint_location)


def save_kettle(kettle):
    checkpoint = get_checkpoint(KETTLE_CHECKPOINT_FILE)
    checkpoint['target_temperature'] = kettle.target_temperature
    checkpoint['observing_steps'] = kettle.observing_steps
    checkpoint['time'] = time()
    checkpoint.close()


def load_kettle():
    checkpoint_location = os.path.join(CHECKPOINT_DIR, KETTLE_CHECKPOINT_FILE)
    if not glob(checkpoint_location + '*'):
        return None
    checkpoint = get_checkpoint(KETTLE_CHECKPOINT_FILE)
    return {"target_temperature": checkpoint["target_temperature"],
            "time": checkpoint["time"],
            "observing_steps": checkpoint["observing_steps"]}


def save_selected_recipe(recipe):
    checkpoint = get_checkpoint(RECIPE_CHECKPOINT_FILE)
    checkpoint["recipe"] = recipe.to_checkpoint()
    checkpoint["time"] = time()
    checkpoint.close()


def get_selected_recipe():
    checkpoint_location = os.path.join(CHECKPOINT_DIR, RECIPE_CHECKPOINT_FILE)
    if not glob(checkpoint_location + '*'):
        return None
    checkpoint = get_checkpoint(RECIPE_CHECKPOINT_FILE)
    return {"recipe": checkpoint["recipe"], "time": checkpoint["time"]}


def save_security(security):
    checkpoint = get_checkpoint(SECURITY_CHECKPOINT_FILE)
    checkpoint['code'] = security.brew_session_code
    checkpoint['time'] = time()
    checkpoint.close()


def load_security():
    checkpoint_location = os.path.join(CHECKPOINT_DIR, SECURITY_CHECKPOINT_FILE)
    if not glob(checkpoint_location + '*'):
        return None, None
    checkpoint = get_checkpoint(SECURITY_CHECKPOINT_FILE)
    return checkpoint['code'], checkpoint['time']


def discard_security():
    checkpoint_location = os.path.join(CHECKPOINT_DIR, SECURITY_CHECKPOINT_FILE)
    for file in glob(checkpoint_location + '*'):
        os.remove(file)


def check_recipe_file_existence(recipe_id):
    return os.path.isfile(os.path.join(RECIPES_DIR, f'{recipe_id}.xml'))


def save_beerxml(filename, content):
    path = os.path.join(RECIPES_DIR, filename)
    with open(path, 'w') as f:
        f.write(content)


def remove_recipe_file(filename):
    path = os.path.join(RECIPES_DIR, filename)
    os.remove(path)

