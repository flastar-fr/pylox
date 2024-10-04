from interpreter import Interpreter
from expr import Visitor as eVisitor, Expr, Variable, Assign, Binary, Call, Grouping, Literal, Logical, Unary
from function_type import FunctionType
from stmt import Visitor as sVisitor, Block, Stmt, Var, Function, Expression, If, Print, Return, While, Token


class Resolver(eVisitor, sVisitor):
    def __init__(self, interpreter: Interpreter, program):
        self.interpreter = interpreter
        self.program = program
        self.scopes = []
        self.current_function = FunctionType.NONE

    def visit_block_stmt(self, statement: Block):
        self.begin_scope()
        self.resolve(statement.statements)
        self.end_scope()

    def visit_expression_stmt(self, statement: Expression):
        self.resolve(statement.expression)

    def visit_function_stmt(self, statement: Function):
        self.declare(statement.name)
        self.define(statement.name)

        self.resolve_function(statement, FunctionType.FUNCTION)

    def visit_if_stmt(self, statement: If):
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)
        if statement.else_branch is not None:
            self.resolve(statement.else_branch)

    def visit_print_stmt(self, statement: Print):
        self.resolve(statement.expression)

    def visit_return_stmt(self, statement: Return):
        if self.current_function == FunctionType.NONE:
            self.program.show_error(statement.keyword, "Can't return from top-level code.")

        if statement.value is not None:
            self.resolve(statement.value)

    def visit_var_stmt(self, statement: Var):
        self.declare(statement.name)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name)

    def visit_while_stmt(self, statement: While):
        self.resolve(statement.condition)
        self.resolve(statement.body)

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return None

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)

    def visit_variable_expr(self, expr: Variable):
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) is False:
            self.program.show_error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)

    def resolve(self, statements: list[Stmt] | Stmt | Expr):
        if isinstance(statements, list):
            for statement in statements:
                self.resolve(statement)
        elif isinstance(statements, Stmt) or isinstance(statements, Expr):
            statements.accept(self)

    def resolve_function(self, function: Function, function_type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return None

        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            self.program.show_error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return None
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
