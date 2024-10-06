from lox_callable import LoxCallable
from lox_instance import LoxInstance
from lox_function import LoxFunction


class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: 'LoxClass', methods: dict[str: LoxFunction]):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def __str__(self):
        return self.name
