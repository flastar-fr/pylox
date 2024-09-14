import expr


class AstPrinter(expr.Visitor):
    def print(self, expre: expr.Expr):
        return expre.accept(self)

    def visit_assign_expr(self, expre):
        pass

    def visit_binary_expr(self, expre: expr.Binary):
        return self.add_parenthesize(expre.operator.lexeme, expre.left, expre.right)

    def visit_call_expr(self, expre):
        pass

    def visit_get_expr(self, expre):
        pass

    def visit_grouping_expr(self, expre: expr.Grouping):
        return self.add_parenthesize("group", expre.expression)

    def visit_literal_expr(self, expre: expr.Literal):
        if expre.value is None:
            return "nil"
        return str(expre.value)

    def visit_logical_expr(self, expre):
        pass

    def visit_set_expr(self, expre):
        pass

    def visit_super_expr(self, expre):
        pass

    def visit_this_expr(self, expre):
        pass

    def visit_unary_expr(self, expre: expr.Unary):
        return self.add_parenthesize(expre.operator.lexeme, expre.right)

    def visit_variable_expr(self, expre):
        pass

    def add_parenthesize(self, name: str, *args: expr.Expr) -> str:
        to_return = f"({name}"

        for expression in args:
            to_return += f" {expression.accept(self)}"

        to_return += ")"

        return to_return
