"""Evaluación numérica de expresiones.

Modos:

* **Real** (por defecto): cualquier resultado complejo es un
  ``DomainError`` (p. ej. ``sqrt(-1)``, ``ln(-2)``). Es el modo seguro para
  cálculo de ingeniería, donde un complejo inesperado suele ser un error.
* **Complejo** (``complex_mode=True``): se usa ``cmath`` y está disponible la
  unidad imaginaria ``j`` (notación de ingeniería eléctrica).
"""

import cmath
import math

from ..errors import DomainError, EvaluationError
from .nodes import Binary, Call, Num, Unary, Var
from .parser import parse

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "phi": (1 + math.sqrt(5)) / 2,
}

MAX_FACTORIAL = 170  # 171! desborda float64


def _factorial(x):
    if isinstance(x, complex) or x < 0 or not float(x).is_integer():
        # Extensión continua: x! = Γ(x+1)
        return _gamma(x + 1)
    if x > MAX_FACTORIAL:
        raise DomainError(f"factorial({x:g}) desborda la precisión doble (máx. {MAX_FACTORIAL})")
    return float(math.factorial(int(x)))


def _gamma(x):
    if isinstance(x, complex):
        raise DomainError("gamma no está implementada para argumentos complejos")
    return math.gamma(x)


def _sign(x):
    if isinstance(x, complex):
        return x / abs(x) if x else 0.0
    return math.copysign(1.0, x) if x else 0.0


def _log(x, base=None):
    if base is None:
        return cmath.log(x)
    return cmath.log(x) / cmath.log(base)


def _round(x, ndigits=0):
    return float(round(x, int(ndigits)))


def _real_only(fn, name):
    def wrapper(*args):
        if any(isinstance(a, complex) for a in args):
            raise DomainError(f"{name} solo admite argumentos reales")
        return fn(*args)

    return wrapper


# nombre -> (función, aridad mínima, aridad máxima)
# Las funciones de cmath se usan en ambos modos; en modo real el resultado
# complejo se rechaza después (ver _coerce). Así sqrt(-1) falla con un
# mensaje de dominio claro en lugar de un ValueError genérico.
FUNCTIONS = {
    "sin": (cmath.sin, 1, 1),
    "cos": (cmath.cos, 1, 1),
    "tan": (cmath.tan, 1, 1),
    "asin": (cmath.asin, 1, 1),
    "acos": (cmath.acos, 1, 1),
    "atan": (cmath.atan, 1, 1),
    "atan2": (_real_only(math.atan2, "atan2"), 2, 2),
    "sinh": (cmath.sinh, 1, 1),
    "cosh": (cmath.cosh, 1, 1),
    "tanh": (cmath.tanh, 1, 1),
    "asinh": (cmath.asinh, 1, 1),
    "acosh": (cmath.acosh, 1, 1),
    "atanh": (cmath.atanh, 1, 1),
    "exp": (cmath.exp, 1, 1),
    "ln": (cmath.log, 1, 1),
    "log": (_log, 1, 2),
    "log10": (cmath.log10, 1, 1),
    "log2": (lambda x: cmath.log(x) / math.log(2), 1, 1),
    "sqrt": (cmath.sqrt, 1, 1),
    "cbrt": (_real_only(lambda x: math.copysign(abs(x) ** (1 / 3), x), "cbrt"), 1, 1),
    "abs": (abs, 1, 1),
    "sign": (_sign, 1, 1),
    "floor": (_real_only(lambda x: float(math.floor(x)), "floor"), 1, 1),
    "ceil": (_real_only(lambda x: float(math.ceil(x)), "ceil"), 1, 1),
    "round": (_real_only(_round, "round"), 1, 2),
    "min": (_real_only(min, "min"), 1, 64),
    "max": (_real_only(max, "max"), 1, 64),
    "hypot": (_real_only(math.hypot, "hypot"), 1, 64),
    "gamma": (_gamma, 1, 1),
    "factorial": (_factorial, 1, 1),
    "deg": (_real_only(math.degrees, "deg"), 1, 1),
    "rad": (_real_only(math.radians, "rad"), 1, 1),
    "re": (lambda z: complex(z).real, 1, 1),
    "im": (lambda z: complex(z).imag, 1, 1),
    "conj": (lambda z: complex(z).conjugate(), 1, 1),
    "arg": (lambda z: cmath.phase(z), 1, 1),
}


