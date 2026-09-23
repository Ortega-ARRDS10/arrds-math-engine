"""Álgebra lineal densa (Capa 2).

Representación: una matriz es ``list[list[float]]`` (por filas) y un vector
es ``list[float]``. Se prioriza la estabilidad numérica sobre la velocidad:
LU con pivoteo parcial, QR por Householder y Jacobi para simétricas.
"""

import math

from .errors import ConvergenceError, DimensionError, InvalidInputError, SingularMatrixError

EPS = 2.220446049250313e-16


# --- validación y utilidades -----------------------------------------

def as_matrix(a, name="A"):
    if not isinstance(a, (list, tuple)) or not a:
        raise InvalidInputError(f"{name} debe ser una lista no vacía de filas")
    if not all(isinstance(r, (list, tuple)) for r in a):
        raise InvalidInputError(f"{name} debe ser una lista de filas (lista de listas)")
    cols = len(a[0])
    if cols == 0 or any(len(r) != cols for r in a):
        raise DimensionError(f"{name}: todas las filas deben tener la misma longitud no nula")
    try:
        return [[float(v) for v in r] for r in a]
    except (TypeError, ValueError) as exc:
        raise InvalidInputError(f"{name} contiene valores no numéricos") from exc


def as_vector(v, name="b"):
    if not isinstance(v, (list, tuple)) or not v:
        raise InvalidInputError(f"{name} debe ser una lista no vacía")
    try:
        return [float(x) for x in v]
    except (TypeError, ValueError) as exc:
        raise InvalidInputError(f"{name} contiene valores no numéricos") from exc


def shape(a):
    return len(a), len(a[0])


def _require_square(a, what):
    n, m = shape(a)
    if n != m:
        raise DimensionError(f"{what} requiere una matriz cuadrada; recibió {n}×{m}")
    return n


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(col) for col in zip(*a)]


def matmul(a, b):
    a, b = as_matrix(a, "A"), as_matrix(b, "B")
    if shape(a)[1] != shape(b)[0]:
        raise DimensionError(f"No se pueden multiplicar {shape(a)} × {shape(b)}")
    bt = transpose(b)
    return [[math.fsum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def matvec(a, v):
    if len(a[0]) != len(v):
        raise DimensionError(f"No se puede multiplicar {shape(a)} por un vector de {len(v)}")
    return [math.fsum(x * y for x, y in zip(row, v)) for row in a]


def add(a, b):
    a, b = as_matrix(a, "A"), as_matrix(b, "B")
    if shape(a) != shape(b):
        raise DimensionError(f"No se pueden sumar {shape(a)} y {shape(b)}")
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(a, k):
    return [[k * x for x in r] for r in as_matrix(a)]


def dot(u, v):
    if len(u) != len(v):
        raise DimensionError("Los vectores deben tener la misma longitud")
    return math.fsum(x * y for x, y in zip(u, v))


def cross(u, v):
    if len(u) != 3 or len(v) != 3:
        raise DimensionError("El producto vectorial requiere vectores de 3 componentes")
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


def norm(x, ord=2):
    """Norma de vector (1, 2, inf) o de matriz (1, inf, 'fro', 2)."""
    if x and isinstance(x[0], (list, tuple)):
        a = as_matrix(x)
        if ord == 1:
            return max(math.fsum(abs(r[j]) for r in a) for j in range(len(a[0])))
        if ord in ("inf", math.inf):
            return max(math.fsum(abs(v) for v in r) for r in a)
        if ord == "fro":
            return math.sqrt(math.fsum(v * v for r in a for v in r))
        if ord == 2:
            ev = eig_symmetric(matmul(transpose(a), a)).value["values"]
            return math.sqrt(max(max(ev), 0.0))
        raise InvalidInputError(f"Norma matricial no soportada: {ord!r}")
    v = as_vector(x, "x")
    if ord == 1:
        return math.fsum(abs(t) for t in v)
    if ord in ("inf", math.inf):
        return max(abs(t) for t in v)
    if ord == 2:
        return math.hypot(*v)
    raise InvalidInputError(f"Norma vectorial no soportada: {ord!r}")


# --- factorizaciones --------------------------------------------------

def lu(a):
    """Factorización PA = LU con pivoteo parcial.

    Devuelve dict con ``P`` (permutación como lista de índices), ``L``, ``U``
    y ``sign`` (signo de la permutación, útil para el determinante).
    Lanza ``SingularMatrixError`` si un pivote es numéricamente nulo.
    """
    a = as_matrix(a)
    n = _require_square(a, "LU")
    u = [list(r) for r in a]
    l = identity(n)
    perm = list(range(n))
    sign = 1.0
    scale_ = max(abs(v) for r in a for v in r) or 1.0
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(u[i][k]))
        if abs(u[p][k]) <= n * EPS * scale_:
            raise SingularMatrixError(
                f"Matriz singular (pivote nulo en la columna {k})",
                hint="Alguna fila o columna es combinación lineal de otras: el sistema no "
                     "tiene solución única. Revisá las ecuaciones o usá lstsq.",
            )
        if p != k:
            u[k], u[p] = u[p], u[k]
            perm[k], perm[p] = perm[p], perm[k]
            for j in range(k):
                l[k][j], l[p][j] = l[p][j], l[k][j]
            sign = -sign
        for i in range(k + 1, n):
            factor = u[i][k] / u[k][k]
            l[i][k] = factor
            for j in range(k, n):
                u[i][j] -= factor * u[k][j]
            u[i][k] = 0.0
    return {"P": perm, "L": l, "U": u, "sign": sign}


def _lu_solve(fact, b):
    l, u, perm = fact["L"], fact["U"], fact["P"]
    n = len(l)
    y = [0.0] * n
    for i in range(n):
        y[i] = b[perm[i]] - math.fsum(l[i][j] * y[j] for j in range(i))
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - math.fsum(u[i][j] * x[j] for j in range(i + 1, n))) / u[i][i]
    return x


