# Lenguaje de la calculadora (LaTeX Arrds)

Esta carpeta recopila **todo lo que Arrds va definiendo** sobre cómo se escribe la matemática en la
calculadora, cómo se renderiza y qué significa: comandos, funciones, propiedades y comportamientos.
Es la fuente de verdad del parser LaTeX ([ADR 0002](../adr/0002-nucleo-cpp.md)).

| Archivo | Contenido |
|---|---|
| [ESPECIFICACION.md](ESPECIFICACION.md) | Reglas generales del subconjunto LaTeX: léxico, precedencia, ambigüedades y decisiones abiertas. |
| [CATALOGO.md](CATALOGO.md) | Cada comando, función o propiedad, por nivel: cómo se escribe, cómo se ve, qué calcula. |
| [EDITOR_Y_CONFIGURACION.md](EDITOR_Y_CONFIGURACION.md) | Atajos de escritura rápida y opciones de configuración de la calculadora. |

## Cómo trabajamos

1. Arrds explica una función o comportamiento, con ejemplos ("se escribe así → se ve así → da esto").
2. Se registra en [CATALOGO.md](CATALOGO.md) con su ficha, **tal como Arrds lo definió**. Lo que agregue
   Claude por su cuenta se marca *(propuesta)* hasta que Arrds lo confirme.
3. Si la explicación resuelve una ambigüedad, se actualiza [ESPECIFICACION.md](ESPECIFICACION.md).
4. Cada ejemplo confirmado se convierte en caso de prueba del parser (texto LaTeX → resultado esperado).
5. Recién entonces se escribe el código.

## Orden de los niveles

1. Aritmética · 2. Álgebra · 3. Funciones elementales · 4. Trigonometría · 5. Exponenciales y logaritmos ·
6. Geometría 2D · 7. Geometría 3D · 8. Cálculo (límites, derivadas, integrales, series) ·
9. Varias variables.

## Estados de una ficha

| Estado | Significado |
|---|---|
| `definido` | Arrds lo explicó y lo confirmó. |
| `propuesta` | Sugerido por Claude; falta confirmar. |
| `implementado` | Ya existe en el código y tiene casos de prueba. |
