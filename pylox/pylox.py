import os

from parser import Parser
from interpreter import Interpreter
from resolver import Resolver
from runtime_exception import RuntimeException
from scanner import Scanner


class Pylox:
    had_error: bool = False
    had_runtime_error: bool = False

    def __init__(self):
        self.interpreter = Interpreter(self)

    def run_command(self, args_list: [str]):
        if len(args_list) > 2:
            print("Usage : fla [script]")
            # ToDo: replace print for a nicer error
        elif len(args_list) == 1:
            self.run_prompt()
        else:
            self.run_file(os.path.join(os.getcwd(), "pylox", args_list[1]))

    def run_prompt(self):
        while True:
            line = input("> ")
            if line == "":
                break
            self.run(line)
            self.had_error = False

    def run_file(self, file_path: str):
        with open(file_path, "r") as f:
            lines = f.readlines()
        self.run("".join(lines))

        if self.had_error:
            exit(65)
        if self.had_runtime_error:
            exit(70)

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens, self)
        statements = parser.parse()

        if self.had_error:
            return None

        resolver = Resolver(self.interpreter, self)
        resolver.resolve(statements)

        if self.had_error:
            return None

        self.interpreter.interprete(statements)

    def show_error(self, line_number: int, message: str):
        self.report(line_number, "", message)

    def report(self, line_number: int, where: str, message: str):
        print(f"Line {line_number} Error {where} : {message}")
        self.had_error = True

    def call_runtime_error(self, error: RuntimeException):
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True
