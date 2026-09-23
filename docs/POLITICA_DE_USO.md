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

**Decisión pendiente de Arrds: tiene que tomarse antes de publicar o aceptar contribuciones.** Sin archivo
`LICENSE` el código queda con todos los derechos reservados, aunque el repositorio sea público.

Propuesta: **MPL-2.0**.

| Opción | A favor | En contra |
|---|---|---|
| **MPL-2.0** (propuesta) | Las mejoras a los archivos del motor vuelven a ser abiertas, pero Arrds Studio (pago único) puede incluirlo sin abrir su propio código. | Menos conocida; exige publicar los archivos del motor modificados. |
| Apache-2.0 | Muy adoptada, con concesión de patentes, compatible con uso comercial. | Un tercero puede cerrar una versión mejorada del motor. |
| MIT | Máxima simplicidad. | Igual que Apache, sin cláusula de patentes. |
| AGPL-3.0 | Máxima reciprocidad. | Complica incluirlo en un producto de pago único cerrado. |

Los documentos de [contexto/](contexto/) también incluyen material personal (guías de aprendizaje,
análisis de herramientas, datos de sponsors): revisá si querés que sean públicos antes de publicar el
repositorio.
