from .brew_session import app as bs
from .hardware import app as hw
from .info import app as info
from .recipes import app as recipes

blueprints = [recipes, bs, hw, info]
