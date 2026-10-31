# Especificación del subconjunto LaTeX ("LaTeX Arrds")

- **Versión:** 0.2 — borrador (regla de las llaves definida por Arrds)
- **Estado:** todo el documento es *(propuesta)* de Claude hasta que Arrds confirme cada regla. Las
  explicaciones de Arrds en [CATALOGO.md](CATALOGO.md) prevalecen sobre este borrador.

## 1. Objetivo

LaTeX es un lenguaje para **mostrar** matemática, no para calcularla: muchas escrituras son ambiguas. Este
documento define un subconjunto con **una sola interpretación** para cada texto, de modo que lo que se
escribe, lo que se renderiza y lo que se calcula coincidan siempre.

Principios:

1. **Todo texto válido se renderiza tal cual con LaTeX estándar** (MicroTeX/KaTeX). Nada de comandos inventados
   que no se vean bien.
2. **Una sola lectura.** Si un texto admite dos interpretaciones, o la regla lo decide o es un error con
   sugerencia (nunca se adivina en silencio).
3. **Mismo AST** que el parser ASCII del motor (`2x^2 + \sin(x)` y `2x^2 + sin(x)` producen el mismo árbol).
4. **Errores pedagógicos:** posición exacta y un `hint` que explique cómo escribirlo bien.

## 2. Léxico

| Elemento | Forma | Ejemplos |
|---|---|---|
| Número | dígitos, punto decimal, notación científica con `\times 10^{n}` | `3`, `2.5`, `6.02 \times 10^{23}` |
| Variable | **una letra** latina o griega, con subíndice opcional entre llaves | `x`, `t`, `\theta`, `x_{1}`, `a_{n}`, `v_{\text{max}}` |
| Etiqueta | `\text{...}` dentro de un subíndice: texto recto, parte del nombre | `x_{\text{max}}`, `T_{\text{amb}}` |
| Nombre largo | `\mathrm{...}` o `\operatorname{...}` | `\mathrm{masa}` |
| Función predefinida | comando con barra | `\sin`, `\cos`, `\ln`, `\log`, `\exp`, `\sqrt` |
| Constantes | `\pi`, `e`, `i`, `\infty` | ver §6 |
| Agrupación | `( )`, `\left( \right)`, `[ ]`, `\{ \}`, `{ }` (grupo LaTeX) | |
| Espacios | ` `, `\,`, `\;`, `\!`, `\quad` | se ignoran para el cálculo |

**Regla clave:** fuera de `\mathrm{}`, letras seguidas son **producto de variables**: `xy` = x·y,
`abc` = a·b·c. Por eso `sin x` sin barra es s·i·n·x, y el parser debe sugerir `\sin x`.

## 3. Operadores y precedencia

De menor a mayor:

| Nivel | Operadores | Asociatividad |
|---|---|---|
| 1 | `=`, `<`, `>`, `\le`, `\ge`, `\ne` (relaciones, ver §5) | no asociativa |
| 2 | `+`, `-` | izquierda |
| 3 | `\cdot`, `\times`, `/`, `\frac`, multiplicación implícita | izquierda |
| 4 | signo unario `-` | — |
| 5 | potencia `^{...}` | **derecha**: `2^{3^{2}}` = 2⁹ |
| 6 | factorial `!`, prima `'` | postfijo |

- `-x^{2}` = −(x²), igual que en el motor actual.
- `^` y `_` exigen llaves siempre (§4, D9): `x^23` es error; se escribe `x^{23}` o `x^{2}3`.
- `\frac{a}{b}` es una división ya agrupada; no necesita paréntesis.

## 4. Regla de las llaves: el argumento va entre `{ }` (definido por Arrds, 2026-10-30)

**Regla:** toda función lleva su argumento **entre llaves**. Sin llaves no hay argumento: es un error con
sugerencia. Ejemplo de Arrds: `a \sin x` no es válido; se escribe `a \sin{x}`.

