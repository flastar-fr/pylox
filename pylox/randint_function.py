from random import randint
from typing import Any

from lox_callable import LoxCallable


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter


class RandintFunction(LoxCallable):
    def arity(self):
        return 2

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        return float(randint(int(arguments[0]), int(arguments[1])))

    def __str__(self):
        return "<native fn>"
