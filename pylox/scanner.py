from typing import Any

from token_class import Token
from token_type import TokenType

keywords = {"and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE}


class Scanner:
    def __init__(self, source: str, program):
        self.source = source
        self.program = program
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 0

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.advance()

        match c:
            case "(": self.add_token(TokenType.LEFT_PAREN)
            case ")": self.add_token(TokenType.RIGHT_PAREN)
            case "{": self.add_token(TokenType.LEFT_BRACE)
            case "}": self.add_token(TokenType.RIGHT_BRACE)
            case ",": self.add_token(TokenType.COMMA)
            case ".": self.add_token(TokenType.DOT)
            case "-": self.add_token(TokenType.MINUS)
            case "+": self.add_token(TokenType.PLUS)
            case ";": self.add_token(TokenType.SEMICOLON)
            case "*": self.add_token(TokenType.STAR)
            case "!": self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
            case "=": self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
            case "<": self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
            case ">": self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t": return
            case "\n":
                self.line += 1
            case '"':
                self.process_string()
            case _:
                if c.isdigit():
                    self.process_number()
                    return
                if self.is_alpha(c):
                    self.process_identifier()
                    return
                self.program.show_error(self.line, "Unexptected character.")

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, token_type):
        self.add_token_literal(token_type, None)

    def add_token_literal(self, token_type: TokenType, literal: Any):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def process_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.program.show_error(self.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        # Trim de surrounding quotes.
        value = self.source[self.start + 1:self.current - 1]
        self.add_token_literal(TokenType.STRING, value)

    def process_number(self):
        while self.peek().isdigit():
            self.advance()

        # Look for a fractional part.
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

        while self.peek().isdigit():
            self.advance()

        self.add_token_literal(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def process_identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        token_type = keywords.get(text, None)
        if token_type is None:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)

    @staticmethod
    def is_alpha(c: str) -> bool:
        return c.isalnum() or c == "_"

    def is_alpha_numeric(self, c: str):
        return self.is_alpha(c) or c.isdigit()
