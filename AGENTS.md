# Documentación para agentes IA — MIDIChords

Este documento orienta a asistentes de código (agentes IA) sobre la estructura, puntos de entrada y convenciones del proyecto. Para una **especificación que permita regenerar el proyecto desde cero**, ver [PROJECT_SPEC.md](PROJECT_SPEC.md).

## Resumen del proyecto

**MIDIChords** es un monorepo con varias versiones de una misma aplicación de acordes y teoría musical:

- **Escritorio (Python/Tkinter)**: `apps/desktop/` — app principal con detección de acordes, generación, escalas, metrónomo y afinador.
- **Web**: `apps/web/` — frontend estático + Cloudflare Worker; misma lógica vía API del worker.
- **Móvil/tablet (Flutter)**: `apps/mobile_flutter/` — app iOS/Android que reutiliza lógica vía llamadas al backend o implementación propia.

La **lógica reutilizable** está en el paquete Python **`midichords`**. Las apps (desktop, web worker, scripts) importan desde `midichords`; Flutter puede llamar a la API web o duplicar reglas de negocio.

## Estructura de directorios

```text
.
├── apps/
│   ├── desktop/          # App escritorio: main.py → midichords.main_app.main
│   ├── web/              # index.html, static/, worker/ (Cloudflare Worker)
│   └── mobile_flutter/   # Flutter (iOS/Android)
├── midichords/           # Paquete Python compartido
│   ├── core/             # Teoría musical, audio, config, i18n
│   ├── mixins/           # Lógica por modo (UI, detección, generación, MIDI, etc.)
│   ├── ui/               # Widgets Tkinter (botones, paneles, canvas)
│   ├── main_app.py       # App Tk principal (MidiChordAnalyzerApp)
│   └── qt_app.py, qt_widgets.py  # (Si existen) UI Qt experimental
├── assets/               # Imágenes, samples de audio compartidos
├── tests/                # Tests unitarios (Python unittest)
├── scripts/              # Build, firma, notarización, utilidades
├── packaging/            # Flatpak, Microsoft Store, etc.
├── launch.py             # Punto de entrada unificado (desktop, web, mobile)
├── app.py                # Alias histórico para desktop
└── requirements.txt     # Dependencias Python
```

## Puntos de entrada

| Objetivo              | Cómo ejecutar |
|-----------------------|----------------|
| App escritorio        | `python launch.py desktop` o `python app.py` (desde la raíz del repo). Trazas **audio/MIDI** en stderr: `python launch.py desktop /verbose` (o `--verbose`/`-v`, o `MIDICHORDS_VERBOSE=1`). Equivalente: `python apps/desktop/main.py` si `PYTHONPATH` incluye la raíz. |
| App web (local)       | `python launch.py web --host 127.0.0.1 --port 8000` (usa `wrangler dev`). Abrir `http://127.0.0.1:8000`. |
| App Flutter           | `python launch.py mobile` (o `python launch.py mobile -d <device_id>`). Requiere Flutter y emulador/dispositivo. |
| Tests Python          | `python -m pytest tests/` o `python -m unittest discover -s tests`. Los tests importan `midichords.*`. |

El **launch unificado** está en `launch.py`: define `run_desktop()`, `run_web()`, `run_mobile()` y parsea argumentos. Las configuraciones de VS Code/Cursor suelen usar `launch.py` o `apps/desktop/main.py` con el directorio de trabajo en la raíz del proyecto.

## Paquete `midichords` — dónde está cada cosa

### `midichords/core/`

- **`music_theory.py`**: Patrones de acordes y escalas (`CHORD_PATTERNS`, `SCALE_PATTERNS`), `analyze_chord_notes(notes)`, `format_intervals(notes)`, `note_name(language, midi_note, with_octave)`. Sin dependencias de UI.
- **`music_service.py`**: API de alto nivel: `generate_chord()`, `detect_chord()`, `generate_scale()`, `list_chord_patterns()`, `list_scale_patterns()`. Usa `music_theory` e `i18n`; pensado para reutilizar en desktop y web/API.
- **`audio_engine.py`**: `PianoAudioEngine` (note_on/note_off), voces para piano, metrónomo, guitarra, samples. Depende de `PROJECT_ROOT` para rutas de samples.
- **`i18n.py`**: Diccionarios de textos (notas, escalas, UI). Idiomas clave: `es`, `en`.
- **`app_config.py`** / **`app_constants.py`**: Configuración, rutas (CONFIG_PATH, PROJECT_ROOT), constantes de UI (imágenes, fuentes).
- **`guitar_chord_cache.py`**: Caché de variaciones de acordes de guitarra.
- **`image_utils.py`**: Utilidades para imágenes Tk (PhotoImage, redimensionar, iconos).

### `midichords/mixins/`

La app de escritorio está compuesta por una clase principal que hereda de varios mixins. Cada mixin aporta un modo o bloque de funcionalidad:

