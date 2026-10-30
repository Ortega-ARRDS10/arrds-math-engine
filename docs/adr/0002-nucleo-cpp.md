# ADR 0002 — Núcleo del motor en C++20; Python como implementación de referencia

- **Estado:** propuesto — se acepta o se corrige después del spike descrito abajo
- **Fecha:** 2026-10-30
- **Relacionado:** [ADR 0001](0001-implementacion-de-referencia-stdlib.md), [especificación LaTeX](../lenguaje/ESPECIFICACION.md)

## Contexto

Arrds va a construir con el motor una calculadora gráfica interactiva al estilo GeoGebra: cálculo, espacios
2D y 3D, entrada y salida en LaTeX, interfaz en Qt 6 / C++ (como fijan los documentos de contexto).

Una calculadora interactiva evalúa expresiones millones de veces por segundo: cada deslizador que se mueve
recalcula miles de puntos por curva y por cuadro; las curvas implícitas y las superficies 3D evalúan grillas
enteras. El presupuesto es ~16 ms por cuadro (60 FPS).

El motor actual es Python (stdlib + SymPy). Para ese camino de ejecución es 50–100× más lento por
evaluación que C++, y llamarlo por punto a través de pybind11 suma costo y queda limitado por el GIL.

## Opciones

1. **Todo en Python** detrás de pybind11. Lo más rápido de escribir; no alcanza los 60 FPS en gráficas densas.
2. **Todo en C++**, incluido un CAS propio. Máximo rendimiento; reimplementar integración simbólica y límites
   no es razonable.
3. **C++ con CAS GPL** (Giac, el que usa GeoGebra; o GiNaC). Muy completo, pero la GPL obliga a liberar
   Arrds Studio entero: incompatible con el modelo de pago único.
4. **Híbrido por camino de ejecución**: lo que corre por punto o por cuadro en C++; lo simbólico pesado en
   SymPy, fuera del camino caliente.

## Decisión (propuesta)

**Opción 4.**

| Parte | Tecnología | Camino |
|---|---|---|
| Parser LaTeX → AST | C++20 propio | por edición |
| Evaluador (AST compilado a bytecode) | C++20 propio | **por punto** |
| Numérico: raíces, integrales, EDO, muestreo adaptativo, curvas implícitas | C++20 propio | por cuadro |
| Simbólico rápido: derivar, expandir, simplificar | SymEngine (C++, BSD-3) | por edición |
| Simbólico pesado: primitivas, límites, series, pasos | SymPy vía pybind11, en un hilo aparte | bajo demanda |
| Gráficos 2D/3D | Qt 6 (QOpenGLWidget / RHI) | por cuadro |
| Render de LaTeX | MicroTeX (C++, MIT) | por edición |

- El motor Python actual queda como **implementación de referencia**: su contrato JSON y el banco
  (`python -m arrds_math.selftest --export`) validan automáticamente al núcleo C++.
- El parser ASCII actual y el nuevo parser LaTeX producen **el mismo AST** (mismos nodos y semántica).
- Licencias permitidas: BSD, MIT, Apache, BSL; LGPL solo con enlace dinámico. **GPL prohibida.**
  (SymEngine debe compilarse con `boostmp` en vez de GMP, o con GMP enlazado dinámicamente.)

## Spike de validación (antes de aceptar)

Prototipo descartable, 2–3 días:

1. Parser C++ de un LaTeX mínimo: números, variables, `+ - \cdot`, `\frac`, `^{}`, `\sin`, `\sqrt`.
2. Evaluador compilado a bytecode.
3. Ventana Qt que dibuja `y = a \sin(x)` con un deslizador para `a`.

**Criterio de aceptación:** 10 curvas de 2 000 puntos recalculadas en < 8 ms por cuadro al mover el
deslizador, en la PC de Arrds; los resultados coinciden con el motor Python en los casos del banco que
cubre el subconjunto.

## Consecuencias

- Se suma C++20, CMake y Qt 6 al proyecto; curva de aprendizaje mayor (los documentos de contexto marcan
  base en C++, no experiencia profesional).
- **(propuesta)** Estructura: el núcleo C++ vive en este repositorio (`core/`) junto a `arrds_math/`, para
  compartir el banco; la aplicación de la calculadora va en su propio repositorio.
- Por decidir en el spike: framework de tests en C++ y gestión de dependencias (vcpkg / FetchContent).
- El trabajo de Matemática A y B en SymPy (ADR 0001) sigue vigente: es la parte "simbólico pesado".
