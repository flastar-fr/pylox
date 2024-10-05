from typing import Any

from lox_callable import LoxCallable


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter


class StrFunction(LoxCallable):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        return str(arguments[0])

    def __str__(self):
        return "<native fn>"
