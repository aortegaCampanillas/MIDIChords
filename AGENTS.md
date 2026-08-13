# Documentación para agentes IA — MIDIChords

Este documento orienta a asistentes de código (agentes IA) sobre la estructura, puntos de entrada y convenciones del proyecto. Para una **especificación que permita regenerar el proyecto desde cero**, ver [PROJECT_SPEC.md](PROJECT_SPEC.md).

## Resumen del proyecto

**MIDIChords** es un monorepo con varias versiones de una misma aplicación de acordes y teoría musical:

- **Escritorio (Python/PySide6)**: `apps/desktop/` — app principal Qt. Conserva una API parecida a Tk mediante `midichords/qt/` para reutilizar la UI histórica.
- **Web**: `apps/web/` — frontend estático + Cloudflare Worker; misma lógica vía API del worker.
- **Móvil/tablet (Flutter)**: `apps/mobile_flutter/` — app iOS/Android que reutiliza lógica vía llamadas al backend o implementación propia.

La implementación Python reutilizable está en **`midichords`** y alimenta el escritorio y scripts. El Worker web y Flutter mantienen implementaciones propias de parte de la teoría musical; deben conservar paridad de contratos y resultados con el core Python.

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
│   ├── qt/               # Compatibilidad de API Tk sobre PySide6
│   ├── ui/               # Widgets Qt y componentes visuales
│   ├── main_app.py       # Ventana Qt principal (MidiChordAnalyzerApp)
│   └── mixins/           # Modos y subsistemas de la UI de escritorio
├── assets/               # Imágenes, samples de audio compartidos
├── tests/                # Tests Python; fixtures/ y helpers en support/
├── scripts/              # Build, firma, notarización, utilidades
├── packaging/            # Flatpak, Microsoft Store y configuración macOS
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
| Verificación          | `python scripts/check.py python|web|mobile|all` desde la raíz. |

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

- **`MidiChordAnalyzerApp`**: Ventana principal PySide6. Hereda de los mixins de funcionalidad, `QtSchedulerMixin` y `QMainWindow`.
- **`main()`**: Punto de entrada que crea `QApplication`, construye la ventana y ejecuta el event loop de Qt.

La app de escritorio se lanza siempre desde `apps/desktop/main.py` → `midichords.main_app.main()`.

### `midichords/ui/widgets_qt.py`

Contiene los widgets personalizados activos de la aplicación Qt. La antigua
implementación Tk se retiró al confirmar que no tenía consumidores.

## Versión de Python (escritorio)

Para instalar **todo** `requirements.txt` (incl. **python-rtmidi**) en **Windows** hace falta **Python 3.12**: en PyPI, `python-rtmidi` 1.5.8 solo ofrece ruedas hasta `cp312` para `win_amd64`. Con **3.13**, NumPy/PySide6/mido/sounddevice suelen instalar, pero **no** hay rueda rtmidi (MIDI hardware falla hasta compilar o cambiar de versión de Python). **Python 3.14** suele fallar en varios paquetes nativos; el CI usa `python-version: '3.12'`.

## Cómo ejecutar tests

Desde la **raíz del proyecto**, con el entorno virtual activado y `requirements-dev.txt` instalado:

```bash
python scripts/check.py python
```

El perfil usa pytest porque la suite contiene tanto casos `unittest` como funciones pytest. Ejecutar solamente `unittest discover` omite parte de la suite.

## Comandos de verificación

Ejecutar desde la **raíz** el perfil correspondiente a los archivos cambiados:

```bash
python scripts/check.py python
python scripts/check.py web
python scripts/check.py mobile
# Todos, en ese orden:
python scripts/check.py all
```

Los perfiles son también la interfaz usada por `.github/workflows/quality.yml`.

## Convenciones útiles para agentes

