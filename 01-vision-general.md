# Visión general — Arrds Studio

## Qué es

Arrds Studio es una estación de trabajo matemática y de ingeniería educativa, pensada como alternativa competitiva a MATLAB para estudiantes de ingeniería, con aprendizaje asistido por IA. No busca competir con calculadoras web, sino con herramientas profesionales, manteniendo:

- Pago único
- Alto rendimiento
- Portabilidad
- Explicaciones paso a paso

## Sobre el autor y el enfoque del proyecto

- Arrds es estudiante de Ingeniería Aeroespacial en la UNLP (Universidad Nacional de La Plata, Argentina); el proyecto es un desarrollo independiente de gran escala en paralelo con la carrera.
- Tiene conocimientos de base en Python y C++, pero no es desarrollador de software profesional.
- Trabaja el proyecto mayormente en español.
- Aborda el desarrollo con un enfoque de "development of knowledge" (desarrollo de conocimiento): el proyecto es tanto un vehículo de aprendizaje como un producto.
- Valora el trabajo técnico en profundidad, ejemplos de código explícitos, y evaluaciones honestas del estado del proyecto.

## Objetivos centrales (Core goals)

1. Motor matemático riguroso multi-capa (SymPy/SciPy/mpmath) con explicaciones pedagógicas.
2. Agente de IA académico con RAG entrenado sobre los PDFs oficiales de cátedra de la UNLP.
3. Frontend en C++/Qt 6 con gráficos 2D/3D.
4. Orquestador multi-agente de IA.
5. Sistema de licenciamiento y distribución.

## Stack tecnológico

**Motor matemático:** SymPy, SciPy, mpmath, NumPy

**Frontend:** C++20, Qt 6, QOpenGLWidget, GLSL, PyQtGraph, matplotlib, VTK

**Puente (bridge):** pybind11 como opción principal; Cython o Rust (vía PyO3) reservados solo para cuellos de botella identificados por profiling.

**IA / RAG:** LlamaIndex, ChromaDB, API de Anthropic (Claude.ai Pro)

**Bases de datos:** ChromaDB (búsqueda semántica), SQLite (caché de renderizado LaTeX), base de datos vectorial versionada con semver y manifiesto.

**Empaquetado:** Nuitka, CPack, GitHub Actions

**Librerías propias diseñadas:** `arrds.detection`, `arrds.diagnostics`, `arrds.precision`, `arrds.context`, `arrds.symbolic_ext`

**Referencias clave:** *Clean Code* / *Clean Architecture* (Robert C. Martin), *Refactoring* (Martin Fowler), *Numerical Recipes* (Press et al.)

**Contexto académico:** planes de estudio completos de Matemática B, C y D del plan de estudios de la UNLP (cálculo, álgebra lineal, análisis complejo, transformadas).

## Estado actual del proyecto

> Nota: estado registrado en una revisión anterior — conviene re-verificar contra el avance real antes de tomar decisiones basadas en él.

- El proyecto está en fase de arquitectura y diseño pre-MVP, con bloqueadores críticos identificados antes del lanzamiento.
- La arquitectura del orquestador multi-agente está completamente diseñada en cinco capas: `QueryClassifier`, `PlanBuilder`, `AgentPool` (basado en ThreadPoolExecutor), tres agentes especializados (`MathAgent`, `RAGAgent`, `ExplainAgent`) y `ResultSynthesizer`. Se produjo código Python completo de esta arquitectura en sesión previa.
- El desarrollo dirigido por *spikes* (prototipos rápidos y descartables) se identificó como la prioridad inmediata.
- Se recomendaron tres spikes técnicos de un día cada uno antes de comprometerse con la arquitectura completa:
  1. Puente pybind11
  2. Empaquetado con Nuitka
  3. ChromaDB con PDFs reales
- Un diagnóstico honesto detectó tres problemas estructurales: falta de prototipos técnicos validados, MVP sin definir, y aprendizaje mezclado con construcción en el mismo cronograma.
- Camino recomendado: completar los spikes → definir el MVP en una página → construir únicamente ese MVP → iterar sobre feedback real.
- Quedan cinco bloqueadores críticos adicionales por resolver, más allá del orquestador.

## Próximos pasos (a re-verificar)

- Resolver los cinco bloqueadores críticos pre-lanzamiento restantes.
- Ejecutar los tres spikes técnicos para validar los supuestos de factibilidad.
- Definir el alcance del MVP en una página para evitar scope creep.
- Avanzar en el roadmap de aprendizaje y construcción de nueve meses (actualmente en fases tempranas).

Ver también: [02-principios-y-workflow.md](02-principios-y-workflow.md) y [03-arquitectura-y-componentes.md](03-arquitectura-y-componentes.md).
