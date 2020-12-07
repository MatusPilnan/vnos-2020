from pybeerxml import recipe


class Ingredient:
    def __init__(self, name: str, amount: float, unit: str) -> None:
        self.name = name
        self.amount = amount
        self.unit = unit

    def to_dict(self):
        return {"name": self.name, "amount": self.amount, "unit": self.unit}


class Fermentable(Ingredient):
    def __init__(self, fermentable: recipe.Fermentable) -> None:
        super().__init__(name=fermentable.name, amount=fermentable.amount, unit='kg')


class Hop(Ingredient):
    def __init__(self, hop: recipe.Hop) -> None:
        super().__init__(name=hop.name, amount=hop.amount * 1000, unit='g')


class Misc(Ingredient):
    def __init__(self, misc: recipe.Misc) -> None:
        super().__init__(name=misc.name, amount=misc.amount, unit='units')
