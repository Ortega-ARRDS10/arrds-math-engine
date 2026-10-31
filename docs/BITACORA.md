# Bitácora de avance

Registro cronológico del proyecto, **la entrada más reciente arriba**. Complementa al historial de git:
git dice *qué* cambió; la bitácora dice *por qué*, qué se decidió y qué quedó pendiente.

Reglas:
- Una entrada por sesión de trabajo (o por hito), con fecha.
- Solo hechos verificados: si se dice "pasan los tests", va el número real de la corrida.
- Las decisiones se resumen en una línea y enlazan a su ADR.
- Al cerrar una sesión, actualizar "Próximo paso".

---

## Estado actual

| | |
|---|---|
| Versión | v0.1 (implementación de referencia) |
| Rama | `main` (sin otras ramas en el remoto) |
| Último commit | `1abc222` — ADR 0001 aceptado |
| Operaciones en la API | 68 |
| Casos del banco | 74/74 pasan |
| Tests | 66, todos pasan (última corrida verificada: 2026-10-30) |
| Dependencias | SymPy + mpmath ([ADR 0001](adr/0001-implementacion-de-referencia-stdlib.md)) |
| Decisiones pendientes | licencia; qué parte de `docs/contexto/` es pública |
| Decisiones propuestas | [ADR 0002](adr/0002-nucleo-cpp.md): núcleo C++20 + Qt (se valida con un spike) |
| Lenguaje LaTeX | nivel 1 (aritmética) definido; niveles 2–9 pendientes |
| Próximo paso | Nivel 2 (álgebra) del [catálogo](lenguaje/CATALOGO.md) |

---

## Plantilla

```markdown
## AAAA-MM-DD — título corto

**Objetivo:** qué se buscaba en la sesión.

**Hecho:**
- …

**Decisiones:**
- … ([ADR NNNN](adr/NNNN-....md))

**Verificación:** tests N/N · banco N/N · otras comprobaciones.

**Problemas encontrados:**
- …

**Pendiente / próximo paso:**
- [ ] …

**Commits:** `abc1234`, …
```

---

## 2026-10-30 — Nivel 1 del lenguaje: aritmética

**Decisiones de Arrds** (fichas 1.1–1.9 en [lenguaje/CATALOGO.md](lenguaje/CATALOGO.md)):
- Números con punto; notación científica solo en LaTeX (`6.02 \times 10^{23}`).
- `--3` válido con advertencia que recomienda `-(-3)`.
- Multiplicación: `\cdot` estándar; `*` lo convierte el editor en `\cdot`; `\times` = producto entre números
  y producto vectorial entre vectores; `abc` = producto implícito sin signo visible.
- División: `\frac{}{}`, `/` y `\div`; la multiplicación implícita liga más fuerte que `/` (D15): `1/2x` = 1/(2x).
- `\sqrt{-4}` es error en los reales; `( )`, `[ ]` y `\left( \right)` equivalentes.
- Porcentaje contextual por defecto (`200 + 10\%` = 220), configurable a 0.1 (D16).
- Resultado exacto con el decimal al lado.
- Nuevo documento [lenguaje/EDITOR_Y_CONFIGURACION.md](lenguaje/EDITOR_Y_CONFIGURACION.md): escritura rápida
  y opciones de configuración.

**Pendiente / próximo paso:**
- [x] Formas de escritura de 1.8 (MCD, MCM, piso, techo, redondeo) confirmadas por Arrds.
- [x] El parser ASCII del motor adoptó D15 (`1/2x` = 1/(2x)): nuevo nivel `implicit` en la gramática,
  test y caso de banco nuevos. Verificación: tests 66/66 · banco 74/74.
- [ ] Nivel 2: álgebra.

---

## 2026-10-30 — Especificación LaTeX completa y `log` en base 10

