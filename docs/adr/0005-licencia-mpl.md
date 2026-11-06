# ADR 0005 — Código abierto bajo MPL-2.0

- **Estado:** aceptado (decisión de Arrds)
- **Fecha:** 2026-10-30

## Contexto

Arrds decidió publicar el proyecto en GitHub como **código abierto** para que otros aporten.

Sin un archivo `LICENSE`, un repositorio público no puede usarse ni recibir aportes legalmente. Y una vez que
hay aportes de terceros, cambiar la licencia exige el permiso de cada autor: la elección debe hacerse antes.

## Opciones

1. **GPL-3.0:** protege que nadie cierre el código; impide un producto comercial cerrado en el futuro.
2. **Apache-2.0 / MIT:** casi sin condiciones; cualquiera, incluso un competidor, puede cerrar una versión mejorada.
3. **MPL-2.0:** copyleft por archivo: quien modifica archivos del proyecto y los distribuye debe publicar esos
   archivos; se pueden combinar con código propio cerrado en un producto mayor.

## Decisión

**MPL-2.0** (texto oficial en [`LICENSE`](../../LICENSE)).

## Consecuencias

- Las mejoras al motor vuelven a la comunidad; un producto mayor puede incluir el motor sin tener que
  abrir su propio código (por ejemplo, una interfaz o funciones exclusivas), siempre que no modifique
  archivos del propio motor sin publicar esos cambios.
- **Dependencias:** se mantienen las licencias permitidas del [ADR 0002](0002-nucleo-cpp.md) (BSD, MIT,
  Apache, BSL, OFL; LGPL solo con enlace dinámico). **GPL sigue prohibida:** incorporar código GPL obligaría
  a distribuir todo el conjunto bajo GPL.
- Los aportes de terceros entran bajo MPL-2.0 (cláusula de "inbound = outbound" en
  [CONTRIBUTING.md](../../CONTRIBUTING.md)). Para **relicenciar** el proyecto en el futuro haría falta el
  permiso de los contribuyentes.
