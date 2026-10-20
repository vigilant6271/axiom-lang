"""Small lexer, Pratt parser, and evaluator for the Axiom 0.1 subset."""
from __future__ import annotations
from dataclasses import dataclass
import ast
import re
from typing import Any


class AxiomError(Exception):
    """Base class for source-facing Axiom errors."""


class LexError(AxiomError):
    pass


class ParseError(AxiomError):
    pass


class RuntimeAxiomError(AxiomError):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int


TOKEN_RE = re.compile(
    r"(?P<SPACE>[ \t\r]+)|(?P<COMMENT>\#[^\n]*)|(?P<NEWLINE>\n)|"
    r"(?P<NUMBER>(?:\d+\.\d+|\d+))|"
    r"(?P<STRING>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')|"
    r"(?P<IDENT>[A-Za-z_][A-Za-z0-9_]*)|"
    r"(?P<OP>==|!=|<=|>=|[+*/()=<>;,\-])"
)


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    pos, line, col = 0, 1, 1
    while pos < len(source):
        match = TOKEN_RE.match(source, pos)
        if not match:
            raise LexError(f"line {line}, column {col}: unexpected character {source[pos]!r}")
        kind, value = match.lastgroup, match.group()
        if kind not in ("SPACE", "COMMENT"):
            tokens.append(Token(kind or "", value, line, col))
        lines = value.split("\n")
        if len(lines) > 1:
            line += len(lines) - 1
            col = len(lines[-1]) + 1
        else:
            col += len(value)
        pos = match.end()
    tokens.append(Token("EOF", "", line, col))
    return tokens


@dataclass
class Node:
    kind: str
    value: Any = None
    children: tuple["Node", ...] = ()
    token: Token | None = None


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens, self.i = tokens, 0

    @property
    def current(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        tok = self.current
        if tok.kind != "EOF":
            self.i += 1
        return tok

    def fail(self, message: str) -> None:
        t = self.current
        raise ParseError(f"line {t.line}, column {t.column}: {message}; got {t.value!r}")

    def accept(self, value: str) -> bool:
        if self.current.value == value:
            self.advance()
            return True
        return False

    def require(self, value: str) -> Token:
        if self.current.value != value:
            self.fail(f"expected {value!r}")
        return self.advance()

    def parse(self) -> list[Node]:
        statements: list[Node] = []
        while self.current.kind != "EOF":
            if self.current.kind == "NEWLINE":
                self.advance()
                continue
            if self.accept(";"):
                continue
            statements.append(self.statement())
            if self.current.kind == "NEWLINE" or self.current.value == ";":
                self.advance()
            elif self.current.kind != "EOF":
                self.fail("expected end of statement")
        return statements

    def statement(self) -> Node:
        if self.current.value in ("let", "var"):
            tok = self.advance()
            if self.current.kind != "IDENT":
                self.fail("expected binding name")
            name = self.advance()
            self.require("=")
            return Node("bind", (tok.value, name.value), (self.expression(),), tok)
        if self.current.value == "print":
            tok = self.advance()
            self.require("(")
            expr = self.expression()
            self.require(")")
            return Node("print", None, (expr,), tok)
        if self.current.kind == "IDENT" and self.tokens[self.i + 1].value == "=":
            name = self.advance()
            self.advance()
            return Node("assign", name.value, (self.expression(),), name)
        return Node("expr", None, (self.expression(),), self.current)

    def expression(self, min_bp: int = 0) -> Node:
        tok = self.advance()
        if tok.kind == "NUMBER":
            left = Node("literal", float(tok.value) if "." in tok.value else int(tok.value), token=tok)
        elif tok.kind == "STRING":
            try:
                value = ast.literal_eval(tok.value)
            except (ValueError, SyntaxError) as exc:
                raise ParseError(f"line {tok.line}, column {tok.column}: invalid string literal") from exc
            left = Node("literal", value, token=tok)
        elif tok.value in ("true", "false"):
            left = Node("literal", tok.value == "true", token=tok)
        elif tok.kind == "IDENT":
            left = Node("name", tok.value, token=tok)
        elif tok.value == "-":
            left = Node("neg", None, (self.expression(30),), tok)
        elif tok.value == "(":
            left = self.expression()
            self.require(")")
        else:
            raise ParseError(f"line {tok.line}, column {tok.column}: expected expression, got {tok.value!r}")

        binding = {
            "==": (5, 6), "!=": (5, 6), "<": (5, 6), "<=": (5, 6), ">": (5, 6), ">=": (5, 6),
            "+": (10, 11), "-": (10, 11), "*": (20, 21), "/": (20, 21),
        }
        while self.current.value in binding:
            op = self.current.value
            lbp, rbp = binding[op]
            if lbp < min_bp:
                break
            op_tok = self.advance()
            right = self.expression(rbp)
            left = Node("binary", op, (left, right), op_tok)
        return left


@dataclass
class Binding:
    value: Any
    mutable: bool


class Interpreter:
    def __init__(self, output=print):
        self.env: dict[str, Binding] = {}
        self.output = output

    def evaluate(self, node: Node) -> Any:
        if node.kind == "literal":
            return node.value
        if node.kind == "name":
            if node.value not in self.env:
                raise RuntimeAxiomError(f"undefined name {node.value!r}")
            return self.env[node.value].value
        if node.kind == "neg":
            return -self.evaluate(node.children[0])
        if node.kind == "binary":
            a, b = (self.evaluate(n) for n in node.children)
            try:
                operations = {
                    "+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b,
                    "/": lambda: a / b, "==": lambda: a == b, "!=": lambda: a != b,
                    "<": lambda: a < b, "<=": lambda: a <= b, ">": lambda: a > b, ">=": lambda: a >= b,
                }
                return operations[node.value]()
            except ZeroDivisionError as exc:
                raise RuntimeAxiomError("division by zero") from exc
            except (TypeError, KeyError) as exc:
                raise RuntimeAxiomError(f"invalid operands for {node.value!r}: {exc}") from exc
        raise RuntimeAxiomError(f"unsupported expression node: {node.kind}")

    def run(self, source: str) -> list[Any]:
        results: list[Any] = []
        for stmt in Parser(lex(source)).parse():
            if stmt.kind == "bind":
                mode, name = stmt.value
                if name in self.env:
                    raise RuntimeAxiomError(f"binding {name!r} already exists")
                self.env[name] = Binding(self.evaluate(stmt.children[0]), mode == "var")
                results.append(self.env[name].value)
            elif stmt.kind == "assign":
                if stmt.value not in self.env:
                    raise RuntimeAxiomError(f"undefined name {stmt.value!r}")
                binding = self.env[stmt.value]
                if not binding.mutable:
                    raise RuntimeAxiomError(f"cannot assign to immutable binding {stmt.value!r}; declare it with 'var'")
                binding.value = self.evaluate(stmt.children[0])
                results.append(binding.value)
            elif stmt.kind == "print":
                value = self.evaluate(stmt.children[0])
                self.output(value)
                results.append(value)
            else:
                results.append(self.evaluate(stmt.children[0]))
        return results


def run(source: str, output=print) -> list[Any]:
    return Interpreter(output=output).run(source)
