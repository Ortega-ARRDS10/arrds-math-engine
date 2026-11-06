# ADR 0004 — Extensiones en dos niveles: declarativas primero, con código después

- **Estado:** propuesto
- **Fecha:** 2026-10-30
- **Relacionado:** [especificación LaTeX](../lenguaje/ESPECIFICACION.md), [ADR 0003](0003-render-propio.md)

## Contexto

Arrds quiere que los usuarios puedan agregar modificaciones a la calculadora mediante extensiones:
funciones y constantes nuevas al principio, y más adelante métodos o tipos de gráfico con código propio.

Riesgos que hay que controlar:

- **Seguridad:** una extensión con código ejecuta software ajeno en la computadora del usuario.
- **Ambigüedad:** si una extensión pudiera redefinir `\sin` o `\frac`, el mismo texto significaría cosas
  distintas según qué extensiones estén instaladas, y se rompe el principio de "una sola lectura".
- **Compatibilidad:** las extensiones deben sobrevivir a las nuevas versiones del lenguaje y del motor.

## Opciones

1. **Solo extensiones con código** (bibliotecas C++ o Python). Máxima potencia; riesgo alto y problemas de
   compatibilidad binaria entre versiones.
2. **Solo extensiones declarativas.** Seguras y portables; limitadas a lo expresable con el lenguaje.
3. **Dos niveles**, empezando por el declarativo.

## Decisión (propuesta)

**Opción 3.**

**Nivel 1 — declarativas (primero).** Un archivo de datos (JSON o similar) que no ejecuta código y solo
combina lo que el lenguaje ya sabe hacer:

| Aporta | Ejemplo |
|---|---|
| Funciones nuevas | `\operatorname{sec}{x} := \frac{1}{\cos{x}}` |
| Constantes con nombre | `g_{\text{0}} := 9.80665` (con unidad, cuando exista) |
| Atajos de escritura rápida | tipear `->` inserta `\to` |
| Estilos del render | colores, tamaños, fuente |
| Casos de verificación | toda función nueva trae sus ejemplos con resultado esperado |

**Nivel 2 — con código (después).** Métodos numéricos, tipos de gráfico, importadores. Requisitos antes
de habilitarlo: sandbox, permisos explícitos que el usuario aprueba y firma de las extensiones.

**Reglas comunes:**

- Una extensión **nunca** redefine comandos, constantes ni operadores del núcleo; si lo intenta, no se carga.
- Sus comandos usan un espacio de nombres propio (p. ej. `\operatorname{nombre}`), y dos extensiones que
  definen el mismo nombre son un conflicto que el usuario debe resolver.
- Cada extensión declara la versión del lenguaje que usa; el motor rechaza versiones incompatibles.
- Las definiciones pasan por el mismo parser y la misma verificación que la entrada del usuario.

## Consecuencias

- El nivel 1 sale "gratis" del registro de operaciones y del parser; puede llegar temprano.
- El nivel 2 depende de decisiones de seguridad (sandbox, firma); queda para una versión posterior.
- El catálogo del lenguaje necesita versionado (para que las extensiones declaren compatibilidad).
