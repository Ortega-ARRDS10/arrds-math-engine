# CLAUDE.md — arrds-math-engine

Motor matemático de Arrds Studio, implementación de referencia en Python. Autor: Arrds (UNLP), trabaja en
español. Contexto del producto: [docs/CONTEXTO.md](docs/CONTEXTO.md) (resumen) y
[docs/contexto/](docs/contexto/README.md) (documentos originales, fuente de verdad).

## Comandos
- Instalar: `pip install -e .` (dependencia: sympy)
- Tests: `python -m unittest discover -s tests` (sin pytest)
- Banco: `python -m arrds_math.selftest [--module X] [--export f.json]`
- Panel: `python -m arrds_math.server` → http://127.0.0.1:8765

## Arquitectura (detalle en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md))
`expr/` (parser → AST → evaluador / simbólico) · `numeric/` · `linalg` · `poly` · `stats` · `vector` (Mat C) ·
`signals` (Mat D) · `units` (Capa 3) → `api.py` (registro + contrato JSON) → `selftest.py` → `server.py` + `web/index.html`.

## Reglas
1. **Dependencias** ([ADR 0001](docs/adr/0001-implementacion-de-referencia-stdlib.md)): Python 3.11+ y **solo SymPy (+mpmath)**, para la Capa 1 simbólica. Núcleo numérico, parser, linalg, señales y unidades en stdlib. Otra dependencia = preguntar a Arrds + ADR.
   Nunca `sympify`/`parse_expr` sobre texto del usuario (usan `eval`): el texto entra por nuestro parser y se convierte a SymPy nodo por nodo. Todo resultado simbólico se verifica con el núcleo numérico.
2. **El parser es la única entrada**: nunca `eval`/`exec`, ni en Python ni en el JS del panel.
3. **Todo iterativo reporta su error**: devuelve `IterativeResult` (`value, converged, iterations, error_estimate, method, extra`).
4. **Errores tipados**: subclase de `MathEngineError` con `code` estable; añadir `hint` pedagógico cuando el usuario pueda corregir algo.
5. **Nada sin caso de verificación**: función → registro en `api.py` → caso en `selftest.CASES` → test → doc ([docs/FLUJO_DE_TRABAJO.md](docs/FLUJO_DE_TRABAJO.md)).
6. Convenciones numéricas (coeficientes descendentes, `log` = natural, modo real por defecto): [docs/CONVENCIONES_NUMERICAS.md](docs/CONVENCIONES_NUMERICAS.md).
7. Código y comentarios en español; nombres de funciones en inglés (como NumPy/MATLAB). Comentar el *por qué*.
8. No inventar contexto de Arrds Studio: lo que no está en `docs/contexto/` se marca como "propuesta".

## Estado
v0.1 completa; roadmap en [docs/TAREAS.md](docs/TAREAS.md). Rama de trabajo actual: `claude/admiring-pascal-56gpjq`.