def solve(a, b, refine=True):
    """Resuelve Ax = b (A cuadrada) por LU, con un paso de refinamiento iterativo."""
    a = as_matrix(a)
    b = as_vector(b)
    n = _require_square(a, "solve")
    if len(b) != n:
        raise DimensionError(f"b tiene {len(b)} componentes; se esperaban {n}")
    fact = lu(a)
    x = _lu_solve(fact, b)
    if refine:
        r = [bi - ri for bi, ri in zip(b, matvec(a, x))]
        dx = _lu_solve(fact, r)
        x = [xi + di for xi, di in zip(x, dx)]
    return x


def det(a):
    a = as_matrix(a)
    _require_square(a, "det")
    try:
        fact = lu(a)
    except SingularMatrixError:
        return 0.0
    result = fact["sign"]
    for i, row in enumerate(fact["U"]):
        result *= row[i]
    return result


def inverse(a):
    a = as_matrix(a)
    n = _require_square(a, "inverse")
    fact = lu(a)
    cols = [_lu_solve(fact, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return transpose(cols)


def cond(a):
    """Número de condición en norma 1: ‖A‖₁·‖A⁻¹‖₁ (∞ si es singular)."""
    try:
        return norm(a, 1) * norm(inverse(a), 1)
    except SingularMatrixError:
        return math.inf


def qr(a):
    """Factorización A = QR por reflexiones de Householder (A de m×n, m ≥ n)."""
    a = as_matrix(a)
    m, n = shape(a)
    if m < n:
        raise DimensionError("QR requiere al menos tantas filas como columnas")
    r = [list(row) for row in a]
    q = identity(m)
    for k in range(min(m - 1, n)):
        x = [r[i][k] for i in range(k, m)]
        alpha = -math.copysign(math.hypot(*x), x[0]) if any(x) else 0.0
        v = list(x)
        v[0] -= alpha
        vnorm2 = math.fsum(t * t for t in v)
        if vnorm2 == 0:
            continue
        for j in range(n):
            s = 2 * math.fsum(v[i] * r[k + i][j] for i in range(len(v))) / vnorm2
            for i in range(len(v)):
                r[k + i][j] -= s * v[i]
        for j in range(m):
            s = 2 * math.fsum(v[i] * q[j][k + i] for i in range(len(v))) / vnorm2
            for i in range(len(v)):
                q[j][k + i] -= s * v[i]
    for i in range(m):
        for j in range(min(i, n)):
            r[i][j] = 0.0
    return {"Q": q, "R": r}


def lstsq(a, b):
    """Mínimos cuadrados: minimiza ‖Ax − b‖₂ vía QR (sin formar AᵀA)."""
    a = as_matrix(a)
    b = as_vector(b)
    m, n = shape(a)
    if len(b) != m:
        raise DimensionError(f"b tiene {len(b)} componentes; se esperaban {m}")
    f = qr(a)
    qtb = matvec(transpose(f["Q"]), b)
    r = f["R"]
    x = [0.0] * n
    rscale = max(abs(r[i][i]) for i in range(n)) or 1.0
    for i in reversed(range(n)):
        if abs(r[i][i]) <= max(m, n) * EPS * rscale:
            raise SingularMatrixError("Las columnas de A son linealmente dependientes")
        x[i] = (qtb[i] - math.fsum(r[i][j] * x[j] for j in range(i + 1, n))) / r[i][i]
    residual = math.hypot(*qtb[n:]) if m > n else 0.0
    return {"x": x, "residual_norm": residual}


def eig_symmetric(a, tol=1e-14, max_sweeps=100):
    """Autovalores y autovectores de una matriz simétrica (método de Jacobi cíclico).

    Devuelve ``IterativeResult`` cuyo ``value`` tiene los autovalores en orden
    ascendente y los autovectores como columnas. El error estimado es la
    norma de Frobenius de la parte fuera de la diagonal al terminar (cota
    de Gershgorin/Wielandt–Hoffman para el error de los autovalores).
    """
    from .numeric._common import IterativeResult

    a = as_matrix(a)
    n = _require_square(a, "eig_symmetric")
    scale_ = max(abs(v) for r in a for v in r) or 1.0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(a[i][j] - a[j][i]) > 1e-10 * scale_:
                raise InvalidInputError("eig_symmetric requiere una matriz simétrica")
    a = [list(r) for r in a]
    v = identity(n)
    for sweep in range(max_sweeps):
        off = math.fsum(a[i][j] ** 2 for i in range(n) for j in range(n) if i != j)
        if off <= (tol * scale_) ** 2:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(a[p][q]) < 1e-300:
                    continue
                theta = (a[q][q] - a[p][p]) / (2 * a[p][q])
                t = math.copysign(1.0, theta) / (abs(theta) + math.sqrt(theta * theta + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(n):
                    akp, akq = a[k][p], a[k][q]
                    a[k][p] = c * akp - s * akq
                    a[k][q] = s * akp + c * akq
                for k in range(n):
                    apk, aqk = a[p][k], a[q][k]
                    a[p][k] = c * apk - s * aqk
                    a[q][k] = s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = v[k][p], v[k][q]
                    v[k][p] = c * vkp - s * vkq
                    v[k][q] = s * vkp + c * vkq
    else:
        raise ConvergenceError("Jacobi no convergió")
    order = sorted(range(n), key=lambda i: a[i][i])
    values = [a[i][i] for i in order]
    vectors = [[v[r][i] for i in order] for r in range(n)]
    return IterativeResult({"values": values, "vectors": vectors}, True, sweep + 1, math.sqrt(off), "jacobi")
