# Arquitectura y componentes

## Encuadre del proyecto

- Arrds Studio es una aplicación de estación de trabajo matemática ambiciosa dirigida a estudiantes de ingeniería de la UNLP — proyecto futuro que sigue a motor-OCR en la hoja de ruta de Arrds.
- El desarrollo se aborda con enfoque de "desarrollo de conocimiento" (no solo código), dado que Arrds no tiene formación formal en ingeniería de software.
- Todavía no existe un repositorio público para Arrds Studio completo — se mantiene el enfoque de "desarrollo de conocimiento" antes de pasar a la construcción completa.
- La primera entrega pública será el repositorio `arrds-math-engine`, con el motor matemático central. El nombre fue elegido para reflejar la marca (Arrds) y ser escalable — permite futuros repos como `arrds-physics-engine`, `arrds-cfd-engine`, etc.
- Se financiará inicialmente a través de GitHub Sponsors del proyecto motor-OCR (tiers de $7/$1); los sponsors acceden al repo privado `arrds-sponsors-updates` con actualizaciones semanales exclusivas.

## Motor matemático

- Motor con tres capas de fallback:
  1. **SymPy** — cálculo simbólico exacto
  2. **SciPy** — cálculo numérico
  3. **mpmath** — precisión arbitraria, con delegación pedagógica si todo lo anterior falla
- El objetivo pedagógico es que el motor explique *por qué* funciona o falla un método, no solo devolver un resultado.

## Puente C++ / Python

- Puente pybind11 con manejo del GIL y arquitectura basada en `QThreadPool`.

## Pipeline RAG (agente académico)

- Ingesta de PDFs oficiales de cátedra.
- Chunking semántico del contenido.
- Recuperación (retrieval) con ChromaDB.
- Sistema de aumento de prompt en cinco capas.
- Formato propietario `.arrds` para PDFs institucionales pre-procesados, con embeddings pre-computados.
- Base de datos vectorial (`vector_db`) versionada con semver y checksums SHA256.

## Validación de código generado por LLM

- Pipeline de validación de código SymPy generado por el LLM: análisis AST, ejecución en sandbox, y verificación matemática del resultado.
- Camino de validación con AST incluye una whitelist de API además de la ejecución en sandbox.

## Sistema multi-agente (Mixture of Experts)

Arquitectura del orquestador diseñada en cinco capas:

1. **QueryClassifier** — clasifica la consulta entrante
2. **PlanBuilder** — construye el plan de resolución
3. **AgentPool** — basado en `ThreadPoolExecutor`
4. **Agentes especializados:**
   - `MathAgent` — cálculo
   - `RAGAgent` — recuperación de contexto académico
   - `ExplainAgent` — explicación paso a paso
5. **ResultSynthesizer** — sintetiza el resultado final

(También referido en discusiones previas como orquestador + agentes de RAG, cálculo, explicación y verificación.)

## Interfaz y rendimiento

- UI adaptativa al hardware, con niveles de efectos visuales configurables.
- Interfaz abstracta `PlotEngine` para desacoplar el motor de renderizado de la implementación gráfica concreta.
- Renderizado LaTeX vía `matplotlib.mathtext`, con persistencia en SQLite.

## Marketplace y extensiones

- Marketplace de extensiones con estructura de comisiones éticas.
- Procesamiento de pagos vía Lemon Squeezy, con webhooks HMAC-SHA256, licencias ligadas a `machine_id`, y caché offline de 30 días.
- Almacenamiento de extensiones en Cloudflare R2 / GitHub Releases, con catálogo `registry.json`.

## Licenciamiento

- Modelo de pago único.
- Claves de licencia ligadas a máquina (`machine_id`-bound).
- Caché offline de 30 días para activación.

## Bloqueadores y orden de desarrollo recomendado

- Una auditoría identificó aproximadamente 30 problemas sin resolver, agrupados en:
  - Bloqueadores críticos: instalador, interfaz Qt, sistema de plugins de micro-kernel, orquestador multi-agente, activación de licencias.
  - Brechas técnicas.
  - Preguntas de negocio/distribución.
  - Desafíos de UX.
  - Necesidades de ecosistema.
- **Orden de desarrollo recomendado:** interfaz Qt mínima funcional → pruebas con usuarios → instalador/licenciamiento → micro-kernel → SDK/marketplace.
- Se recibió una guía visual de aprendizaje con metáforas, estructura de capas del proyecto, estructura de archivos, orden de construcción y una hoja de ruta de aprendizaje de 9 meses.

## Alcance matemático

- Cálculo simbólico, álgebra lineal, análisis complejo y visualización 2D/3D.

Ver también: [01-vision-general.md](01-vision-general.md), [02-principios-y-workflow.md](02-principios-y-workflow.md), [04-repositorios-github.md](04-repositorios-github.md).
