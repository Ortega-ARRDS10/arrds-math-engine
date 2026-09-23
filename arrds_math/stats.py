"""Estadística descriptiva y regresión, orientada a análisis de mediciones."""

import math

from .errors import InvalidInputError


def _data(xs, min_len=1):
    if not isinstance(xs, (list, tuple)) or len(xs) < min_len:
        raise InvalidInputError(f"Se necesitan al menos {min_len} dato(s)")
    try:
        return [float(v) for v in xs]
    except (TypeError, ValueError) as exc:
        raise InvalidInputError("Los datos deben ser numéricos") from exc


def mean(xs):
    xs = _data(xs)
    return math.fsum(xs) / len(xs)


def variance(xs, ddof=1):
    """Varianza. ``ddof=1`` (muestral, por defecto) o ``ddof=0`` (poblacional)."""
    xs = _data(xs, ddof + 1)
    m = mean(xs)
    return math.fsum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def std(xs, ddof=1):
    return math.sqrt(variance(xs, ddof))


def median(xs):
    xs = sorted(_data(xs))
    n = len(xs)
    mid = n // 2
    return xs[mid] if n % 2 else 0.5 * (xs[mid - 1] + xs[mid])


def describe(xs):
    xs = _data(xs)
    n = len(xs)
    out = {"n": n, "mean": mean(xs), "median": median(xs), "min": min(xs), "max": max(xs)}
    if n > 1:
        s = std(xs)
        out["std"] = s
        out["sem"] = s / math.sqrt(n)  # error estándar de la media
    return out


def linregress(x, y):
    """Regresión lineal y = m·x + b con incertidumbres de pendiente y ordenada."""
    x, y = _data(x, 2), _data(y, 2)
    if len(x) != len(y):
        raise InvalidInputError("x e y deben tener la misma longitud")
    n = len(x)
    mx, my = mean(x), mean(y)
    sxx = math.fsum((a - mx) ** 2 for a in x)
    syy = math.fsum((b - my) ** 2 for b in y)
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx == 0:
        raise InvalidInputError("Todos los x son iguales: la pendiente no está definida")
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = math.fsum((b - (slope * a + intercept)) ** 2 for a, b in zip(x, y))
    r2 = 1 - ss_res / syy if syy > 0 else 1.0
    out = {"slope": slope, "intercept": intercept, "r2": r2, "r": math.copysign(math.sqrt(max(r2, 0)), slope)}
    if n > 2:
        s = math.sqrt(ss_res / (n - 2))
        out["slope_stderr"] = s / math.sqrt(sxx)
        out["intercept_stderr"] = s * math.sqrt(math.fsum(a * a for a in x) / (n * sxx))
    return out