| Escritura | Lectura |
|---|---|
| `\sin{x}` | sen(x) |
| `\sin{2x}` | sen(2x) |
| `\sin{2}x` | sen(2)·x |
| `a\sin{x}` | a·sen(x) |
| `\sin{x}\cos{x}` | sen(x)·cos(x) |
| `\sin x` | **error**: "escribí `\sin{x}`" |
| `\sin(x)` | **error** (D8, definido por Arrds): "En Arrds el argumento va entre llaves: `\sin{x}`. Los paréntesis los agrega la calculadora al mostrarlo." |
| `\sin{(x+1)}` | válido: los paréntesis dentro de las llaves solo agrupan (redundantes) |
| `x^{2}`, `e^{-t}` | potencia; llaves **obligatorias** aunque sea un carácter (D9, definido por Arrds) |
| `x^2` | **error**: "escribí `x^{2}`" |
| `x_{1}`, `v_{0}`, `a_{n}` | variable con **subíndice índice**: un número o una letra, en cursiva; llaves obligatorias (D9) |
| `x_{\text{max}}`, `v_{\text{inicial}}` | variable con **subíndice etiqueta** (`\text{}`, idea de Arrds): letra recta, es parte del nombre y nunca se calcula |
| `x_{max}` | **error** (D11, definido por Arrds): "si es una etiqueta, escribí `x_{\text{max}}`; si son índices, separalos con coma: `x_{m,a,x}`". Sin `\text` las letras en cursiva son símbolos matemáticos |
| `a_{i,j}` | **índices múltiples**: la escritura con coma está definida (es la que sugiere el error de `x_{max}`); su significado (p. ej. elemento de una matriz) queda **pendiente (D13)** |

**Todo subíndice crea una variable distinta** (definido por Arrds): `x`, `x_{1}`, `x_{n}` y `x_{\text{max}}` son
cuatro variables independientes; definir `x = 3` no le da valor a `x_{\text{max}}`.
| `x_max` | **error**: en LaTeX el subíndice tomaría solo la "m" (se vería x_m·ax) |
| `\sin^{2}{x}` | (sen x)² *(propuesta)*; `\sin^{-1}{x}` = arcsen x *(propuesta)* |
| `\log_{2}{x}`, `\sqrt[3]{x}` | logaritmo en base 2, raíz cúbica *(propuesta)* |

**Escritura estricta, render con paréntesis** (definido por Arrds, 2026-10-30): las llaves son la única
forma de escribir el argumento, para que el usuario aprenda una sola notación; los paréntesis son solo
del render. Las llaves son invisibles en LaTeX (`\sin{x+1}` se vería "sin x + 1"), así que la calculadora no
muestra el texto tal cual: lo regenera desde el árbol y **siempre** pone el argumento entre paréntesis.

| Escribís | Se ve |
|---|---|
| `\sin{x}` | sin(x) |
| `\sin{2x}` | sin(2x) |
| `\sin{x+1}` | sin(x + 1) |
| `a\sin{x}` | a sin(x) |

Nota pedagógica: en LaTeX estándar `\sin(x)` es válido (`\sin` no tiene argumento obligatorio y las llaves
solo agrupan). La exigencia de llaves es una **regla de Arrds**, más estricta que LaTeX; los mensajes de
error deben decirlo así.

**Multiplicación implícita** (sin cambios): `2x`, `2\pi r`, `xy`, `2(x+1)`, `(a)(b)` son productos. `f(x)` es
aplicación si `f` está **definida como función**; si no, producto f·(x).

## 5. Tipos de entrada (lo que el usuario escribe en una línea)

| Forma | Interpretación propuesta |
|---|---|
| `2 + 3 \cdot 4` | expresión: se evalúa |
| `a = 3` | definición de variable o parámetro (deslizador) |
| `f(x) = x^{2}` | definición de función |
| `y = 2x + 1` | curva explícita en 2D |
| `x^{2} + y^{2} = 1` | curva implícita en 2D |
| `z = x^{2} + y^{2}` | superficie en 3D |
| `y > x^{2}` | región (inecuación) |

El comportamiento exacto de cada tipo (qué se dibuja, cómo se nombran los objetos) lo define Arrds.

