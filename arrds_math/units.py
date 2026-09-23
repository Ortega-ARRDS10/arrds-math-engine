"""Capa 3 — Contexto físico: unidades y análisis dimensional.

Una dimensión es un vector de 7 exponentes sobre las magnitudes base del SI:
(longitud L, masa M, tiempo T, corriente I, temperatura Θ, cantidad N,
intensidad luminosa J).

Las expresiones de unidades reutilizan el parser del motor, por lo que
``"kN*m"``, ``"m/s^2"`` o ``"kg*m^2/s^2"`` son válidas.
"""

import math

from .errors import DimensionError, InvalidInputError, ParseError
from .expr.nodes import Binary, Num, Unary, Var
from .expr.parser import parse

BASE_NAMES = ("m", "kg", "s", "A", "K", "mol", "cd")
DIM_SYMBOLS = ("L", "M", "T", "I", "Θ", "N", "J")


def _dim(**exps):
    order = ("L", "M", "T", "I", "Th", "N", "J")
    return tuple(exps.get(k, 0) for k in order)


DIMENSIONLESS = _dim()

# nombre -> (factor al SI, dimensión, admite prefijos)
UNITS = {
    # Base SI (el kilogramo se define vía el gramo para admitir prefijos)
    "m": (1.0, _dim(L=1), True),
    "g": (1e-3, _dim(M=1), True),
    "s": (1.0, _dim(T=1), True),
    "A": (1.0, _dim(I=1), True),
    "K": (1.0, _dim(Th=1), True),
    "mol": (1.0, _dim(N=1), True),
    "cd": (1.0, _dim(J=1), True),
    # Derivadas SI
    "N": (1.0, _dim(L=1, M=1, T=-2), True),
    "Pa": (1.0, _dim(L=-1, M=1, T=-2), True),
    "J": (1.0, _dim(L=2, M=1, T=-2), True),
    "W": (1.0, _dim(L=2, M=1, T=-3), True),
    "C": (1.0, _dim(T=1, I=1), True),
    "V": (1.0, _dim(L=2, M=1, T=-3, I=-1), True),
    "ohm": (1.0, _dim(L=2, M=1, T=-3, I=-2), True),
    "S": (1.0, _dim(L=-2, M=-1, T=3, I=2), True),
    "F": (1.0, _dim(L=-2, M=-1, T=4, I=2), True),
    "H": (1.0, _dim(L=2, M=1, T=-2, I=-2), True),
    "T": (1.0, _dim(M=1, T=-2, I=-1), True),
    "Wb": (1.0, _dim(L=2, M=1, T=-2, I=-1), True),
    "Hz": (1.0, _dim(T=-1), True),
    "rad": (1.0, DIMENSIONLESS, False),
    "sr": (1.0, DIMENSIONLESS, False),
    # Aceptadas / prácticas
    "L": (1e-3, _dim(L=3), True),
    "min": (60.0, _dim(T=1), False),
    "h": (3600.0, _dim(T=1), False),
    "day": (86400.0, _dim(T=1), False),
    "deg": (math.pi / 180, DIMENSIONLESS, False),
    "rpm": (2 * math.pi / 60, _dim(T=-1), False),
    "bar": (1e5, _dim(L=-1, M=1, T=-2), True),
    "atm": (101325.0, _dim(L=-1, M=1, T=-2), False),
    "t": (1000.0, _dim(M=1), False),
    "eV": (1.602176634e-19, _dim(L=2, M=1, T=-2), True),
    "cal": (4.184, _dim(L=2, M=1, T=-2), True),
    "Wh": (3600.0, _dim(L=2, M=1, T=-2), True),
    # Imperiales
    "in": (0.0254, _dim(L=1), False),
    "ft": (0.3048, _dim(L=1), False),
    "yd": (0.9144, _dim(L=1), False),
    "mi": (1609.344, _dim(L=1), False),
    "nmi": (1852.0, _dim(L=1), False),
    "lb": (0.45359237, _dim(M=1), False),
    "slug": (14.593902937206364, _dim(M=1), False),
    "lbf": (4.4482216152605, _dim(L=1, M=1, T=-2), False),
    "psi": (6894.757293168361, _dim(L=-1, M=1, T=-2), True),
    "BTU": (1055.05585262, _dim(L=2, M=1, T=-2), False),
    "hp": (745.6998715822702, _dim(L=2, M=1, T=-3), False),
    "kn": (1852.0 / 3600.0, _dim(L=1, T=-1), False),
    "gal": (3.785411784e-3, _dim(L=3), False),
}

PREFIXES = {
    "Y": 1e24, "Z": 1e21, "E": 1e18, "P": 1e15, "T": 1e12, "G": 1e9, "M": 1e6, "k": 1e3,
    "h": 1e2, "da": 1e1, "d": 1e-1, "c": 1e-2, "m": 1e-3, "u": 1e-6, "µ": 1e-6,
    "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18,
}

