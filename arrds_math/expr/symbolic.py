"""Capa 1 — Abstracción simbólica.

Derivación simbólica exacta sobre el AST, simplificación algebraica
conservadora y exportación a LaTeX.

La simplificación es deliberadamente *conservadora*: solo aplica reglas
que son identidades válidas en todo el dominio (x*1 = x, x+0 = x,
plegado de constantes...). No cancela x/x ni simplifica sqrt(x^2), porque
esas "simplificaciones" cambian el dominio de definición y en ingeniería
eso oculta singularidades reales.
"""

import math

from ..errors import EvaluationError
from .nodes import Binary, Call, Num, Unary, Var, to_string
from .parser import parse

ZERO = Num(0.0)
ONE = Num(1.0)
TWO = Num(2.0)


# --- constructores con simplificación local ---------------------------

def _is_num(node, value=None):
    return isinstance(node, Num) and (value is None or node.value == value)


def add(a, b):
    if _is_num(a, 0):
        return b
    if _is_num(b, 0):
        return a
    if _is_num(a) and _is_num(b):
        return Num(a.value + b.value)
    if isinstance(b, Unary) and b.op == "-":
        return sub(a, b.operand)
    if a == b:
        return mul(TWO, a)
    return Binary("+", a, b)


def sub(a, b):
    if _is_num(b, 0):
        return a
    if _is_num(a, 0):
        return neg(b)
    if _is_num(a) and _is_num(b):
        return Num(a.value - b.value)
    if a == b:
        return ZERO
    if isinstance(b, Unary) and b.op == "-":
        return add(a, b.operand)
    return Binary("-", a, b)


def neg(a):
    if _is_num(a):
        return Num(-a.value)
    if isinstance(a, Unary) and a.op == "-":
        return a.operand
    return Unary("-", a)


def mul(a, b):
    if _is_num(a, 0) or _is_num(b, 0):
        return ZERO
    if _is_num(a, 1):
        return b
    if _is_num(b, 1):
        return a
    if _is_num(a, -1):
        return neg(b)
    if _is_num(b, -1):
        return neg(a)
    if _is_num(a) and _is_num(b):
        return Num(a.value * b.value)
    if _is_num(b) and not _is_num(a):
        a, b = b, a  # constante a la izquierda: 2*x en vez de x*2
    if isinstance(a, Unary) and a.op == "-":
        return neg(mul(a.operand, b))
    if isinstance(b, Unary) and b.op == "-":
        return neg(mul(a, b.operand))
    # c1 * (c2 * x) -> (c1*c2) * x
    if _is_num(a) and isinstance(b, Binary) and b.op == "*" and _is_num(b.left):
        return mul(Num(a.value * b.left.value), b.right)
    if a == b:
        return power(a, TWO)
    return Binary("*", a, b)


def div(a, b):
    if _is_num(b, 1):
        return a
    if _is_num(a, 0) and not _is_num(b, 0):
        return ZERO
    if _is_num(a) and _is_num(b) and b.value != 0:
        q = a.value / b.value
        if q.is_integer():
            return Num(q)
    if isinstance(a, Unary) and a.op == "-":
        return neg(div(a.operand, b))
    return Binary("/", a, b)


def power(a, b):
    if _is_num(b, 0):
        return ONE
    if _is_num(b, 1):
        return a
    if _is_num(a, 1):
        return ONE
    if _is_num(a) and _is_num(b):
        try:
            value = a.value ** b.value
            if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
                return Num(value)
        except (OverflowError, ZeroDivisionError):
            pass
    # (x^m)^n -> x^(m*n) solo para exponentes enteros (identidad segura)
    if (isinstance(a, Binary) and a.op == "^" and _is_num(a.right) and _is_num(b)
            and float(a.right.value).is_integer() and float(b.value).is_integer()):
        return power(a.left, Num(a.right.value * b.value))
    return Binary("^", a, b)


def call(name, *args):
    return Call(name, tuple(args))


def simplify(node):
    """Reconstruye el árbol de abajo arriba aplicando las reglas locales."""
    if isinstance(node, (Num, Var)):
        return node
    if isinstance(node, Unary):
        inner = simplify(node.operand)
        if node.op == "-":
            return neg(inner)
        if node.op == "!" and _is_num(inner) and float(inner.value).is_integer() and 0 <= inner.value <= 20:
            return Num(float(math.factorial(int(inner.value))))
        return Unary(node.op, inner)
    if isinstance(node, Binary):
        a, b = simplify(node.left), simplify(node.right)
        return {"+": add, "-": sub, "*": mul, "/": div, "^": power}[node.op](a, b)
    if isinstance(node, Call):
        return Call(node.name, tuple(simplify(arg) for arg in node.args))
    raise TypeError(f"Nodo desconocido: {node!r}")