## 6. Constantes y nombres reservados

`\pi`, `e` (número de Euler), `\infty`: no se pueden redefinir; `e = 5` es error (D2).
`i`: por ahora índice o variable; en el campo complejo será la unidad imaginaria y no podrá ser variable (D14).

## 7. Cálculo (reservado; se especifica al llegar a ese nivel)

Formas previstas, a confirmar en el catálogo:

`f'(x)`, `f''(x)`, `\frac{\mathrm{d}}{\mathrm{d}x} f(x)`, `\frac{\mathrm{d}y}{\mathrm{d}x}`,
`\frac{\partial f}{\partial x}`, `\int f(x)\,\mathrm{d}x`, `\int_{a}^{b} f(x)\,\mathrm{d}x`,
`\lim_{x \to a} f(x)`, `\sum_{n=1}^{N} a_{n}`, `\prod`, `\nabla f`.

El diferencial siempre es `\mathrm{d}` (D3). Cómo se aplica la regla de las llaves a estas formas se define
al llegar a este nivel.

## 8. Decisiones abiertas

| Id | Pregunta | Propuesta de Claude |
|---|---|---|
| D1 | ~~`\sin 2x`: ¿sen(2x) o sen(2)·x?~~ | **Resuelta por Arrds:** regla de las llaves (§4) |
| D2 | ~~¿Se pueden redefinir `e`, `i`, `\pi`?~~ | **Resuelta por Arrds:** no; son constantes y en la universidad no se usan como variables. `e = 5` es error (para `i`, ver D14) |
| D3 | ~~¿Cuándo `d` es diferencial y cuándo variable?~~ | **Resuelta por Arrds:** el diferencial se escribe `\mathrm{d}` (d recta, ISO 80000): `\mathrm{d}y`, `\frac{\mathrm{d}y}{\mathrm{d}x}`, `\int{f}\,\mathrm{d}x`; `d` en cursiva siempre es variable. El editor ofrece un atajo que inserta `\mathrm{d}`. (Se descartó `\d{y}`: `\d` ya existe en LaTeX y falla en fórmulas) |
| D4 | ~~¿Ángulos en radianes o grados?~~ | **Resuelta por Arrds:** radianes por defecto; grados se activan en la configuración; la calculadora muestra **siempre** un indicador RAD/DEG visible |
| D5 | ~~¿Coma decimal o punto?~~ | **Resuelta por Arrds:** punto decimal; la coma separa coordenadas `(x, y, z)`, elementos de conjuntos `\{1, 2\}`, argumentos e índices |
| D6 | ~~`\log`: ¿natural o base 10?~~ | **Resuelta por Arrds:** `\ln{x}` natural, `\log{x}` base 10, `\log_{b}{x}` base b con llaves en base y argumento (`\log_{2}{x}`, `\log_{\frac{1}{2}}{x}`, `\log_{b}{x}`); la base debe ser > 0 y ≠ 1. El motor Python se alinea: `log` pasa a ser base 10 en todos lados (opción a, §9) |
| D7 | ~~¿Cómo se escribe el valor absoluto?~~ | **Resuelta por Arrds:** solo `\left| x \right|` (`|x|` es error por ambiguo al anidarse). Atajo del editor al tipear `|` *(propuesta)* |
| D8 | ~~¿`\sin(x)`, con paréntesis, se acepta igual que `\sin{x}`?~~ | **Resuelta por Arrds:** no; solo `\sin{x}`. Los paréntesis son del render (§4) |
| D9 | ~~¿Llaves obligatorias también en potencias y subíndices (`x^2`, `x_1`)?~~ | **Resuelta por Arrds:** sí, siempre (ejemplo: `x_{max}`) (§4) |
| D10 | ~~En sucesiones (`a_{n+1}`), ¿el subíndice se calcula?~~ | **Resuelta por Arrds:** con `\text{}` nunca (etiqueta); sin `\text`, se calcula solo al definir sucesiones (nivel 8) |
| D11 | ~~¿Un subíndice de varias letras exige `\text{}` (`x_{max}` → error)?~~ | **Resuelta por Arrds:** sí, error con sugerencia (aunque LaTeX lo renderice) |
| D13 | ¿Qué significan los índices múltiples (`a_{i,j}`): elemento de matriz, sucesión doble…? | **Pendiente para el futuro** (Arrds, 2026-10-30). La escritura con coma ya está definida; `a_{ij}` es error por D11 |
| D15 | ~~`1/2x`: ¿(1/2)·x o 1/(2x)?~~ | **Resuelta por Arrds:** 1/(2x). **La multiplicación implícita liga más fuerte que `/` y `\div`** (sin depender de espacios, que son invisibles en el render): `1/2x` = `1 / 2x` = 1/(2x); el render muestra 1/(2x) y una advertencia recomienda `{1}/{2x}`. El `\cdot` explícito no forma bloque: `1/2 \cdot x` = (1/2)·x |
| D16 | ~~`200 + 10\%`: ¿220 o 200.1?~~ | **Resuelta por Arrds:** por defecto el porcentaje es **contextual** (`200 + 10\%` = 220); en la configuración puede pasar a ser siempre 0.1. Precisión (confirmada por Arrds): la regla contextual aplica solo cuando el porcentaje se suma o resta directamente (`a \pm p\%` = a·(1 ± p/100), con `a` = todo lo de la izquierda); en otro caso `p\%` = p/100 |
| D12 | ~~¿`\text{}` fuera de subíndices?~~ | **Resuelta por Arrds:** `\text{}` es **notación, nunca cálculo**: nada de su interior es variable. Se usa para etiquetas (en subíndices) y para **unidades** (`3\,\text{m/s}`). Mecanismo (confirmado por Arrds): el significado depende de la posición: dentro de un subíndice → etiqueta; después de una cantidad → unidad, que se interpreta con el módulo de unidades (`m` = metro, no la variable m); en otra posición → error |
| D14 | ~~¿`i` como índice o variable?~~ | **Resuelta por Arrds:** por ahora `i` se usa como índice o variable (`x_{i}`, `\sum_{i=1}^{n}`). Al llegar al campo complejo se separa el significado: ahí `i` es la unidad imaginaria y no se permite como variable |

