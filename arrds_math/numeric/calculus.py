"""Derivación e integración numéricas."""

import math

from ..errors import ConvergenceError, InvalidInputError
from ._common import IterativeResult, as_callable, check_finite, check_tol

MAX_EVALUATIONS = 1_000_000


# --- derivación -------------------------------------------------------

def derivative(f, x, order=1, h=None):
    """Derivada numérica por diferencias centradas + extrapolación de Richardson.

    Devuelve ``IterativeResult`` con la estimación de error de la última
    extrapolación. Orden 1 o 2.
    """
    f = as_callable(f)
    if order not in (1, 2):
        raise InvalidInputError("Solo se admite derivada numérica de orden 1 o 2")
    x = float(x)
    h = float(h) if h else (1e-2 if order == 1 else 5e-2) * max(1.0, abs(x))

    def central(step):
        if order == 1:
            return (f(x + step) - f(x - step)) / (2 * step)
        return (f(x + step) - 2 * f(x) + f(x - step)) / (step * step)

    # Tabla de Richardson: T[i][j], paso h/2^i, error O(h^(2j+2)).
    table = [[central(h)]]
    best, best_err = table[0][0], math.inf
    for i in range(1, 10):
        step = h / 2 ** i
        row = [central(step)]
        for j in range(1, i + 1):
            factor = 4 ** j
            row.append(row[j - 1] + (row[j - 1] - table[i - 1][j - 1]) / (factor - 1))
        err = abs(row[i] - table[i - 1][i - 1])
        if err < best_err:
            best, best_err = row[i], err
        elif err > 2 * best_err:
            break  # el redondeo empieza a dominar
        table.append(row)
    check_finite(best, "La derivada")
    return IterativeResult(best, True, len(table), best_err, "richardson")


# --- integración ------------------------------------------------------

def simpson_adaptive(f, a, b, tol=1e-10, max_depth=50):
    """Simpson adaptativo con corrección de Richardson."""
    f = as_callable(f)
    tol = check_tol(tol)
    a, b = float(a), float(b)
    if a == b:
        return IterativeResult(0.0, True, 0, 0.0, "simpson_adaptive")
    evals = [0]

    def fx(x):
        evals[0] += 1
        return check_finite(f(x), f"f({x:g})")

    def simpson(fa, fm, fb, a_, b_):
        return (b_ - a_) / 6 * (fa + 4 * fm + fb)

    def recurse(a_, b_, fa, fm, fb, whole, tol_, depth):
        m = 0.5 * (a_ + b_)
        lm, rm = 0.5 * (a_ + m), 0.5 * (m + b_)
        flm, frm = fx(lm), fx(rm)
        left = simpson(fa, flm, fm, a_, m)
        right = simpson(fm, frm, fb, m, b_)
        delta = left + right - whole
        if depth <= 0:
            raise ConvergenceError(
                "Simpson adaptativo alcanzó la profundidad máxima (¿singularidad?)",
                hint="El integrando no es suave en algún punto (singularidad, discontinuidad "
                     "o oscilación rápida). Partí el intervalo en ese punto o relajá tol.",
            )
        if evals[0] > MAX_EVALUATIONS:
            raise ConvergenceError(
                f"Simpson adaptativo superó {MAX_EVALUATIONS} evaluaciones",
                hint="La tolerancia pedida es demasiado exigente para este integrando; "
                     "relajá tol o probá gauss_legendre.",
            )
        if abs(delta) <= 15 * tol_:
            return left + right + delta / 15, abs(delta) / 15
        lv, le = recurse(a_, m, fa, flm, fm, left, tol_ / 2, depth - 1)
        rv, re_ = recurse(m, b_, fm, frm, fb, right, tol_ / 2, depth - 1)
        return lv + rv, le + re_

    fa, fb, fm = fx(a), fx(b), fx(0.5 * (a + b))
    value, err = recurse(a, b, fa, fm, fb, simpson(fa, fm, fb, a, b), tol, max_depth)
    return IterativeResult(value, True, evals[0], err, "simpson_adaptive", {"evaluations": evals[0]})


_GL_CACHE = {}


def gauss_legendre_nodes(n):
    """Nodos y pesos de Gauss–Legendre de n puntos (Newton sobre P_n)."""
    if not 1 <= n <= 200:
        raise InvalidInputError("n debe estar entre 1 y 200")
    if n in _GL_CACHE:
        return _GL_CACHE[n]
    nodes, weights = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))  # aproximación inicial
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-15:
                break
        nodes.append(x)
        weights.append(2 / ((1 - x * x) * dp * dp))
    _GL_CACHE[n] = (nodes, weights)
    return nodes, weights


def gauss_legendre(f, a, b, n=20):
    """Cuadratura de Gauss–Legendre de n puntos (exacta para polinomios de grado ≤ 2n−1).

    El error se estima comparando con la regla de n+10 puntos.
    """
    f = as_callable(f)
    a, b = float(a), float(b)

    def rule(m):
        xs, ws = gauss_legendre_nodes(m)
        half, mid = 0.5 * (b - a), 0.5 * (a + b)
        return half * sum(w * check_finite(f(mid + half * x), "f(x)") for x, w in zip(xs, ws))

    value = rule(n)
    err = abs(rule(min(n + 10, 200)) - value)
    return IterativeResult(value, True, n, err, "gauss_legendre")


def trapezoid(y, x=None, dx=1.0):
    """Regla del trapecio sobre datos muestreados (p. ej. mediciones)."""
    if len(y) < 2:
        raise InvalidInputError("Se necesitan al menos 2 muestras")
    if x is None:
        return sum(dx * (y[i] + y[i + 1]) / 2 for i in range(len(y) - 1))
    if len(x) != len(y):
        raise InvalidInputError("x e y deben tener la misma longitud")
    return sum((x[i + 1] - x[i]) * (y[i] + y[i + 1]) / 2 for i in range(len(y) - 1))


def integrate(f, a, b, method="simpson_adaptive", **kwargs):
    methods = {"simpson_adaptive": simpson_adaptive, "gauss_legendre": gauss_legendre}
    if method not in methods:
        raise InvalidInputError(f"Método desconocido {method!r}; opciones: {', '.join(methods)}")
    return methods[method](f, a, b, **kwargs)
