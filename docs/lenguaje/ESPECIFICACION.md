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
cuatro variables independientes; `x = 3` no le da valor a `x_{\text{max}}`.
| `x_max` | **error**: en LaTeX el subíndice tomaría solo la "m" (se vería x_m·ax) |
| `\sin^{2}{x}` | (sen x)²: exponente positivo pegado a la función = potencia del valor |
| `\sin^{-1}{x}` | arcsen x, igual que `\arcsin{x}`: exponente -1 pegado a la función = inversa (Arrds, catálogo 3.4) |
| `(\sin{x})^{-1}` | 1/sen x: recíproco |
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

## 5. Objetos y etiquetas (definido por Arrds, 2026-10-30)

**Regla:** cada línea que escribe el usuario es un **objeto** con una **etiqueta** (su tipo), asignada según
sus características y propiedades. La etiqueta determina qué **acciones** ofrece la calculadora sobre ese
objeto, y los objetos pueden **interactuar con otras expresiones** (Arrds).

**Bloques y propiedades** (concepto de Arrds; el funcionamiento práctico lo explica más adelante):

- Un **bloque** es una **celda** de la lista de expresiones, como en GeoGebra y Desmos (Arrds, 2026-10-30):
  un panel lateral con celdas numeradas, cada una con su expresión, y el gráfico al costado. El significado
  de una misma escritura depende del contexto: si está dentro de un bloque junto a otras expresiones o fuera
  de él.
- Las celdas se organizan en **grupos de celdas** (Arrds, 2026-10-30). "En el mismo bloque" significa **en el
  mismo grupo**: las expresiones de un grupo pueden interactuar entre sí. A diferencia de las carpetas de Desmos,
  que solo ordenan visualmente, el grupo es un **ámbito**: limita dónde vale una definición.
- Alcance de las definiciones (independiente o estándar), excepciones, regla de no interferencia, grupos
  anidados, pestañas y ventanas gráficas: ver [CELDAS_Y_DOCUMENTOS.md](CELDAS_Y_DOCUMENTOS.md).
- Cada bloque tiene **propiedades**, donde el usuario puede cambiar la etiqueta y asignar acciones.

**Interpretación de `x = 3`** (D17 y D27, definido por Arrds): siempre es una **recta o un plano**, nunca asigna un
valor a `x`. Interactúa con otras expresiones solo si el usuario lo pide con un **botón**.

| Contexto | Ejemplo | Resultado |
|---|---|---|
| Vista 2D | `x = 3` | recta vertical x = 3 |
| Vista 3D | `x = 3` | plano x = 3 (depende del plano de trabajo, p. ej. xy o xz) |
| Botón de interacción con `f(x) = x^{2}` | `x = 3` | intersección: el punto (3, 9) |
| Botón de interacción con `f(x,y) = x^{2} + y^{2}` | `x = 3` | intersección: la curva f(3, y) = 3² + y² |
| Varias a la vez | `x = 4`, `x = e` en el mismo grupo | válido: son rectas o planos distintos y pueden interactuar con una o varias funciones. No viola la regla de no interferencia, porque no son definiciones |
| Para evaluar | `x_{\text{max}} = 3` y `f(x_{\text{max}})` | usar otra variable: da el valor al lado (D24) |
| Otra letra usada como eje | `t = x^{2}` y `t = 3` en el grupo | `t = 3` es una recta horizontal que puede interactuar con otras expresiones; una letra que es eje no se puede definir. Si `t` no es eje de nada, `t = 3` es una definición (D28) |
| En una ecuación | `2x + 3 = 8` | `x` es una variable común (incógnita); al lado aparece la solución `x = 2.5`, y el usuario tiene la **opción de ubicarla en un plano de ejes cartesianos** (Arrds) |

Así, `x`, `y`, `z` suelen ser variables de los ejes, pero no están reservadas: el contexto decide.

Etiquetas nombradas por Arrds: **función, ecuación, definición, punto, vector, matriz, plano, superficie,
superficie de nivel** (la lista crece con los niveles).

