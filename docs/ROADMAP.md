# Roadmap vivo

Este es el único backlog documental vigente del repositorio. Los planes cerrados
se conservan en [`archive/`](archive/README.md); no deben usarse para decidir el
estado actual de una función sin comprobar antes el código y sus tests.

## Mantenibilidad

1. Continuar extracciones funcionales solo después de ampliar el contrato del
   widget, canvas o ciclo de vida afectado. Los límites actuales están descritos
   en [`architecture/AGENT_MAINTAINABILITY.md`](architecture/AGENT_MAINTAINABILITY.md).

## Producto pendiente de validación

Estos asuntos proceden de TODO históricos. Antes de implementarlos hay que
reproducir el comportamiento actual y confirmar que siguen siendo necesarios:

- Mostrar en detección el nombre completo del acorde además del símbolo abreviado.
- Revisar las digitaciones de escalas menores y blues menor contra sus fuentes.
- Evaluar una selección de tónica/alteración más directa y coherente entre modos.
- Valorar digitaciones de escalas a dos manos.

## Regla de actualización

- Añadir aquí únicamente trabajo confirmado y aún no completado.
- Los cambios funcionales terminados se registran en `CHANGELOG.md`.
- Los planes cerrados o sustituidos se mueven a `docs/archive/` con una nota de
  contexto, en vez de permanecer como instrucciones activas en la raíz.
