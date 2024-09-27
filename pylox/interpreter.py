from typing import Any, final

import expr as expre
import stmt

from environment import Environment
from runtime_error import RuntimeException
from token_class import Token
from token_type import TokenType


class Interpreter(expre.Visitor, stmt.Visitor):
    def __init__(self, program):
        self.program = program
        self.environment = Environment()

    def interprete(self, statements: list[stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeException as e:
            self.program.call_runtime_error(e)

    @staticmethod
    def stringify(to_string: Any) -> str:
        if to_string is None:
            return "nil"

        if isinstance(to_string, float):
            text = str(to_string)
            if text.endswith(".0"):
                text = text[0:-2]
            return text

        if isinstance(to_string, bool):
            if to_string:
                return "true"
            return "false"

        return str(to_string)

    def visit_print_stmt(self, statement):
        value = self.evaluate(statement.expression)
        print(self.stringify(value))

    def visit_expression_stmt(self, statement):
        self.evaluate(statement.expression)

    def visit_var_stmt(self, statement: stmt.Var):
        value = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)

        self.environment.define(statement.name.lexeme, value)

    def visit_block_stmt(self, statement: stmt.Block):
        self.execute_block(statement.statements, Environment(self.environment))

    def visit_assign_expr(self, expr: expre.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: expre.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)

                raise RuntimeException(expr.operator, "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)

        return None

    def visit_call_expr(self, expr):
        pass

    def visit_get_expr(self, expr):
        pass

    def visit_grouping_expr(self, expr: expre.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: expre.Literal):
        return expr.value

    def visit_logical_expr(self, expr):
        pass

    def visit_set_expr(self, expr):
        pass

    def visit_super_expr(self, expr):
        pass

    def visit_this_expr(self, expr):
        pass

    def visit_unary_expr(self, expr: expre.Unary):
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return float(-right)

        return None

    def visit_variable_expr(self, expr: expre.Variable):
        return self.environment.get(expr.name)

    def evaluate(self, expr: expre.Expr) -> Any:
        return expr.accept(self)

    def execute(self, statement: stmt.Stmt):
        statement.accept(self)

    def execute_block(self, statements: list[stmt.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    @staticmethod
    def is_truthy(object_to_verify: expre.Expr) -> bool:
        if object_to_verify is None:
            return False
        if isinstance(object_to_verify, bool):
            return bool(object_to_verify)
        return True

    @staticmethod
    def is_equal(left: Any, right: Any) -> bool:
        if left is None and right is None:
            return True

        return left == right

    @staticmethod
    def check_number_operand(operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return None
        raise RuntimeException(operator, "Operand must be a number.")

    @staticmethod
    def check_number_operands(operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return None
        print(left, right)
        raise RuntimeException(operator, "Operands must be numbers.")
