from typing import Any

from lox_callable import LoxCallable


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from interpreter import Interpreter


class IntFunction(LoxCallable):
    def arity(self):
        return 1

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        try:
            return float(arguments[0])
        except ValueError:
            raise RuntimeError("Cannot be casted to an integer.")

    def __str__(self):
        return "<native fn>"
