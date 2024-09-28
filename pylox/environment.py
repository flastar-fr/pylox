from typing import Any

from runtime_error import RuntimeException
from token_class import Token


class Environment:
    def __init__(self, enclosing: 'Environment' = None):
        self.enclosing = enclosing
        self.values = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable {name.lexeme}.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return None

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return None

        raise RuntimeException(name, f"Undefined variable {name.lexeme}.")
