# ADR 0001 — Implementación de referencia solo con biblioteca estándar

- **Estado:** propuesto (pendiente de aprobación de Arrds)
- **Fecha:** 2026-09-22

## Contexto

Los documentos de contexto fijan como stack del motor **SymPy, SciPy, mpmath y NumPy**, con una cascada de
fallback SymPy → SciPy → mpmath → explicación pedagógica
([01](../contexto/01-vision-general.md), [03](../contexto/03-arquitectura-y-componentes.md)).

La v0.1 se escribió con **solo la biblioteca estándar de Python** por pedido explícito, para que sirva como
implementación de referencia auditable: cada algoritmo es legible (valor pedagógico), el contrato JSON no
depende de tipos de NumPy y el banco de verificación se puede portar a otra implementación sin arrastrar
dependencias.

## Opciones

1. **Solo stdlib** en todo el motor. Máxima portabilidad y control; hay que reimplementar (y mantener)
   algoritmos que SciPy ya resuelve mejor, y no hay CAS completo ni precisión arbitraria.
2. **Stack de los documentos** (SymPy/SciPy/mpmath/NumPy) detrás del mismo contrato. Potencia y
   robustez inmediatas; dependencia pesada para empaquetar (Nuitka) y menos control del error reportado.
3. **Híbrido**: la referencia stdlib queda como oráculo y *fallback*; los backends SymPy/SciPy/mpmath se
   agregan como estrategias intercambiables detrás de `api.run`, y el banco valida ambos.

## Decisión (propuesta)

Opción 3. La v0.1 es la referencia stdlib; incorporar SymPy/SciPy/mpmath se decide operación por operación
con un ADR propio, siempre detrás del contrato JSON y validado por el mismo banco.

## Consecuencias

- El contrato JSON y el banco son lo estable; los backends son reemplazables.
- Hasta que Arrds decida, **no se agregan dependencias** (regla de `CLAUDE.md`).
- La cascada de fallback de los documentos queda en el roadmap v0.2 ([TAREAS.md](../TAREAS.md)).
