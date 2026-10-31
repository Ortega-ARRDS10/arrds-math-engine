# ADR 0005 — Código abierto bajo MPL-2.0

- **Estado:** aceptado (decisión de Arrds)
- **Fecha:** 2026-10-30

## Contexto

Los documentos de contexto plantean Arrds Studio como producto de **pago único**. Arrds decidió que, por el
momento, el proyecto se publica en GitHub como **código abierto** para que otros aporten, sin descartar
cobrar en el futuro.

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

- Las mejoras al motor vuelven a la comunidad; un futuro producto pago puede incluir el motor sin abrir su
  propio código (por ejemplo, la interfaz o funciones exclusivas).
- **Dependencias:** se mantienen las licencias permitidas del [ADR 0002](0002-nucleo-cpp.md) (BSD, MIT,
  Apache, BSL, OFL; LGPL solo con enlace dinámico). **GPL sigue prohibida:** incorporar código GPL obligaría a
  distribuir todo el conjunto bajo GPL y cerraría la puerta al cobro futuro.
- Los aportes de terceros entran bajo MPL-2.0 (cláusula de "inbound = outbound" en
  [CONTRIBUTING.md](../../CONTRIBUTING.md)). Para **relicenciar** el proyecto en el futuro haría falta el
  permiso de los contribuyentes; para **vender** un producto que lo incluya, no.
- Los documentos de contexto que hablan de "pago único" no se modifican (son la fuente de verdad del
  autor); el cambio de rumbo se registra en [CONTEXTO.md](../CONTEXTO.md) y en la bitácora.