1. **Idioma por defecto**: La UI y los textos por defecto suelen estar en español (`es`). `midichords.core.i18n` y `music_service.note_name(..., language="es")` son los puntos de uso.
2. **Ruta del proyecto**: Las rutas a assets/samples/config se resuelven con `midichords.core.app_constants.PROJECT_ROOT` (o equivalente). En Flatpak puede ser `/app/share/midichords`.
3. **Detección de acordes**: La fuente de verdad para “qué acorde es un conjunto de notas” está en `music_theory.analyze_chord_notes()` y en la capa de “spelling”/detección armónica en `music_service` / `InputDetectionMixin` (`_detect_harmonic_spelling`, `detect_chord`).
4. **Escritorio Qt con compatibilidad Tk**: En `main` la ventana real es PySide6. Los imports `midichords.qt.tk_compat as tk` son una capa de adaptación, no Tkinter real. Antes de cambiar un widget, comprobar si procede de `widgets_qt.py`, `midichords/qt/` o de PySide6 directamente.
5. **Web**: La API está en `apps/web/worker/`. El cliente es una SPA en **`apps/web/static/app.js`** (y `style.css`): modos detección, generación, **círculo de quintas**, escalas, metrónomo y afinador. Cualquier cambio en respuestas o rutas API debe reflejarse en el worker y, si aplica, en `apps/web/static/` y los HTML bajo `apps/web/`. El modo **círculo de quintas** (`state.mode === "circle_fifths"`) dibuja el círculo en canvas (`renderCircleFifths`), fija tonalidad con clic (anillo mayor/menor), acorde diatónico con Mayús+clic y usa `POST /api/generate/chord`; detalle en **`apps/web/README.md`** → sección *Frontend (modos SPA)*. El toggle **`soundOutputToggle`** (en el header, junto al botón MIDI) controla `state.soundOutput` (`"audio"` | `"midi"`): en modo `"audio"` la app genera audio WebAudio; en modo `"midi"` todas las notas (escalas, acordes, botones ▶) se envían al dispositivo MIDI conectado vía Web MIDI API (`getMidiOutput`, `sendMidiNote`, `sendMidiNoteOn/Off`), y la entrada MIDI del dispositivo no genera audio de la app. La preferencia se persiste en `localStorage("soundOutput")`.

## Resumen rápido por tarea

| Si necesitas… | Mira en… |
|---------------|----------|
| Añadir/cambiar un patrón de acorde o escala | `midichords/core/music_theory.py` |
| Cambiar textos de UI o nombres de notas | `midichords/core/i18n.py` |
| Lógica de generación de acordes / inversiones | `midichords/core/music_service.py` (`generate_chord`) y `midichords/mixins/generation_mixin.py` |
| Cómo se detecta el acorde desde notas activas | `midichords/mixins/input_detection_mixin.py` y `music_theory.analyze_chord_notes` |
| Reproducción de notas (piano/guitarra) | `midichords/core/audio_engine.py` |
| Entrada MIDI | `midichords/mixins/midi_io_mixin.py` |
| UI de escritorio (paneles, botones, teclado, pentagrama) | `midichords/main_app.py`, `midichords/ui/widgets_qt.py`, `midichords/ui/desktop_ui_builders.py`, `midichords/mixins/ui_mixin.py`, `midichords/mixins/render_mixin.py` |
| Lanzar desktop / web / mobile | `launch.py` |
| Web: modo círculo de quintas (canvas, tonalidad, Mayús+clic diatónico) | `apps/web/static/app.js` (`renderCircleFifths`, `circleChordRootPcFromClick`, `runGenerateChordCircle`) |
| Tests unitarios | `tests/` (importan `midichords.*`) |

## Instrucciones locales y fuentes de verdad

- Al trabajar bajo `midichords/`, leer también `midichords/AGENTS.md`.
- Al trabajar en web, leer `apps/web/AGENTS.md`.
- Al trabajar en Flutter, leer `apps/mobile_flutter/AGENTS.md`.
- Para saber qué datos son canónicos, cuáles se duplican por plataforma y cómo validarlos, ver `docs/architecture/SOURCE_OF_TRUTH.md`.

## Términos clave

