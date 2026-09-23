"""Jerarquía de errores del motor.

Todo error que el motor lance de forma intencionada hereda de
``MathEngineError`` y lleva un ``code`` estable, pensado para que la API
y el panel de pruebas puedan clasificar fallos sin parsear mensajes.
"""


class MathEngineError(Exception):
    """Error base del motor."""

    code = "ENGINE_ERROR"


class ParseError(MathEngineError):
    """La expresión no es sintácticamente válida."""

    code = "PARSE_ERROR"

    def __init__(self, message, position=None):
        if position is not None:
            message = f"{message} (posición {position})"
        super().__init__(message)
        self.position = position


class EvaluationError(MathEngineError):
    """Fallo al evaluar: variable indefinida, función desconocida, aridad..."""

    code = "EVALUATION_ERROR"


class DomainError(MathEngineError):
    """Argumento fuera del dominio matemático (ln(-1) en modo real, 1/0...)."""

    code = "DOMAIN_ERROR"


class ConvergenceError(MathEngineError):
    """Un método iterativo no alcanzó la tolerancia pedida."""

    code = "CONVERGENCE_ERROR"


class DimensionError(MathEngineError):
    """Dimensiones incompatibles en operaciones con vectores o matrices."""

    code = "DIMENSION_ERROR"


class SingularMatrixError(MathEngineError):
    """La matriz es singular (o numéricamente singular)."""

    code = "SINGULAR_MATRIX"


class InvalidInputError(MathEngineError):
    """Parámetros de entrada inválidos (tipo, rango, forma)."""

    code = "INVALID_INPUT"
