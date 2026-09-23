# El motor dentro de Arrds Studio

> Resumen para orientarse. La fuente de verdad son los documentos de [contexto/](contexto/README.md);
> lo marcado **(propuesta)** no figura en ellos y requiere validación de Arrds.

## Qué es Arrds Studio

Estación de trabajo matemática y de ingeniería para estudiantes y profesionales, pensada como alternativa
a MATLAB: pago único, alto rendimiento, portabilidad y **explicaciones paso a paso**
([01-vision-general](contexto/01-vision-general.md)). El alcance académico sigue Matemática B, C y D de la
UNLP: cálculo, álgebra lineal, análisis complejo y transformadas.

`arrds-math-engine` es la **primera entrega pública** del ecosistema
([04-repositorios-github](contexto/04-repositorios-github.md)) y el núcleo que da la "verdad técnica" al
resto: frontend Qt 6, agente académico con RAG y orquestador multi-agente (`MathAgent` delega aquí).

## Principios que el motor hereda

De [02-principios-y-workflow](contexto/02-principios-y-workflow.md):

- **Nunca un fallo silencioso**: si un método falla, el motor explica por qué → campo `hint` de los errores.
- **Pedagogía**: explicar *por qué* funciona o falla un método, no solo devolver números.
- **Spec-driven + TDD**: cada operación nace con su especificación verificable (caso de `selftest`).
- **ADRs** para decisiones relevantes ([adr/](adr/)).
- **Spike antes de arquitecturar**: esta v0.1 es también el spike del contrato del motor.

## Capas

Los documentos describen una **cascada de fallback**: SymPy (simbólico exacto) → SciPy (numérico) →
mpmath (precisión arbitraria) → explicación pedagógica del fallo
([03-arquitectura](contexto/03-arquitectura-y-componentes.md)).

La v0.1 organiza el código en capas **(propuesta)**, compatibles con esa cascada:

| Capa | Rol | Módulos |
|---|---|---|
| 1 · Abstracción simbólica | expresiones, derivadas exactas, LaTeX | `expr/` |
| 2 · Cálculo numérico | métodos con error estimado | `numeric/`, `linalg`, `poly`, `stats`, `signals`, `vector` |
| 3 · Contexto físico | unidades y análisis dimensional | `units` |
| 4 · Orquestación | contrato JSON, registro de operaciones | `api` (la HAL y el orquestador multi-agente quedan fuera de este repo) |

## Tensión abierta: dependencias

Los documentos fijan SymPy/SciPy/mpmath/NumPy; la v0.1 usa **solo biblioteca estándar** para ser una
referencia auditable y portable. Cómo se reconcilian está en
[ADR 0001](adr/0001-implementacion-de-referencia-stdlib.md). **Decisión pendiente de Arrds.**

## Relación con el frontend

Según los documentos, el frontend es C++20/Qt 6 y se conecta al motor Python vía **pybind11**
(con `QThreadPool` y manejo del GIL). La idea de portar el núcleo a C++ y validarlo con este banco es una
**(propuesta)** (ver [TAREAS.md](TAREAS.md)); el contrato JSON sirve para ambos caminos.

## Identidad visual del panel

El panel de pruebas usa fondo negro, texto blanco, acento cian, tipografía monoespaciada para datos e
indicador de integridad verde/amarillo/rojo **(propuesta "Ruido Cero")**: no figura en los documentos de
contexto; se validará cuando exista la guía de estilo de Arrds Studio.
