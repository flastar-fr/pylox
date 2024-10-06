from typing import Any

import expr as expre
import stmt

from environment import Environment
from lox_callable import LoxCallable
from clock_function import ClockFunction
from lox_function import LoxFunction
from lox_class import LoxClass
from lox_instance import LoxInstance
from int_function import IntFunction
from randint_function import RandintFunction
from str_function import StrFunction
from runtime_exception import RuntimeException
from return_exception import Return
from token_class import Token
from token_type import TokenType


class Interpreter(expre.Visitor, stmt.Visitor):
    def __init__(self, program):
        self.program = program
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

        self.globals.define("clock", ClockFunction())
        self.globals.define("str", StrFunction())
        self.globals.define("float", IntFunction())
        self.globals.define("randint", RandintFunction())

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

    def visit_return_stmt(self, statement: stmt.Return):
        value = None
        if statement.value is not None:
            value = self.evaluate(statement.value)

        raise Return(value)

    def visit_expression_stmt(self, statement):
        self.evaluate(statement.expression)

    def visit_function_stmt(self, statement: stmt.Function):
        function_var = LoxFunction(statement, self.environment, False)
        self.environment.define(statement.name.lexeme, function_var)

    def visit_var_stmt(self, statement: stmt.Var):
        value = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        self.environment.define(statement.name.lexeme, value)

    def visit_while_stmt(self, statement: stmt.While):
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)

    def visit_block_stmt(self, statement: stmt.Block):
        self.execute_block(statement.statements, Environment(self.environment))

    def visit_class_stmt(self, statement: stmt.Class):
        superclass = None
        if statement.superclass is not None:
            superclass = self.evaluate(statement.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeException(statement.superclass.name, "Superclass must be a class.")

        self.environment.define(statement.name.lexeme, None)

        if statement.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in statement.methods:
            function = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = LoxClass(statement.name.lexeme, superclass, methods)

        if statement.superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(statement.name, klass)

    def visit_if_stmt(self, statement: stmt.If):
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    def visit_assign_expr(self, expr: expre.Assign):
        value = self.evaluate(expr.value)

        distance = self.locals[expr]
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

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

    def visit_call_expr(self, expr: expre.Call):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(expr.paren, "Can only call functions and classes.")

        function_call = callee

        if len(arguments) != function_call.arity():
            raise RuntimeException(expr.paren, f"Expected {function_call.arity()} arguments but got {len(arguments)}.")
        return function_call.call(self, arguments)

    def visit_get_expr(self, expr: expre.Get):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise RuntimeException(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: expre.Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: expre.Literal):
        return expr.value

    def visit_logical_expr(self, expr: expre.Logical):
        left = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: expre.Set):
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise RuntimeException(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: expre.Super):
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(distance, "super")

        obj = self.environment.get_at(distance - 1, "this")

        method = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise RuntimeException(expr.method, f"Undefined property '{expr.method.lexeme}'.")

        return method.bind(obj)

    def visit_this_expr(self, expr: expre.This):
        return self.look_up_variable(expr.keyword, expr)

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
        return self.look_up_variable(expr.name, expr)

    def look_up_variable(self, name: Token, expr: expre.Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def evaluate(self, expr: expre.Expr) -> Any:
        return expr.accept(self)

    def execute(self, statement: stmt.Stmt):
        statement.accept(self)

    def resolve(self, expr: expre.Expr, depth: int):
        self.locals[expr] = depth

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

        raise RuntimeException(operator, "Operands must be numbers.")
