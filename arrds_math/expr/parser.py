"""Tokenizador y parser descendente recursivo de expresiones.

Gramática (de menor a mayor precedencia)::

    expr     := additive
    additive := term (("+" | "-") term)*
    term     := unary (("*" | "/" | <implícita>) unary)*
    unary    := ("+" | "-") unary | power
    power    := postfix ("^" unary)?          # asociativa por la derecha
    postfix  := primary "!"*
    primary  := NUMBER | IDENT | IDENT "(" args ")" | "(" expr ")"

Notas de diseño:

* ``**`` es sinónimo de ``^``.
* ``-2^2`` = -4 (la potencia liga más fuerte que el signo), como en la
  notación matemática habitual.
* Multiplicación implícita: ``2x``, ``2(x+1)``, ``(a)(b)``, ``3 sin(x)``,
  ``x(x+1)``. Solo se inserta cuando el siguiente token es un identificador
  o ``(``. ``nombre(...)`` es una llamada solo si ``nombre`` es una función
  del catálogo (``FUNCTIONS``); si no, se lee como producto.
* Nunca se usa ``eval`` de Python: el parser es la única puerta de entrada.
"""

import re

from ..errors import ParseError
from .nodes import Binary, Call, Num, Unary, Var

MAX_EXPRESSION_LENGTH = 10_000
# Cada nivel de paréntesis consume ~7 marcos de pila de Python (límite 1000).
MAX_DEPTH = 100

_TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
  | (?P<number>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)
  | (?P<ident>[A-Za-z_][A-Za-z_0-9]*)
  | (?P<op>\*\*|[-+*/^!(),])
    """,
    re.VERBOSE,
)


class Token:
    __slots__ = ("kind", "text", "pos")

    def __init__(self, kind, text, pos):
        self.kind = kind
        self.text = text
        self.pos = pos

    def __repr__(self):
        return f"Token({self.kind}, {self.text!r}, {self.pos})"


def tokenize(source):
    if not isinstance(source, str):
        raise ParseError("La expresión debe ser texto")
    if len(source) > MAX_EXPRESSION_LENGTH:
        raise ParseError(f"Expresión demasiado larga (máx. {MAX_EXPRESSION_LENGTH} caracteres)")
    tokens = []
    pos = 0
    while pos < len(source):
        match = _TOKEN_RE.match(source, pos)
        if not match:
            raise ParseError(f"Carácter inesperado {source[pos]!r}", pos)
        kind = match.lastgroup
        text = match.group()
        if kind != "ws":
            if text == "**":
                text = "^"
            tokens.append(Token(kind, text, pos))
        pos = match.end()
    tokens.append(Token("eof", "", len(source)))
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.depth = 0

    @property
    def tok(self):
        return self.tokens[self.i]

    def advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def accept(self, text):
        if self.tok.kind == "op" and self.tok.text == text:
            return self.advance()
        return None

    def expect(self, text):
        tok = self.accept(text)
        if tok is None:
            found = self.tok.text or "fin de la expresión"
            raise ParseError(f"Se esperaba {text!r} y se encontró {found!r}", self.tok.pos)
        return tok

    def enter(self):
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise ParseError("Expresión demasiado anidada", self.tok.pos)

    def leave(self):
        self.depth -= 1

    # --- reglas -------------------------------------------------------
    def parse(self):
        if self.tok.kind == "eof":
            raise ParseError("Expresión vacía", 0)
        node = self.additive()
        if self.tok.kind != "eof":
            raise ParseError(f"Token inesperado {self.tok.text!r}", self.tok.pos)
        return node

    def additive(self):
        node = self.term()
        while self.tok.kind == "op" and self.tok.text in ("+", "-"):
            op = self.advance().text
            node = Binary(op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while True:
            if self.tok.kind == "op" and self.tok.text in ("*", "/"):
                op = self.advance().text
                node = Binary(op, node, self.unary())
            elif self.tok.kind == "ident" or (self.tok.kind == "op" and self.tok.text == "("):
                node = Binary("*", node, self.unary())
            else:
                return node

    def unary(self):
        if self.tok.kind == "op" and self.tok.text in ("+", "-"):
            op = self.advance().text
            self.enter()
            operand = self.unary()
            self.leave()
            if op == "+":
                return operand
            return Unary("-", operand)
        return self.power()

    def power(self):
        base = self.postfix()
        if self.accept("^"):
            self.enter()
            exponent = self.unary()
            self.leave()
            return Binary("^", base, exponent)
        return base

    def postfix(self):
        node = self.primary()
        while self.accept("!"):
            node = Unary("!", node)
        return node

    def primary(self):
        tok = self.tok
        if tok.kind == "number":
            self.advance()
            return Num(float(tok.text))
        if tok.kind == "ident":
            self.advance()
            # ``nombre(`` es llamada solo si ``nombre`` es una función conocida;
            # si no, es multiplicación implícita: 2x(x+1) = 2·x·(x+1).
            if tok.text in _function_names() and self.accept("("):
                args = []
                self.enter()
                if not self.accept(")"):
                    args.append(self.additive())
                    while self.accept(","):
                        args.append(self.additive())
                    self.expect(")")
                self.leave()
                return Call(tok.text, tuple(args))
            return Var(tok.text)
        if self.accept("("):
            self.enter()
            node = self.additive()
            self.leave()
            self.expect(")")
            return node
        found = tok.text or "fin de la expresión"
        raise ParseError(f"Se esperaba un número, variable o '(' y se encontró {found!r}", tok.pos)


def _function_names():
    # Import diferido: el evaluador importa este módulo.
    from .evaluator import FUNCTIONS

    return FUNCTIONS


def parse(source):
    """Convierte texto en un AST. Lanza ``ParseError`` si no es válido."""
    return _Parser(tokenize(source)).parse()