**Decisiones de Arrds** (detalle en [lenguaje/ESPECIFICACION.md](lenguaje/ESPECIFICACION.md)):
- Regla de las llaves: el argumento va siempre entre `{ }` (`a\sin{x}`); `\sin x` y `\sin(x)` son error; los
  paréntesis solo aparecen en el render: `\sin{x}` → sin(x).
- Llaves obligatorias también en `^{}` y `_{}`. Subíndice etiqueta con `\text{}` (`x_{\text{max}}`); varias
  letras sin `\text` son error (`x_{max}` → etiqueta o índices con coma `x_{m,a,x}`). Todo subíndice crea una
  variable distinta.
- `e` y `\pi` no se redefinen; `i` es índice/variable hasta llegar al campo complejo.
- Diferencial con `\mathrm{d}` (+ atajo del editor). Radianes por defecto, grados por configuración, con
  indicador RAD/DEG visible. Punto decimal; la coma separa coordenadas y elementos.
- `\ln` natural, `\log` base 10, `\log_{b}{x}` base b. Valor absoluto solo con `\left| x \right|`.
- `\text{}` es notación, nunca cálculo: etiqueta en subíndices, unidad después de una cantidad.
- Pendiente para el futuro: D13 (significado de los índices múltiples `a_{i,j}`).

**Hecho:**
- Motor Python alineado con D6: `log(x)` = base 10 (antes natural), `log(x, b)` valida la base (> 0, ≠ 1),
  derivada simbólica corregida, `log10` se renderiza igual que `log` y `log2` como `\log_{2}`.
- 3 casos nuevos en el banco (log base 10, derivada de log, base 1 inválida) y tests de logaritmos ampliados.

**Verificación:** tests 65/65 · banco 73/73.

**Próximo paso:** nivel 1 del catálogo (aritmética).

---

## 2026-10-30 — Calculadora gráfica: lenguaje del motor y ADR 0002

**Objetivo:** decidir el lenguaje del motor para una calculadora tipo GeoGebra (cálculo, 2D, 3D) en
Qt/C++, con la matemática expresada en LaTeX.

**Decisiones:**
- Propuesto el núcleo en **C++20** (evaluación por punto a 60 FPS), con SymEngine para lo simbólico rápido,
  SymPy vía pybind11 para lo pesado y el motor Python como referencia. Sin librerías GPL (Giac/GiNaC), por el
  modelo de pago único. Se acepta tras un spike. ([ADR 0002](adr/0002-nucleo-cpp.md))

**Hecho:**
- [docs/lenguaje/](lenguaje/README.md): `ESPECIFICACION.md` (borrador del subconjunto LaTeX, con 7 decisiones
  abiertas D1–D7) y `CATALOGO.md` (fichas por nivel, vacías: se llenan con las explicaciones de Arrds).

**Pendiente / próximo paso:**
- [ ] Arrds explica el lenguaje desde la aritmética hasta el cálculo; resolver D1–D7.
- [ ] Spike C++/Qt del ADR 0002.

---

## 2026-10-30 — Bitácora

**Hecho:**
- Se crea esta bitácora con la reconstrucción de las sesiones anteriores a partir del historial de git y
  de lo registrado en `docs/`.
- Se constata que el trabajo ya vive en `main` (la rama `claude/admiring-pascal-56gpjq` no existe más en
  el remoto) y que todavía no se cargó el temario de cálculo.

**Pendiente / próximo paso:**
- [x] `CLAUDE.md` actualizado: rama `main` y lectura de la bitácora al inicio de cada sesión.
- [ ] Cargar el temario de Matemática A y B en `docs/temario/`.

---

## 2026-09-22 — Política de dependencias (ADR 0001)

**Objetivo:** decidir cómo encarar Matemática A y B (límites, primitivas, series) antes de programarlas.

**Decisiones:**
- Esquema **híbrido con SymPy obligatorio**: SymPy (+mpmath) para la Capa 1 simbólica; parser, evaluador,
  métodos numéricos, álgebra lineal, señales y unidades siguen en biblioteca estándar. NumPy/SciPy fuera
  hasta que el rendimiento lo justifique. ([ADR 0001](adr/0001-implementacion-de-referencia-stdlib.md))
