from typing import Any, TYPE_CHECKING

from runtime_exception import RuntimeException
from token_class import Token

if TYPE_CHECKING:
    from lox_class import LoxClass


class LoxInstance:
    def __init__(self, klass: 'LoxClass'):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeException(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance"
