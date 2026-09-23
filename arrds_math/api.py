"""Capa API: registro de operaciones y contrato JSON del motor.

Toda operación se invoca por nombre con un diccionario de parámetros
JSON-compatibles, y toda respuesta tiene la misma forma::

    {"ok": true,  "operation": "...", "result": {...},            "elapsed_ms": 0.42}
    {"ok": false, "operation": "...", "error": {"code", "message", "hint"?}, "elapsed_ms": 0.1}

El contrato es independiente del lenguaje: el futuro núcleo nativo debe
aceptar los mismos parámetros y devolver los mismos resultados (ver
``docs/ARQUITECTURA.md``). Por eso la serialización es explícita:

* complejo  -> ``{"re": x, "im": y}``
* inf / nan -> ``"inf"``, ``"-inf"``, ``"nan"`` (JSON no los admite)
* resultado iterativo -> ``{value, converged, iterations, error_estimate, method, extra}``

Los resultados que conviene graficar traen ``plots``: una lista de
``{title, x_label, y_label, log_x, series: [{name, x, y}]}``.
"""

import dataclasses
import math
import time

from . import linalg, poly, signals, stats, units, vector
from . import numeric
from .errors import InvalidInputError, MathEngineError
from .expr import (
    CONSTANTS, FUNCTIONS, compile_function, derivative, free_variables, gradient, parse,
    simplify, to_latex, to_string, tokenize,
)
from .expr.nodes import Node
from .numeric._common import IterativeResult
from .numeric.calculus import gauss_legendre_nodes

API_VERSION = "0.1"
MAX_LIST = 100_000       # elementos por lista de entrada
MAX_MATRIX_DIM = 200     # filas/columnas de una matriz de entrada
MAX_SAMPLES = 10_000     # puntos de muestreo de una función

_REQUIRED = object()


# --- serialización --------------------------------------------------

