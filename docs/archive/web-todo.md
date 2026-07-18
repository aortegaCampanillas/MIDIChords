# TODO web histórico

> Lista archivada. Los asuntos todavía no confirmados se han trasladado a la
> sección de validación de [`../ROADMAP.md`](../ROADMAP.md).

## Alta prioridad
- [ ] En detección de acordes a la derecha del acorde poner el nombre sin simplificar
- [ ] Las digitaciones de escalas menores y minor blues están mal

## Media prioridad
- [ ] Añadir los cambios de la versión web al resto de plataformas

## Baja prioridad

- [X] Dividir `app.js` en librerías declarativas/puras (textos, notación, teoría del círculo y ayudas); las extracciones con estado quedan planificadas en `docs/architecture/AGENT_MAINTAINABILITY.md`
- [ ] Repensar el botón de bemoles y sostenidos, igual es mejor que al elegir la escala poder seleccionar sin combo, sino con botones para seleccionar la nota y si es sostenida o bemol, pero hay que ver cómo funciona en otros módulos como detección
- [ ] En digitaciones de escala se podría añadir "a 2 manos"

## Finalizadas
- [X] No se detecta bien Lam7
- [X] En escalas y acordes los intervalos son absolutos, es más razonable relativos
- [X] VII grado en círculo de quintas: Verificado que "Sidim" es CORRECTO (acorde disminuido diatónico en tonalidad mayor). "Si5dis" no es notación estándar en teoría musical.
- [X] Investigar si se puede activar el midi sin preguntar al usuario (Implementado con navigator.permissions.query())
