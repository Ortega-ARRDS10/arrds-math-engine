"""Polinomios.

Convención: coeficientes en orden **descendente** (como MATLAB/NumPy):
``[1, -3, 2]`` representa x² − 3x + 2.
"""

import cmath
import math

from .errors import ConvergenceError, InvalidInputError
from .numeric._common import IterativeResult


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

    Devuelve ``IterativeResult`` cuyo ``value`` es la lista de complejos (las
    raíces reales tienen parte imaginaria exactamente 0). El error estimado
    es el mayor paso de Newton del pulido final (≈ distancia a la raíz
    exacta para raíces simples; las múltiples convergen peor).
    """
    p = _coeffs(p)
    # Raíces nulas: se factorizan exactamente para no perder precisión.
    zeros = 0
    while len(p) > 1 and p[-1] == 0:
        p.pop()
        zeros += 1
    n = len(p) - 1
    if n == 0:
        return IterativeResult([0j] * zeros, True, 0, 0.0, "durand_kerner")
    lead = p[0]
    monic = [c / lead for c in p]
    # Cota de Cauchy para escalar el punto de arranque.
    radius = 1 + max(abs(c) for c in monic[1:])
    abs_coeffs = [abs(c) for c in monic]
    z = [radius * cmath.exp(1j * (2 * math.pi * k / n + 0.4)) for k in range(n)]
    for it in range(1, max_iter + 1):
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
        # Criterio de retroceso: si |p(z)| ya está al nivel del redondeo en
        # todas las aproximaciones, seguir iterando no mejora nada (típico de
        # raíces múltiples, que convergen solo linealmente).
        if all(abs(polyval(monic, zi)) <= 16 * 2.220446049250313e-16 * polyval(abs_coeffs, abs(zi))
               for zi in z):
            break
    else:
        raise ConvergenceError(
            "Durand–Kerner no convergió",
            hint="Suele pasar con raíces múltiples o coeficientes de escalas muy distintas. "
                 "Normalizá los coeficientes o factorizá las raíces conocidas.",
        )
    dp = polyder(monic)
    polished, errs = [], []
    for r in z:
        last = 0.0
        for _ in range(3):
            d = polyval(dp, r)
            if d == 0:
                break
            last = polyval(monic, r) / d
            r -= last
        polished.append(r)
        errs.append(max(abs(last), 2.220446049250313e-16 * max(1.0, abs(r))))
    # Raíces agrupadas (múltiples o casi múltiples): el paso de Newton
    # subestima el error, que escala como eps^(1/m). Se usa el diámetro del
    # grupo como estimación (conservadora).
    for i, r in enumerate(polished):
        for j, q in enumerate(polished):
            if i != j and abs(r - q) <= 1e-3 * max(1.0, abs(r)):
                errs[i] = max(errs[i], abs(r - q))
    # Parte imaginaria indistinguible de cero dentro del error -> raíz real.
    for i, r in enumerate(polished):
        if abs(r.imag) <= max(1e-10 * max(1.0, abs(r)), errs[i]):
            polished[i] = complex(r.real, 0.0)
    order = sorted(range(n), key=lambda k: (round(polished[k].real, 12), polished[k].imag))
    polished = [polished[k] for k in order]
    err = max(errs)
    return IterativeResult(polished + [0j] * zeros, True, it, err, "durand_kerner")


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
