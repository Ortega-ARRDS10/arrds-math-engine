# Convenciones numéricas

## Expresiones

- `^` y `**` son potencia, **asociativa por la derecha**: `2^3^2 = 512`. `-2^2 = -4`.
- Multiplicación implícita: `2x`, `2(x+1)`, `(a)(b)`, `3 sin(x)`, `x(x+1)`. `nombre(...)` es llamada solo
  si `nombre` está en el catálogo de funciones; si no, es producto.
- `log(x)` = **logaritmo natural** (igual que `ln`); `log(x, b)` en base b; `log10`, `log2` explícitos.
- Ángulos en **radianes**; `deg(x)` y `rad(x)` convierten.
- `x!` = factorial; para no enteros usa Γ(x+1). Máximo 170! (límite de float64).
- Constantes: `pi`, `e`, `tau`, `phi`, `inf`.

## Modo real vs. complejo

- **Real (por defecto)**: todo resultado complejo es `DOMAIN_ERROR` (`ln(-1)`, `sqrt(-4)`, `(-8)^(1/3)`).
  En ingeniería un complejo inesperado casi siempre es un error de modelo.
- **Complejo** (`complex_mode: true`): se usa `cmath`, existe la unidad imaginaria `j` (notación de
  ingeniería eléctrica) y se devuelve la rama principal.
- Una parte imaginaria ≤ 1e-15·|parte real| se considera ruido de redondeo y se descarta en modo real.

## Simbólico

La simplificación es **conservadora**: solo identidades válidas en todo el dominio (`x·1 = x`, `x+0 = x`,
`(x^m)^n = x^(mn)` con enteros). No cancela `x/x` ni `sqrt(x^2)`: cambiaría el dominio y ocultaría
singularidades.

## Polinomios y señales

- Coeficientes en **orden descendente** (como MATLAB/NumPy): `[1, -3, 2]` = x² − 3x + 2.
- Las raíces se devuelven como complejos; una raíz es real (parte imaginaria exactamente 0) si su parte
  imaginaria es menor que su error estimado.
- H(s) = num(s)/den(s) con la misma convención. Estable: todos los polos con Re < −1e-12.
- Bode: magnitud en dB (20·log₁₀|H|), fase en grados **desenvuelta** (sin saltos de ±360°).
- FFT sin normalizar; la inversa incluye el factor 1/N. El espectro es de lado único y normalizado: una
  senoidal de amplitud A en un bin exacto aparece con amplitud A.

## Tolerancias por defecto

| Método | Parámetro | Valor |
|---|---|---|
| Raíces (todas) | `tol` | 1e-12 (relativa a max(1, |x|) en Newton/secante) |
| Simpson adaptativo | `tol` | 1e-10 absoluta, profundidad 50, ≤ 1e6 evaluaciones |
| Gauss–Legendre | `n` | 20 puntos |
| RK45 | `rtol`, `atol` | 1e-8, 1e-10 |
| RK4 | `steps` | 1000 |
| Jacobi (autovalores) | `tol` | 1e-14 relativa |
| Durand–Kerner | `tol` | 1e-14 relativa a la cota de Cauchy |
| Pivote nulo (LU) | — | n·eps·max|aᵢⱼ| |

## Cómo se reporta el error

Todo método iterativo devuelve `IterativeResult`:

| Campo | Significado |
|---|---|
| `value` | resultado |
| `converged` | `true` si alcanzó la tolerancia (si no, se lanza `CONVERGENCE_ERROR` en vez de devolver) |
| `iterations` | iteraciones, evaluaciones o pasos según el método |
| `error_estimate` | estimación del error absoluto (ver tabla) |
| `method`, `extra` | nombre del método y datos adicionales (residuo, pasos rechazados…) |

| Método | Cómo se estima el error |
|---|---|
| Bisección | semiancho del intervalo final |
| Newton / secante | último paso \|xₙ₊₁ − xₙ\| |
| Brent | semiancho del intervalo de confianza |
| Derivada (Richardson) | diferencia entre las dos últimas extrapolaciones |
| Simpson adaptativo | suma de \|S₂ − S₁\|/15 de los subintervalos |
| Gauss–Legendre | \|Gₙ − Gₙ₊₁₀\| |
| RK4 | duplicación de paso: \|y_h − y_2h\|/(2⁴ − 1), norma máx. sobre componentes |
| RK45 | suma de los errores locales estimados (cota heurística del global) |
| Durand–Kerner | último paso de Newton; para raíces agrupadas (múltiples), el diámetro del grupo |
| Jacobi | norma de Frobenius de la parte fuera de la diagonal |

El banco de verificación comprueba en varios casos que el error real no supere 10× el estimado
(`check_error_estimate`).

## Unidades

- 7 dimensiones base del SI: L, M, T, I, Θ, N, J. Una unidad es (factor al SI, vector de exponentes).
- Expresiones de unidades con el mismo parser: `kN*m`, `m/s^2`, `N/mm^2`, `kW*h`. Solo `*`, `/` y `^`
  con exponente numérico. `µ` se acepta como `u`.
- Prefijos SI (de `a` a `Y`) solo en unidades que los admiten (`km`, `MPa`, `kcal`; no `kft`).
- Ambigüedades resueltas: `min` = minuto, `h` = hora, `t` = tonelada, `T` = tesla, `kn` = nudo.
- Temperaturas con desplazamiento (`degC`, `degF`, `degR`) solo en conversión directa entre escalas;
  dentro de expresiones compuestas se usa `K`.
- Las constantes imperiales son las definiciones exactas (1 ft = 0.3048 m, 1 lb = 0.45359237 kg,
  1 lbf = 4.4482216152605 N).