**Punto** (etiqueta agregada por Arrds; escritura *(propuesta)*): `(2, 3)` en 2D, `(1, 2, 3)` en 3D, con nombre
`A = (2, 3)` (mayúscula, como en geometría). Usa la coma como separador de coordenadas (D5). `(a, b)` es
punto por defecto; si es un intervalo abierto, se le cambia la etiqueta (D20).

| Forma | Etiqueta | Comportamiento |
|---|---|---|
| `a = 3` | definición | asigna el valor a la variable; se puede **fijar** el valor o convertirlo en **deslizador** (Arrds) |
| `y = 2x + 1` | función (curva) | se grafica (Arrds) |
| `2x + 3 = 7` | ecuación | se resuelve, en automático o con un comando; la ecuación se mantiene y **al lado** se muestra el resultado `x = 2` (Arrds) |
| `2 + 3 \cdot 4` | expresión | se evalúa *(propuesta)* |
| `f(x) = x^{2}` | función | definición con nombre; puede generar una gráfica (Arrds, §5.1) |
| `x^{2} + y^{2} = 1` | curva implícita (D18) | se grafica |
| `x^{2} + y^{2} + z^{2} = 1` | superficie de nivel (D18) | se grafica en 3D |
| `z = x^{2} + y^{2}` | superficie *(propuesta)* | se grafica en 3D |
| `y > x^{2}` | región *(propuesta)* | se define en el nivel 2 (inecuaciones) |

Las acciones concretas de cada etiqueta se registran en el [catálogo](CATALOGO.md) al llegar a su nivel.

### 5.1 Resolución de nombres: función o producto

Pregunta de Arrds (2026-11-01): ¿cómo entiende el motor que `f(x)` es una función y no f·(x)? Mecanismo
*(propuesta)*: cada grupo tiene una **tabla de nombres**, y el análisis se hace en dos pasos.

1. **Definición, por la forma:** `nombre(v1, v2, ...) = expresión`, con variables simples y distintas entre los
   paréntesis, define una función y la anota en la tabla.
2. **Uso, por la tabla:** `f(...)` es aplicación si `f` figura como función; si no, es producto.

| Escritura | Tabla | Lectura |
|---|---|---|
| `f(2)` | `f` es función | aplicación |
| `a(x+1)` | `a` es variable o no está | producto a·(x + 1) |
| `a(x+1) = 5` | argumento no simple | ecuación, no define nada |
| `f(x) = x^{2}` con `f = 3` en el grupo | `f` ya es variable | error: nombre en uso |

`f` debe existir en el grupo para usarla. Su celda no necesita estar más arriba, aunque es lo recomendado; las
dependencias circulares son error (D23).

**Paréntesis en funciones del usuario:** `f(x)` lleva paréntesis, no llaves. No contradice la regla de §4: `\sin` es
un comando de LaTeX, mientras que `f{x}` se vería "fx", igual que un producto.

### 5.2 Variables libres y ejes

Regla (confirmada por Arrds, 2026-11-01): se cuentan las **variables libres**, es decir, las letras que no están
definidas en el grupo. Así, `a = b + 1` se grafica en ejes a-b si ninguna está definida, y es una definición de
`a` si `b` lo está.

| Entrada | Libres | Etiqueta | Ejes |
|---|---|---|---|
| `2x + 3 = 7` | 1 | ecuación | se resuelve |
| `y = x^{2}` | 2 | ecuación y función (Arrds) | x horizontal, y vertical |
| `t = x^{2}` | 2 | ecuación y función (Arrds) | x horizontal, t vertical |
| `f(x) = x^{2}` | 1 + valor | función | misma gráfica que `y = x^{2}` (Arrds) |
| `f(x, y) = x^{2} + y^{2}` | 2 + valor | función | superficie, x-y-z |

