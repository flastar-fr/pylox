import os.path

from ast_printer import AstPrinter
from parser import Parser
from scanner import Scanner


class Pylox:
    had_error: bool = False

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
        self.run("\n".join(lines))

        if self.had_error:
            exit(65)

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens, self)
        expression = parser.parse()

        if self.had_error:
            return

        print(AstPrinter().print(expression))

    def show_error(self, line_number: int, message: str):
        self.report(line_number, "", message)

    def report(self, line_number: int, where: str, message: str):
        print(f"Line {line_number} Error {where} : {message}")
        self.had_error = True
