"""Expresiones: parser, evaluación y álgebra simbólica (Capa 1)."""

from .evaluator import CONSTANTS, FUNCTIONS, Evaluator, compile_function, evaluate
from .nodes import Binary, Call, Num, Unary, Var, free_variables, to_string
from .parser import parse, tokenize
from .symbolic import derivative, diff, gradient, simplify, to_latex

__all__ = [
    "CONSTANTS", "FUNCTIONS", "Evaluator", "compile_function", "evaluate",
    "Binary", "Call", "Num", "Unary", "Var", "free_variables", "to_string",
    "parse", "tokenize", "derivative", "diff", "gradient", "simplify", "to_latex",
]
