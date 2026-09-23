"""Capa 2 — Cálculo numérico: raíces, derivación, integración y EDO."""

from ._common import IterativeResult
from .calculus import derivative, gauss_legendre, integrate, simpson_adaptive, trapezoid
from .ode import rk4, rk45, solve_ivp, system_from_expressions
from .roots import bisection, brent, find_root, newton, secant

__all__ = [
    "IterativeResult", "derivative", "gauss_legendre", "integrate", "simpson_adaptive",
    "trapezoid", "rk4", "rk45", "solve_ivp", "system_from_expressions",
    "bisection", "brent", "find_root", "newton", "secant",
]