# --- derivación -------------------------------------------------------

def _d_call(node, var):
    """Regla de la cadena para funciones de una variable: f(u)' = f'(u)·u'."""
    name = node.name
    if name == "log" and len(node.args) == 2:
        # log_b(u) = ln(u)/ln(b)
        u, b = node.args
        return diff(div(call("ln", u), call("ln", b)), var)
    if name in ("min", "max", "hypot", "atan2", "round", "floor", "ceil") and len(node.args) != 1 or name in (
        "atan2", "min", "max", "hypot", "round"
    ):
        if name == "atan2":
            y, x = node.args
            dy, dx = diff(y, var), diff(x, var)
            return simplify(div(sub(mul(x, dy), mul(y, dx)), add(power(x, TWO), power(y, TWO))))
        if name == "hypot":
            num = None
            for u in node.args:
                term = mul(u, diff(u, var))
                num = term if num is None else add(num, term)
            return simplify(div(num, node))
        raise EvaluationError(f"La derivada simbólica de {name}() no está definida")
    if len(node.args) != 1:
        raise EvaluationError(f"{name}() con {len(node.args)} argumentos no es derivable simbólicamente")
    u = node.args[0]
    du = diff(u, var)
    if _is_num(du, 0):
        return ZERO
    outer = {
        "sin": lambda: call("cos", u),
        "cos": lambda: neg(call("sin", u)),
        "tan": lambda: power(call("cos", u), Num(-2.0)),
        "asin": lambda: div(ONE, call("sqrt", sub(ONE, power(u, TWO)))),
        "acos": lambda: neg(div(ONE, call("sqrt", sub(ONE, power(u, TWO))))),
        "atan": lambda: div(ONE, add(ONE, power(u, TWO))),
        "sinh": lambda: call("cosh", u),
        "cosh": lambda: call("sinh", u),
        "tanh": lambda: power(call("cosh", u), Num(-2.0)),
        "asinh": lambda: div(ONE, call("sqrt", add(power(u, TWO), ONE))),
        "acosh": lambda: div(ONE, call("sqrt", sub(power(u, TWO), ONE))),
        "atanh": lambda: div(ONE, sub(ONE, power(u, TWO))),
        "exp": lambda: call("exp", u),
        "ln": lambda: div(ONE, u),
        "log": lambda: div(ONE, u),
        "log10": lambda: div(ONE, mul(u, call("ln", Num(10.0)))),
        "log2": lambda: div(ONE, mul(u, call("ln", TWO))),
        "sqrt": lambda: div(ONE, mul(TWO, call("sqrt", u))),
        "cbrt": lambda: div(ONE, mul(Num(3.0), power(call("cbrt", u), TWO))),
        "abs": lambda: call("sign", u),
        "sign": lambda: ZERO,
        "floor": lambda: ZERO,
        "ceil": lambda: ZERO,
        "deg": lambda: div(Num(180.0), Var("pi")),
        "rad": lambda: div(Var("pi"), Num(180.0)),
    }.get(name)
    if outer is None:
        raise EvaluationError(f"La derivada simbólica de {name}() no está definida")
    return mul(outer(), du)


def diff(node, var):
    """Derivada simbólica de ``node`` respecto de la variable ``var``."""
    if isinstance(node, str):
        node = parse(node)
    if isinstance(node, Num):
        return ZERO
    if isinstance(node, Var):
        return ONE if node.name == var else ZERO
    if isinstance(node, Unary):
        if node.op == "-":
            return neg(diff(node.operand, var))
        if node.op == "+":
            return diff(node.operand, var)
        if node.op == "!":
            if _is_num(diff(node.operand, var), 0):
                return ZERO
            raise EvaluationError("La derivada simbólica del factorial no está definida")
    if isinstance(node, Binary):
        u, v = node.left, node.right
        du, dv = diff(u, var), diff(v, var)
        op = node.op
        if op == "+":
            return add(du, dv)
        if op == "-":
            return sub(du, dv)
        if op == "*":
            return add(mul(du, v), mul(u, dv))
        if op == "/":
            if _is_num(dv, 0):
                return div(du, v)
            return div(sub(mul(du, v), mul(u, dv)), power(v, TWO))
        if op == "^":
            if _is_num(dv, 0):
                # Regla de la potencia: (u^n)' = n·u^(n-1)·u'
                return mul(mul(v, power(u, sub(v, ONE))), du)
            if _is_num(du, 0):
                # Exponencial: (a^v)' = a^v·ln(a)·v'
                return mul(mul(node, call("ln", u)), dv)
            # Caso general: (u^v)' = u^v·(v'·ln(u) + v·u'/u)
            return mul(node, add(mul(dv, call("ln", u)), div(mul(v, du), u)))
    if isinstance(node, Call):
        return _d_call(node, var)
    raise TypeError(f"Nodo desconocido: {node!r}")


