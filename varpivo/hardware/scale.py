from random import random


class Scale:
    __instance = None

    @staticmethod
    def get_instance():
        if Scale.__instance is None:
            Scale()

        return Scale.__instance

    def __init__(self) -> None:
        super().__init__()
        if Scale.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Scale.__instance = self

    @property
    def weight(self):
        return random() * 100
