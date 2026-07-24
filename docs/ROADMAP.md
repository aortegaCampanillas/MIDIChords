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

## Calidad visual y layouts

- Revisar sistemáticamente el comportamiento al redimensionar las ventanas y
  cambiar de orientación en escritorio, web y móvil/tablet. Cubrir todos los
  modos y tamaños representativos; comprobar solapamientos, recortes, scroll,
  alturas mínimas, paneles e instrumentos, tablas y ayudas contextuales, además
  de verificar que el estado y el foco se conservan durante el cambio de tamaño.

## Posibles implementaciones futuras

- Evaluar soporte AUv3 para iOS y macOS mediante un prototipo técnico aislado.
  Priorizar como primer alcance un **AUv3 MIDI Processor** que reciba notas del
  host, detecte o genere acordes e intervalos y pueda devolver MIDI. Evitar
  inicialmente convertir toda la aplicación Flutter o incorporar generación de
  audio: la extensión requiere un target nativo, una interfaz adaptada al espacio
  del plugin y portar a Swift una parte verificable de la teoría musical. Solo
  plantear un AUv3 Instrument con samples y audio en tiempo real después de
  validar el prototipo MIDI en varios hosts.

## Regla de actualización

- Añadir aquí únicamente trabajo confirmado y aún no completado.
- Los cambios funcionales terminados se registran en `CHANGELOG.md`.
- Los planes cerrados o sustituidos se mueven a `docs/archive/` con una nota de
  contexto, en vez de permanecer como instrucciones activas en la raíz.
