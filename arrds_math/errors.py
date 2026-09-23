"""Jerarquía de errores del motor.

Todo error que el motor lance de forma intencionada hereda de
``MathEngineError`` y lleva un ``code`` estable, pensado para que la API
y el panel de pruebas puedan clasificar fallos sin parsear mensajes.

Además, cada error puede llevar un ``hint``: la explicación pedagógica de
*por qué* falló el método y qué probar (principio "nunca un fallo
silencioso" de los documentos de contexto).
"""


class MathEngineError(Exception):
    """Error base del motor."""

    code = "ENGINE_ERROR"

    def __init__(self, message="", hint=None):
        super().__init__(message)
        self.hint = hint

    def to_dict(self):
        out = {"code": self.code, "message": str(self)}
        if self.hint:
            out["hint"] = self.hint
        return out


class ParseError(MathEngineError):
    """La expresión no es sintácticamente válida."""

    code = "PARSE_ERROR"

    def __init__(self, message, position=None, hint=None):
        if position is not None:
            message = f"{message} (posición {position})"
        super().__init__(message, hint)
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
