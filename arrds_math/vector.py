"""Análisis vectorial (Matemática C): gradiente, divergencia, rotor, laplaciano.

Todas las operaciones son **simbólicas** (exactas) sobre expresiones en
texto, y opcionalmente se evalúan en un punto. Así el resultado sirve tanto
para mostrar la fórmula (LaTeX) como para simular.
"""

from .errors import DimensionError, InvalidInputError
from .expr import compile_function, parse, simplify, to_latex, to_string
from .expr.symbolic import add, diff, sub


def _fields(components, variables):
    if isinstance(components, str):
        components = [components]
    if not variables:
        raise InvalidInputError("Se requiere la lista de variables de coordenadas")
    return [parse(c) if isinstance(c, str) else c for c in components]


def _package(nodes, variables, point):
    out = {
        "expressions": [to_string(n) for n in nodes],
        "latex": [to_latex(n) for n in nodes],
    }
    if point is not None:
        if len(point) != len(variables):
            raise DimensionError(f"El punto tiene {len(point)} coordenadas; se esperaban {len(variables)}")
        out["value"] = [compile_function(n, variables)(*point) for n in nodes]
    return out


def gradient(scalar, variables, point=None):
    """∇f = (∂f/∂x₁, …, ∂f/∂xₙ)."""
    (f,) = _fields(scalar, variables)
    return _package([simplify(diff(f, v)) for v in variables], variables, point)


def divergence(field, variables, point=None):
    """∇·F = Σ ∂Fᵢ/∂xᵢ."""
    comps = _fields(field, variables)
    if len(comps) != len(variables):
        raise DimensionError("El campo debe tener tantas componentes como variables")
    total = None
    for c, v in zip(comps, variables):
        d = diff(c, v)
        total = d if total is None else add(total, d)
    return _package([simplify(total)], variables, point)


def curl(field, variables, point=None):
    """∇×F para campos en R³ (variables x, y, z en ese orden)."""
    comps = _fields(field, variables)
    if len(comps) != 3 or len(variables) != 3:
        raise DimensionError("El rotor está definido para campos de 3 componentes en R³")
    (p, q, r), (x, y, z) = comps, variables
    nodes = [
        simplify(sub(diff(r, y), diff(q, z))),
        simplify(sub(diff(p, z), diff(r, x))),
        simplify(sub(diff(q, x), diff(p, y))),
    ]
    return _package(nodes, variables, point)


def laplacian(scalar, variables, point=None):
    """∇²f = Σ ∂²f/∂xᵢ²."""
    (f,) = _fields(scalar, variables)
    total = None
    for v in variables:
        d2 = diff(simplify(diff(f, v)), v)
        total = d2 if total is None else add(total, d2)
    return _package([simplify(total)], variables, point)


def jacobian(field, variables, point=None):
    """Matriz jacobiana J[i][j] = ∂Fᵢ/∂xⱼ."""
    comps = _fields(field, variables)
    rows = [[simplify(diff(c, v)) for v in variables] for c in comps]
    out = {
        "expressions": [[to_string(n) for n in row] for row in rows],
        "latex": [[to_latex(n) for n in row] for row in rows],
    }
    if point is not None:
        if len(point) != len(variables):
            raise DimensionError(f"El punto tiene {len(point)} coordenadas; se esperaban {len(variables)}")
        out["value"] = [[compile_function(n, variables)(*point) for n in row] for row in rows]
    return out