- Nunca `sympify`/`parse_expr` sobre texto del usuario (usan `eval`): conversión propia AST → SymPy.
- Todo resultado simbólico se verifica con el núcleo numérico.

**Hecho:** `pyproject.toml` con `sympy>=1.13`; `CLAUDE.md`, README, CONTEXTO y TAREAS actualizados.

**Verificación:** tests 65/65 · SymPy 1.14.0 y mpmath 1.3.0 presentes en el entorno.

**Commits:** `1abc222`

---

## 2026-09-22 — v0.1 del motor: API, banco, tests, panel y documentación

**Objetivo:** completar la v0.1 a partir del WIP previo y alinearla con los documentos de contexto.

**Hecho:**
- Repositorio local conectado al remoto; documentos de contexto commiteados y luego movidos a
  `docs/contexto/` sin cambios.
- Ajustes al núcleo: errores con `hint` pedagógico; RK4, RK45, raíces de polinomios y autovalores
  devuelven `IterativeResult` con error estimado; error honesto para raíces múltiples.
- `api.py`: 68 operaciones con contrato JSON uniforme (`ok`, `result`/`error`, `elapsed_ms`).
- `selftest.py`: 70 casos con valor de referencia analítico o tabulado, exportables a JSON.
- Tests `unittest` por módulo, del contrato, del banco y del servidor.
- Panel local (`python -m arrds_math.server`): catálogo, editor JSON, gráficas SVG, banco con indicador
  de integridad, barra de comandos `Ctrl+K`.
- Documentación: README, `CLAUDE.md`, `docs/` (contexto, arquitectura, convenciones numéricas, política
  de uso, flujo de trabajo, roadmap) y ADR 0001.

**Problemas encontrados y corregidos:**
- `2x(x+1)` se leía como llamada a una función `x` → `nombre(...)` es llamada solo si es función conocida.
- ~150 paréntesis anidados desbordaban la pila de Python antes del límite del parser → límite bajado a 100.
- En Windows, el servidor cortaba la conexión antes de enviar el 413 de cuerpo demasiado grande → se
  descarta el cuerpo (acotado a 8 MiB) antes de responder.
- `__pycache__` estaba versionado → `.gitignore`.

**Contradicciones detectadas con los documentos de contexto** (registradas en `docs/CONTEXTO.md`):
- Los documentos piden SymPy/SciPy/mpmath; la v0.1 era solo stdlib → resuelto en el ADR 0001.
- Las 4 capas con HAL, la estética "Ruido Cero" y el port del núcleo a C++ no figuran en los documentos →
  marcados como *propuesta*.

**Verificación:** tests 65/65 (estable en 20 corridas, Python 3.12 y 3.14) · banco 70/70 · `curl` a
`/api/operations`, `/api/run` y `/api/selftest` contra el servidor levantado · panel revisado en el navegador.
No probado en Python 3.11 (no instalado).

**Pendiente:**
- [ ] Decidir la licencia (propuesta: MPL-2.0, ver [POLITICA_DE_USO.md](POLITICA_DE_USO.md#licencia)).
- [ ] Revisar si `docs/contexto/` debe ser público.
- [ ] CI con GitHub Actions.

**Commits:** `73b6e99`, `3c52530`, `f5b88cf`, `64dacbd`, `ece674b`, `6e31922`, `3506896`

---

## Antes del 2026-09-22 — núcleo inicial (WIP)

**Hecho:** primer commit del paquete `arrds_math/`: parser y evaluador propios, derivada simbólica y LaTeX,
métodos numéricos (raíces, integración, EDO), álgebra lineal, polinomios, estadística, análisis vectorial,
señales y unidades. Solo biblioteca estándar; sin tests formales (solo una prueba manual).

**Commits:** `8c66797`
