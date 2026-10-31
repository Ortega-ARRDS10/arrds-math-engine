# Fuentes bibliográficas

Material de referencia para definir el lenguaje de la calculadora, los métodos del motor y los casos del
banco de verificación. Los libros están en la biblioteca personal de Arrds (fuera del repositorio).

## Política de uso (el repositorio es público, bajo MPL-2.0)

| Uso | ¿Se puede? |
|---|---|
| Consultar los libros localmente para decidir temas, orden y alcance de cada nivel del catálogo | Sí |
| Tomar un resultado matemático y escribir **nuestro propio** caso de prueba o ejemplo, citando la fuente | Sí: los hechos matemáticos no tienen copyright y la cita es legítima |
| Subir PDFs, sus conversiones a `.md`, o copiar enunciados, explicaciones o ejemplos textuales | **No**: reproducción de obras con copyright |
| Incorporar texto de material con licencia abierta | Solo si la licencia es compatible con MPL-2.0 (las **no comerciales**, como CC BY-NC-SA, **no** lo son) |

**Cómo citar** en el campo `reference` de un caso del banco: `Autor, título corto, edición, ej./sección`.
Ejemplo: `"reference": "Stewart, Calculus ET, 8.ª ed., ej. 2.3.15"`.

## Cómo el material da robustez al motor

1. **Valores de referencia independientes:** cada caso del banco puede contrastarse con el resultado de un libro;
   un mismo problema resuelto en dos libros da doble verificación.
2. **Análisis de error:** los libros de análisis numérico describen el error de cada método; sirven para
   validar que el `error_estimate` del motor sea honesto.
3. **Casos límite:** los ejercicios "difíciles" de los libros (singularidades, raíces múltiples, sistemas mal
   condicionados) son los que rompen motores ingenuos.
4. **Alcance y orden de los niveles del catálogo**, alineados con las materias de la UNLP.

## Bibliografía por nivel del catálogo y módulo del motor

### Niveles 1–5: aritmética, álgebra, funciones, trigonometría, exponenciales y logaritmos (D1001)

- Di Domenicantonio, Lubomirsky y Rivera — *Matemática inicial para Ingeniería* (ed. 2025, UNLP)
- Stewart, Redlin, Watson — *Precálculo: Matemáticas para el cálculo*, 6.ª y 7.ª ed. (también en inglés, 7.ª ed.)
- Swokowski, Cole — *Álgebra y trigonometría con geometría analítica*, 12.ª y 13.ª ed. (también en inglés, 12.ª ed.)

### Nivel 8: cálculo — Matemática A y B

- Búcari, Langoni y Vallejo — *Cálculo diferencial*, 1.ª ed. (UNLP)
- Stewart — *Calculus: Early Transcendentals*, 8.ª ed.
- Thomas, Weir, Hass — *Thomas' Calculus: Early Transcendentals*, 13.ª ed.; Thomas, Hass, Heil, Weir — *Thomas' Calculus*, 14.ª ed.
- Larson, Edwards — *Calculus*, 12.ª ed. (Int. Metric) y *Calculus: Early Transcendental Functions*, 5.ª ed.
- Smith, Minton — *Calculus: Early Transcendental Functions*, 4.ª ed.

### Nivel 9 y Matemática C: varias variables, cálculo vectorial (`vector`)

- Los textos de cálculo anteriores (capítulos de varias variables y cálculo vectorial)
- Kreyszig — *Advanced Engineering Mathematics*, 10.ª ed.
- Riley, Hobson, Bence — *Mathematical Methods for Physics and Engineering*, 3.ª ed.

### Ecuaciones diferenciales (`numeric.solve_ivp`, Matemática B–D)

- Zill — *A First Course in Differential Equations with Modeling Applications*, 10.ª ed. / *Ecuaciones diferenciales con aplicaciones de modelado*, 9.ª ed.
- Edwards, Penney (y Calvis) — *Differential Equations and Boundary Value Problems*, 5.ª ed. / en español, 4.ª ed.; *Elementary Differential Equations*, 6.ª ed.
- Boyce, DiPrima, Meade — *Elementary Differential Equations and Boundary Value Problems*, 11.ª ed.
- Nagle, Saff, Snider — *Fundamentals of Differential Equations*, 9.ª ed.
- Naón, Rossignoli y Santangelo — *Ecuaciones diferenciales en Física*, 1.ª ed. (UNLP)

### Análisis complejo, Fourier, Laplace (`signals`, Matemática D)

- Brown, Churchill — *Complex Variables and Applications*, 8.ª y 9.ª ed.
- Brown, Churchill — *Fourier Series and Boundary Value Problems*, 8.ª ed.
- Kreyszig (ver arriba)

### Álgebra lineal (`linalg`)

- Grossman, Flores Godoy — *Álgebra lineal*, 7.ª ed.

### Métodos numéricos (`numeric`, análisis de error)

- Burden, Faires (Burden) — *Numerical Analysis*, 9.ª ed. (la 10.ª está escaneada, sin texto)
- Chapra, Canale — *Métodos numéricos para ingenieros*, 7.ª ed.
- Hamming — *Numerical Methods for Scientists and Engineers*, 2.ª ed. (escaneado, sin texto)

### Probabilidad y estadística (`stats`)

- Montgomery, Runger — *Applied Statistics and Probability for Engineers*, 7.ª ed.
- Devore — *Probability and Statistics for Engineering and the Sciences*, 9.ª ed.
- Walpole, Myers — *Probabilidad y estadística para ingeniería y ciencias*, 9.ª ed.

### Escritura matemática (mensajes de error, explicaciones paso a paso)

- Halmos — *How to Write Mathematics*; Ewing — *How to Write Mathematics* (trad. Navarro Saad)
- Vivaldi — *Mathematical Writing*
- Velleman — *How to Prove It*, 3.ª ed.; Chartrand, Polimeni, Zhang — *Mathematical Proofs*, 4.ª ed.

## Material de la UNLP: licencias a verificar

Pueden tener licencia abierta; hay que revisar la página de créditos de cada uno antes de usar algo más que citas.

| Material | Licencia |
|---|---|
| *Matemática inicial para Ingeniería* (Di Domenicantonio, Lubomirsky, Rivera) | *por verificar* |
| *Cálculo diferencial* (Búcari, Langoni, Vallejo) | *por verificar* |
| *Ecuaciones diferenciales en Física* (Naón, Rossignoli, Santangelo) | *por verificar* |
| Cuadernillos de cátedra de Matemática A, B, C y D | *por verificar* |
