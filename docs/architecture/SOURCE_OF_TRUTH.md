# Fuentes de verdad y paridad multiplataforma

Este documento indica a humanos y agentes dónde debe comenzar un cambio y qué copias o consumidores deben comprobarse.

## Matriz

| Concepto | Fuente o referencia actual | Consumidores/copias | Verificación existente |
|---|---|---|---|
| Patrones de acordes y escalas | `midichords/core/music_theory.py` | `apps/web/worker/_worker.js`, `apps/mobile_flutter/lib/music_catalog.dart` | Tests Python, `apps/mobile_flutter/test/music_catalog_test.dart` y `scripts/compare_api_parity.py` (comparación con producción) |
| Contrato musical Python | `midichords/core/music_service.py` | Worker y `apps/mobile_flutter/lib/music_service.dart` implementan resultados equivalentes | Tests Python, `apps/mobile_flutter/test/music_service_test.dart` y `scripts/compare_api_parity.py` para una muestra Python/producción |
| Ayuda de variantes | `assets/chord_variant_theory.json` | `apps/mobile_flutter/assets/chord_variant_theory.json`; la web mantiene su catálogo en `apps/web/static/chord_help.js` | `tests/test_chord_help_cross_platform.py` y `tests/test_web_chord_variant_help.py` |
| Textos generales de la web | `apps/web/static/ui_texts.js` | La SPA los consume mediante `globalThis.MidiChordsUiTexts` | `tests/test_web_ui_texts.py` |
| Notación básica de la web | `apps/web/static/music_notation.js` | Nombres de notas, alteraciones, armaduras y mapeos diatónicos de la SPA | `apps/web/test/catalogs.test.js` |
| Teoría del círculo web | `apps/web/static/circle_theory.js` | El renderer y las interacciones con estado permanecen en `apps/web/static/app.js` | `apps/web/test/catalogs.test.js` |
| Teoría de intervalos web | `apps/web/static/interval_theory.js` | Cola, temporizadores, reproducción y renderer permanecen en `apps/web/static/app.js` | `apps/web/test/catalogs.test.js` |
| Digitaciones de piano web | `apps/web/static/piano_fingering.js` | La UI de escalas consume resultados puros y puede recibir vacío si no hay patrón documentado | `apps/web/test/catalogs.test.js` y tests Python de digitaciones |
| Armaduras de la web | `apps/web/static/key_signature.js` | `getStaffContext()` adapta el estado de cada modo en `apps/web/static/app.js` | `apps/web/test/catalogs.test.js` y tests Python de armaduras |
| Presentación de escalas web | `apps/web/static/scale_theory.js` | Instrumento, nota inicial y reproducción se adaptan desde el estado de `apps/web/static/app.js` | `apps/web/test/catalogs.test.js` |
| Salida Web MIDI | `apps/web/static/midi_output.js` | `apps/web/static/app.js` aporta dispositivo, permisos, preferencia e instrumento | `apps/web/test/midi_output.test.js` |
| Samples de audio web | `apps/web/static/audio_samples.js` (catálogo y matemática), `apps/web/static/audio_sample_loader.js` (descarga y caché) | `apps/web/static/app.js` aporta gesto, `AudioContext`, nodos y ciclo de vida | `apps/web/test/audio_samples.test.js` y `apps/web/test/audio_sample_loader.test.js` |
| Ayuda contextual de la web | `apps/web/static/help_callouts.js` | La SPA selecciona los callouts según el modo activo | `apps/web/test/catalogs.test.js` |
| Acordes de guitarra | `assets/guitar_chord_cache.json` | `apps/web/static/` y `apps/mobile_flutter/assets/` | `tests/test_shared_assets_cross_platform.py` |
| Changelog de producto | `apps/web/static/changelog.json` | Escritorio lo carga desde esa ruta; Flutter conserva copia en assets | `tests/test_shared_assets_cross_platform.py` |
| Samples compartidos | `assets/` | Copias necesarias para web y bundle Flutter | `tests/test_shared_assets_cross_platform.py` |
| Build web publicable | Fuentes bajo `apps/web/`; `app.html` declara JS/CSS y su orden | `apps/web/pages-dist/` generado y no versionado | `scripts/build_web_pages_dist.py` descubre y versiona automáticamente los assets enlazados |

## Reglas de cambio

1. Editar primero la fuente indicada; no comenzar por una copia empaquetada.
2. Actualizar todos los consumidores en el mismo cambio cuando el formato o comportamiento sea incompatible.
3. No editar `apps/web/pages-dist/`: se regenera.
4. Si una copia de assets es necesaria para el bundle, mantenerla idéntica y ejecutar los tests de assets.
5. Un cambio de algoritmo musical debe añadir casos que puedan reutilizar Python, JavaScript y Dart, aunque la infraestructura común todavía sea parcial.

## Verificación reproducible

`scripts/check.py` es la interfaz común para desarrollo local, agentes y CI:

```bash
python scripts/check.py python
python scripts/check.py web
python scripts/check.py mobile
python scripts/check.py all
```

El workflow `.github/workflows/quality.yml` ejecuta los tres perfiles en jobs aislados para que un fallo de herramientas de una plataforma no oculte los resultados de las demás.

## Carencias conocidas y dirección recomendada

- Los patrones musicales están declarados en tres lenguajes. La dirección recomendada es mover los datos declarativos a un catálogo canónico, manteniendo lectores o generación por plataforma.
- Los algoritmos no deben depender de una llamada de red para compartirse. La paridad debe apoyarse en fixtures de entrada/salida comunes y tests locales.
- `scripts/compare_api_parity.py` depende de producción y no sustituye una comprobación offline en CI.
- Falta una orden única de sincronización de assets; hasta que exista, los tests de igualdad son el guardarraíl obligatorio.
