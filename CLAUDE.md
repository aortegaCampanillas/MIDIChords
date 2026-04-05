# MIDIChords — contexto para Claude Code

> Documentación completa para agentes en [AGENTS.md](AGENTS.md). Este archivo es un resumen de arranque rápido.

## Qué es este proyecto

Monorepo con tres plataformas de la misma app de acordes/teoría musical:
- **Escritorio**: Python/Tkinter — `apps/desktop/` + paquete `midichords/`
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
| Web: círculo de quintas | `apps/web/static/app.js` (`renderCircleFifths`) |
| Lanzar la app | `python launch.py desktop` / `web` / `mobile` |
| Tests | `python -m pytest tests/` |

## Convenciones clave

- Idioma UI por defecto: **español** (`es`). Ver `midichords/core/i18n.py`.
- App escritorio = **Tkinter** (rama `main`). Los archivos `qt_*.py` son experimentales.
- Rutas a assets/samples: usar `midichords.core.app_constants.PROJECT_ROOT`.
- Python requerido: **3.12** (python-rtmidi solo tiene rueda hasta cp312 en Windows).
- Deploy web: solo se lanza con **push de etiqueta `v*`**, no con push a `main`.

## Archivos grandes — leer solo lo necesario

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| `midichords/mixins/ui_mixin.py` | ~3000 | Construcción de paneles y tabs Tk |
| `midichords/main_app.py` | ~1600 | Clase principal (hereda todos los mixins) |
| `midichords/mixins/render_mixin.py` | ~1550 | Dibujo de teclado y pentagrama |
| `apps/web/static/app.js` | grande | SPA completa |

Pide siempre el método o la sección concreta, no el archivo entero.

## Antes de cerrar un cambio

```bash
python -m pytest tests/
```
