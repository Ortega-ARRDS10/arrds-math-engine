"""Resolución numérica de sistemas de EDO de primer orden y' = f(t, y).

Una EDO de orden superior se reescribe como sistema: para
x'' + 2ζω x' + ω² x = 0 se usa y1 = x, y2 = x'.
"""

import math

from ..errors import ConvergenceError, InvalidInputError
from ._common import IterativeResult, check_tol

MAX_STEPS = 200_000

_HINT_STIFF = (
    "Un método explícito necesita pasos diminutos cuando el sistema es rígido (escalas de "
    "tiempo muy distintas) o la solución explota en tiempo finito. Revisá el modelo o "
    "acortá el intervalo; los métodos implícitos (BDF) están en el roadmap v0.2."
)


def _as_system(f, n):
    """Normaliza f para que siempre devuelva una lista de floats de longitud n."""

    def wrapped(t, y):
        out = f(t, y)
        if isinstance(out, (int, float)):
            out = [out]
        out = [float(v) for v in out]
        if len(out) != n:
            raise InvalidInputError(f"f(t, y) devolvió {len(out)} componentes; se esperaban {n}")
        for v in out:
            if not math.isfinite(v):
                raise ConvergenceError(f"La solución diverge (valor no finito en t = {t:g})")
        return out

    return wrapped


def _axpy(y, h, *pairs):
    """y + h·Σ cᵢ·kᵢ, componente a componente."""
    out = list(y)
    for c, k in pairs:
        if c:
            for i in range(len(out)):
                out[i] += h * c * k[i]
    return out


def _rk4_run(f, t0, y, h, steps):
    t = float(t0)
    ts, ys = [t], [list(y)]
    for i in range(steps):
        k1 = f(t, y)
        k2 = f(t + h / 2, _axpy(y, h, (0.5, k1)))
        k3 = f(t + h / 2, _axpy(y, h, (0.5, k2)))
        k4 = f(t + h, _axpy(y, h, (1.0, k3)))
        y = _axpy(y, h, (1 / 6, k1), (1 / 3, k2), (1 / 3, k3), (1 / 6, k4))
        t = t0 + (i + 1) * h
        ts.append(t)
        ys.append(y)
    return ts, ys


def rk4(f, t0, y0, t1, steps=1000):
    """Runge–Kutta clásico de 4.º orden con paso fijo.

    El error se estima por duplicación de paso (Richardson): se repite la
    integración con la mitad de pasos y se compara el estado final,
    err ≈ |y_h − y_H| / (r⁴ − 1) con r = H/h.
    """
    y0 = [float(v) for v in (y0 if isinstance(y0, (list, tuple)) else [y0])]
    if steps < 1 or steps > MAX_STEPS:
        raise InvalidInputError(f"steps debe estar entre 1 y {MAX_STEPS}")
    f = _as_system(f, len(y0))
    t0, t1 = float(t0), float(t1)
    ts, ys = _rk4_run(f, t0, y0, (t1 - t0) / steps, steps)
    err = math.nan
    coarse = steps // 2
    if coarse >= 1:
        _, yc = _rk4_run(f, t0, y0, (t1 - t0) / coarse, coarse)
        r = steps / coarse
        err = max(abs(a - b) for a, b in zip(ys[-1], yc[-1])) / (r ** 4 - 1)
    return IterativeResult(
        {"t": ts, "y": ys}, True, steps, err, "rk4",
        {"steps": steps, "rejected": 0, "error_kind": "richardson_final_state"},
    )


# Tablero de Butcher de Dormand–Prince 5(4)
_C = (0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1)
_A = (
    (),
    (1 / 5,),
    (3 / 40, 9 / 40),
    (44 / 45, -56 / 15, 32 / 9),
    (19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729),
    (9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656),
    (35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84),
)
_B5 = (35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0)
_B4 = (5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40)


def rk45(f, t0, y0, t1, rtol=1e-8, atol=1e-10, h0=None, max_steps=MAX_STEPS):
    """Dormand–Prince 5(4) con control de paso adaptativo (como ode45 de MATLAB)."""
    rtol, atol = check_tol(rtol), check_tol(atol)
    y0 = [float(v) for v in (y0 if isinstance(y0, (list, tuple)) else [y0])]
    n = len(y0)
    f = _as_system(f, n)
    t, y = float(t0), y0
    t1 = float(t1)
    direction = 1.0 if t1 >= t else -1.0
    span = abs(t1 - t)
    if span == 0:
        return IterativeResult({"t": [t], "y": [list(y)]}, True, 0, 0.0, "rk45", {"steps": 0, "rejected": 0})
    h = abs(h0) if h0 else span / 100
    ts, ys = [t], [list(y)]
    k1 = f(t, y)
    accepted = rejected = 0
    global_err = 0.0  # suma de los errores locales estimados (cota heurística del global)
    while (t1 - t) * direction > 1e-14 * max(1.0, abs(t1)):
        if accepted + rejected > max_steps:
            raise ConvergenceError(f"rk45 superó {max_steps} pasos (¿sistema rígido?)", hint=_HINT_STIFF)
        h = min(h, abs(t1 - t))
        hs = h * direction
        ks = [k1]
        for s in range(1, 7):
            yi = _axpy(y, hs, *zip(_A[s], ks))
            ks.append(f(t + _C[s] * hs, yi))
        y5 = _axpy(y, hs, *zip(_B5, ks))
        err = local = 0.0
        for i in range(n):
            e_i = hs * sum((b5 - b4) * k[i] for b5, b4, k in zip(_B5, _B4, ks))
            scale = atol + rtol * max(abs(y[i]), abs(y5[i]))
            err = max(err, abs(e_i) / scale)
            local = max(local, abs(e_i))
        if err <= 1.0:
            global_err += local
            t += hs
            y = y5
            k1 = ks[6]  # FSAL: la última etapa es la primera del siguiente paso
            ts.append(t)
            ys.append(list(y))
            accepted += 1
        else:
            rejected += 1
        factor = 0.9 * err ** -0.2 if err > 0 else 5.0
        h *= min(5.0, max(0.2, factor))
        if h < 1e-14 * max(1.0, abs(t)):
            raise ConvergenceError(f"Paso demasiado pequeño en t = {t:g} (¿singularidad o rigidez?)", hint=_HINT_STIFF)
    return IterativeResult(
        {"t": ts, "y": ys}, True, accepted, global_err, "rk45",
        {"steps": accepted, "rejected": rejected, "error_kind": "sum_local_errors"},
    )


def solve_ivp(f, t0, y0, t1, method="rk45", **kwargs):
    methods = {"rk4": rk4, "rk45": rk45}
    if method not in methods:
        raise InvalidInputError(f"Método desconocido {method!r}; opciones: {', '.join(methods)}")
    return methods[method](f, t0, y0, t1, **kwargs)


def system_from_expressions(expressions, state_vars, time_var="t", complex_mode=False):
    """Construye f(t, y) a partir de expresiones en texto.

    >>> f = system_from_expressions(["y2", "-y1"], ["y1", "y2"])
    """
    from ..expr import compile_function

    if isinstance(expressions, str):
        expressions = [expressions]
    if len(expressions) != len(state_vars):
        raise InvalidInputError("Debe haber una expresión por cada variable de estado")
    names = [time_var] + list(state_vars)
    fns = [compile_function(e, names, complex_mode) for e in expressions]
    return lambda t, y: [fn(t, *y) for fn in fns]
