# ADR 0001 — Política de dependencias: núcleo stdlib + SymPy/mpmath para lo simbólico

- **Estado:** aceptado (decisión de Arrds)
- **Fecha:** 2026-09-22

## Contexto

Los documentos de contexto fijan como stack del motor **SymPy, SciPy, mpmath y NumPy**, con una cascada de
fallback SymPy → SciPy → mpmath → explicación pedagógica
([01](../contexto/01-vision-general.md), [03](../contexto/03-arquitectura-y-componentes.md)).

La v0.1 se escribió con **solo la biblioteca estándar**: implementación de referencia auditable, algoritmos
legibles y un contrato JSON que no depende de tipos de NumPy.

El siguiente objetivo, Matemática A y B (cálculo), exige límites, primitivas, series y resolución simbólica
de ecuaciones. La integración simbólica en serio (algoritmo de Risch y heurísticas) no es razonable de
reimplementar, y SymPy además ofrece los pasos de integración (`manualintegrate`), que encajan con la
explicación paso a paso del producto.

## Opciones

1. **Solo stdlib.** Máximo control; sin primitivas simbólicas reales y con meses de trabajo para límites y series.
2. **Stack completo de los documentos** (SymPy + SciPy + mpmath + NumPy). Más potencia numérica; NumPy/SciPy
   son binarios pesados de empaquetar y hoy el núcleo numérico propio cubre A, B, C y D.
3. **Híbrido.** SymPy (+ mpmath) para la Capa 1 simbólica; el núcleo numérico en stdlib queda como motor
   numérico y como **verificación cruzada** de lo simbólico.

## Decisión

**Opción 3, con SymPy obligatorio.**

- **Dependencias permitidas:** `sympy` (trae `mpmath`). Se declaran en `pyproject.toml`.
- **SymPy se usa para:** límites, primitivas e integrales simbólicas, series (Taylor, sumatorias), resolución
  simbólica de ecuaciones, simplificación avanzada y pasos de resolución. mpmath, para precisión extendida
  cuando float64 no alcance.
- **Sigue en stdlib:** el parser (única entrada de texto: nunca `sympify`/`parse_expr` sobre texto del
  usuario, porque usan `eval`), el evaluador, los métodos numéricos, álgebra lineal, señales y unidades.
- **Puente:** el AST propio se traduce a objetos SymPy y de vuelta mediante un conversor explícito
  (nodo por nodo, lista blanca de funciones).
- **Verificación cruzada obligatoria:** todo resultado simbólico se contrasta con el núcleo numérico
  (p. ej. derivar la primitiva y comparar con el integrando en puntos de prueba; comparar la integral
  definida simbólica con Simpson). Si no coinciden, es un error, no un resultado.
- **NumPy y SciPy:** fuera, hasta que un perfil de rendimiento lo justifique (nuevo ADR).

## Consecuencias

- Todo sigue detrás del mismo contrato JSON y del mismo banco de verificación.
- Instalación: `pip install -e .` (o `pip install sympy`). El motor ya no es "cero dependencias".
- Empaquetado: SymPy y mpmath son Python puro (~30 MB); compatibles con Nuitka sin compilar extensiones.
- La propuesta de portar el núcleo a C++ solo alcanzaría a la parte stdlib; lo simbólico seguiría en Python
  (coherente con el puente pybind11 de los documentos).
- Cualquier otra dependencia requiere preguntar a Arrds y un ADR nuevo.
