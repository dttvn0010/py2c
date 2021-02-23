from type_ import Type

class Variable:
    def __init__(self, name: str, type_:Type):
        self.name = name
        self.type_ = type_

    def __repr__(self):
        return self.name