# Celdas, grupos, pestañas y ventanas

Modelo de documento de la calculadora, definido por Arrds (2026-10-30). Lo marcado *(propuesta)* es de
Claude y falta confirmar. Las reglas del lenguaje están en [ESPECIFICACION.md](ESPECIFICACION.md).

## Estructura

```
Pestaña (archivo)
└── Lista de celdas
    ├── Celda suelta
    ├── Grupo de celdas
    │   ├── Celda
    │   └── Grupo de celdas (anidado, permitido en teoría)
    └── ...
Ventanas gráficas (una o varias)
```

| Elemento | Qué es |
|---|---|
| **Celda** (bloque) | Una expresión de la lista, como en GeoGebra y Desmos. Tiene una etiqueta (función, ecuación, punto…) y propiedades. |
| **Grupo de celdas** | Conjunto de celdas que forma un **ámbito**: sus expresiones interactúan entre sí. Se pueden anidar (en teoría). |
| **Pestaña** | En realidad un **archivo**: guarda las expresiones y las propiedades de las celdas con las que trabajó el usuario. |
| **Ventana gráfica** | Vista donde se dibujan los objetos; puede haber varias. |

## Propiedades de una celda

- **Visuales:** color, etiqueta, grosor, etc.: todo lo que se pueda hacer con esa variable u objeto.
- **Banda de color y nombre:** la celda se puede editar con una banda de color y un nombre propio, para
  identificarla.
- **Alcance de una definición:**
  - **independiente** del grupo: vale solo dentro de su propio grupo;
  - **estándar**: vale para todas las celdas (p. ej. `g = 9.81` en todo el documento).
- **Excepciones:** una celda puede excluir grupos concretos: "no interferir con el grupo de celdas 3, pero sí
  con los demás".

## Regla de no interferencia

Un nombre definido no se puede redefinir en otro lugar: **las definiciones no pueden interferir**. Si en un
grupo se quiere otro valor, se crea **una variable nueva**:

| Situación | Resultado |
|---|---|
| `g = 9.81` estándar y, en un grupo, `g = 10` | error: el nombre ya está definido |
| En ese grupo, `g_{0} = 10` | válido: es otra variable |

## Decisiones (Arrds, 2026-10-30)

| Tema | Decisión |
|---|---|
| Alcance por defecto de una definición nueva | **independiente** (solo su grupo), para que los ejercicios no se pisen; "estándar" se elige en las propiedades |
| `g` estándar que excluye al grupo 3 | el grupo 3 **puede** definir su propia `g`: para ese grupo, `g` no existe |
| Grupos anidados | el grupo interior **ve** las definiciones del exterior, como los ámbitos en programación |
| Ventanas gráficas | cada ventana elige qué grupos muestra y si es 1D (recta numérica, para inecuaciones), 2D o 3D; además tendrá funciones de software CAD (AutoCAD, Inventor) que GeoGebra no tiene (ver abajo) |
| Archivo de una pestaña | **JSON** con el texto LaTeX de cada celda y sus propiedades: legible y versionable con git |

## Funciones de tipo CAD en las ventanas gráficas

Elegidas por Arrds (2026-10-30) entre las que tienen AutoCAD e Inventor y GeoGebra no. El comportamiento
detallado de cada una se define más adelante; la columna "En la calculadora" es *(propuesta)*.

| Función | Origen | En la calculadora |
|---|---|---|
| **Vistas múltiples sincronizadas** | AutoCAD / Inventor | el mismo objeto 3D visto a la vez desde superior, frontal, lateral e isométrica, en ventanas que se mueven juntas |
| **Referencia a objetos (snap)** | AutoCAD | el cursor se engancha a puntos notables: intersecciones, extremos, centros, tangencias, raíces, máximos y mínimos |
| **Restricciones** | Inventor | relaciones que se mantienen al mover objetos: paralelo, perpendicular, tangente, coincidente, y cotas que modifican el dibujo |
| **Sistema de coordenadas del usuario (SCU)** | AutoCAD | mover y rotar los ejes para trabajar en un plano inclinado del espacio 3D |
| **Cortes y secciones** | AutoCAD / Inventor | intersección de una superficie con un plano: curvas de nivel y perfiles (Matemática C) |

Descartadas por ahora: proyección ortogonal/perspectiva, capas, cotas y medición como función aparte.
