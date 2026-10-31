# Escritura rápida y configuración

La calculadora tiene dos apartados pedidos por Arrds (2026-10-30):

- **Escritura rápida:** atajos del editor que insertan el LaTeX correcto mientras se tipea. El texto guardado
  siempre queda en LaTeX Arrds válido; los atajos son solo comodidad.
- **Configuración:** opciones que el usuario puede cambiar.

## Escritura rápida

| Al tipear | Se inserta | Origen |
|---|---|---|
| `*` | `\cdot` (también al pegar texto) | Arrds, nivel 1.3 |
| `(` | `\left( \right)` con el cursor adentro (opcional, ver configuración) | Arrds, nivel 1.6 |
| `\|` | `\left| \right|` con el cursor adentro | D7 *(propuesta)* |
| `\d` | `\mathrm{d}` | D3 |

## Combinaciones de teclas

Funcionalidad pedida por Arrds (2026-10-31). Todas las combinaciones de esta tabla son *(propuesta)* hasta que
Arrds las confirme, y el usuario podrá **reasignarlas** en la configuración (con aviso si dos acciones usan
la misma combinación).

**Escritura** (el cursor queda dentro de las llaves):

| Combinación | Inserta | Motivo |
|---|---|---|
| `^` | `^{}` | llaves obligatorias en potencias (D9) |
| `_` | `_{}` | llaves obligatorias en subíndices (D9) |
| `Ctrl + /` | `\frac{}{}` (si hay texto seleccionado, pasa a ser el numerador) | división clásica (1.4) |
| `Ctrl + R` | `\sqrt{}` | raíz (1.5) |
| `Ctrl + T` | `\text{}` | etiquetas y unidades (D12) |

**Celdas y grupos:**

| Combinación | Acción |
|---|---|
| `Enter` | nueva celda debajo |
| `Ctrl + Enter` | resolver la ecuación de la celda (equivale al botón "resolver", D19) |
| `Ctrl + D` | duplicar la celda |
| `Ctrl + G` | crear un grupo con las celdas seleccionadas |
| `Ctrl + Shift + Supr` | borrar la celda |
| `F2` | abrir las propiedades de la celda |
| `Alt + ↑` / `Alt + ↓` | mover la celda arriba / abajo |

**General:**

| Combinación | Acción |
|---|---|
| `Ctrl + Z` / `Ctrl + Y` | deshacer / rehacer |
| `Ctrl + K` | barra de comandos (buscar cualquier acción por nombre) |
| `Ctrl + S` | guardar la pestaña (archivo) |
| `Ctrl + Tab` | cambiar de pestaña |
| `Ctrl + 1`, `Ctrl + 2`… | enfocar la ventana gráfica 1, 2… |
| `Ctrl + ,` | abrir la configuración |

## Configuración

| Opción | Valores | Por defecto | Origen |
|---|---|---|---|
| Unidad angular | radianes / grados (indicador RAD/DEG siempre visible) | radianes | D4 |
| Paréntesis automáticos `\left( \right)` | sí / no | *(por definir)* | Arrds, nivel 1.6 |
| Porcentaje | contextual (`200 + 10\%` = 220) / siempre decimal (`10\%` = 0.1) | contextual | Arrds, D16 |
| Resolver ecuaciones automáticamente | sí / no (si no, con el botón "resolver") | sí | Arrds, D19 |
| Decimales del resultado | número | *(por definir)* | nivel 1.9 *(propuesta)* |
| Umbral de notación científica | exponente | *(por definir)* | nivel 1.1 *(propuesta)* |
| Combinaciones de teclas | reasignables por el usuario | las de la tabla de arriba | Arrds, 2026-10-31 |
