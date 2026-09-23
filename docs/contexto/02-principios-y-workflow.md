# Principios de ingeniería y forma de trabajo

## Aprendizajes y principios clave

- **Spike antes de arquitecturar:** los supuestos técnicos no validados (capa de puente, empaquetado, base de datos vectorial) son el mayor riesgo del proyecto — resolverlos con prototipos descartables antes de comprometer una estructura definitiva.
- **Separar problemas de usuario de problemas técnicos:** el alcance (qué entra, qué no entra, qué queda para después) debe definirse antes de empezar a implementar.
- **ADRs por sobre comentarios de código:** documentar el *por qué* de una decisión, no solo el *qué* se hizo (Architecture Decision Records).
- **La pedagogía del motor matemático importa:** el motor debe explicar *por qué* un método funciona o falla, no solo devolver resultados — es un diferencial central del producto.
- **Diseño de cascada de fallback:** SymPy (simbólico exacto) → SciPy (numérico) → mpmath (precisión arbitraria), con una capa pedagógica en caso de fallo.
- **SOLID aplicado con pragmatismo** — donde reduce complejidad real, no de forma dogmática.
- **Flujo de trabajo TDD:** Red/Green/Refactor como disciplina de implementación.

## Enfoque y patrones de trabajo

- Trabaja los bloqueadores en profundidad, uno por uno, en vez de hacer un relevamiento superficial y amplio.
- Prefiere desgloses técnicos completos con código funcional por sobre resúmenes de alto nivel.
- Responde bien a evaluaciones honestas del proyecto, incluso cuando son críticas.
- **Secuencia estructurada del roadmap (9 meses):** fundamentos de Python y CI primero → motor matemático → UI en Qt/C++ → puente pybind11 → UI completa → agente RAG → distribución.
- **Estrategia de selección de modelo para el desarrollo:**
  - Modelos clase Opus → decisiones de arquitectura
  - Modelos clase Sonnet → implementación diaria por defecto
  - Modelos clase Haiku → tareas mecánicas/repetitivas

## Cómo usar estos principios en la práctica

1. Antes de construir un módulo nuevo, escribir una especificación breve de qué debe hacer, qué casos límite cubre y cómo se verifica que funciona (spec-driven development).
2. No avanzar en arquitectura completa sin haber validado con un spike los supuestos técnicos de mayor riesgo.
3. Cada decisión de arquitectura relevante se documenta como ADR (contexto, opciones consideradas, decisión, consecuencias).
4. El motor de cálculo sigue siempre la cascada SymPy → SciPy → mpmath → explicación pedagógica del fallo, nunca un fallo silencioso.
5. Revisar periódicamente el estado general del proyecto contra el roadmap de 9 meses y ajustar prioridades con honestidad.

Ver también: [01-vision-general.md](01-vision-general.md) y [05-guia-ingenieria-software-ia.md](05-guia-ingenieria-software-ia.md).
