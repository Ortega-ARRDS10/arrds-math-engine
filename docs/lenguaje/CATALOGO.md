# Catálogo de comandos, funciones y propiedades

Registro de **lo que Arrds explica**, paso a paso, de la matemática simple al cálculo. Cada entrada sigue la
ficha de abajo. Las reglas generales están en [ESPECIFICACION.md](ESPECIFICACION.md).

## Ficha

```markdown
### Nombre

- **Estado:** definido | propuesta | implementado
- **Nivel:** 1–9
- **Se escribe:** `\comando{...}`
- **Se renderiza:** cómo se ve (descripción o imagen)
- **Significado:** qué calcula o qué hace en la calculadora
- **Propiedades / comportamiento:** reglas, dominio, casos especiales, qué pasa en 2D/3D
- **Ejemplos:**

  | Entrada | Se ve | Resultado |
  |---|---|---|
  | `...` | ... | ... |

- **Errores:** qué entradas son inválidas y qué mensaje recibe el usuario
- **Notas de Arrds:** lo que haga falta recordar
```

## Índice

| Nivel | Tema | Entradas |
|---|---|---|
| 1 | Aritmética | números, suma y resta, multiplicación, división, potencias y raíces, agrupación, orden de operaciones, otras operaciones, resultado |
| 2 | Álgebra | — |
| 3 | Funciones elementales | — |
| 4 | Trigonometría | — |
| 5 | Exponenciales y logaritmos | — |
| 6 | Geometría 2D | — |
| 7 | Geometría 3D | — |
| 8 | Cálculo | — |
| 9 | Varias variables | — |

---

## 1. Aritmética

Definido por Arrds el 2026-10-30. Los atajos de teclado y opciones mencionados están en
[EDITOR_Y_CONFIGURACION.md](EDITOR_Y_CONFIGURACION.md).

### 1.1 Números

- **Estado:** definido
- **Se escribe:** enteros y decimales con punto (`3`, `2.5`); notación científica solo en forma LaTeX:
  `6.02 \times 10^{23}` (`6.02e23` no es válido).
- **Se renderiza:** igual que se escribe.
- **Resultado:** se muestra en notación científica cuando es muy grande o muy chico (umbral configurable).

### 1.2 Suma y resta

- **Estado:** definido
- **Se escribe:** `a + b`, `a - b`.
- **Doble signo:** `--3` es válido (= 3) pero genera una **advertencia** que recomienda escribir `-(-3)`.
  Una advertencia no bloquea el cálculo: solo sugiere la forma correcta.

### 1.3 Multiplicación

- **Estado:** definido
- **Se escribe:**

  | Entrada | Se ve | Significado |
  |---|---|---|
  | `a \cdot b` | a · b | producto (forma estándar) |
  | `a \times b` | a × b | producto entre números; entre vectores, producto vectorial (nivel 7) |
  | `abc`, `2x`, `2\pi r` | abc, 2x, 2πr | producto implícito, **sin** punto ni cruz visibles |
  | `*` | — | el editor lo reemplaza por `\cdot` al tipearlo o pegarlo (escritura rápida); el texto guardado nunca contiene `*` |

- **Vectores (adelanto, se define en el nivel 7):** `\cdot` = producto escalar, `\times` = producto vectorial.
- **Notas de Arrds:** el `*` es cómodo, pero quien quiera aprender LaTeX debe usar `\cdot`.

### 1.4 División

- **Estado:** definido
- **Se escribe:**

  | Entrada | Se ve | Notas |
  |---|---|---|
  | `\frac{a}{b}` | fracción a sobre b | forma clásica |
  | `2 / 4` | 2 / 4 | `/` válido entre operandos simples |
  | `{24x} / {42y}` | (24x) / (42y) | forma recomendada con operandos compuestos; el render agrega paréntesis porque las llaves son invisibles *(propuesta)* |
  | `1/2x`, `1 / 2x` | 1/(2x) | válido (D15): la multiplicación implícita forma un bloque; advertencia que recomienda `{1}/{2x}` |
  | `2x / 4y` | (2x)/(4y) | válido, misma regla y misma advertencia |
  | `1/2 \cdot x` | 1/2 · x | (1/2)·x: el `\cdot` explícito no forma bloque |
  | `a \div b` | a ÷ b | igual que `/` (mismas reglas) |

