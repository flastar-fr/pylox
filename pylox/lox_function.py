from typing import Any, TYPE_CHECKING

from environment import Environment
from return_exception import Return
from stmt import Function
from lox_callable import LoxCallable


if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', arguments: list[Any]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as e:
            return e.value

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