def _coerce(value, complex_mode, what):
    """Normaliza un resultado: complejo con parte imaginaria nula -> float."""
    if isinstance(value, complex):
        if value.imag == 0 or (not complex_mode and abs(value.imag) <= 1e-15 * max(1.0, abs(value.real))):
            value = value.real
        elif not complex_mode:
            raise DomainError(f"{what} produce un resultado complejo; active complex_mode para permitirlo")
    if isinstance(value, bool):
        value = float(value)
    if isinstance(value, int):
        value = float(value)
    return value


class Evaluator:
    """Evalúa ASTs con un entorno de variables dado."""

    def __init__(self, complex_mode=False):
        self.complex_mode = complex_mode

    def evaluate(self, node, env=None):
        env = env or {}
        try:
            return self._eval(node, env)
        except OverflowError as exc:
            raise DomainError(f"Desbordamiento numérico: {exc}") from exc
        except ZeroDivisionError as exc:
            raise DomainError("División por cero") from exc
        except ValueError as exc:
            raise DomainError(f"Argumento fuera de dominio: {exc}") from exc
        except RecursionError as exc:
            raise EvaluationError("Expresión demasiado profunda") from exc

    def _eval(self, node, env):
        cm = self.complex_mode
        if isinstance(node, Num):
            return node.value
        if isinstance(node, Var):
            if node.name in env:
                return _coerce(env[node.name], True, node.name)
            if node.name in CONSTANTS:
                return CONSTANTS[node.name]
            if cm and node.name == "j":
                return 1j
            raise EvaluationError(f"Variable no definida: {node.name!r}")
        if isinstance(node, Unary):
            value = self._eval(node.operand, env)
            if node.op == "-":
                return -value
            if node.op == "!":
                return _coerce(_factorial(value), cm, "factorial")
            return value
        if isinstance(node, Binary):
            a = self._eval(node.left, env)
            b = self._eval(node.right, env)
            op = node.op
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if op == "/":
                if b == 0:
                    raise DomainError("División por cero")
                return a / b
            if op == "^":
                return self._pow(a, b)
        if isinstance(node, Call):
            if node.name not in FUNCTIONS:
                raise EvaluationError(f"Función desconocida: {node.name!r}")
            fn, lo, hi = FUNCTIONS[node.name]
            n = len(node.args)
            if not lo <= n <= hi:
                expected = str(lo) if lo == hi else f"{lo}–{hi}"
                raise EvaluationError(f"{node.name}() espera {expected} argumento(s), recibió {n}")
            args = [self._eval(arg, env) for arg in node.args]
            return _coerce(fn(*args), cm, f"{node.name}()")
        raise EvaluationError(f"Nodo no evaluable: {node!r}")

    def _pow(self, a, b):
        if isinstance(a, complex) or isinstance(b, complex):
            if a == 0:
                return 0.0 if b != 0 else 1.0
            return _coerce(a ** b, self.complex_mode, "La potencia")
        if a == 0 and b < 0:
            raise DomainError("0 elevado a exponente negativo")
        if a < 0 and not float(b).is_integer():
            if not self.complex_mode:
                raise DomainError("Base negativa con exponente no entero produce un complejo")
            return _coerce(complex(a) ** b, True, "La potencia")
        return math.pow(a, b)


def evaluate(expression, variables=None, complex_mode=False):
    """Atajo: parsea (si es texto) y evalúa."""
    node = parse(expression) if isinstance(expression, str) else expression
    return Evaluator(complex_mode=complex_mode).evaluate(node, variables or {})


def compile_function(expression, variables, complex_mode=False):
    """Compila ``expression`` a una función de Python de los argumentos dados.

    >>> f = compile_function("x^2 + y", ["x", "y"])
    >>> f(3, 1)
    10.0
    """
    node = parse(expression) if isinstance(expression, str) else expression
    names = list(variables)
    evaluator = Evaluator(complex_mode=complex_mode)
    unknown = _unknown_names(node, names, complex_mode)
    if unknown:
        raise EvaluationError(f"Variables no declaradas en la expresión: {', '.join(sorted(unknown))}")

    def fn(*args):
        if len(args) != len(names):
            raise EvaluationError(f"Se esperaban {len(names)} argumento(s), se recibieron {len(args)}")
        return evaluator.evaluate(node, dict(zip(names, args)))

    fn.node = node
    fn.variables = names
    return fn


def _unknown_names(node, names, complex_mode):
    from .nodes import free_variables

    known = set(names) | set(CONSTANTS)
    if complex_mode:
        known.add("j")
    return free_variables(node) - known