# Escalas con desplazamiento: solo válidas para conversión directa de temperatura.
OFFSET_UNITS = {
    "degC": (1.0, 273.15),
    "degF": (5 / 9, 459.67 * 5 / 9),
    "K": (1.0, 0.0),
    "degR": (5 / 9, 0.0),
}


def lookup(symbol):
    """Resuelve un símbolo (con prefijo opcional) a (factor, dimensión)."""
    if symbol in UNITS:
        factor, dim, _ = UNITS[symbol]
        return factor, dim
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if symbol.startswith(prefix):
            base = symbol[len(prefix):]
            if base in UNITS and UNITS[base][2]:
                factor, dim, _ = UNITS[base]
                return PREFIXES[prefix] * factor, dim
    raise InvalidInputError(f"Unidad desconocida: {symbol!r}")


def _combine(a, b, sign):
    return tuple(x + sign * y for x, y in zip(a, b))


def _eval_unit(node):
    if isinstance(node, Var):
        return lookup(node.name)
    if isinstance(node, Num):
        return node.value, DIMENSIONLESS
    if isinstance(node, Binary):
        if node.op in ("*", "/"):
            fa, da = _eval_unit(node.left)
            fb, db = _eval_unit(node.right)
            if node.op == "*":
                return fa * fb, _combine(da, db, 1)
            return fa / fb, _combine(da, db, -1)
        if node.op == "^":
            exp = _exponent(node.right)
            fa, da = _eval_unit(node.left)
            return fa ** exp, tuple(d * exp for d in da)
    raise InvalidInputError("Una expresión de unidades solo admite *, / y ^ con exponente numérico")


def _exponent(node):
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Unary) and node.op == "-" and isinstance(node.operand, Num):
        return -node.operand.value
    raise InvalidInputError("El exponente de una unidad debe ser un número")


def parse_unit(text):
    """Convierte ``"kN*m"`` en (factor al SI, dimensión)."""
    if not isinstance(text, str) or not text.strip():
        raise InvalidInputError("La unidad debe ser un texto no vacío")
    if text.strip() == "1":
        return 1.0, DIMENSIONLESS
    try:
        node = parse(text.replace("·", "*").replace("µ", "u"))
    except ParseError as exc:
        raise InvalidInputError(f"Unidad mal formada {text!r}: {exc}") from exc
    return _eval_unit(node)


def format_dimension(dim):
    parts = []
    for sym, e in zip(DIM_SYMBOLS, dim):
        if e:
            e = int(e) if float(e).is_integer() else e
            parts.append(sym if e == 1 else f"{sym}^{e}")
    return "·".join(parts) or "1"


def si_unit(dim):
    parts = []
    for name, e in zip(BASE_NAMES, dim):
        if e:
            e = int(e) if float(e).is_integer() else e
            parts.append(name if e == 1 else f"{name}^{e}")
    return "*".join(parts) or "1"


def convert(value, from_unit, to_unit):
    """Convierte ``value`` entre unidades con verificación dimensional."""
    value = float(value)
    if from_unit in ("degC", "degF", "degR") or to_unit in ("degC", "degF", "degR"):
        if from_unit not in OFFSET_UNITS or to_unit not in OFFSET_UNITS:
            raise DimensionError("degC/degF/degR solo se convierten entre escalas de temperatura")
        fs, fo = OFFSET_UNITS[from_unit]
        ts, to = OFFSET_UNITS[to_unit]
        return (value * fs + fo - to) / ts
    f_from, d_from = parse_unit(from_unit)
    f_to, d_to = parse_unit(to_unit)
    if d_from != d_to:
        raise DimensionError(
            f"Dimensiones incompatibles: {from_unit} [{format_dimension(d_from)}] "
            f"→ {to_unit} [{format_dimension(d_to)}]"
        )
    return value * f_from / f_to


def analyze(unit):
    """Describe una expresión de unidades: dimensión, factor y equivalente SI."""
    factor, dim = parse_unit(unit)
    return {
        "unit": unit,
        "factor_to_si": factor,
        "dimension": format_dimension(dim),
        "exponents": dict(zip(DIM_SYMBOLS, dim)),
        "si_unit": si_unit(dim),
    }


def check_consistency(terms):
    """Verifica que todas las unidades de una suma sean dimensionalmente compatibles.

    ``terms`` es una lista de unidades (una por término). Devuelve la
    dimensión común o lanza ``DimensionError`` indicando el término culpable.
    """
    if not terms:
        raise InvalidInputError("Se requiere al menos un término")
    _, ref = parse_unit(terms[0])
    for i, t in enumerate(terms[1:], start=2):
        _, d = parse_unit(t)
        if d != ref:
            raise DimensionError(
                f"Término {i} ({t}) tiene dimensión {format_dimension(d)}; "
                f"se esperaba {format_dimension(ref)}"
            )
    return {"consistent": True, "dimension": format_dimension(ref), "si_unit": si_unit(ref)}
