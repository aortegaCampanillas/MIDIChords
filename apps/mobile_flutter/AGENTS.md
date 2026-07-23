# Instrucciones para `apps/mobile_flutter/`

Estas reglas complementan el `AGENTS.md` de la raíz.

## Arquitectura actual

- `lib/main.dart` concentra todavía gran parte del estado, lógica local, servicios y UI.
- `lib/music_catalog.dart` contiene los datos declarativos de acordes, escalas y nombres localizados; modificarlo junto con sus tests de integridad y comprobar la paridad multiplataforma.
- `lib/music_service.dart` contiene generación, detección, inversiones, spelling y presentación de patrones sin dependencias de Flutter/UI. La UI debe consumir este módulo en vez de volver a introducir esas reglas en `main.dart`.
- `lib/main_painters.dart` es un `part` de `main.dart` que agrupa los painters privados de pentagrama, metrónomo y afinador. Comparte deliberadamente símbolos privados con la pantalla; usarlo para dibujo, no para estado o reglas musicales.
- `lib/main_pages.dart` es un `part` con una extensión privada que agrupa los constructores de las páginas de cada modo. Comparte deliberadamente el estado de `_HomeScreenState`; mantener aquí composición de widgets y callbacks breves, no añadir reglas musicales ni servicios con ciclo de vida.
- `lib/main_help.dart` es un `part` con el catálogo contextual, resolución de anclas y geometría del tour de ayuda. Comparte las claves y el estado privado de `_HomeScreenState`; reutilizar `_updateState` en vez de llamar directamente a `setState` desde la extensión.
- `lib/piano_layout.dart` calcula tamaños y necesidad de scroll del teclado sin widgets ni estado; sus constantes conservan la proporción visual compartida con web.
- `lib/tuner_capture_session.dart` posee el ciclo de vida de `FlutterAudioCapture` detrás de un puerto inyectable. `main.dart` conserva DSP y estado visual; probar inicialización, errores, reintentos y cierre sin micrófono en `test/tuner_capture_session_test.dart`.
- `lib/native_audio_bridge.dart` concentra las llamadas al canal nativo para tonos, acordes y metrónomo en Android/iOS. Normaliza sus argumentos detrás de `NativeAudioPort`; `main.dart` conserva el enrutado por plataforma, los fallbacks y el estado visual.
- `lib/transient_player_lifecycle.dart` posee las suscripciones de finalización y la liberación idempotente de los `AudioPlayer` transitorios. Registrar ahí cada reproductor que deba cerrarse al completar y usar el mismo controlador para cierres manuales o globales.
- `lib/audio_player_port.dart` es la frontera con `audioplayers`: configura modo, liberación y contexto antes de devolver `AudioPlayerPort`, y descarta instancias cuya configuración falle. El estado y los mapas de notas retenidas deben depender del puerto, no de `AudioPlayer`.
- `lib/sample_tone_plan.dart` es la fuente de los bancos de samples móviles y decide de forma pura el asset cercano, rango reproducible y velocidad de transposición. La pantalla solo ejecuta el plan o usa su fallback sintetizado.
- Los módulos ya extraídos en `lib/` son preferibles como destino para lógica pura y componentes acotados.
- La app mantiene implementaciones locales de generación/detección musical para funcionar sin depender de la API web.

## Criterio para nuevas extracciones

1. Extraer primero datos declarativos, funciones puras y modelos, con tests. `music_catalog.dart` y `music_service.dart` son los primeros ejemplos de este patrón.
2. Después extraer servicios con ciclo de vida: audio, MIDI, preferencias y cachés.
3. Extraer painters y widgets sin trasladar estado global innecesario.
4. Separar páginas por modo en `main_pages.dart`; extraer widgets autónomos cuando ya no necesiten acceso amplio al estado de la pantalla.
5. Mantener catálogo, anclas y geometría de la ayuda en `main_help.dart`; los widgets solo deben registrar sus identificadores mediante `_helpAnchor`.

No introducir una librería nueva de gestión de estado únicamente para reducir el tamaño de `main.dart`. La separación debe conservar comportamiento, reproducción, MIDI, scroll y ciclo de vida de cada modo.

## Assets compartidos

`assets/guitar_chord_cache.json`, `assets/chord_variant_theory.json` y varios samples tienen copias canónicas o equivalentes en la raíz/web. `assets/changelog.json` es una copia generada desde `../../assets/changelog.json`: no editarla directamente; usar `python scripts/sync_shared_assets.py` desde la raíz. Los tests Python validan su igualdad; consultar `docs/architecture/SOURCE_OF_TRUTH.md` antes de editarlos.

## Verificación

Desde la raíz:

```bash
python scripts/check.py mobile
```

El perfil ejecuta `flutter analyze` y `flutter test` dentro de `apps/mobile_flutter/`. Ejecutar además `python scripts/check.py python` cuando cambien assets o contratos multiplataforma.
