"""Búsqueda de raíces de funciones escalares f(x) = 0."""

import math

from ..errors import ConvergenceError, DomainError, InvalidInputError
from ._common import IterativeResult, as_callable, check_finite, check_tol


def _eval(f, x):
    return check_finite(f(x), f"f({x:g})")


def bisection(f, a, b, tol=1e-12, max_iter=200):
    """Bisección. Robusta y lenta; exige cambio de signo en [a, b]."""
    f = as_callable(f)
    tol = check_tol(tol)
    a, b = float(a), float(b)
    fa, fb = _eval(f, a), _eval(f, b)
    if fa == 0:
        return IterativeResult(a, True, 0, 0.0, "bisection")
    if fb == 0:
        return IterativeResult(b, True, 0, 0.0, "bisection")
    if fa * fb > 0:
        raise DomainError("f(a) y f(b) deben tener signos opuestos")
    for i in range(1, max_iter + 1):
        m = 0.5 * (a + b)
        fm = _eval(f, m)
        if fm == 0 or 0.5 * (b - a) < tol:
            return IterativeResult(m, True, i, 0.5 * abs(b - a), "bisection", {"residual": abs(fm)})
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    raise ConvergenceError(f"Bisección no convergió en {max_iter} iteraciones")


def newton(f, x0, df=None, tol=1e-12, max_iter=100):
    """Newton-Raphson. Si no se da ``df`` y ``f`` es texto, se deriva simbólicamente."""
    if df is None:
        if isinstance(f, str):
            from ..expr import compile_function, derivative

            df = compile_function(derivative(f, "x"), ["x"])
        else:
            from .calculus import derivative as num_derivative

            fc = f
            df = lambda x: num_derivative(fc, x).value  # noqa: E731
    f = as_callable(f)
    df = as_callable(df)
    tol = check_tol(tol)
    x = float(x0)
    for i in range(1, max_iter + 1):
        fx = _eval(f, x)
        dfx = _eval(df, x)
        if dfx == 0:
            raise ConvergenceError(f"Derivada nula en x = {x:g}; Newton no puede continuar")
        step = fx / dfx
        x -= step
        if abs(step) <= tol * max(1.0, abs(x)):
            return IterativeResult(x, True, i, abs(step), "newton", {"residual": abs(_eval(f, x))})
    raise ConvergenceError(f"Newton no convergió en {max_iter} iteraciones (último x = {x:g})")


def secant(f, x0, x1, tol=1e-12, max_iter=100):
    """Secante: como Newton pero sin derivada."""
    f = as_callable(f)
    tol = check_tol(tol)
    x0, x1 = float(x0), float(x1)
    f0, f1 = _eval(f, x0), _eval(f, x1)
    for i in range(1, max_iter + 1):
        if f1 == f0:
            if f1 == 0:
                return IterativeResult(x1, True, i, 0.0, "secant", {"residual": 0.0})
            raise ConvergenceError("Pendiente de la secante nula")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) <= tol * max(1.0, abs(x2)):
            return IterativeResult(x2, True, i, abs(x2 - x1), "secant", {"residual": abs(_eval(f, x2))})
        x0, f0, x1, f1 = x1, f1, x2, _eval(f, x2)
    raise ConvergenceError(f"Secante no convergió en {max_iter} iteraciones")


def brent(f, a, b, tol=1e-12, max_iter=200):
    """Método de Brent (Brent–Dekker): garantía de la bisección, velocidad superlineal.

    Es el método por defecto recomendado cuando se conoce un intervalo con
    cambio de signo.
    """
    f = as_callable(f)
    tol = check_tol(tol)
    a, b = float(a), float(b)
    fa, fb = _eval(f, a), _eval(f, b)
    if fa * fb > 0:
        raise DomainError("f(a) y f(b) deben tener signos opuestos")
    if abs(fa) < abs(fb):
        a, b, fa, fb = b, a, fb, fa
    c, fc = a, fa
    d = e = b - a
    for i in range(1, max_iter + 1):
        if fb == 0:
            return IterativeResult(b, True, i, 0.0, "brent", {"residual": 0.0})
        if fa * fb > 0:
            a, fa = c, fc
            d = e = b - a
        if abs(fa) < abs(fb):
            c, fc = b, fb
            b, fb = a, fa
            a, fa = c, fc
        tol1 = 2 * 2.220446049250313e-16 * abs(b) + 0.5 * tol
        xm = 0.5 * (a - b)
        if abs(xm) <= tol1:
            return IterativeResult(b, True, i, abs(xm), "brent", {"residual": abs(fb)})
        if abs(e) >= tol1 and abs(fc) > abs(fb):
            s = fb / fc
            if a == c:
                p, q = 2 * xm * s, 1 - s  # secante
            else:
                q, r = fc / fa, fb / fa  # interpolación cuadrática inversa
                p = s * (2 * xm * q * (q - r) - (b - c) * (r - 1))
                q = (q - 1) * (r - 1) * (s - 1)
            if p > 0:
                q = -q
            p = abs(p)
            if 2 * p < min(3 * xm * q - abs(tol1 * q), abs(e * q)):
                e, d = d, p / q
            else:
                d = e = xm
        else:
            d = e = xm
        c, fc = b, fb
        b += d if abs(d) > tol1 else math.copysign(tol1, xm)
        fb = _eval(f, b)
    raise ConvergenceError(f"Brent no convergió en {max_iter} iteraciones")


METHODS = {"bisection": bisection, "newton": newton, "secant": secant, "brent": brent}


def find_root(f, method="brent", **kwargs):
    if method not in METHODS:
        raise InvalidInputError(f"Método desconocido {method!r}; opciones: {', '.join(METHODS)}")
    return METHODS[method](f, **kwargs)
