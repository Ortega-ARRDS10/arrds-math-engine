# Guía de aprendizaje: ingeniería de software para programar Arrds Studio con IA

Guía pensada para alguien sin formación formal en ingeniería de software que quiere aprender la terminología, la arquitectura y las prácticas necesarias para dirigir un proyecto grande (como Arrds Studio) trabajando junto a un agente de IA como Claude Code. No busca convertirte en programador tradicional de la noche a la mañana — busca darte el vocabulario y los criterios para **tomar buenas decisiones técnicas y supervisar al agente con criterio propio**, que es la habilidad que realmente vas a necesitar.

---

## Índice

1. [Cómo usar esta guía](#1-cómo-usar-esta-guía)
2. [Nivel 0 — Vocabulario mínimo indispensable](#2-nivel-0--vocabulario-mínimo-indispensable)
3. [Nivel 1 — Fundamentos de ciencias de la computación](#3-nivel-1--fundamentos-de-ciencias-de-la-computación)
4. [Nivel 2 — Arquitectura de software](#4-nivel-2--arquitectura-de-software)
5. [Nivel 3 — Patrones de diseño y buenas prácticas de código](#5-nivel-3--patrones-de-diseño-y-buenas-prácticas-de-código)
6. [Nivel 4 — Ingeniería de software "clásica" (proceso, testing, control de versiones)](#6-nivel-4--ingeniería-de-software-clásica-proceso-testing-control-de-versiones)
7. [Nivel 5 — Desarrollo asistido/agéntico con IA (lo específico de tu caso)](#7-nivel-5--desarrollo-asistidoagéntico-con-ia-lo-específico-de-tu-caso)
8. [Nivel 6 — Lo específico de Arrds Studio (software matemático/numérico)](#8-nivel-6--lo-específico-de-arrds-studio-software-matemáticonumérico)
9. [Libros recomendados, en orden de lectura](#9-libros-recomendados-en-orden-de-lectura)
10. [Repositorios y sitios de referencia](#10-repositorios-y-sitios-de-referencia)
11. [Plan de estudio sugerido (12 semanas)](#11-plan-de-estudio-sugerido-12-semanas)

---

## 1. Cómo usar esta guía

No la leas de punta a punta antes de programar — sería el error clásico de "primero preparo todo, después empiezo". La idea es: avanzás en Arrds Studio con el agente de IA, y cuando aparece un término que no entendés (monolito, acoplamiento, inyección de dependencias, CI/CD, etc.) volvés a esta guía, lo buscás en el nivel correspondiente, y seguís. El aprendizaje "justo a tiempo" funciona mejor que el aprendizaje "por si acaso" cuando ya tenés un proyecto real corriendo.

---

## 2. Nivel 0 — Vocabulario mínimo indispensable

Términos que vas a escuchar constantemente y que conviene tener claros desde el día uno (definiciones breves, en tus propias palabras después de leerlas):

- **Repositorio (repo):** la carpeta de tu proyecto con historial de cambios versionado (Git).
- **Commit:** una "foto" guardada de cómo estaba el código en un momento dado, con un mensaje que explica qué cambió.
- **Rama (branch):** una línea de desarrollo paralela — por ejemplo, trabajar una función nueva sin tocar la versión estable.
- **Dependencia:** una librería/paquete externo del que tu código depende para funcionar (por ejemplo, una librería de álgebra lineal).
- **API (interfaz de programación de aplicaciones):** el "contrato" que expone una parte del sistema para que otra parte la use, sin necesidad de conocer cómo está implementada por dentro.
- **Backend / Frontend:** la lógica interna y de datos (backend) versus lo que ve/usa el usuario (frontend) — en tu caso, el motor simbólico sería backend, la interfaz de visualización 2D/3D sería frontend.
- **Arquitectura:** cómo están organizadas y conectadas las piezas grandes del sistema (no el código línea por línea, sino el "mapa" general).
- **Módulo / componente:** una unidad de código con una responsabilidad concreta (por ejemplo, el módulo de transformadas de Laplace).
- **Acoplamiento (coupling):** cuánto depende una parte del código de los detalles internos de otra. Bajo acoplamiento = módulos más independientes = más fácil de mantener.
- **Cohesión:** cuánto se relacionan entre sí las cosas que están agrupadas en un mismo módulo. Alta cohesión = cada módulo hace una cosa clara.
- **Refactorizar:** reorganizar código existente para que sea más claro/mantenible, sin cambiar lo que hace.
- **Bug / debugging:** un error de comportamiento; el proceso de encontrarlo y corregirlo.
- **Test (prueba automatizada):** código que verifica que otro código funciona como se espera, para detectar errores automáticamente.
- **CI/CD (integración/entrega continua):** automatizar que cada cambio se pruebe (y opcionalmente se publique) sin intervención manual.
- **Deuda técnica:** atajos tomados por velocidad que después cuestan tiempo extra corregir — normal que exista, hay que gestionarla, no eliminarla del todo.

---

## 3. Nivel 1 — Fundamentos de ciencias de la computación

Esto es opcional pero de altísimo valor para un software matemático/numérico como el tuyo, porque muchas decisiones de rendimiento y precisión dependen de entender esto:

- **Estructuras de datos y algoritmos:** cómo se representa la información en memoria (arrays, listas, árboles, grafos, hash maps) y cómo eso afecta la velocidad de tu motor simbólico.
- **Complejidad algorítmica (notación Big-O):** entender por qué un algoritmo de álgebra lineal es rápido o lento según el tamaño del problema — crítico si vas a competir con herramientas profesionales en rendimiento.
- **Representación numérica:** punto flotante vs. precisión arbitraria/exacta (relevante directamente para tu "cálculo simbólico exacto") — errores de redondeo, estabilidad numérica.
- **Paradigmas de programación:** imperativo, orientado a objetos, funcional — cada uno te da un vocabulario distinto para razonar sobre el código que el agente te propone.

**Recurso ancla:** [teachyourselfcs.com](https://teachyourselfcs.com/) — currícula autodidacta de ciencias de la computación a nivel universitario, con libros y cursos gratuitos recomendados por tema (algoritmos, sistemas, matemática discreta, etc.). No hace falta hacerla completa; usala como mapa de referencia.

---

## 4. Nivel 2 — Arquitectura de software

Esto es lo más importante para vos como director de un proyecto grande con IA, porque **la arquitectura es la decisión que más cuesta revertir después** — mejor entenderla bien antes de que el proyecto crezca mucho.

Conceptos clave:

- **Monolito vs. arquitectura modular/microservicios:** un monolito es todo el sistema en una sola unidad desplegable; una arquitectura modular separa responsabilidades en piezas independientes. Para software de escritorio de pago único como Arrds Studio, probablemente un **monolito bien modularizado** (separado internamente en capas/módulos claros, pero empaquetado como una sola aplicación) sea lo más razonable — los microservicios resuelven problemas de escalado distribuido que probablemente no tengas.
- **Arquitectura en capas (layered architecture):** separar el sistema en capas horizontales (por ejemplo: interfaz de usuario → lógica de negocio/motor de cálculo → acceso a datos/persistencia), donde cada capa solo habla con la de al lado.
- **Arquitectura hexagonal / puertos y adaptadores:** aislar el "núcleo" de tu lógica (el motor matemático) de los detalles externos (interfaz gráfica, formato de archivo, backend de renderizado), de modo que puedas cambiar la interfaz sin tocar el motor.
- **Domain-Driven Design (DDD):** diseñar el software alrededor del "dominio" del problema real (en tu caso, el dominio matemático: expresiones, transformadas, matrices, espacios vectoriales) en vez de organizarlo por detalles técnicos.
- **Diagramas de arquitectura (C4 model):** una forma estándar de dibujar un sistema en distintos niveles de zoom (contexto → contenedores → componentes → código) — útil para que vos y el agente de IA compartan el mismo "mapa mental" del proyecto.

**Recurso ancla:** [roadmap.sh/software-design-architecture](https://roadmap.sh/software-design-architecture) y [roadmap.sh/software-architect](https://roadmap.sh/software-architect) — rutas de aprendizaje visuales e interactivas, gratuitas, con enlaces a recursos por cada tema.

---

## 5. Nivel 3 — Patrones de diseño y buenas prácticas de código

Los patrones de diseño son "soluciones con nombre" a problemas recurrentes — útiles porque te dan vocabulario compartido con el agente de IA ("usá el patrón Strategy acá" es una instrucción mucho más precisa que describir el problema desde cero cada vez).

Patrones que probablemente vas a necesitar en un motor matemático:
- **Strategy:** intercambiar algoritmos (por ejemplo, distintos métodos de resolución numérica) sin cambiar el código que los usa.
- **Factory:** centralizar la creación de objetos complejos (por ejemplo, construir distintos tipos de expresiones simbólicas).
- **Visitor:** recorrer y operar sobre estructuras de árbol (muy común en motores de cálculo simbólico, donde una expresión matemática se representa como un árbol de sintaxis).
- **Composite:** representar jerarquías parte-todo (una expresión matemática compuesta de sub-expresiones es un caso clásico).
- **Observer:** notificar cambios entre partes del sistema (por ejemplo, que la visualización 3D se actualice cuando cambia una expresión).

Principios generales de buen código (más importantes que los patrones puntuales):
- **SOLID** (cinco principios de diseño orientado a objetos: responsabilidad única, abierto/cerrado, sustitución de Liskov, segregación de interfaces, inversión de dependencias).
- **DRY** (Don't Repeat Yourself — no dupliques lógica).
- **KISS** (Keep It Simple — no compliques de más).
- **YAGNI** (You Aren't Gonna Need It — no construyas flexibilidad que no necesitás todavía; muy relevante cuando trabajás con IA, que tiende a "over-engineerizar" si no la frenás).

**Recurso ancla:** [refactoring.guru](https://refactoring.guru/es) — probablemente la mejor referencia visual y gratuita de patrones de diseño, con ejemplos de código y explicación de cuándo usarlos y cuándo no.

---

## 6. Nivel 4 — Ingeniería de software "clásica" (proceso, testing, control de versiones)

- **Git:** control de versiones — indispensable, no negociable, incluso trabajando solo con un agente de IA (te permite deshacer cambios, comparar versiones, y darle al agente instrucciones sobre qué rama tocar).
- **Testing:** pruebas unitarias (una función aislada), de integración (varias piezas juntas), y de regresión (que lo que ya andaba siga andando). Para un motor matemático, además necesitás **pruebas de precisión numérica** (comparar resultados contra valores conocidos con una tolerancia).
- **Documentación técnica:** README, comentarios de código, documentación de arquitectura — el agente de IA la necesita tanto como un humano nuevo en el equipo la necesitaría.
- **Gestión de issues/tareas:** llevar registro de qué falta, qué está roto, qué se decidió y por qué (aunque trabajes solo, esto evita que vos mismo pierdas el hilo del proyecto).
- **Versionado semántico (SemVer):** convención de numerar versiones (1.2.3 = mayor.menor.parche) para comunicar qué tan grande es un cambio.

**Recurso ancla:** [Pro Git](https://git-scm.com/book/es/v2) — el libro oficial y gratuito de Git, disponible en español completo online.

---

## 7. Nivel 5 — Desarrollo asistido/agéntico con IA (lo específico de tu caso)

Esta es la parte más nueva y la que menos literatura "clásica" tiene, porque es una disciplina que está formándose ahora mismo (2025-2026). Términos clave:

- **Vibe coding:** programar dejando que la IA genere código sin supervisión ni entendimiento profundo del resultado — funciona para prototipos chicos, **no** para un proyecto grande y de pago único como el tuyo, porque la deuda técnica se acumula invisible.
- **Ingeniería agéntica (agentic engineering):** el enfoque opuesto — dirigir al agente con especificaciones claras, revisar su trabajo, mantener arquitectura y tests como "barandas" que el agente no puede saltarse.
- **Spec-driven development (desarrollo dirigido por especificaciones):** escribir primero qué tiene que hacer una función/módulo (la especificación) antes de que el agente la implemente, y usar esa especificación para verificar el resultado. Es el patrón que más te conviene adoptar para Arrds Studio, dado que es software matemático donde la corrección del resultado es crítica.
- **Prompt engineering / context engineering:** la habilidad de darle al agente el contexto correcto (qué archivos, qué convenciones, qué restricciones) para que su trabajo sea útil sin tener que corregirlo constantemente.
- **Orquestación de agentes (Command → Agent → Skill):** patrón donde separás "qué quiero lograr" (comando), "quién lo coordina" (agente) y "cómo se ejecuta un paso concreto" (skill) — ya lo vimos en el repo `claude-code-best-practice` de tu análisis anterior.
- **Code review humano del código generado por IA:** revisar (aunque sea a alto nivel, sin entender cada línea) que la arquitectura general tenga sentido, que no haya funciones gigantes haciendo de todo, y que los tests pasen — es la disciplina mínima que necesitás aprender vos mismo, no delegable al 100%.

**Recursos ancla:**
- [Claude Code — documentación oficial](https://docs.claude.com/en/docs/claude-code) — la fuente primaria sobre cómo estructurar un proyecto para trabajar bien con el agente (CLAUDE.md, subagentes, hooks, skills).
- [ianhxu/agentic-engineering-field-study](https://github.com/ianhxu/agentic-engineering-field-study) — notas de campo sobre desarrollo dirigido por especificaciones con agentes de IA, en formato Markdown legible.
- El repo `shanraisshan/claude-code-best-practice` que ya analizamos, específicamente las carpetas `best-practice/` y `orchestration-workflow/`.

---

## 8. Nivel 6 — Lo específico de Arrds Studio (software matemático/numérico)

Términos de dominio que te van a aparecer seguido al construir un motor de cálculo simbólico y de visualización:

- **Árbol de sintaxis abstracta (AST):** cómo se representa internamente una expresión matemática para poder manipularla (simplificar, derivar, evaluar).
- **Aritmética de precisión arbitraria:** cálculo con números exactos (fracciones, enteros grandes) en vez de punto flotante — clave para tu "cálculo simbólico exacto".
- **Sistemas de álgebra computacional (CAS):** la categoría de software a la que pertenece Arrds Studio (como Mathematica, Maple, SymPy, Maxima) — vale la pena leer cómo están arquitecturados los CAS open source (SymPy en particular, por ser Python legible) para entender decisiones de diseño ya probadas.
- **Renderizado 2D/3D en tiempo real:** pipeline gráfico, GPU vs. CPU, frameworks de visualización científica.
- **Estabilidad numérica:** que un algoritmo no amplifique errores de redondeo — relevante en álgebra lineal avanzada (resolución de sistemas, autovalores).

**Recursos ancla:**
- Código fuente de [SymPy](https://github.com/sympy/sympy) — CAS open source en Python, extremadamente bien documentado; sirve como referencia de arquitectura real de un motor simbólico, no para copiar sino para entender decisiones.
- [Numerical Recipes](http://numerical.recipes/) — referencia clásica de algoritmos numéricos con explicación práctica (no es gratis, pero es la biblia del área).

---

## 9. Libros recomendados, en orden de lectura

No hace falta comprarlos/leerlos todos — es una lista priorizada. Los primeros tres son los de mayor retorno para tu situación puntual.

1. **"The Pragmatic Programmer"** (Andrew Hunt, David Thomas) — el libro más práctico y menos técnico de la lista; vocabulario y mentalidad de ingeniería sin necesitar base previa. Ideal como primer libro.
2. **"A Philosophy of Software Design"** (John Ousterhout) — corto, directo, específicamente sobre cómo pensar la complejidad y el diseño de módulos — muy aplicable a decidir cómo separar tu motor simbólico de la interfaz.
3. **"Clean Architecture"** (Robert C. Martin) — arquitectura en capas, independencia de frameworks, por qué separar el "núcleo" del sistema de los detalles externos (justo el problema de separar tu motor matemático de la UI/renderizado).
4. **"Design Patterns: Elements of Reusable Object-Oriented Software"** (Gang of Four) — el clásico de patrones; denso, mejor como referencia que como lectura corrida (usar refactoring.guru como versión más digerible primero).
5. **"Domain-Driven Design"** (Eric Evans) — más avanzado, útil cuando el proyecto ya tenga varios módulos y necesites organizar el "lenguaje" del dominio matemático dentro del código.
6. **"Working Effectively with Legacy Code"** (Michael Feathers) — sobre cómo modificar con seguridad código que ya existe y no entendés del todo — extremadamente relevante cuando el agente de IA generó una porción grande del código y vos necesitás intervenir después.
7. **"Building Evolutionary Architectures"** (Neal Ford, Rebecca Parsons, Patrick Kua) — cómo diseñar sistemas que puedan cambiar de arquitectura con el tiempo sin reescribir todo — útil para un proyecto de largo aliento como el tuyo.

Fuentes en español si preferís esa vía primero:
- [reactiveprogramming.io — Introducción a los patrones de diseño](https://reactiveprogramming.io/books/design-patterns/es) (libro gratuito online, en español)
- [reactiveprogramming.io — Introducción a la arquitectura de software](https://reactiveprogramming.io/books/software-architecture/es) (libro gratuito online, en español)
- [Pro Git en español](https://git-scm.com/book/es/v2) (gratuito, completo)

---

## 10. Repositorios y sitios de referencia

| Recurso | Qué te da | Nivel |
|---|---|---|
| [roadmap.sh](https://roadmap.sh/) | Rutas visuales interactivas y gratuitas para casi cualquier rol técnico (arquitecto, backend, IA, etc.) | Todos |
| [teachyourselfcs.com](https://teachyourselfcs.com/) | Currícula autodidacta de CS con libros/cursos gratuitos organizados por tema | Fundamentos |
| [refactoring.guru](https://refactoring.guru/es) | Patrones de diseño explicados visualmente, en español, con ejemplos de código | Patrones |
| [mehdihadeli/awesome-software-architecture](https://github.com/mehdihadeli/awesome-software-architecture) | Lista curada de artículos, videos y recursos sobre arquitectura, patrones y principios | Arquitectura |
| [DovAmir/awesome-design-patterns](https://github.com/DovAmir/awesome-design-patterns) | Lista curada de patrones de diseño y arquitectura, por lenguaje/paradigma | Patrones |
| [simskij/awesome-software-architecture](https://github.com/simskij/awesome-software-architecture) | Otra lista curada de recursos de arquitectura de software | Arquitectura |
| [git-scm.com/book/es](https://git-scm.com/book/es/v2) | Libro oficial y gratuito de Git en español | Control de versiones |
| [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code) | Documentación oficial de Claude Code: cómo estructurar proyectos para trabajar con el agente | Desarrollo con IA |
| [ianhxu/agentic-engineering-field-study](https://github.com/ianhxu/agentic-engineering-field-study) | Notas prácticas sobre desarrollo dirigido por especificaciones con agentes de IA | Desarrollo con IA |
| [sympy/sympy](https://github.com/sympy/sympy) | Código fuente real de un CAS (sistema de álgebra computacional) open source, legible en Python | Dominio matemático |
| `shanraisshan/claude-code-best-practice` (ya analizado) | Patrones de orquestación Command → Agent → Skill aplicables a tu propio proyecto | Desarrollo con IA |

---

## 11. Plan de estudio sugerido (12 semanas)

Pensado para avanzar en paralelo con el desarrollo real de Arrds Studio, no en abstracto — cada semana incluye una acción concreta sobre tu propio proyecto.

**Semanas 1-2 — Vocabulario y Git**
Leé el Nivel 0 completo de esta guía. Empezá (o formalizá) el repositorio de Arrds Studio en Git si todavía no lo tenés versionado. Practicá hacer commits con mensajes claros.

**Semanas 3-4 — Arquitectura general**
Recorré `roadmap.sh/software-design-architecture`. Con el agente de IA, pedile que te dibuje (en texto o diagrama) la arquitectura actual de Arrds Studio tal como está hoy, y discutila con él: ¿está separado el motor matemático de la interfaz? ¿Cómo se comunican?

**Semanas 5-6 — Patrones de diseño aplicados**
Recorré refactoring.guru enfocándote en Strategy, Factory, Visitor y Composite. Identificá con el agente en qué parte de tu motor simbólico ya se usa (aunque sea sin nombrarlo) alguno de estos patrones.

**Semanas 7-8 — Testing y calidad**
Leé sobre testing unitario/de integración. Pedile al agente que te arme una batería mínima de tests de precisión numérica para el motor (comparar resultados simbólicos contra valores conocidos).

**Semanas 9-10 — Desarrollo dirigido por especificaciones**
Practicá el flujo: antes de pedirle al agente que implemente algo nuevo, escribí vos (o con su ayuda) una especificación corta de qué debe hacer, qué casos límite debe cubrir, y cómo se verifica que está bien. Usalo en un módulo real (por ejemplo, la resolución de un tipo de transformada).

**Semanas 11-12 — Consolidación**
Leé "The Pragmatic Programmer" (o al menos los primeros capítulos) y "A Philosophy of Software Design". Revisá con el agente el estado general de la arquitectura de Arrds Studio y decidan juntos qué refactorizar antes de seguir sumando funcionalidad.

---

*Documento generado como guía de aprendizaje personal para el desarrollo de Arrds Studio. Volvé a esta guía cada vez que aparezca un término nuevo durante el trabajo con el agente de IA.*
