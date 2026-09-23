# Roadmap

## v0.1 — implementación de referencia (hecho)

- [x] Parser propio sin `eval` (multiplicación implícita, `^`/`**`, `!`), límites de tamaño y anidación
- [x] Evaluador en modo real y complejo; `compile_function`
- [x] Derivada simbólica, simplificación conservadora, gradiente, LaTeX
- [x] Raíces (bisección, Newton, secante, Brent), derivada con Richardson
- [x] Integración (Simpson adaptativo, Gauss–Legendre, trapecio)
- [x] EDO (RK4 con error por duplicación de paso, Dormand–Prince RK45 adaptativo)
- [x] Álgebra lineal (LU, solve con refinamiento, det, inversa, cond, QR, mínimos cuadrados, Jacobi, normas)
- [x] Polinomios (raíces con error honesto para raíces múltiples, ajuste por QR)
- [x] Estadística descriptiva y regresión con incertidumbres
- [x] Mat C: gradiente, divergencia, rotor, laplaciano, jacobiano
- [x] Mat D: FFT/DFT, espectro, funciones de transferencia, Bode
- [x] Unidades: SI, derivadas, imperiales, prefijos, análisis dimensional
- [x] Todo iterativo devuelve `IterativeResult`; errores tipados con `hint` pedagógico
- [x] API con registro de 68 operaciones y contrato JSON
- [x] Banco de verificación (70 casos, exportable a JSON)
- [x] Tests `unittest` por módulo, contrato y servidor
- [x] Panel de pruebas local (catálogo, editor JSON, gráficas SVG, banco, integridad, `Ctrl+K`)
- [ ] **Decidir la licencia** (ver [POLITICA_DE_USO.md](POLITICA_DE_USO.md#licencia))
- [ ] **Decidir la política de dependencias** ([ADR 0001](adr/0001-implementacion-de-referencia-stdlib.md))
- [ ] CI en GitHub Actions que corra tests + banco en cada push (el roadmap de los documentos pone CI primero)

## v0.2 — ampliación numérica

- [ ] Transformada de Laplace inversa numérica (Talbot o Stehfest) y Laplace/Fourier simbólica de tablas
- [ ] EDO rígidas: BDF y Rosenbrock (implícitos)
- [ ] Autovalores de matrices no simétricas (QR con desplazamientos / Hessenberg)
- [ ] Integración 2D/3D (cuadratura tensorial y adaptativa en dominios rectangulares)
- [ ] Unidades dentro de las expresiones (`3 m/s * 2 s`) con verificación dimensional
- [ ] Propagación de incertidumbre (lineal por derivadas; Monte Carlo como contraste)
- [ ] Explicación paso a paso en los resultados (campo `steps`), alineado con la pedagogía del producto
- [ ] Cascada de fallback hacia precisión extendida (según la decisión del ADR 0001)

## v0.3+ — integración con Arrds Studio

- [ ] Spike del puente **pybind11** con este contrato (según los documentos de contexto)
- [ ] **(propuesta)** Port del núcleo a C++ validado contra el banco exportado (`--export`)
- [ ] Rendimiento: perfiles, casos grandes, límites de tiempo por operación
- [ ] **(propuesta)** HAL / capa de orquestación para el `MathAgent` del orquestador multi-agente
