from abc import ABC, abstractmethod

from expr import Expr
from token_class import Token


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class Visitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, statement):
        pass

    @abstractmethod
    def visit_print_stmt(self, statement):
        pass

    @abstractmethod
    def visit_var_stmt(self, statement):
        pass

    @abstractmethod
    def visit_block_stmt(self, statement):
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor):
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor: Visitor):
        return visitor.visit_block_stmt(self)