- **`UiMixin`**: Construcción de paneles, pestañas, variables de UI (Tk).
- **`RenderMixin`**: Dibujo del teclado y del pentagrama (canvas Tk).
- **`InputDetectionMixin`**: Notas activas (ratón + MIDI), detección armónica de acordes, actualización de labels (notas, intervalo, acorde detectado). Usa `analyze_chord_notes` y lógica de “notas sobrantes”.
- **`GenerationMixin`**: Generación de acordes (patrón, inversión), vista de acorde generado y reproducción.
- **`ScalesMixin`**: Escalas (patrón, tónica), vista y reproducción.
- **`MetronomeMixin`**: Metrónomo (BPM, clic).
- **`TunerMixin`**: Afinador (detección de frecuencia).
- **`MidiIOMixin`**: Entrada/salida MIDI (dispositivos, mensajes).
- **`OverlaysMixin`**: Diálogos/overlays (selector de modo, etc.).

Para **añadir o cambiar comportamiento** en un modo concreto, localizar el mixin correspondiente y el método que enlaza con la UI (por ejemplo, en detección: `update_music_views`, `_current_detection_notes`, `detect_chord`).

### `midichords/main_app.py`

- **`MidiChordAnalyzerApp`**: Clase principal Tk que hereda de todos los mixins y de `tk.Tk`. Orden de herencia: UiMixin, RenderMixin, OverlaysMixin, TunerMixin, MetronomeMixin, ScalesMixin, GenerationMixin, MidiIOMixin, InputDetectionMixin, tk.Tk.
- **`main()`**: Punto de entrada que crea la app y ejecuta el mainloop.

La app de escritorio se lanza siempre desde `apps/desktop/main.py` → `midichords.main_app.main()`.

### `midichords/ui/widgets.py`

Widgets Tkinter reutilizables: `RoundedChoiceButton`, `RoundedPanel`, `GreenRoundedButton`, `GrayRoundedButton`, `PlayTransportButton`, etc. No contienen lógica de negocio; solo presentación y eventos básicos.

## Versión de Python (escritorio)

Para instalar **todo** `requirements.txt` (incl. **python-rtmidi**) en **Windows** hace falta **Python 3.12**: en PyPI, `python-rtmidi` 1.5.8 solo ofrece ruedas hasta `cp312` para `win_amd64`. Con **3.13**, NumPy/PySide6/mido/sounddevice suelen instalar, pero **no** hay rueda rtmidi (MIDI hardware falla hasta compilar o cambiar de versión de Python). **Python 3.14** suele fallar en varios paquetes nativos; el CI usa `python-version: '3.12'`.

## Cómo ejecutar tests

Desde la **raíz del proyecto**, con el entorno virtual activado y dependencias instaladas:

```bash
python -m unittest discover -s tests -p "test_*.py"
# o
python -m pytest tests/
```

Los tests importan módulos de `midichords`; el directorio de trabajo debe ser la raíz del repo (o `PYTHONPATH` debe incluirla) para que `midichords` se resuelva.

## Comandos de verificación

Antes de dar por cerrado un cambio en código Python, ejecutar desde la **raíz** del repo:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Si el proyecto usa pytest: `python -m pytest tests/`. Si hay linter (ruff, etc.): ejecutarlo según `CONTRIBUTING.md` o scripts del repo.

## Convenciones útiles para agentes

1. **Idioma por defecto**: La UI y los textos por defecto suelen estar en español (`es`). `midichords.core.i18n` y `music_service.note_name(..., language="es")` son los puntos de uso.
2. **Ruta del proyecto**: Las rutas a assets/samples/config se resuelven con `midichords.core.app_constants.PROJECT_ROOT` (o equivalente). En Flatpak puede ser `/app/share/midichords`.
3. **Detección de acordes**: La fuente de verdad para “qué acorde es un conjunto de notas” está en `music_theory.analyze_chord_notes()` y en la capa de “spelling”/detección armónica en `music_service` / `InputDetectionMixin` (`_detect_harmonic_spelling`, `detect_chord`).
4. **No asumir Qt**: En la rama `main` la app de escritorio es Tkinter. Si existen `qt_app.py` / `qt_widgets.py`, son experimentales o de otra rama; no modificar la UI Tk sin tener en cuenta que es la referencia actual.
5. **Web**: La API está en `apps/web/worker/`. El cliente es una SPA en **`apps/web/static/app.js`** (y `style.css`): modos detección, generación, **círculo de quintas**, escalas, metrónomo y afinador. Cualquier cambio en respuestas o rutas API debe reflejarse en el worker y, si aplica, en `apps/web/static/` y `apps/web/templates/`. El modo **círculo de quintas** (`state.mode === "circle_fifths"`) dibuja el círculo en canvas (`renderCircleFifths`), fija tonalidad con clic (anillo mayor/menor), acorde diatónico con Mayús+clic y usa `POST /api/generate/chord`; detalle en **`apps/web/README.md`** → sección *Frontend (modos SPA)*. El toggle **`soundOutputToggle`** (en el header, junto al botón MIDI) controla `state.soundOutput` (`"audio"` | `"midi"`): en modo `"audio"` la app genera audio WebAudio; en modo `"midi"` todas las notas (escalas, acordes, botones ▶) se envían al dispositivo MIDI conectado vía Web MIDI API (`getMidiOutput`, `sendMidiNote`, `sendMidiNoteOn/Off`), y la entrada MIDI del dispositivo no genera audio de la app. La preferencia se persiste en `localStorage("soundOutput")`.

