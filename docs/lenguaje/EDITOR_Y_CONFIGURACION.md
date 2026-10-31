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

## Configuración

| Opción | Valores | Por defecto | Origen |
|---|---|---|---|
| Unidad angular | radianes / grados (indicador RAD/DEG siempre visible) | radianes | D4 |
| Paréntesis automáticos `\left( \right)` | sí / no | *(por definir)* | Arrds, nivel 1.6 |
| Porcentaje | contextual (`200 + 10\%` = 220) / siempre decimal (`10\%` = 0.1) | contextual | Arrds, D16 |
| Decimales del resultado | número | *(por definir)* | nivel 1.9 *(propuesta)* |
| Umbral de notación científica | exponente | *(por definir)* | nivel 1.1 *(propuesta)* |
