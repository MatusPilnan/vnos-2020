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
