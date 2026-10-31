# ADR 0003 — Render matemático propio, dibujado desde el AST

- **Estado:** propuesto
- **Fecha:** 2026-10-30
- **Relacionado:** [ADR 0002](0002-nucleo-cpp.md), [especificación LaTeX](../lenguaje/ESPECIFICACION.md)

## Contexto

La especificación del lenguaje ya decidió que la calculadora **no muestra el texto LaTeX tal cual**, sino una
forma canónica regenerada desde el árbol de la expresión (AST): `\sin{x}` se ve sin(x), `{24x} / {42y}` se ve
(24x) / (42y), `1/2x` se ve 1/(2x). Arrds preguntó si se puede diseñar un render propio.

Una librería externa (MicroTeX, KaTeX) recibe texto LaTeX y devuelve una imagen: no sabe qué parte del dibujo
corresponde a qué nodo del árbol. Eso impide funciones que distinguen a una calculadora como GeoGebra o Desmos:

- hacer clic sobre una parte de la fórmula y seleccionarla, o editar directamente sobre la fórmula;
- resaltar el lugar exacto de un error o una advertencia;
- colorear cada parte según el objeto o la curva a la que pertenece;
- animar o mostrar pasos de resolución sobre la misma fórmula.

## Opciones

1. **Solo librería externa** (MicroTeX, MIT). Rápido de integrar; sin interacción con partes de la fórmula.
2. **Render propio completo de TeX.** Inviable: TeX es enorme y casi todo queda fuera del subconjunto.
3. **Render propio del subconjunto LaTeX Arrds**, dibujado desde el AST: cada nodo produce una caja con
   posición y medidas; el render conoce la correspondencia caja ↔ nodo.

## Decisión (propuesta)

**Opción 3, en dos fases.**

- **Fase 1 (spike y primeras versiones):** MicroTeX, alimentado con el LaTeX canónico generado desde el AST.
- **Fase 2:** render propio en C++ sobre Qt:
  - **Algoritmo:** reglas de composición de fórmulas de TeX (apéndice G de *The TeXbook*, Knuth):
    fracciones, superíndices y subíndices, radicales, delimitadores que crecen, espaciado entre átomos.
  - **Fuente:** matemática OpenType con tabla MATH (*Latin Modern Math* o *STIX Two Math*, licencia OFL), que
    trae las medidas tipográficas (alturas de fracción, desplazamiento de exponentes, variantes de tamaño).
  - **Salida:** árbol de cajas con referencia al nodo del AST → dibujo con QPainter, selección e interacción.
  - **Validación:** comparación visual contra MicroTeX/KaTeX para todas las fichas del catálogo.

## Consecuencias

- El render es parte del núcleo C++ y comparte el AST con el parser y el evaluador.
- Fase 2 es un proyecto de meses; no bloquea nada porque la fase 1 funciona desde el principio.
- Las extensiones declarativas ([ADR 0004](0004-extensiones.md)) podrán aportar estilos de render.
- Licencias: MicroTeX (MIT) y fuentes OFL son compatibles con el modelo de pago único.
