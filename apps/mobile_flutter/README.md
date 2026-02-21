# MIDIChords Mobile (Flutter)

Base Flutter para tablets iOS/Android del proyecto MIDIChords.

## Estado

- Estructura de navegación por módulos:
  - Detección
  - Generación de acordes
  - Escalas
  - Metrónomo
  - Afinador
- Integración con backend Python web:
  - `/api/meta`
  - `/api/detect`
  - `/api/generate/chord`
  - `/api/generate/scale`
- Detección con teclado táctil en pantalla + entrada manual de notas MIDI.
- Metrónomo nativo implementado (BPM, compás, start/stop, pulso visual).
- Afinador nativo implementado (captura de micrófono + estimación de pitch + cents).

## Ejecutar

```bash
python launch.py mobile
```

Para ejecutar directamente en iPad (arranca backend web en LAN y configura la app móvil con la URL automática):

```bash
python launch.py mobile-ipad --device "<ID_O_NOMBRE_IPAD>"
```

Puedes listar dispositivos con:

```bash
flutter devices
```

También puedes ejecutar Flutter directamente:

```bash
cd apps/mobile_flutter
flutter run
```

## Nota de arquitectura

El objetivo es compartir lógica musical a través del backend Python (`apps/web` + `midichords/core/music_service.py`) y consumirla desde Flutter por HTTP.
