# MIDIChords — contexto para Claude Code

> Documentación completa para agentes en [AGENTS.md](AGENTS.md). Este archivo es un resumen de arranque rápido.

## Qué es este proyecto

Monorepo con tres plataformas de la misma app de acordes/teoría musical:
- **Escritorio**: Python/PySide6 — `apps/desktop/` + paquete `midichords/`; `midichords/qt/` adapta parte de la API Tk histórica
- **Web**: SPA estática + Cloudflare Worker — `apps/web/`
- **Móvil**: Flutter iOS/Android — `apps/mobile_flutter/`

La lógica reutilizable está en el paquete Python `midichords/`.

## Navegación rápida por tarea

| Tarea | Archivo |
|-------|---------|
| Patrón de acorde o escala | `midichords/core/music_theory.py` |
| Textos de UI / nombres de notas | `midichords/core/i18n.py` |
| Generación de acordes | `midichords/core/music_service.py`, `midichords/mixins/generation_mixin.py` |
| Detección de acorde desde notas | `midichords/mixins/input_detection_mixin.py` |
| Reproducción de audio | `midichords/core/audio_engine.py` |
| Entrada MIDI | `midichords/mixins/midi_io_mixin.py` |
| UI escritorio (paneles, teclado, pentagrama) | `midichords/mixins/ui_mixin.py`, `midichords/mixins/render_mixin.py` |
| Web: círculo de quintas | `apps/web/static/circle_theory.js` (teoría/geometría/hit-testing), `apps/web/static/app.js` (`renderCircleFifths`) |
| Web: detección de intervalos | `apps/web/static/interval_theory.js` (teoría/melodías), `apps/web/static/app.js` (estado/reproducción) |
| Web: generación de intervalos | `apps/web/static/interval_theory.js` (`INTERVAL_GRID_COLUMNS`, tabla de intervalos por semitono/categoría), `apps/web/static/app.js` (estado `intervalGen*`, tabla y reproducción) |
| Web: digitaciones de piano | `apps/web/static/piano_fingering.js` |
| Web: armaduras y relativos modales | `apps/web/static/key_signature.js` |
| Web: normalización y etiquetas de escalas | `apps/web/static/scale_theory.js` |
| Web: salida MIDI de bajo nivel | `apps/web/static/midi_output.js` |
| Web: catálogo y matemática de samples | `apps/web/static/audio_samples.js` |
| Web: descarga y caché de samples | `apps/web/static/audio_sample_loader.js` |
| Web: envolventes y liberación de voces | `apps/web/static/audio_voice.js` |
| Web: autocorrelación y frecuencia/MIDI | `apps/web/static/tuner_math.js` |
| Web: resaltado durante reproducción | `apps/web/static/playback_highlight.js` |
| Web: textos generales ES/EN | `apps/web/static/ui_texts.js` |
| Web: nombres, alteraciones y armaduras | `apps/web/static/music_notation.js` |
| Web: ayuda teórica de acordes | `apps/web/static/chord_help.js` |
| Web: ayuda contextual por modo | `apps/web/static/help_callouts.js` |
| Lanzar la app | `python launch.py desktop` / `web` / `mobile` |
| Verificación | `python scripts/check.py python|web|mobile|all` |

## Convenciones clave

- Idioma UI por defecto: **español** (`es`). Ver `midichords/core/i18n.py`.
- App escritorio = **Qt/PySide6** (rama `main`). Los imports `tk_compat` son adaptadores sobre Qt, no una segunda UI Tkinter.
- Rutas a assets/samples: usar `midichords.core.app_constants.PROJECT_ROOT`.
- Python requerido: **3.12** (python-rtmidi solo tiene rueda hasta cp312 en Windows).
- Deploy web: solo se lanza con **push de etiqueta `v*`**, no con push a `main`.
- **Versión unificada**: `VERSION` en la raíz es la única fuente de verdad para escritorio, web y móvil. No edites `APP_RELEASE_NAME`, `APP_VERSION`, `WEB_APP_VERSION_FALLBACK`, `softwareVersion` (HTML) ni `version:` de `pubspec.yaml` a mano — cambia `VERSION` y ejecuta `python scripts/sync_shared_assets.py` (o cualquier `launch.py`/`scripts/check.py`, que ya lo invocan). El build number de Flutter (`+N`) se autoincrementa solo cuando cambia la versión base.

## Archivos grandes — leer solo lo necesario

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| `apps/mobile_flutter/lib/main.dart` | ~7360 | Estado y composición transversal de la UI móvil |
| `apps/web/static/app.js` | ~6980 | Estado, modos, renderers y ciclos de vida de audio/MIDI de la SPA |
| `midichords/mixins/ui_mixin.py` | ~3870 | Construcción de paneles y modos Qt |
| `midichords/mixins/render_mixin.py` | ~2180 | Dibujo de instrumentos y pentagrama |
| `midichords/main_app.py` | ~1800 | Ventana principal y estado transversal |
| `apps/mobile_flutter/lib/main_painters.dart` | ~1650 | Painters privados compartidos como `part` de `main.dart` |
| `apps/mobile_flutter/lib/main_pages.dart` | ~2100 | Constructores de páginas por modo como extensión privada de la pantalla |
| `apps/mobile_flutter/lib/main_help.dart` | ~1050 | Catálogo, anclas y geometría del tour de ayuda móvil |

Pide siempre el método o la sección concreta, no el archivo entero.

Hay instrucciones específicas en `midichords/AGENTS.md`, `apps/web/AGENTS.md` y `apps/mobile_flutter/AGENTS.md`.
El estado y los siguientes límites de la refactorización están en `docs/architecture/AGENT_MAINTAINABILITY.md`.

## Antes de cerrar un cambio

```bash
python scripts/check.py python
```