### 1.5 Potencias y raíces

- **Estado:** definido
- **Se escribe:** `x^{2}` (llaves obligatorias, D9), `\sqrt{x}`, `\sqrt[n]{x}`.
- **Errores:** `\sqrt{-4}` es error en los reales. El campo complejo se trata en el futuro.

### 1.6 Agrupación

- **Estado:** definido
- **Se escribe:** `( )`, `[ ]` y `\left( \right)` son válidos y equivalentes (no hay ambigüedad: el símbolo que
  abre y el que cierra son distintos, a diferencia de `|`).
- **Escritura rápida:** opción para que al tipear `(` se inserte `\left( \right)`.

### 1.7 Orden de operaciones

- **Estado:** definido
- **Regla:** potencias → multiplicación implícita (`2x`, D15) → multiplicación y división explícitas
  (`\cdot`, `\times`, `/`, `\div`) → suma y resta; a igual nivel, de izquierda a derecha.
- **Ejemplo:** `a \div b \cdot c` se ve igual y se calcula (a ÷ b) · c.

### 1.8 Otras operaciones

- **Estado:** admitidas por Arrds; la forma de escritura es *(propuesta)*.

  | Operación | Se escribe *(propuesta)* | Ejemplo |
  |---|---|---|
  | Factorial | `n!` | `5!` = 120 |
  | Porcentaje | `15\%` | = 0.15 (ver D16) |
  | Resto | `a \bmod b` | `17 \bmod 5` = 2 |
  | MCD | `\gcd{a, b}` | `\gcd{12, 18}` = 6 |
  | MCM | `\operatorname{mcm}{a, b}` | `\operatorname{mcm}{4, 6}` = 12 |
  | Parte entera (piso / techo) | `\lfloor x \rfloor`, `\lceil x \rceil` | `\lfloor 2.7 \rfloor` = 2 |
  | Redondeo | `\operatorname{round}{x}` | `\operatorname{round}{2.5}` = 3 |
  | Valor absoluto | `\left| x \right|` (D7) | `\left| -3 \right|` = 3 |

- **Porcentaje (D16, definido por Arrds):** por defecto **contextual**: `200 + 10\%` = 220 (el 10 % de 200).
  En la configuración puede pasar a ser siempre 0.1 (`200 + 10\%` = 200.1). La regla contextual aplica solo
  cuando el porcentaje se suma o resta directamente (confirmado por Arrds):

  | Entrada | Contextual (por defecto) | Siempre 0.1 |
  |---|---|---|
  | `200 + 10\%` | 220 | 200.1 |
  | `200 - 10\%` | 180 | 199.9 |
  | `200 + 50 + 10\%` | 275 (aplica a todo lo de la izquierda) | 250.1 |
  | `10\% \cdot 50` | 5 (no hay suma: vale 0.1) | 5 |
  | `y = x + 10\%` | y = 1.1x | y = x + 0.1 |

### 1.9 Cómo se muestra el resultado

- **Estado:** definido
- **Regla:** resultado **exacto** con el **decimal al lado**.

  | Entrada | Resultado |
  |---|---|
  | `\frac{1}{3}` | 1/3 ≈ 0.3333 |
  | `\sqrt{8}` | 2√2 ≈ 2.8284 |
  | `2 + 3` | 5 (si el exacto y el decimal coinciden, uno solo) *(propuesta)* |

- Cantidad de decimales: configurable *(propuesta)*.
- Implicación técnica: el resultado exacto lo calcula el motor simbólico (SymPy/SymEngine).

## 2. Álgebra

*(sin entradas todavía)*

## 3. Funciones elementales

*(sin entradas todavía)*

## 4. Trigonometría

*(sin entradas todavía)*

## 5. Exponenciales y logaritmos

*(sin entradas todavía)*

## 6. Geometría 2D

*(sin entradas todavía)*

## 7. Geometría 3D

*(sin entradas todavía)*

## 8. Cálculo

*(sin entradas todavía)*

## 9. Varias variables

*(sin entradas todavía)*