Un objeto puede tener **más de una etiqueta**: `y = x^{2}` es ecuación y función a la vez (Arrds).

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
| D17 | ~~`x = 3`: ¿definición o recta vertical?~~ | **Resuelta por Arrds, corregida por D27:** siempre recta o plano según la vista 2D/3D; en una ecuación, `x` es una incógnita (§5) |
| D18 | ~~¿Ecuación con varias variables: ecuación o curva?~~ | **Resuelta por Arrds:** solo `x, y` → curva implícita; `x, y, z` → superficie de nivel; el usuario puede cambiar la etiqueta a mano. **Corregida el 2026-11-01:** "otras letras → ecuación" ya no vale, porque `t = x^{2}` se grafica en ejes x-t (§5.2) |
| D23 | ~~"Definir antes": ¿la celda de `f` debe estar más arriba que su uso?~~ | **Resuelta por Arrds:** basta con que exista en el grupo, porque mover una celda no debe romper el documento; tenerla más arriba es lo **recomendado**. Las dependencias circulares son error |
| D24 | ~~Con `x = 3` en el grupo, ¿cuánto da `f(2)`?~~ | **Resuelta por Arrds:** `f(2)`, `f(5)` o `f(x_{\text{max}})` con `x_{\text{max}} = 3` dan el valor al lado. `x = 3` no asigna: genera su gráfica, que se puede intersecar con la de f |
| D25 | ~~`g(x, y, z)`: ¿cómo se grafica?~~ | **Resuelta por Arrds:** no se grafica directo: superficies de nivel g = c, con c como deslizador; además, **mapa de calor sobre planos de corte móviles** (idea de Arrds). *(Propuesta)*: también sobre superficies de nivel, con escala visible y mapas perceptualmente uniformes (viridis) |
| D26 | ~~¿Dominio e imagen se muestran solos o con botón?~~ | **Resuelta por Arrds:** dominio solo; imagen con botón "analizar", porque calcularla puede fallar en funciones complicadas |
| D27 | ~~¿`f(3, y)` sale de sustituir o de intersecar?~~ | **Resuelta por Arrds:** de intersecar, **con un botón**. `x = 3` es siempre recta o plano; pueden convivir varias (`x = 4`, `x = e`) e interactuar con una o varias funciones |
| D28 | ~~`t = 3` en un grupo donde `t = x^{2}` usa `t` como eje: ¿recta o definición?~~ | **Resuelta por Arrds:** recta horizontal, que puede interactuar con otras expresiones. Si `t` no es eje de nada, `t = 3` es una definición |
| D29 | ~~`\sin^{-2}{x}` y `f^{2}(x)`: ¿qué significan?~~ | **Resuelta por Arrds:** error con sugerencia y con el **motivo** en el mensaje (mensajes en el catálogo 3.4) |
| D19 | ~~¿La ecuación se resuelve sola o con un comando?~~ | **Resuelta por Arrds:** sola por defecto (desactivable en la configuración) y con botón "resolver" |
| D20 | ~~`(2, 3)`: ¿punto o intervalo abierto?~~ | **Resuelta por Arrds:** se distingue por la **etiqueta**: `(a, b)` es un punto por defecto, y el usuario puede etiquetarlo como intervalo. La escritura no cambia |
| D21 | ~~Sistema con menos ecuaciones que incógnitas: ¿error?~~ | **Resuelta por Arrds:** no es error; se informa la clasificación del sistema (compatible determinado, compatible indeterminado con solución paramétrica, incompatible) (catálogo 2.5) |
| D22 | ~~El decimal del resultado, ¿con `=` o con `≈`?~~ | **Resuelta por Arrds:** `≈` cuando es aproximado (√8 ≈ 2.83); `=` solo si es exacto (catálogo 2.7) |
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
- **Multiplicación implícita (D15):** el parser ASCII del motor Python adoptó la regla (decisión de Arrds,
  2026-10-30): `1/2x` = 1/(2x) en ambos lenguajes.
- **Grados (D4):** la configuración cambia el resultado de un mismo texto (`\sin{30}`); por eso el indicador
  RAD/DEG es obligatorio. *(Propuesta)*: el AST guarda la unidad angular explícitamente.
