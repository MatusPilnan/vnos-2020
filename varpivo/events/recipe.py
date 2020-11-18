import datetime
from typing import Union

from actorio import DataMessage
from actorio._abc import ReferenceABC, ActorABC

from varpivo.recipe import Recipe


class RecipeSelected(DataMessage):

    data: Recipe

    def __init__(self, *args, data: Recipe, creation_date: datetime.datetime = None,
                 sender: Union[ReferenceABC, ActorABC] = None, **kwargs) -> None:
        super().__init__(*args, data=data, creation_date=creation_date, sender=sender, **kwargs)
        self.data = data


    @property
    def data(self)-> Recipe:
        return self.data
