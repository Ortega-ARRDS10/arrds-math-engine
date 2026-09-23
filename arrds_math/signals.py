"""Análisis en el plano complejo y señales (Matemática D).

* Transformada discreta de Fourier (FFT radix-2 con respaldo DFT).
* Funciones de transferencia H(s) = N(s)/D(s): polos, ceros, estabilidad
  y respuesta en frecuencia (diagrama de Bode).

Los polinomios usan la convención descendente de :mod:`arrds_math.poly`.
"""

import cmath
import math

from .errors import InvalidInputError
from .poly import _coeffs, polyval, roots


def _is_pow2(n):
    return n > 0 and n & (n - 1) == 0


def _fft(x, inverse):
    n = len(x)
    if n == 1:
        return list(x)
    even = _fft(x[0::2], inverse)
    odd = _fft(x[1::2], inverse)
    sign = 1 if inverse else -1
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(sign * 2j * math.pi * k / n) * odd[k]
        out[k] = even[k] + t
        out[k + n // 2] = even[k] - t
    return out


def _dft(x, inverse):
    n = len(x)
    sign = 1 if inverse else -1
    return [sum(x[t] * cmath.exp(sign * 2j * math.pi * k * t / n) for t in range(n)) for k in range(n)]


def fft(x, inverse=False):
    """DFT de una secuencia (real o compleja). ``inverse=True`` incluye el factor 1/N."""
    if not isinstance(x, (list, tuple)) or not x:
        raise InvalidInputError("La señal debe ser una lista no vacía")
    if len(x) > 1 << 16:
        raise InvalidInputError("Señal demasiado larga para la v0.1 (máx. 65536 muestras)")
    data = [complex(v) for v in x]
    out = _fft(data, inverse) if _is_pow2(len(data)) else _dft(data, inverse)
    if inverse:
        out = [v / len(data) for v in out]
    return out


def spectrum(x, sample_rate=1.0):
    """Espectro de amplitud de una señal real (lado único).

    Devuelve frecuencias [Hz] y amplitudes normalizadas: una senoidal de
    amplitud A en una frecuencia de bin exacta aparece con amplitud A.
    """
    n = len(x)
    coeffs = fft(x)
    half = n // 2 + 1
    freqs = [k * sample_rate / n for k in range(half)]
    amps = []
    for k in range(half):
        a = abs(coeffs[k]) / n
        if 0 < k < n / 2:
            a *= 2
        amps.append(a)
    return {"frequency": freqs, "amplitude": amps}


def transfer_function(num, den):
    """Analiza H(s) = num(s)/den(s): polos, ceros, ganancia DC y estabilidad."""
    num, den = _coeffs(num), _coeffs(den)
    if all(c == 0 for c in den):
        raise InvalidInputError("El denominador no puede ser nulo")
    poles = roots(den) if len(den) > 1 else []
    zeros = roots(num) if len(num) > 1 else []
    d0 = polyval(den, 0)
    dc_gain = polyval(num, 0) / d0 if d0 != 0 else math.inf
    max_re = max((p.real for p in poles), default=-math.inf)
    if max_re < -1e-12:
        stability = "estable"
    elif max_re <= 1e-12:
        stability = "marginalmente estable"
    else:
        stability = "inestable"
    return {
        "poles": poles,
        "zeros": zeros,
        "dc_gain": dc_gain,
        "stability": stability,
        "order": len(den) - 1,
        "proper": len(num) <= len(den),
    }


def logspace(start_exp, stop_exp, n):
    if n < 2:
        raise InvalidInputError("Se necesitan al menos 2 puntos")
    return [10 ** (start_exp + (stop_exp - start_exp) * i / (n - 1)) for i in range(n)]


def freq_response(num, den, w=None, w_min=1e-2, w_max=1e2, n=200):
    """Respuesta en frecuencia H(jω): magnitud [dB] y fase [grados] (desenvuelta)."""
    num, den = _coeffs(num), _coeffs(den)
    if w is None:
        if w_min <= 0 or w_max <= w_min:
            raise InvalidInputError("Se requiere 0 < w_min < w_max")
        w = logspace(math.log10(w_min), math.log10(w_max), int(n))
    mags, phases = [], []
    prev = None
    offset = 0.0
    for wi in w:
        d = polyval(den, 1j * wi)
        if d == 0:
            raise InvalidInputError(f"H(jω) tiene un polo sobre el eje imaginario en ω = {wi:g}")
        h = polyval(num, 1j * wi) / d
        mags.append(20 * math.log10(abs(h)) if h != 0 else -math.inf)
        ph = math.degrees(cmath.phase(h))
        if prev is not None:
            # Desenvolver la fase para evitar saltos de ±360°.
            while ph + offset - prev > 180:
                offset -= 360
            while ph + offset - prev < -180:
                offset += 360
        prev = ph + offset
        phases.append(prev)
    return {"w": list(w), "magnitude_db": mags, "phase_deg": phases}
