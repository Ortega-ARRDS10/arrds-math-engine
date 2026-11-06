# Política de uso

## Alcance

El motor cubre cálculo simbólico básico, métodos numéricos clásicos, álgebra lineal densa, polinomios,
estadística descriptiva, análisis vectorial, señales/funciones de transferencia y unidades, con el nivel de
Matemática B, C y D de ingeniería. Está pensado para **aprendizaje y verificación de cálculos de
ingeniería**.

## Límites de validez

- Aritmética de **doble precisión** (float64, ~15–16 cifras). No hay precisión arbitraria ni aritmética
  exacta de racionales en la v0.1.
- La simplificación simbólica es conservadora y no es un CAS completo (no integra simbólicamente, no
  factoriza, no resuelve ecuaciones simbólicas).
- EDO: solo métodos explícitos; los sistemas **rígidos** pueden fallar o ser muy lentos.
- Autovalores: solo matrices **simétricas**.
- Raíces múltiples de polinomios: precisión reducida (~eps^(1/m)); el error estimado lo refleja.
- Álgebra lineal pensada para matrices chicas y medianas (≤ 200×200 vía API).
- El error estimado es una **estimación**, no una cota rigurosa (salvo en bisección).

## Responsabilidad profesional

Los resultados no sustituyen el criterio de un profesional. Para cálculos **críticos** (estructurales,
de seguridad, aeronáuticos, médicos) verificá siempre con un método independiente, revisá unidades y
órdenes de magnitud, y leé `converged` y `error_estimate` antes de usar un número. El software se ofrece
"tal cual", sin garantía de ningún tipo.

## Privacidad (local-first)

- El motor corre **íntegramente en la máquina del usuario**: no hace peticiones de red, no tiene
  telemetría y no guarda datos.
- El panel de pruebas escucha solo en `127.0.0.1` y no carga recursos externos. Recuerda la última
  operación abierta en el `localStorage` del navegador, nada más.

## Licencia

El proyecto es **código abierto bajo la Mozilla Public License 2.0** (MPL-2.0); el texto completo está en
[`LICENSE`](../LICENSE) y la decisión, en el [ADR 0005](adr/0005-licencia-mpl.md).

En pocas palabras (resumen informativo; lo que vale es el texto de la licencia):

- Podés usar, copiar, modificar y distribuir el código, también en proyectos comerciales.
- Si distribuís archivos de este proyecto **modificados**, tenés que publicar esos archivos bajo MPL-2.0.
- Podés combinarlo con código propio bajo otra licencia, incluso cerrado, en un producto mayor.
- Se ofrece "tal cual", sin garantía.