def derivative(expression, var, order=1):
    """Derivada de orden ``order`` (simplificada) de una expresión."""
    if order < 0:
        raise EvaluationError("El orden de derivación debe ser ≥ 0")
    node = parse(expression) if isinstance(expression, str) else expression
    for _ in range(order):
        node = simplify(diff(node, var))
    return simplify(node)


def gradient(expression, variables):
    """Gradiente simbólico: lista de derivadas parciales."""
    node = parse(expression) if isinstance(expression, str) else expression
    return [simplify(diff(node, v)) for v in variables]


# --- LaTeX -----------------------------------------------------------

_LATEX_FUNCS = {
    "sin": r"\sin", "cos": r"\cos", "tan": r"\tan", "asin": r"\arcsin", "acos": r"\arccos",
    "atan": r"\arctan", "sinh": r"\sinh", "cosh": r"\cosh", "tanh": r"\tanh", "exp": r"\exp",
    "ln": r"\ln", "log": r"\log", "min": r"\min", "max": r"\max", "arg": r"\arg",
}
_LATEX_SYMBOLS = {
    "pi": r"\pi", "tau": r"\tau", "phi": r"\varphi", "inf": r"\infty", "alpha": r"\alpha",
    "beta": r"\beta", "gamma": r"\gamma", "delta": r"\delta", "theta": r"\theta", "omega": r"\omega",
    "lambda": r"\lambda", "mu": r"\mu", "sigma": r"\sigma", "rho": r"\rho", "epsilon": r"\varepsilon",
    "zeta": r"\zeta", "eta": r"\eta", "nu": r"\nu", "xi": r"\xi", "kappa": r"\kappa",
}
_LPREC = {"+": 1, "-": 1, "*": 2, "/": 5, "neg": 3, "^": 4}


def to_latex(node):
    """Exporta un AST (o texto) a LaTeX."""
    if isinstance(node, str):
        node = parse(node)
    return _latex(node)[0]


def _latex_var(name):
    if name in _LATEX_SYMBOLS:
        return _LATEX_SYMBOLS[name]
    if "_" in name:
        base, sub_ = name.split("_", 1)
        return f"{_latex_var(base)}_{{{sub_}}}"
    if len(name) > 1:
        return rf"\mathrm{{{name}}}"
    return name


def _latex(node):
    if isinstance(node, Num):
        text = to_string(node)
        return text, (3 if text.startswith("-") else 10)
    if isinstance(node, Var):
        return _latex_var(node.name), 10
    if isinstance(node, Call):
        args = [to_latex(a) for a in node.args]
        if node.name == "sqrt":
            return rf"\sqrt{{{args[0]}}}", 10
        if node.name == "cbrt":
            return rf"\sqrt[3]{{{args[0]}}}", 10
        if node.name == "abs":
            return rf"\left|{args[0]}\right|", 10
        if node.name == "log" and len(args) == 2:
            return rf"\log_{{{args[1]}}}\left({args[0]}\right)", 10
        if node.name == "log10":
            return rf"\log_{{10}}\left({args[0]}\right)", 10
        name = _LATEX_FUNCS.get(node.name, rf"\operatorname{{{node.name}}}")
        return rf"{name}\left({', '.join(args)}\right)", 10
    if isinstance(node, Unary):
        inner, p = _latex(node.operand)
        if node.op == "!":
            return (f"{inner}!" if p >= 10 else rf"\left({inner}\right)!"), 10
        if node.op == "+":
            return inner, p
        return (f"-{inner}" if p > 3 else rf"-\left({inner}\right)"), 3
    if isinstance(node, Binary):
        left, lp = _latex(node.left)
        right, rp = _latex(node.right)
        if node.op == "/":
            return rf"\frac{{{left}}}{{{right}}}", 5
        if node.op == "^":
            if lp <= 4:
                left = rf"\left({left}\right)"
            return f"{{{left}}}^{{{right}}}", 4
        prec = _LPREC[node.op]
        if lp < prec:
            left = rf"\left({left}\right)"
        if rp < prec or (rp == prec and node.op == "-"):
            right = rf"\left({right}\right)"
        if node.op == "*":
            # Coeficiente numérico seguido de símbolo: 2x; si no, \cdot.
            sep = " " if _is_num(node.left) and not _is_num(node.right) and not right.startswith("-") else r" \cdot "
            return f"{left}{sep}{right}", prec
        return f"{left} {node.op} {right}", prec
    raise TypeError(f"Nodo desconocido: {node!r}")
