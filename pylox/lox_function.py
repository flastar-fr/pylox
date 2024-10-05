from typing import Any, TYPE_CHECKING

from environment import Environment
from return_exception import Return
from stmt import Function
from lox_callable import LoxCallable


if TYPE_CHECKING:
    from interpreter import Interpreter
    from lox_instance import LoxInstance


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance: 'LoxInstance') -> 'LoxFunction':
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', arguments: list[Any]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as e:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
