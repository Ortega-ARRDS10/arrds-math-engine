# Cómo contribuir

¡Gracias por querer aportar a **arrds-math-engine**, el motor matemático de Arrds Studio! El proyecto se
trabaja en español: issues, pull requests, código y comentarios.

## Licencia de los aportes

El proyecto se distribuye bajo la **Mozilla Public License 2.0** ([`LICENSE`](LICENSE)). Al enviar un aporte
aceptás que se publique bajo esa misma licencia, y declarás que tenés derecho a hacerlo (el código es tuyo o
su licencia lo permite). **No se acepta código GPL** ni copiado de proyectos GPL
([ADR 0005](docs/adr/0005-licencia-mpl.md)).

## Antes de empezar

1. Leé [CLAUDE.md](CLAUDE.md): son las reglas del proyecto en una página (sirven igual para personas).
2. Para cambios grandes, abrí primero un **issue** y contá qué querés hacer. Así evitamos trabajo duplicado
   o que choque con decisiones ya tomadas ([docs/adr/](docs/adr/)).
3. El lenguaje de la calculadora lo define el autor paso a paso en [docs/lenguaje/](docs/lenguaje/README.md).
   Propuestas de sintaxis nueva: por issue, no directo en un pull request.

## Preparar el entorno

```bash
git clone https://github.com/Ortega-ARRDS10/arrds-math-engine.git
cd arrds-math-engine
pip install -e .
python -m unittest discover -s tests
python -m arrds_math.selftest
```

## Reglas principales

- **Dependencias:** solo la biblioteca estándar de Python y SymPy (+mpmath). Una dependencia nueva requiere
  un issue y un ADR ([ADR 0001](docs/adr/0001-implementacion-de-referencia-stdlib.md)).
- **Nunca `eval` ni `exec`**, ni `sympify`/`parse_expr` sobre texto del usuario: toda expresión entra por el
  parser del motor.
- **Todo método iterativo** devuelve `IterativeResult` con `converged`, `iterations` y `error_estimate`.
- **Errores tipados:** subclases de `MathEngineError` con `code` estable y, si ayuda, un `hint` que explique
  por qué falló.
- **Nada sin caso de verificación:** cada operación nueva trae al menos un caso con valor de referencia y un
  caso de error esperado en el banco ([docs/FLUJO_DE_TRABAJO.md](docs/FLUJO_DE_TRABAJO.md)).

## Pull requests

1. Una rama por cambio: `feat/<tema>`, `fix/<tema>`, `docs/<tema>`.
2. Commits chicos, en español y en imperativo: `feat: añade …`, `fix: corrige …`.
3. Antes de enviar, pegá en el PR la salida real de:
   - `python -m unittest discover -s tests` → `OK`
   - `python -m arrds_math.selftest` → `N/N casos pasan`
4. Si tu cambio altera el contrato JSON (lo que devuelve una operación), decilo explícitamente en el PR.
5. Actualizá la documentación que corresponda (ver la checklist de
   [docs/FLUJO_DE_TRABAJO.md](docs/FLUJO_DE_TRABAJO.md)).

## Reportar errores

Abrí un issue con: la operación o expresión, los parámetros exactos, el resultado obtenido, el esperado y
de dónde sale el valor esperado (cálculo analítico, tabla, libro).
