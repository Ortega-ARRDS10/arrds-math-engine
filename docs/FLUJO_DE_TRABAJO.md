# Flujo de trabajo

Aplica los principios de [contexto/02-principios-y-workflow](contexto/02-principios-y-workflow.md):
spec antes de código, TDD (rojo → verde → refactor) y ADR para cada decisión relevante.

## Ramas y commits

- `main`: siempre verde (tests + banco al 100 %). **(propuesta)**: hoy el trabajo vive en
  `claude/admiring-pascal-56gpjq`; conviene crear `main` desde ahí cuando Arrds apruebe la v0.1.
- Una rama por cambio: `feat/<tema>`, `fix/<tema>`, `docs/<tema>`. Las ramas creadas por agentes de IA
  usan el prefijo `claude/`.
- Commits chicos, en español y en imperativo, con prefijo de tipo:
  `feat: añade transformada de Laplace inversa`, `fix: corrige el signo del rotor`, `docs: …`, `test: …`.
- Nunca subir `__pycache__/` (ya está en `.gitignore`).

## Cómo añadir una operación

1. **Especificación**: qué calcula, qué entradas acepta, casos límite, cómo se sabe que está bien
   (valor de referencia analítico o tabulado y su tolerancia).
2. **Caso de verificación primero** (rojo): añadilo en `arrds_math/selftest.py` → `CASES`, con
   `reference`. Incluí al menos un caso de error esperado.
3. **Función** en el módulo que corresponda. Si es iterativa, devuelve `IterativeResult` con un
   `error_estimate` honesto. Errores con subclases de `MathEngineError` y `hint` si el usuario puede
   corregir algo.
4. **Registro en la API** (`arrds_math/api.py`): `@operation("modulo.nombre", descripción, params, ejemplo)`.
   Validá cada parámetro con los helpers (`_num`, `_list`, `_matrix`…) y respetá los límites de tamaño.
5. **Tests unitarios** en `tests/`: propiedades (identidades, ida y vuelta, contraste con otro método).
6. **Documentación**: convenciones nuevas en [CONVENCIONES_NUMERICAS.md](CONVENCIONES_NUMERICAS.md),
   casilla en [TAREAS.md](TAREAS.md), ADR si hubo una decisión con alternativas.

## Definición de "listo"

Un cambio está listo cuando se cumplen **todas**:

- [ ] `python -m unittest discover -s tests` → `OK`, 0 fallos, 0 errores.
- [ ] `python -m arrds_math.selftest` → `N/N casos pasan`.
- [ ] Toda operación nueva tiene ≥ 1 caso con valor de referencia y ≥ 1 caso de error esperado.
- [ ] Todo método iterativo nuevo reporta `converged`, `iterations` y `error_estimate`, y al menos un caso
      usa `check_error_estimate`.
- [ ] El ejemplo de la operación se ejecuta en el panel sin error.
- [ ] Sin dependencias nuevas (o con ADR aprobado por Arrds).
- [ ] Sin `eval`/`exec`: `git grep -nwE "eval|exec" -- "*.py" "*.html"` solo muestra comentarios.

## Checklist antes del push

- [ ] Tests y banco en verde (salida real pegada en el PR o el commit).
- [ ] `git status` limpio de archivos generados.
- [ ] Mensajes de commit claros.
- [ ] Docs actualizados (README si cambia el uso; ARQUITECTURA si cambia el contrato).
- [ ] Si cambió el contrato JSON: indicarlo en el commit, porque rompe a otras implementaciones.
