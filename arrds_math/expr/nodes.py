"""Nodos del árbol sintáctico (AST) de expresiones.

Los nodos son inmutables y comparables por valor, lo que permite que la
simplificación simbólica compare subárboles con ``==``.
"""

from dataclasses import dataclass
from typing import Tuple


class Node:
    """Clase base de todos los nodos."""

    __slots__ = ()


@dataclass(frozen=True)
class Num(Node):
    value: float


@dataclass(frozen=True)
class Var(Node):
    name: str


@dataclass(frozen=True)
class Unary(Node):
    op: str  # "-" | "+" | "!"
    operand: Node


@dataclass(frozen=True)
class Binary(Node):
    op: str  # "+" | "-" | "*" | "/" | "^"
    left: Node
    right: Node


@dataclass(frozen=True)
class Call(Node):
    name: str
    args: Tuple[Node, ...]


def free_variables(node):
    """Devuelve el conjunto de nombres de variable usados en ``node``."""
    if isinstance(node, Var):
        return {node.name}
    if isinstance(node, Num):
        return set()
    if isinstance(node, Unary):
        return free_variables(node.operand)
    if isinstance(node, Binary):
        return free_variables(node.left) | free_variables(node.right)
    if isinstance(node, Call):
        out = set()
        for arg in node.args:
            out |= free_variables(arg)
        return out
    raise TypeError(f"Nodo desconocido: {node!r}")


_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "neg": 3, "^": 4, "!": 5}


def _fmt_num(value):
    if isinstance(value, complex):
        return f"({value.real:g}{value.imag:+g}j)"
    if float(value).is_integer() and abs(value) < 1e16:
        return str(int(value))
    return repr(float(value))


def to_string(node):
    """Convierte un AST en texto con el mínimo de paréntesis necesario."""
    text, _ = _to_str(node)
    return text


def _to_str(node):
    # Devuelve (texto, precedencia del operador raíz).
    if isinstance(node, Num):
        text = _fmt_num(node.value)
        prec = 3 if text.startswith("-") else 10
        return text, prec
    if isinstance(node, Var):
        return node.name, 10
    if isinstance(node, Call):
        return f"{node.name}({', '.join(to_string(a) for a in node.args)})", 10
    if isinstance(node, Unary):
        inner, p = _to_str(node.operand)
        if node.op == "!":
            return (f"{inner}!" if p >= 10 else f"({inner})!"), _PRECEDENCE["!"]
        if node.op == "+":
            return inner, p
        return (f"-{inner}" if p > _PRECEDENCE["neg"] else f"-({inner})"), _PRECEDENCE["neg"]
    if isinstance(node, Binary):
        prec = _PRECEDENCE[node.op]
        left, lp = _to_str(node.left)
        right, rp = _to_str(node.right)
        if node.op == "^":
            # Asociativa por la derecha; la base negativa siempre se agrupa.
            if lp <= prec:
                left = f"({left})"
            if rp < prec:
                right = f"({right})"
            return f"{left}^{right}", prec
        if lp < prec:
            left = f"({left})"
        # Operadores no conmutativos: a-(b+c), a/(b*c).
        if rp < prec or (rp == prec and node.op in "-/"):
            right = f"({right})"
        return f"{left} {node.op} {right}", prec
    raise TypeError(f"Nodo desconocido: {node!r}")
