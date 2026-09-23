# arrds-math-engine

Motor matemático de **Arrds Studio**: la estación de trabajo matemática y de ingeniería para estudiantes
y profesionales (visión completa en [docs/contexto/](docs/contexto/README.md)). Es la primera entrega
pública del ecosistema Arrds.

Esta versión (**v0.1**) es la **implementación de referencia**: Python 3.11+, sin `eval`. El núcleo
numérico usa solo la biblioteca estándar; desde la v0.2 la parte simbólica usa **SymPy** (+mpmath),
verificada siempre contra el núcleo numérico ([ADR 0001](docs/adr/0001-implementacion-de-referencia-stdlib.md)). Toda operación se expone con un contrato JSON independiente del lenguaje y se valida contra
un banco de casos con valores de referencia analíticos.

| Área | Qué cubre |
|---|---|
| Expresiones y simbólico | parser propio (multiplicación implícita, `^`/`**`, `!`), modo real/complejo, derivada simbólica, simplificación conservadora, LaTeX |
| Cálculo numérico | raíces (bisección, Newton, secante, Brent), derivada (Richardson), integrales (Simpson adaptativo, Gauss–Legendre, trapecio), EDO (RK4, Dormand–Prince RK45) |
| Álgebra lineal | LU, solve con refinamiento, det, inversa, cond, QR, mínimos cuadrados, autovalores simétricos |
| Polinomios y estadística | raíces complejas, ajuste por QR, descriptiva con error estándar, regresión con incertidumbres |
| Matemática C | gradiente, divergencia, rotor, laplaciano, jacobiano (simbólicos + evaluación) |
| Matemática D | FFT/DFT, espectro, funciones de transferencia, Bode |
| Unidades | SI, derivadas, imperiales, prefijos, conversión con verificación dimensional |

Todo método iterativo informa **si convergió, cuántas iteraciones usó y su error estimado**. Todo error
tiene un `code` estable y, cuando aplica, un `hint` que explica por qué falló el método.

## Instalación

```bash
pip install -e .
```

## Uso rápido

```python
from arrds_math.api import run

run("numeric.brent", {"expression": "x^3 - 2x - 5", "a": 2, "b": 3})
# {'ok': True, 'result': {'value': 2.0945514815423265, 'converged': True,
#   'iterations': 7, 'error_estimate': 2.5e-13, 'method': 'brent', ...}, 'elapsed_ms': 0.2}

run("units.convert", {"value": 1, "from": "kN*m", "to": "lbf*ft"})   # 737.5621…
```

Las funciones también se pueden usar directo (`arrds_math.numeric.brent(...)`), pero la API es el
contrato estable.

## Tests y banco de verificación

```bash
python -m unittest discover -s tests
```

```bash
python -m arrds_math.selftest
```

El segundo comando corre el banco (casos con valor de referencia y tolerancia); `--module units` filtra
y `--export casos.json` los exporta para validar otra implementación.

## Panel de pruebas

```bash
python -m arrds_math.server
```

Abre <http://127.0.0.1:8765>: catálogo de operaciones, editor JSON con ejemplos, gráficas, banco de
pruebas con indicador de integridad y barra de comandos (`Ctrl+K`). Es un banco de pruebas local, **no**
la interfaz de Arrds Studio. Escucha solo en `127.0.0.1` y funciona sin conexión.

## Documentación

- [docs/CONTEXTO.md](docs/CONTEXTO.md) — el motor dentro de Arrds Studio.
- [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) — módulos, flujo y contrato JSON.
- [docs/CONVENCIONES_NUMERICAS.md](docs/CONVENCIONES_NUMERICAS.md) — tolerancias, convenciones, unidades.
- [docs/FLUJO_DE_TRABAJO.md](docs/FLUJO_DE_TRABAJO.md) — ramas, cómo añadir una operación, definición de "listo".
- [docs/TAREAS.md](docs/TAREAS.md) — roadmap.
- [docs/POLITICA_DE_USO.md](docs/POLITICA_DE_USO.md) — alcance, responsabilidad, privacidad, licencia.
- [docs/adr/](docs/adr/) — decisiones de arquitectura.

## Licencia

**Pendiente de decisión** (ver [POLITICA_DE_USO.md](docs/POLITICA_DE_USO.md#licencia)). Mientras no haya
un archivo `LICENSE`, rige "todos los derechos reservados".