def to_jsonable(obj):
    """Convierte un resultado del motor en algo que ``json.dumps`` acepta sin pérdidas."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj):
            return "nan"
        if math.isinf(obj):
            return "inf" if obj > 0 else "-inf"
        return obj
    if isinstance(obj, complex):
        return {"re": to_jsonable(obj.real), "im": to_jsonable(obj.imag)}
    if isinstance(obj, IterativeResult):
        return {k: to_jsonable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, Node):
        return to_string(obj)
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")


def from_jsonable_number(value, name="valor", allow_complex=False):
    """Inverso de ``to_jsonable`` para un número de entrada."""
    if isinstance(value, bool):
        raise InvalidInputError(f"{name} debe ser un número, no un booleano")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value in ("inf", "-inf", "nan"):
        return float(value)
    if isinstance(value, dict) and set(value) == {"re", "im"}:
        if not allow_complex:
            raise InvalidInputError(f"{name} debe ser real")
        return complex(from_jsonable_number(value["re"], name), from_jsonable_number(value["im"], name))
    raise InvalidInputError(f"{name} debe ser un número (recibido {type(value).__name__})")


# --- lectura de parámetros ------------------------------------------

def _get(p, key, default=_REQUIRED):
    if key in p:
        return p[key]
    if default is _REQUIRED:
        raise InvalidInputError(f"Falta el parámetro obligatorio {key!r}")
    return default


def _num(p, key, default=_REQUIRED, allow_complex=False):
    if key not in p and default is not _REQUIRED:
        return default
    return from_jsonable_number(_get(p, key), key, allow_complex)


def _int(p, key, default=_REQUIRED, lo=None, hi=None):
    value = _get(p, key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        else:
            raise InvalidInputError(f"{key} debe ser un entero")
    if (lo is not None and value < lo) or (hi is not None and value > hi):
        raise InvalidInputError(f"{key} debe estar entre {lo} y {hi}")
    return value


def _str(p, key, default=_REQUIRED):
    value = _get(p, key, default)
    if not isinstance(value, str):
        raise InvalidInputError(f"{key} debe ser texto")
    return value


def _bool(p, key, default=False):
    value = _get(p, key, default)
    if not isinstance(value, bool):
        raise InvalidInputError(f"{key} debe ser true o false")
    return value


def _list(p, key, default=_REQUIRED, allow_complex=False, min_len=1):
    if key not in p and default is not _REQUIRED:
        return default
    value = _get(p, key)
    if not isinstance(value, list) or len(value) < min_len:
        raise InvalidInputError(f"{key} debe ser una lista de al menos {min_len} elemento(s)")
    if len(value) > MAX_LIST:
        raise InvalidInputError(f"{key} supera el máximo de {MAX_LIST} elementos")
    return [from_jsonable_number(v, key, allow_complex) for v in value]


def _strs(p, key, default=_REQUIRED):
    value = _get(p, key, default)
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
        raise InvalidInputError(f"{key} debe ser una lista de textos")
    return value


def _matrix(p, key):
    value = _get(p, key)
    if not isinstance(value, list) or not value or not all(isinstance(r, list) for r in value):
        raise InvalidInputError(f"{key} debe ser una matriz (lista de filas)")
    if len(value) > MAX_MATRIX_DIM or any(len(r) > MAX_MATRIX_DIM for r in value):
        raise InvalidInputError(f"{key} supera el tamaño máximo {MAX_MATRIX_DIM}×{MAX_MATRIX_DIM}")
    return [[from_jsonable_number(v, key) for v in r] for r in value]


# --- registro --------------------------------------------------------

@dataclasses.dataclass
class Operation:
    name: str
    module: str
    description: str
    params: dict      # nombre -> descripción ("(opcional)" si lo es)
    example: dict
    handler: object

    def describe(self):
        return {
            "name": self.name, "module": self.module, "description": self.description,
            "params": self.params, "example": self.example,
        }


OPERATIONS = {}

MODULES = {
    "expr": "Capa 1 · Expresiones y simbólico",
    "numeric": "Capa 2 · Cálculo numérico",
    "linalg": "Capa 2 · Álgebra lineal",
    "poly": "Capa 2 · Polinomios",
    "stats": "Capa 2 · Estadística",
    "vector": "Mat C · Análisis vectorial",
    "signals": "Mat D · Plano complejo y señales",
    "units": "Capa 3 · Unidades y dimensiones",
}


def operation(name, description, params, example):
    """Decorador: registra ``handler(params) -> resultado`` bajo ``name``."""
    module = name.split(".", 1)[0]
    if module not in MODULES:
        raise ValueError(f"Módulo no registrado: {module}")
    unknown = set(example) - set(params)
    if unknown:
        raise ValueError(f"{name}: el ejemplo usa parámetros no declarados {unknown}")

    def register(handler):
        OPERATIONS[name] = Operation(name, module, description, params, example, handler)
        return handler

    return register


def list_operations():
    return {
        "api_version": API_VERSION,
        "modules": MODULES,
        "operations": [op.describe() for op in OPERATIONS.values()],
    }


def run(name, params=None):
    """Ejecuta una operación y devuelve la respuesta uniforme (nunca lanza)."""
    start = time.perf_counter()
    params = {} if params is None else params
    try:
        if name not in OPERATIONS:
            raise _UnknownOperation(f"Operación desconocida: {name!r}")
        if not isinstance(params, dict):
            raise InvalidInputError("params debe ser un objeto JSON")
        op = OPERATIONS[name]
        extra = set(params) - set(op.params)
        if extra:
            raise InvalidInputError(f"Parámetro(s) no reconocido(s): {', '.join(sorted(extra))}")
        result = to_jsonable(op.handler(params))
        response = {"ok": True, "operation": name, "result": result}
    except MathEngineError as exc:
        response = {"ok": False, "operation": name, "error": exc.to_dict()}
    except RecursionError:
        response = {"ok": False, "operation": name,
                    "error": {"code": "EVALUATION_ERROR", "message": "Recursión demasiado profunda"}}
    except Exception as exc:  # noqa: BLE001 — la API nunca debe caerse
        response = {"ok": False, "operation": name,
                    "error": {"code": "INTERNAL_ERROR", "message": f"{type(exc).__name__}: {exc}"}}
    response["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 3)
    return response


class _UnknownOperation(MathEngineError):
    code = "UNKNOWN_OPERATION"


# --- helpers de resultado -------------------------------------------

def _plot(title, x_label, y_label, series, log_x=False):
    return {"title": title, "x_label": x_label, "y_label": y_label, "log_x": log_x, "series": series}


def _expr_out(node):
    return {"expression": to_string(node), "latex": to_latex(node)}


def _vars_param(p, expression):
    """Variables declaradas; si faltan se infieren de la expresión (orden alfabético)."""
    if "variables" in p:
        return _strs(p, "variables")
    return sorted(free_variables(parse(expression)) - set(CONSTANTS))


# ====================================================================
# expr — Capa 1
# ====================================================================

_E = "Expresión en texto (sintaxis del parser del motor)"


@operation("expr.tokenize", "Divide una expresión en tokens (diagnóstico del parser).",
           {"expression": _E}, {"expression": "2x^2 + sin(x)"})
def _h(p):
    return [{"kind": t.kind, "text": t.text, "pos": t.pos} for t in tokenize(_str(p, "expression"))]


@operation("expr.parse", "Parsea una expresión: forma canónica, variables libres y LaTeX.",
           {"expression": _E}, {"expression": "2x(x+1) - 3 sin(x)^2"})
def _h(p):
    node = parse(_str(p, "expression"))
    out = _expr_out(node)
    out["variables"] = sorted(free_variables(node) - set(CONSTANTS))
    return out


@operation("expr.evaluate", "Evalúa una expresión con variables (modo real o complejo).",
           {"expression": _E, "variables": "(opcional) objeto nombre → valor",
            "complex_mode": "(opcional) true habilita complejos y la unidad j"},
           {"expression": "sqrt(x^2 + y^2)", "variables": {"x": 3, "y": 4}})
def _h(p):
    cm = _bool(p, "complex_mode", False)
    env = _get(p, "variables", {})
    if not isinstance(env, dict):
        raise InvalidInputError("variables debe ser un objeto nombre → valor")
    env = {k: from_jsonable_number(v, k, allow_complex=cm) for k, v in env.items()}
    from .expr import evaluate
    return {"value": evaluate(_str(p, "expression"), env, complex_mode=cm)}


@operation("expr.simplify", "Simplificación algebraica conservadora (no cambia el dominio).",
           {"expression": _E}, {"expression": "0*x + 1*y + (x^2)^3 + 2 + 3"})
def _h(p):
    return _expr_out(simplify(parse(_str(p, "expression"))))


@operation("expr.derivative", "Derivada simbólica exacta de orden n.",
           {"expression": _E, "var": "Variable de derivación", "order": "(opcional) orden, por defecto 1"},
           {"expression": "x^3 * sin(x)", "var": "x", "order": 1})
def _h(p):
    return _expr_out(derivative(_str(p, "expression"), _str(p, "var"), _int(p, "order", 1, 0, 10)))


@operation("expr.gradient", "Gradiente simbólico (lista de derivadas parciales).",
           {"expression": _E, "variables": "Lista de variables"},
           {"expression": "x^2*y + exp(y)", "variables": ["x", "y"]})
def _h(p):
    nodes = gradient(_str(p, "expression"), _strs(p, "variables"))
    return {"expressions": [to_string(n) for n in nodes], "latex": [to_latex(n) for n in nodes]}


@operation("expr.to_latex", "Exporta una expresión a LaTeX.",
           {"expression": _E}, {"expression": "sqrt(x^2+1)/(2 pi) + abs(z)"})
def _h(p):
    return {"latex": to_latex(_str(p, "expression"))}


@operation("expr.sample", "Muestrea f(var) en [a, b] (puntos fuera de dominio → null) para graficar.",
           {"expression": _E, "var": "(opcional) variable, por defecto x", "a": "Inicio", "b": "Fin",
            "n": f"(opcional) puntos, 2–{MAX_SAMPLES}, por defecto 200"},
           {"expression": "sin(x)/x", "var": "x", "a": -20, "b": 20, "n": 400})
def _h(p):
    expr, var = _str(p, "expression"), _str(p, "var", "x")
    a, b, n = _num(p, "a"), _num(p, "b"), _int(p, "n", 200, 2, MAX_SAMPLES)
    f = compile_function(expr, [var])
    xs = [a + (b - a) * i / (n - 1) for i in range(n)]
    ys, failures = [], 0
    for x in xs:
        try:
            ys.append(f(x))
        except MathEngineError:
            ys.append(None)
            failures += 1
    return {"x": xs, "y": ys, "undefined_points": failures,
            "plots": [_plot(f"f({var}) = {expr}", var, "f", [{"name": expr, "x": xs, "y": ys}])]}


@operation("expr.catalog", "Funciones y constantes que entiende el parser.", {}, {})
def _h(p):
    return {
        "functions": {k: {"min_args": lo, "max_args": hi} for k, (_, lo, hi) in sorted(FUNCTIONS.items())},
        "constants": CONSTANTS,
        "operators": ["+", "-", "*", "/", "^", "**", "!", "multiplicación implícita (2x, 2(x+1))"],
    }


# ====================================================================
# numeric — Capa 2
# ====================================================================

_F = "Función de x en texto"
_TOL = "(opcional) tolerancia"


_ROOT_REQUIRED = {"bisection": ("a", "b"), "brent": ("a", "b"), "newton": ("x0",), "secant": ("x0", "x1")}


def _root_kwargs(p, keys, method):
    missing = [k for k in _ROOT_REQUIRED.get(method, ()) if k not in p]
    if missing:
        raise InvalidInputError(f"El método {method} requiere: {', '.join(missing)}")
    kw = {}
    for k in keys:
        if k in p:
            kw[k] = _int(p, k, lo=1, hi=100_000) if k == "max_iter" else _bound(p, k)
    return kw


@operation("numeric.bisection", "Raíz por bisección (requiere cambio de signo en [a, b]).",
           {"expression": _F, "a": "Extremo izquierdo", "b": "Extremo derecho", "tol": _TOL,
            "max_iter": "(opcional)"},
           {"expression": "x^3 - 2x - 5", "a": 2, "b": 3})
def _h(p):
    return numeric.bisection(_str(p, "expression"), **_root_kwargs(p, ("a", "b", "tol", "max_iter"), "bisection"))


@operation("numeric.newton", "Raíz por Newton–Raphson (derivada simbólica automática).",
           {"expression": _F, "x0": "Punto inicial", "derivative": "(opcional) f'(x) en texto",
            "tol": _TOL, "max_iter": "(opcional)"},
           {"expression": "x^3 - 2x - 5", "x0": 2})
def _h(p):
    return numeric.newton(_str(p, "expression"), df=_get(p, "derivative", None),
                          **_root_kwargs(p, ("x0", "tol", "max_iter"), "newton"))


@operation("numeric.secant", "Raíz por el método de la secante.",
           {"expression": _F, "x0": "Primer punto", "x1": "Segundo punto", "tol": _TOL,
            "max_iter": "(opcional)"},
           {"expression": "cos(x) - x", "x0": 0, "x1": 1})
def _h(p):
    return numeric.secant(_str(p, "expression"), **_root_kwargs(p, ("x0", "x1", "tol", "max_iter"), "secant"))


@operation("numeric.brent", "Raíz por Brent–Dekker (recomendado con intervalo).",
           {"expression": _F, "a": "Extremo izquierdo", "b": "Extremo derecho", "tol": _TOL,
            "max_iter": "(opcional)"},
           {"expression": "x^3 - 2x - 5", "a": 2, "b": 3})
def _h(p):
    return numeric.brent(_str(p, "expression"), **_root_kwargs(p, ("a", "b", "tol", "max_iter"), "brent"))


@operation("numeric.find_root", "Raíz con el método elegido (bisection | newton | secant | brent).",
           {"expression": _F, "method": "(opcional) por defecto brent", "a": "(según método)",
            "b": "(según método)", "x0": "(según método)", "x1": "(según método)", "tol": _TOL,
            "max_iter": "(opcional)"},
           {"expression": "exp(-x) - x", "method": "brent", "a": 0, "b": 1})
def _h(p):
    method = _str(p, "method", "brent")
    keys = _ROOT_REQUIRED.get(method, ()) + ("tol", "max_iter")
    return numeric.find_root(_str(p, "expression"), method=method, **_root_kwargs(p, keys, method))


@operation("numeric.derivative", "Derivada numérica (diferencias centradas + Richardson), orden 1 o 2.",
           {"expression": _F, "x": "Punto", "order": "(opcional) 1 o 2", "h": "(opcional) paso inicial"},
           {"expression": "exp(x) * sin(x)", "x": 1.0, "order": 1})
def _h(p):
    return numeric.derivative(_str(p, "expression"), _num(p, "x"), order=_int(p, "order", 1, 1, 2),
                              h=_num(p, "h", None))


@operation("numeric.simpson_adaptive", "Integral definida por Simpson adaptativo.",
           {"expression": _F, "a": "Límite inferior", "b": "Límite superior", "tol": _TOL},
           {"expression": "sin(x)", "a": 0, "b": "pi"})
def _h(p):
    return numeric.simpson_adaptive(_str(p, "expression"), _bound(p, "a"), _bound(p, "b"),
                                    tol=_num(p, "tol", 1e-10))


@operation("numeric.gauss_legendre", "Integral definida por cuadratura de Gauss–Legendre de n puntos.",
           {"expression": _F, "a": "Límite inferior", "b": "Límite superior", "n": "(opcional) 1–190"},
           {"expression": "exp(-x^2)", "a": -3, "b": 3, "n": 20})
def _h(p):
    return numeric.gauss_legendre(_str(p, "expression"), _bound(p, "a"), _bound(p, "b"),
                                  n=_int(p, "n", 20, 1, 190))


@operation("numeric.integrate", "Integral definida con el método elegido (simpson_adaptive | gauss_legendre).",
           {"expression": _F, "a": "Límite inferior", "b": "Límite superior",
            "method": "(opcional) por defecto simpson_adaptive", "tol": "(opcional, Simpson)",
            "n": "(opcional, Gauss–Legendre)"},
           {"expression": "1/(1+x^2)", "a": 0, "b": 1, "method": "simpson_adaptive"})
def _h(p):
    method = _str(p, "method", "simpson_adaptive")
    kw = {}
    if "tol" in p:
        kw["tol"] = _num(p, "tol")
    if "n" in p:
        kw["n"] = _int(p, "n", lo=1, hi=190)
    return numeric.integrate(_str(p, "expression"), _bound(p, "a"), _bound(p, "b"), method=method, **kw)


def _bound(p, key):
    """Un límite puede ser número o expresión constante ("pi", "2*pi")."""
    value = _get(p, key)
    if isinstance(value, str) and value not in ("inf", "-inf", "nan"):
        from .expr import evaluate
        return evaluate(value)
    return from_jsonable_number(value, key)


@operation("numeric.trapezoid", "Regla del trapecio sobre datos muestreados.",
           {"y": "Lista de valores", "x": "(opcional) abscisas", "dx": "(opcional) paso uniforme"},
           {"y": [0, 1, 4, 9, 16], "x": [0, 1, 2, 3, 4]})
def _h(p):
    y = _list(p, "y", min_len=2)
    x = _list(p, "x", None, min_len=2) if "x" in p else None
    return {"value": numeric.trapezoid(y, x, dx=_num(p, "dx", 1.0))}


@operation("numeric.gauss_legendre_nodes", "Nodos y pesos de Gauss–Legendre en [−1, 1].",
           {"n": "Número de puntos (1–200)"}, {"n": 5})
def _h(p):
    nodes, weights = gauss_legendre_nodes(_int(p, "n", lo=1, hi=200))
    return {"nodes": nodes, "weights": weights}


_ODE_PARAMS = {
    "expressions": "Lista de expresiones y_i' = f_i(t, y)", "state_vars": "Nombres de las variables de estado",
    "time_var": "(opcional) por defecto t", "t0": "Tiempo inicial", "t1": "Tiempo final",
    "y0": "Estado inicial",
}


def _ode(p, method):
    exprs, names = _strs(p, "expressions"), _strs(p, "state_vars")
    f = numeric.system_from_expressions(exprs, names, _str(p, "time_var", "t"))
    kw = {}
    if method == "rk4":
        kw["steps"] = _int(p, "steps", 1000, 1, 200_000)
    else:
        for k in ("rtol", "atol"):
            if k in p:
                kw[k] = _num(p, k)
    res = numeric.solve_ivp(f, _bound(p, "t0"), _list(p, "y0"), _bound(p, "t1"), method=method, **kw)
    ts, ys = res.value["t"], res.value["y"]
    series = [{"name": n, "x": ts, "y": [row[i] for row in ys]} for i, n in enumerate(names)]
    out = to_jsonable(res)
    out["plots"] = [_plot("Solución de la EDO", _str(p, "time_var", "t"), "y", series)]
    return out


@operation("numeric.solve_ivp", "Sistema de EDO y' = f(t, y) (método rk45 adaptativo o rk4).",
           dict(_ODE_PARAMS, method="(opcional) rk45 | rk4", steps="(opcional, rk4)",
                rtol="(opcional, rk45)", atol="(opcional, rk45)"),
           {"expressions": ["v", "-4*x - 0.4*v"], "state_vars": ["x", "v"], "t0": 0, "t1": 10,
            "y0": [1, 0], "method": "rk45"})
def _h(p):
    method = _str(p, "method", "rk45")
    if method not in ("rk4", "rk45"):
        raise InvalidInputError("method debe ser rk4 o rk45")
    return _ode(p, method)


@operation("numeric.rk4", "EDO por Runge–Kutta 4 de paso fijo (error por duplicación de paso).",
           dict(_ODE_PARAMS, steps="(opcional) número de pasos"),
           {"expressions": ["y2", "-y1"], "state_vars": ["y1", "y2"], "t0": 0, "t1": "2*pi",
            "y0": [1, 0], "steps": 200})
def _h(p):
    return _ode(p, "rk4")


@operation("numeric.rk45", "EDO por Dormand–Prince 5(4) con paso adaptativo.",
           dict(_ODE_PARAMS, rtol="(opcional)", atol="(opcional)"),
           {"expressions": ["-2*y"], "state_vars": ["y"], "t0": 0, "t1": 3, "y0": [1]})
def _h(p):
    return _ode(p, "rk45")


# ====================================================================
# linalg — Capa 2
# ====================================================================

_A = [[4, -2, 1], [-2, 4, -2], [1, -2, 4]]


@operation("linalg.solve", "Resuelve Ax = b por LU con pivoteo y refinamiento iterativo.",
           {"A": "Matriz cuadrada", "b": "Vector", "refine": "(opcional) por defecto true"},
           {"A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], "b": [8, -11, -3]})
def _h(p):
    a, b = _matrix(p, "A"), _list(p, "b")
    x = linalg.solve(a, b, refine=_bool(p, "refine", True))
    residual = linalg.norm([bi - ri for bi, ri in zip(b, linalg.matvec(a, x))], "inf")
    return {"x": x, "residual_inf": residual, "cond_1": linalg.cond(a)}


@operation("linalg.det", "Determinante (vía LU).", {"A": "Matriz cuadrada"}, {"A": _A})
def _h(p):
    return {"value": linalg.det(_matrix(p, "A"))}


@operation("linalg.inverse", "Matriz inversa (vía LU).", {"A": "Matriz cuadrada"}, {"A": _A})
def _h(p):
    return {"value": linalg.inverse(_matrix(p, "A"))}


@operation("linalg.cond", "Número de condición en norma 1 (∞ si es singular).", {"A": "Matriz cuadrada"},
           {"A": [[1, 2], [2, 4.0001]]})
def _h(p):
    return {"value": linalg.cond(_matrix(p, "A"))}


@operation("linalg.lu", "Factorización PA = LU con pivoteo parcial.", {"A": "Matriz cuadrada"}, {"A": _A})
def _h(p):
    return linalg.lu(_matrix(p, "A"))


@operation("linalg.qr", "Factorización A = QR por Householder (m ≥ n).", {"A": "Matriz m×n"},
           {"A": [[12, -51, 4], [6, 167, -68], [-4, 24, -41]]})
def _h(p):
    return linalg.qr(_matrix(p, "A"))


@operation("linalg.lstsq", "Mínimos cuadrados min ‖Ax − b‖₂ vía QR.", {"A": "Matriz m×n", "b": "Vector"},
           {"A": [[1, 0], [1, 1], [1, 2]], "b": [1, 2, 2]})
def _h(p):
    return linalg.lstsq(_matrix(p, "A"), _list(p, "b"))


@operation("linalg.eig_symmetric", "Autovalores/autovectores de una matriz simétrica (Jacobi).",
           {"A": "Matriz simétrica", "tol": _TOL}, {"A": [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]})
def _h(p):
    return linalg.eig_symmetric(_matrix(p, "A"), tol=_num(p, "tol", 1e-14))


@operation("linalg.norm", "Norma de vector (1, 2, inf) o de matriz (1, 2, inf, fro).",
           {"x": "Vector o matriz", "ord": "(opcional) 1 | 2 | \"inf\" | \"fro\""},
           {"x": [[1, 2], [3, 4]], "ord": "fro"})
def _h(p):
    x = _get(p, "x")
    x = _matrix(p, "x") if isinstance(x, list) and x and isinstance(x[0], list) else _list(p, "x")
    return {"value": linalg.norm(x, _get(p, "ord", 2))}


@operation("linalg.matmul", "Producto de matrices A·B.", {"A": "Matriz", "B": "Matriz"},
           {"A": [[1, 2], [3, 4]], "B": [[0, 1], [1, 0]]})
def _h(p):
    return {"value": linalg.matmul(_matrix(p, "A"), _matrix(p, "B"))}


@operation("linalg.matvec", "Producto matriz·vector.", {"A": "Matriz", "v": "Vector"},
           {"A": [[1, 2], [3, 4]], "v": [1, 1]})
def _h(p):
    return {"value": linalg.matvec(_matrix(p, "A"), _list(p, "v"))}


@operation("linalg.add", "Suma de matrices.", {"A": "Matriz", "B": "Matriz"},
           {"A": [[1, 2], [3, 4]], "B": [[1, 1], [1, 1]]})
def _h(p):
    return {"value": linalg.add(_matrix(p, "A"), _matrix(p, "B"))}


@operation("linalg.scale", "Producto de una matriz por un escalar.", {"A": "Matriz", "k": "Escalar"},
           {"A": [[1, 2], [3, 4]], "k": 2.5})
def _h(p):
    return {"value": linalg.scale(_matrix(p, "A"), _num(p, "k"))}


@operation("linalg.transpose", "Traspuesta.", {"A": "Matriz"}, {"A": [[1, 2, 3], [4, 5, 6]]})
def _h(p):
    return {"value": linalg.transpose(_matrix(p, "A"))}


@operation("linalg.identity", "Matriz identidad n×n.", {"n": f"Tamaño (1–{MAX_MATRIX_DIM})"}, {"n": 3})
def _h(p):
    return {"value": linalg.identity(_int(p, "n", lo=1, hi=MAX_MATRIX_DIM))}


@operation("linalg.dot", "Producto escalar.", {"u": "Vector", "v": "Vector"}, {"u": [1, 2, 3], "v": [4, 5, 6]})
def _h(p):
    return {"value": linalg.dot(_list(p, "u"), _list(p, "v"))}


@operation("linalg.cross", "Producto vectorial en R³.", {"u": "Vector 3D", "v": "Vector 3D"},
           {"u": [1, 0, 0], "v": [0, 1, 0]})
def _h(p):
    return {"value": linalg.cross(_list(p, "u"), _list(p, "v"))}


# ====================================================================
# poly — Capa 2
# ====================================================================

_P = "Coeficientes en orden descendente"


@operation("poly.polyval", "Evalúa un polinomio (Horner); x puede ser complejo {re, im}.",
           {"p": _P, "x": "Punto (real o complejo)"}, {"p": [1, -3, 2], "x": 5})
def _h(p):
    return {"value": poly.polyval(_list(p, "p"), _num(p, "x", allow_complex=True))}


@operation("poly.polyder", "Derivada de un polinomio.", {"p": _P}, {"p": [1, 0, -3, 2]})
def _h(p):
    return {"value": poly.polyder(_list(p, "p"))}


@operation("poly.polyint", "Primitiva de un polinomio (constante k).", {"p": _P, "k": "(opcional) constante"},
           {"p": [3, 0, 1], "k": 0})
def _h(p):
    return {"value": poly.polyint(_list(p, "p"), _num(p, "k", 0.0))}


@operation("poly.polymul", "Producto de polinomios.", {"p": _P, "q": _P}, {"p": [1, 1], "q": [1, -1]})
def _h(p):
    return {"value": poly.polymul(_list(p, "p"), _list(p, "q"))}


@operation("poly.polyadd", "Suma de polinomios.", {"p": _P, "q": _P}, {"p": [1, 0, 1], "q": [2, 3]})
def _h(p):
    return {"value": poly.polyadd(_list(p, "p"), _list(p, "q"))}


@operation("poly.roots", "Todas las raíces complejas (Durand–Kerner + pulido de Newton).",
           {"p": _P}, {"p": [1, -6, 11, -6]})
def _h(p):
    return poly.roots(_list(p, "p"))


@operation("poly.polyfit", "Ajuste polinomial por mínimos cuadrados (QR).",
           {"x": "Abscisas", "y": "Ordenadas", "degree": "Grado"},
           {"x": [0, 1, 2, 3, 4], "y": [1, 3, 7, 13, 21], "degree": 2})
def _h(p):
    x, y = _list(p, "x"), _list(p, "y")
    fit = poly.polyfit(x, y, _int(p, "degree", lo=0, hi=20))
    fit["plots"] = [_plot("Ajuste polinomial", "x", "y", [
        {"name": "datos", "x": x, "y": y, "points": True},
        {"name": "ajuste", "x": _grid(x), "y": [poly.polyval(fit["coefficients"], t) for t in _grid(x)]},
    ])]
    return fit


def _grid(xs, n=200):
    lo, hi = min(xs), max(xs)
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


# ====================================================================
# stats — Capa 2
# ====================================================================

_D = "Lista de datos"


@operation("stats.mean", "Media aritmética.", {"data": _D}, {"data": [9.81, 9.79, 9.83, 9.80]})
def _h(p):
    return {"value": stats.mean(_list(p, "data"))}


@operation("stats.variance", "Varianza (ddof=1 muestral, 0 poblacional).",
           {"data": _D, "ddof": "(opcional) 0 o 1"}, {"data": [2, 4, 4, 4, 5, 5, 7, 9], "ddof": 0})
def _h(p):
    return {"value": stats.variance(_list(p, "data"), _int(p, "ddof", 1, 0, 1))}


@operation("stats.std", "Desviación estándar.", {"data": _D, "ddof": "(opcional) 0 o 1"},
           {"data": [2, 4, 4, 4, 5, 5, 7, 9], "ddof": 0})
def _h(p):
    return {"value": stats.std(_list(p, "data"), _int(p, "ddof", 1, 0, 1))}


@operation("stats.median", "Mediana.", {"data": _D}, {"data": [3, 1, 4, 1, 5, 9, 2, 6]})
def _h(p):
    return {"value": stats.median(_list(p, "data"))}


@operation("stats.describe", "Resumen: n, media, mediana, extremos, σ y error estándar de la media.",
           {"data": _D}, {"data": [9.81, 9.79, 9.83, 9.80, 9.82]})
def _h(p):
    return stats.describe(_list(p, "data"))


@operation("stats.linregress", "Regresión lineal y = m·x + b con incertidumbres.",
           {"x": "Abscisas", "y": "Ordenadas"}, {"x": [0, 1, 2, 3, 4], "y": [0.1, 2.1, 3.9, 6.2, 7.9]})
def _h(p):
    x, y = _list(p, "x", min_len=2), _list(p, "y", min_len=2)
    out = stats.linregress(x, y)
    xs = [min(x), max(x)]
    out["plots"] = [_plot("Regresión lineal", "x", "y", [
        {"name": "datos", "x": x, "y": y, "points": True},
        {"name": "recta", "x": xs, "y": [out["slope"] * t + out["intercept"] for t in xs]},
    ])]
    return out


# ====================================================================
# vector — Mat C
# ====================================================================

_V = "Variables de coordenadas"
_PT = "(opcional) punto donde evaluar"


def _point(p):
    return _list(p, "point") if "point" in p else None


@operation("vector.gradient", "∇f simbólico (y evaluado en un punto).",
           {"expression": "Campo escalar", "variables": _V, "point": _PT},
           {"expression": "x^2 + y^2 + z^2", "variables": ["x", "y", "z"], "point": [1, 2, 3]})
def _h(p):
    return vector.gradient(_str(p, "expression"), _strs(p, "variables"), _point(p))


@operation("vector.divergence", "∇·F simbólica.", {"field": "Componentes del campo", "variables": _V, "point": _PT},
           {"field": ["x*y", "y*z", "z*x"], "variables": ["x", "y", "z"], "point": [1, 1, 1]})
def _h(p):
    return vector.divergence(_strs(p, "field"), _strs(p, "variables"), _point(p))


@operation("vector.curl", "∇×F simbólico en R³.", {"field": "Componentes (P, Q, R)", "variables": _V, "point": _PT},
           {"field": ["-y", "x", "0"], "variables": ["x", "y", "z"]})
def _h(p):
    return vector.curl(_strs(p, "field"), _strs(p, "variables"), _point(p))


@operation("vector.laplacian", "∇²f simbólico.", {"expression": "Campo escalar", "variables": _V, "point": _PT},
           {"expression": "x^2*y + sin(z)", "variables": ["x", "y", "z"], "point": [1, 2, 0]})
def _h(p):
    return vector.laplacian(_str(p, "expression"), _strs(p, "variables"), _point(p))


@operation("vector.jacobian", "Matriz jacobiana simbólica.", {"field": "Componentes", "variables": _V, "point": _PT},
           {"field": ["r*cos(t)", "r*sin(t)"], "variables": ["r", "t"], "point": [2, 0]})
def _h(p):
    return vector.jacobian(_strs(p, "field"), _strs(p, "variables"), _point(p))


# ====================================================================
# signals — Mat D
# ====================================================================

@operation("signals.fft", "DFT de una secuencia (FFT radix-2 si N es potencia de 2).",
           {"x": "Muestras (reales o {re, im})", "inverse": "(opcional) true para la inversa"},
           {"x": [1, 0, -1, 0], "inverse": False})
def _h(p):
    return {"value": signals.fft(_list(p, "x", allow_complex=True), inverse=_bool(p, "inverse", False))}


@operation("signals.spectrum", "Espectro de amplitud de una señal real (o de una expresión muestreada).",
           {"x": "(opcional) muestras", "expression": "(opcional) señal f(t) en texto",
            "sample_rate": "Frecuencia de muestreo [Hz]", "n": "(opcional, con expression) muestras"},
           {"expression": "sin(2*pi*50*t) + 0.5*sin(2*pi*120*t)", "sample_rate": 1024, "n": 1024})
def _h(p):
    fs = _num(p, "sample_rate", 1.0)
    if "expression" in p:
        n = _int(p, "n", 1024, 2, 1 << 16)
        f = compile_function(_str(p, "expression"), ["t"])
        x = [f(i / fs) for i in range(n)]
    else:
        x = _list(p, "x", min_len=2)
    out = signals.spectrum(x, fs)
    out["plots"] = [_plot("Espectro de amplitud", "f [Hz]", "|X|",
                          [{"name": "amplitud", "x": out["frequency"], "y": out["amplitude"]}])]
    return out


@operation("signals.transfer_function", "H(s) = N(s)/D(s): polos, ceros, ganancia DC y estabilidad.",
           {"num": "Numerador (descendente)", "den": "Denominador (descendente)"},
           {"num": [1], "den": [1, 0.4, 4]})
def _h(p):
    return signals.transfer_function(_list(p, "num"), _list(p, "den"))


@operation("signals.bode", "Respuesta en frecuencia H(jω): magnitud [dB] y fase [°] desenvuelta.",
           {"num": "Numerador", "den": "Denominador", "w_min": "(opcional) rad/s", "w_max": "(opcional) rad/s",
            "n": "(opcional) puntos", "w": "(opcional) lista explícita de ω"},
           {"num": [1], "den": [1, 0.4, 4], "w_min": 0.1, "w_max": 100, "n": 300})
def _h(p):
    kw = {"w": _list(p, "w")} if "w" in p else {
        "w_min": _num(p, "w_min", 1e-2), "w_max": _num(p, "w_max", 1e2), "n": _int(p, "n", 200, 2, MAX_SAMPLES)}
    out = signals.freq_response(_list(p, "num"), _list(p, "den"), **kw)
    out["plots"] = [
        _plot("Bode — magnitud", "ω [rad/s]", "|H| [dB]",
              [{"name": "magnitud", "x": out["w"], "y": out["magnitude_db"]}], log_x=True),
        _plot("Bode — fase", "ω [rad/s]", "fase [°]",
              [{"name": "fase", "x": out["w"], "y": out["phase_deg"]}], log_x=True),
    ]
    return out


@operation("signals.logspace", "n puntos logarítmicamente espaciados entre 10^a y 10^b.",
           {"start_exp": "a", "stop_exp": "b", "n": "Puntos"}, {"start_exp": -1, "stop_exp": 2, "n": 4})
def _h(p):
    return {"value": signals.logspace(_num(p, "start_exp"), _num(p, "stop_exp"), _int(p, "n", lo=2, hi=MAX_SAMPLES))}


# ====================================================================
# units — Capa 3
# ====================================================================

@operation("units.convert", "Convierte un valor entre unidades con verificación dimensional (incluye degC/degF).",
           {"value": "Valor", "from": "Unidad de origen", "to": "Unidad de destino"},
           {"value": 1, "from": "kN*m", "to": "lbf*ft"})
def _h(p):
    return {"value": units.convert(_num(p, "value"), _str(p, "from"), _str(p, "to"))}


@operation("units.analyze", "Dimensión, factor al SI y unidad SI equivalente.", {"unit": "Expresión de unidades"},
           {"unit": "kW*h"})
def _h(p):
    return units.analyze(_str(p, "unit"))


@operation("units.parse_unit", "Factor al SI y exponentes dimensionales (L, M, T, I, Θ, N, J).",
           {"unit": "Expresión de unidades"}, {"unit": "N/mm^2"})
def _h(p):
    factor, dim = units.parse_unit(_str(p, "unit"))
    return {"factor_to_si": factor, "dimension": list(dim)}


@operation("units.check_consistency", "Verifica que los términos de una suma tengan la misma dimensión.",
           {"terms": "Lista de unidades, una por término"}, {"terms": ["m/s", "km/h", "kn"]})
def _h(p):
    return units.check_consistency(_strs(p, "terms"))


@operation("units.catalog", "Unidades y prefijos disponibles.", {}, {})
def _h(p):
    return {
        "units": {k: {"factor_to_si": f, "dimension": units.format_dimension(d), "prefixable": pre}
                  for k, (f, d, pre) in units.UNITS.items()},
        "prefixes": units.PREFIXES,
        "temperature_scales": sorted(units.OFFSET_UNITS),
    }


del _h
