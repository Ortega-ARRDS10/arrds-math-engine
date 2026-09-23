# Arquitectura

## Flujo

```
texto ──► expr.parser ──► AST (expr.nodes, inmutable)
                           ├─► expr.evaluator   (real | complejo)  ──► números
                           └─► expr.symbolic    (diff, simplify, to_latex)
                                     │
numeric · linalg · poly · stats · vector · signals · units   (usan el AST o funciones compiladas)
                                     │
                              api.run(nombre, params)   ← contrato JSON
                               │                 │
                         selftest.CASES     server.py ──► web/index.html (panel)
```

El parser es la **única** puerta de entrada de texto: no hay `eval` en ninguna capa. Las funciones
numéricas aceptan una expresión en texto (se compila con `compile_function`) o una función de Python.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `errors.py` | Jerarquía `MathEngineError` con `code` estable y `hint` pedagógico opcional. |
| `expr/parser.py` | Tokenizador + parser descendente recursivo. Límites: 10 000 caracteres, 100 niveles de anidación. |
| `expr/nodes.py` | Nodos `Num`, `Var`, `Unary`, `Binary`, `Call`; `to_string` con paréntesis mínimos. |
| `expr/evaluator.py` | Catálogo `FUNCTIONS`/`CONSTANTS`, `evaluate`, `compile_function`. |
| `expr/symbolic.py` | Derivada exacta, simplificación conservadora, gradiente, LaTeX. |
| `numeric/` | `IterativeResult`; raíces, derivada, integrales, EDO. |
| `linalg.py` | Matrices como `list[list[float]]`; LU, QR, Jacobi, normas. |
| `poly.py` | Polinomios descendentes; raíces por Durand–Kerner. |
| `stats.py` | Descriptiva y regresión lineal con incertidumbres. |
| `vector.py` | Operadores diferenciales (Mat C), simbólicos + evaluación. |
| `signals.py` | FFT, espectro, funciones de transferencia, Bode (Mat D). |
| `units.py` | Unidades, prefijos, análisis dimensional (7 dimensiones base del SI). |
| `api.py` | Registro `nombre → handler`, validación de parámetros, serialización. |
| `selftest.py` | Casos de verificación (datos JSON) y comparador. |
| `server.py`, `web/` | Panel local de pruebas. |

## Contrato JSON

Pensado para que cualquier implementación (el núcleo nativo, un binding pybind11, un servicio) lo replique
y se valide con los mismos casos.

### Petición

```json
{"operation": "numeric.brent", "params": {"expression": "x^3 - 2x - 5", "a": 2, "b": 3}}
```

- `operation`: `modulo.nombre`. El catálogo completo (descripción, parámetros, ejemplo) sale de
  `GET /api/operations` o `api.list_operations()`.
- Parámetros desconocidos → `INVALID_INPUT` (detecta errores de tipeo).
- Números: JSON number, `"inf"`, `"-inf"`, `"nan"` o complejo `{"re": x, "im": y}` donde se admita.
- Límites (texto como `"pi"`, `"2*pi"`) se aceptan en `a`, `b`, `t0`, `t1`, `x0`, `x1`.

### Respuesta

```json
{"ok": true,  "operation": "numeric.brent", "result": { ... }, "elapsed_ms": 0.21}
{"ok": false, "operation": "numeric.brent",
 "error": {"code": "DOMAIN_ERROR", "message": "...", "hint": "..."}, "elapsed_ms": 0.05}
```

- `run()` **nunca lanza**: cualquier excepción inesperada se devuelve como `INTERNAL_ERROR` (y es un bug).
- Resultado iterativo: `{value, converged, iterations, error_estimate, method, extra}`.
- Serialización: complejo → `{"re","im"}`; `inf`/`nan` → texto; el JSON es estricto (`allow_nan=False`).
- Resultados graficables incluyen `plots: [{title, x_label, y_label, log_x, series: [{name, x, y, points?}]}]`;
  un `y` en `null` es un punto fuera de dominio (la curva se corta).

### Códigos de error

| `code` | Significado |
|---|---|
| `PARSE_ERROR` | Sintaxis inválida (incluye posición). |
| `EVALUATION_ERROR` | Variable no definida, función desconocida, aridad. |
| `DOMAIN_ERROR` | Fuera de dominio (ln(−1) en modo real, 1/0, sin cambio de signo). |
| `CONVERGENCE_ERROR` | El método no alcanzó la tolerancia. |
| `DIMENSION_ERROR` | Tamaños o dimensiones físicas incompatibles. |
| `SINGULAR_MATRIX` | Matriz singular o numéricamente singular. |
| `INVALID_INPUT` | Parámetro faltante, de tipo erróneo, fuera de rango o desconocido. |
| `UNKNOWN_OPERATION` | Operación no registrada. |
| `INTERNAL_ERROR` | Bug del motor. |

### Endpoints del panel

| Método | Ruta | Cuerpo | Respuesta |
|---|---|---|---|
| GET | `/api/operations` | — | catálogo |
| POST | `/api/run` | `{operation, params}` | respuesta uniforme |
| POST | `/api/selftest` | `{module?}` | `{total, passed, failed, cases[]}` |

Seguridad: solo `127.0.0.1`, cuerpo ≤ 1 MiB, `Content-Type: application/json`, `Host`/`Origin`
verificados, CSP estricta en el HTML, sin `eval` en el JS. Límites de tamaño en la API (matrices ≤ 200×200,
listas ≤ 100 000, muestreos ≤ 10 000, DFT no potencia de 2 ≤ 4096). No hay límite de tiempo por petición:
es un banco local, no un servicio expuesto.