**Nota D7 (valor absoluto):** la pregunta es cómo se escribe |x|. LaTeX ofrece tres formas que se ven casi
igual: `|x|` (barras simples), `\left| x \right|` (barras que crecen con el contenido, p. ej. alrededor de una
fracción) y `\lvert x \rvert`. Las barras simples son ambiguas al anidarse: `|a|b|c|` puede ser |a|·b·|c| o
|a·|b|·c|, porque la misma barra abre y cierra. Siguiendo el criterio de "una sola forma", la propuesta es
aceptar solo `\left| x \right|` (abre y cierra explícitamente, como las llaves) y que el editor la inserte
con un atajo al tipear `|`.

## 9. Impacto en el motor actual

- **`log` (D6, opción a, decidido por Arrds):** el parser ASCII del motor Python (`arrds_math/expr`) pasa a
  `log(x)` = base 10, igual que `\log{x}`. Cambia el contrato JSON: hay que actualizar el evaluador, la derivada
  simbólica, `to_latex`, los casos del banco, los tests y
  [CONVENCIONES_NUMERICAS.md](../CONVENCIONES_NUMERICAS.md). Tarea registrada en [TAREAS.md](../TAREAS.md).
- **Multiplicación implícita (D15):** el parser ASCII del motor Python lee `1/2x` como (1/2)·x (la implícita
  tiene la misma precedencia que `*`). En LaTeX Arrds es 1/(2x). Hay que decidir si el parser ASCII adopta la
  misma regla, para que ambos produzcan el mismo AST.
- **Grados (D4):** la configuración cambia el resultado de un mismo texto (`\sin{30}`); por eso el indicador
  RAD/DEG es obligatorio. *(Propuesta)*: el AST guarda la unidad angular explícitamente.
