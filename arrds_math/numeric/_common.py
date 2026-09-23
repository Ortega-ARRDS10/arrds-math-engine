"""Utilidades compartidas por los métodos numéricos."""

import math
from dataclasses import asdict, dataclass, field

from ..errors import DomainError, InvalidInputError


@dataclass
class IterativeResult:
    """Resultado estándar de todo método iterativo.

    Siempre se reporta si convergió, cuántas iteraciones usó y una
    estimación del error: en ingeniería un número sin su error estimado
    no es un resultado.
    """

    value: object
    converged: bool
    iterations: int
    error_estimate: float
    method: str
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def as_callable(f, var="x"):
    """Acepta una función de Python o una expresión en texto de una variable."""
    if callable(f):
        return f
    if isinstance(f, str):
        from ..expr import compile_function

        return compile_function(f, [var])
    raise InvalidInputError("Se esperaba una función o una expresión en texto")


def check_finite(value, what):
    if isinstance(value, complex) or not math.isfinite(value):
        raise DomainError(f"{what} no es un número real finito ({value})")
    return value


def check_tol(tol):
    if not (isinstance(tol, (int, float)) and tol > 0):
        raise InvalidInputError("La tolerancia debe ser un número positivo")
    return float(tol)