## Resumen rápido por tarea

| Si necesitas… | Mira en… |
|---------------|----------|
| Añadir/cambiar un patrón de acorde o escala | `midichords/core/music_theory.py` |
| Cambiar textos de UI o nombres de notas | `midichords/core/i18n.py` |
| Lógica de generación de acordes / inversiones | `midichords/core/music_service.py` (`generate_chord`) y `midichords/mixins/generation_mixin.py` |
| Cómo se detecta el acorde desde notas activas | `midichords/mixins/input_detection_mixin.py` y `music_theory.analyze_chord_notes` |
| Reproducción de notas (piano/guitarra) | `midichords/core/audio_engine.py` |
| Entrada MIDI | `midichords/mixins/midi_io_mixin.py` |
| UI de escritorio (paneles, botones, teclado, pentagrama) | `midichords/main_app.py`, `midichords/ui/widgets.py`, `midichords/mixins/ui_mixin.py`, `midichords/mixins/render_mixin.py` |
| Lanzar desktop / web / mobile | `launch.py` |
| Web: modo círculo de quintas (canvas, tonalidad, Mayús+clic diatónico) | `apps/web/static/app.js` (`renderCircleFifths`, `circleChordRootPcFromClick`, `runGenerateChordCircle`) |
| Tests unitarios | `tests/` (importan `midichords.*`) |

## Términos clave

- **root_pc** / **tonic_pc**: clase de pitch 0–11 (C=0, C#=1, …, B=11).
- **suffix**: variante del acorde (ej. `""`, `"m"`, `"7"`, `"maj7"`) según `ChordPattern.suffix`.
- **inversion**: índice de inversión (0 = fundamental en el bajo).
- **Notas sobrantes**: notas que no pertenecen al acorde detectado (según el mejor ajuste armónico).
- **PROJECT_ROOT**: raíz de recursos (assets, samples, config); ver `app_constants`.

## Convenciones del usuario

- **"Sube etiqueta"** (o equivalente): hacer **commit** de los cambios pendientes, **push** a la rama actual y **mover la última etiqueta** (p. ej. `v1.0.1`) al último commit, con `git tag -f <tag>` y `git push --force origin <tag>`. Así se re-dispara el workflow de instaladores para esa versión.
- **Despliegue a producción (web):** el deploy a Cloudflare Pages **solo** se lanza con **push de una etiqueta** `v*`, no con push a `main`. Ver `README.md` y `apps/web/README.md`.
- **Changelog (obligatorio mantenerlo):** cuando se hace un cambio relevante, actualizar `CHANGELOG.md` (sección **Unreleased**) para que la próxima subida/release quede trazable.
  - **Con el agente de Cursor:** la regla **`.cursor/rules/github-update-triggers.mdc`** (`alwaysApply: true`) hace que, si pides en natural *«actualiza cambios»*, *«haz commit y push»*, *«sube a github»*, etc., el agente ejecute el flujo (con CHANGELOG + análisis por app cuando encaje la intención “actualizar cambios” / release; con commit+push más ligero si solo pides subir). El detalle del CHANGELOG está en **`.cursor/rules/release-changelog-agent.mdc`** (también puedes mencionarlo con `@release-changelog-agent`).
  - **Manual:** script `scripts/document_release_changes.py` (menú interactivo o flags CLI) si prefieres no usar el agente. En particular:
  - **iOS/App Store**: la etiqueta `v1.0.0` se usa para referenciar la build de iOS publicada **1.0.0 (2)**; no mover esa etiqueta sin actualizar `CHANGELOG.md` y sin una razón clara.

## Publicar en iOS App Store

Flujo resumido (detalles completos en `README.md` → *Publicar en iOS App Store*):

1. Incrementar `version: X.Y.Z+N` en `apps/mobile_flutter/pubspec.yaml` (N siempre mayor que el anterior).
2. `flutter build ios --release` en `apps/mobile_flutter/`.
3. `xcodebuild archive` con `CODE_SIGN_STYLE=Automatic DEVELOPMENT_TEAM=977G5A733H -allowProvisioningUpdates`.
4. `xcodebuild -exportArchive` con `/tmp/ExportOptions_AppStore.plist` (method: app-store-connect, teamID: 977G5A733H, signingStyle: automatic).
5. Subir el IPA resultante con la app **Transporter** (no usar `notarytool` — ese perfil es solo para macOS).
6. En App Store Connect: crear versión → seleccionar build → enviar a revisión.

Bundle ID: `com.FPAlanTuring.FreeMIDIChords` · Team ID: `977G5A733H`

## Otros documentos

- **CONTRIBUTING.md**: ramas, estilo, cómo hacer PRs.
- **PROJECT_SPEC.md**: especificación para regenerar el proyecto.

---

*Documento pensado para que agentes IA encuentren contexto y rutas sin leer todo el código.*
