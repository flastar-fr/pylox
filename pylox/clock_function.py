from time import time

from typing import Any

from lox_callable import LoxCallable


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter


class ClockFunction(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        return time() / 1000

    def __str__(self):
        return "<native fn>"