- **root_pc** / **tonic_pc**: clase de pitch 0–11 (C=0, C#=1, …, B=11).
- **suffix**: variante del acorde (ej. `""`, `"m"`, `"7"`, `"maj7"`) según `ChordPattern.suffix`.
- **inversion**: índice de inversión (0 = fundamental en el bajo).
- **Notas sobrantes**: notas que no pertenecen al acorde detectado (según el mejor ajuste armónico).
- **PROJECT_ROOT**: raíz de recursos (assets, samples, config); ver `app_constants`.

## Convenciones del usuario

- **"Sube etiqueta"** (o equivalente): hacer **commit** de los cambios pendientes, **push** a la rama actual y **mover la última etiqueta** (p. ej. `v1.0.1`) al último commit, con `git tag -f <tag>` y `git push --force origin <tag>`. Así se re-dispara el workflow de instaladores para esa versión.
- **Builds de prueba sin gastar versión (tags `beta-N`):** `.github/workflows/build-installers.yml` también dispara con tags `beta-1`, `beta-2`, … (contador plano, sin `X.Y.Z` propio — evita acoplar el intento a la versión candidata y evita el problema de que Microsoft Store exige que el 4º segmento de versión del MSIX sea `0`).
  - `git tag beta-1 && git push origin beta-1` genera los mismos artefactos (Windows `.exe`/`.msix`, macOS `.dmg`, Debian `.deb`) que un tag `vX.Y.Z`, pero publica la GitHub Release marcada **prerelease** (no sustituye la "latest release" estable) y **no se sincroniza** al repo público `FreeMIDIChords_Releases`.
  - La versión que llevan los artefactos (instalador Windows, manifiesto MSIX, `.deb`) sigue viniendo de `APP_RELEASE_NAME` en `midichords/core/app_constants.py` (fuente de verdad del proyecto), no del nombre del tag — no hace falta repetir el número de versión al crear el tag beta.
  - Para siguientes tags usar el número siguiente (`beta-2`, `beta-3`, …); no hace falta borrar los anteriores, pero conviene limpiarlos de vez en cuando (son prereleases, no releases públicas).
  - **Cuando la beta ya se validó en Windows/Mac**, crear el tag `vX.Y.Z` real (proceso normal de "sube etiqueta" arriba) para la release pública — el tag `beta-N` no se convierte en `vX.Y.Z`, son independientes.
- **Despliegue a producción (web):** el deploy a Cloudflare Pages **solo** se lanza con **push de una etiqueta** `v*`, no con push a `main`. Ver `README.md` y `apps/web/README.md`.
- **Changelog (obligatorio mantenerlo):** cuando se hace un cambio relevante, actualizar `CHANGELOG.md` (sección **Unreleased**) para que la próxima subida/release quede trazable.
  - La única fuente editable del changelog mostrado por las aplicaciones es `assets/changelog.json`. No editar directamente `apps/web/static/changelog.json` ni `apps/mobile_flutter/assets/changelog.json`: son copias generadas por `python scripts/sync_shared_assets.py`. `launch.py` y `scripts/check.py` las actualizan automáticamente.
  - En los `changelog.json`, la plataforma se indica exclusivamente mediante el campo `platforms`; no repetir en los textos `es`/`en` expresiones como "en web", "en escritorio", "en móvil" o "en todas las plataformas".
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

### Capturas para App Store Connect

- Antes de entregar o subir capturas de escritorio, verificar sus dimensiones reales.
- Apple solo admite estas resoluciones para este conjunto: `1280 × 800`, `1440 × 900`, `2560 × 1600` o `2880 × 1800` píxeles.
- No basta con conservar la proporción: el ancho y el alto deben coincidir exactamente con una resolución admitida.
- Si hay que adaptar una captura, recortarla centrada a proporción `16:10` y redimensionarla después, evitando deformar la interfaz.

## Otros documentos

- **CONTRIBUTING.md**: ramas, estilo, cómo hacer PRs.
- **PROJECT_SPEC.md**: especificación para regenerar el proyecto.
- **`docs/architecture/AGENT_MAINTAINABILITY.md`**: resultado de la refactorización para agentes, límites actuales y siguientes candidatos seguros.
- **`docs/ROADMAP.md`**: único backlog documental vigente; `docs/archive/` es solo contexto histórico.

---

*Documento pensado para que agentes IA encuentren contexto y rutas sin leer todo el código.*
