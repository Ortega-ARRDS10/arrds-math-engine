"""Polinomios.

Convención: coeficientes en orden **descendente** (como MATLAB/NumPy):
``[1, -3, 2]`` representa x² − 3x + 2.
"""

import cmath
import math

from .errors import ConvergenceError, InvalidInputError


def _coeffs(p):
    if not isinstance(p, (list, tuple)) or not p:
        raise InvalidInputError("El polinomio debe ser una lista no vacía de coeficientes")
    out = list(p)
    while len(out) > 1 and out[0] == 0:
        out.pop(0)
    return out


def polyval(p, x):
    """Evalúa por el esquema de Horner (acepta x complejo)."""
    acc = 0
    for c in _coeffs(p):
        acc = acc * x + c
    return acc


def polyder(p):
    p = _coeffs(p)
    n = len(p) - 1
    return [c * (n - i) for i, c in enumerate(p[:-1])] or [0.0]


def polyint(p, k=0.0):
    p = _coeffs(p)
    n = len(p)
    return [c / (n - i) for i, c in enumerate(p)] + [k]


def polymul(p, q):
    p, q = _coeffs(p), _coeffs(q)
    out = [0.0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


def polyadd(p, q):
    p, q = _coeffs(p), _coeffs(q)
    n = max(len(p), len(q))
    p = [0.0] * (n - len(p)) + p
    q = [0.0] * (n - len(q)) + q
    return _coeffs([a + b for a, b in zip(p, q)])


def roots(p, tol=1e-14, max_iter=2000):
    """Todas las raíces (complejas) por Durand–Kerner + pulido con Newton.

    Devuelve una lista de complejos; las raíces reales tienen parte
    imaginaria exactamente 0.
    """
    p = _coeffs(p)
    # Raíces nulas: se factorizan exactamente para no perder precisión.
    zeros = 0
    while len(p) > 1 and p[-1] == 0:
        p.pop()
        zeros += 1
    n = len(p) - 1
    if n == 0:
        return [0j] * zeros
    lead = p[0]
    monic = [c / lead for c in p]
    # Cota de Cauchy para escalar el punto de arranque.
    radius = 1 + max(abs(c) for c in monic[1:])
    z = [radius * cmath.exp(1j * (2 * math.pi * k / n + 0.4)) for k in range(n)]
    for _ in range(max_iter):
        delta = 0.0
        for i in range(n):
            denom = 1
            for j in range(n):
                if i != j:
                    denom *= z[i] - z[j]
            if denom == 0:
                denom = 1e-300
            step = polyval(monic, z[i]) / denom
            z[i] -= step
            delta = max(delta, abs(step))
        if delta <= tol * radius:
            break
    else:
        raise ConvergenceError("Durand–Kerner no convergió")
    dp = polyder(monic)
    polished = []
    for r in z:
        for _ in range(3):
            d = polyval(dp, r)
            if d == 0:
                break
            r -= polyval(monic, r) / d
        if abs(r.imag) <= 1e-10 * max(1.0, abs(r)):
            r = complex(r.real, 0.0)
        polished.append(r)
    polished.sort(key=lambda c: (round(c.real, 12), c.imag))
    return polished + [0j] * zeros


def polyfit(x, y, degree):
    """Ajuste por mínimos cuadrados de grado ``degree`` (vía QR, no ecuaciones normales).

    Devuelve dict con ``coefficients`` (descendentes) y ``r2``.
    """
    from .linalg import lstsq

    if len(x) != len(y):
        raise InvalidInputError("x e y deben tener la misma longitud")
    if not isinstance(degree, int) or degree < 0:
        raise InvalidInputError("El grado debe ser un entero ≥ 0")
    if len(x) <= degree:
        raise InvalidInputError(f"Se necesitan al menos {degree + 1} puntos para grado {degree}")
    a = [[float(xi) ** (degree - k) for k in range(degree + 1)] for xi in x]
    fit = lstsq(a, y)
    coeffs = fit["x"]
    mean = math.fsum(y) / len(y)
    ss_tot = math.fsum((yi - mean) ** 2 for yi in y)
    ss_res = math.fsum((yi - polyval(coeffs, xi)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"coefficients": coeffs, "r2": r2, "residual_norm": math.sqrt(ss_res)}
