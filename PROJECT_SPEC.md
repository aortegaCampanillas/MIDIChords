# Especificación del proyecto MIDIChords

Documento pensado para **regenerar o recrear** el proyecto desde cero. Describe qué es la aplicación, qué tecnologías usa, cómo está organizado el repo y qué debe cumplir cada parte.

---

## 1. Objetivo del producto

**MIDIChords** es una aplicación de **teoría musical y acordes** que permite:

- **Detección de acordes**: el usuario pulsa notas (en un teclado virtual, guitarra virtual o dispositivo MIDI) y la app muestra el nombre del acorde, las notas activas, las “notas sobrantes” respecto al acorde detectado y los intervalos.
- **Generación de acordes**: elegir tónica, variante (sufijo) e inversión; ver y escuchar el acorde generado.
- **Escalas**: elegir tónica y tipo de escala; ver notas e intervalos y reproducir la escala (opcionalmente con metrónomo).
- **Metrónomo**: tempo, compás, volumen, acento en el primer tiempo, presets de carácter.
- **Afinador**: escuchar el micrófono y mostrar la nota más cercana y la desviación en cents.
- **Círculo de quintas**: modo interactivo para fijar tonalidad y elegir acordes diatónicos sobre un círculo de tónicas, disponible en las implementaciones actuales de escritorio, web y móvil.

La app existe en tres formas: **escritorio** (Python/PySide6), **web** (frontend estático + API en Cloudflare Worker) y **móvil/tablet** (Flutter). Las tres implementaciones deben mantener contratos y resultados musicales equivalentes. Actualmente Python, JavaScript y Dart reimplementan parte de la lógica; la paridad se valida mediante tests y casos compartidos.

---

## 2. Stack y requisitos

- **Python 3.12 o 3.13** para la app de escritorio; **3.14** suele fallar al instalar dependencias nativas. En **Windows**, `python-rtmidi` (MIDI) solo tiene rueda PyPI hasta **3.12**; con 3.13 conviene **3.12** para un `requirements.txt` completo.
- **PySide6/Qt** para la UI de escritorio. `midichords/qt/` ofrece adaptadores con nombres similares a Tk para conservar parte de la implementación histórica.
- **Dependencias Python** (ejemplo): `mido`, `python-rtmidi`, `numpy`, `sounddevice` (ver `requirements.txt`).
- **Web**: frontend HTML/JS/CSS estático; backend API en **Cloudflare Worker** (JavaScript). Desarrollo local con **wrangler** (`wrangler dev`).
- **Móvil**: **Flutter** (iOS/Android); puede consumir la API web o reimplementar lógica.
- **Idioma por defecto**: español (`es`); soporte opcional para inglés (`en`) y otros en textos de UI y nombres de notas.

---

## 3. Estructura del repositorio (monorepo)

```text
.
├── apps/
│   ├── desktop/           # App escritorio
│   │   └── main.py        # Entrada: from midichords.main_app import main; main()
│   ├── web/               # Frontend + Worker
│   │   ├── index.html
│   │   ├── static/        # JS, CSS, assets estáticos
│   │   └── worker/       # Cloudflare Worker (API)
│   │       └── _worker.js
│   └── mobile_flutter/    # Proyecto Flutter
├── midichords/            # Paquete Python compartido (sin UI web/Flutter)
│   ├── core/              # Teoría, audio, config, i18n
│   ├── mixins/            # Lógica por modo (detección, generación, MIDI, etc.)
│   ├── qt/                # Adaptadores de API Tk sobre PySide6
│   ├── ui/                # Widgets y componentes visuales Qt
│   └── main_app.py        # Ventana Qt principal
├── assets/                # Imágenes, samples de audio (piano, guitarra)
├── tests/                 # Tests unitarios Python
├── scripts/               # Build, firma, notarización
├── packaging/             # Flatpak, Microsoft Store, etc.
├── launch.py              # Entrada unificada: desktop | web | mobile
├── app.py                 # Alias a desktop (opcional)
├── requirements.txt
├── AGENTS.md              # Guía para agentes (navegación del código)
└── PROJECT_SPEC.md        # Este documento
```

- **Raíz del proyecto** = directorio que contiene `midichords/`, `apps/`, `launch.py`. El paquete `midichords` se importa con la raíz en `PYTHONPATH` o con el cwd en la raíz.
- **launch.py**: script que recibe subcomando (`desktop`, `web`, `mobile`), parsea argumentos (por ejemplo `--host`, `--port` para web, `-d <device>` para Flutter) y llama a la función correspondiente (`run_desktop()`, `run_web()`, `run_mobile()`). Para web usa `wrangler dev` con el Worker y los assets en `apps/web`.

---

## 4. Paquete `midichords`

### 4.1 `midichords/core/`

- **music_theory.py**
  - Tipos: `ChordPattern(suffix, intervals)`, `ScalePattern(name, intervals)` (dataclasses inmutables).
  - Constantes: `CHORD_PATTERNS` (lista de ChordPattern con intervalos en semitonos desde la fundamental, p. ej. mayor `(0,4,7)`, menor `(0,3,7)`, `7` `(0,4,7,10)`, etc.), `SCALE_PATTERNS`, `WHITE_PCS`, `PC_TO_DIATONIC_LETTER`, `COMMON_CHORD_SUFFIX_ORDER`.
  - Funciones puras (sin UI): `analyze_chord_notes(notes: set[int]) -> (root_pc, pattern, bass_pc)`, `format_intervals(notes) -> str`, `note_name(language, midi_note, with_octave) -> str`, `chord_patterns_for_ui()`.
  - Depende solo de `i18n` (NOTE_NAMES).

- **music_service.py**
  - API de alto nivel de la implementación Python: `generate_chord(root_pc, suffix, inversion, language, prefer_flat) -> dict` (incluye `notes_midi`, nombres, intervalos), `detect_chord(notes=None) -> str`, `generate_scale(tonic_pc, pattern_name, language, prefer_flat) -> dict`, `list_chord_patterns()`, `list_scale_patterns(language)`. El Worker reproduce el mismo contrato en JavaScript; no importa Python en tiempo de ejecución.
  - Inversiones: la fundamental del acorde generado debe corresponder al bajo según el índice de inversión.
  - Usa `music_theory` e `i18n`; sin dependencias de UI ni audio.

- **i18n.py**
  - Diccionarios: `NOTE_NAMES` por idioma (lista de 12 nombres por clase de pitch, ej. `es`: Do, Do#, Re, …; `en`: C, C#, D, …), `UI_TEXTS` (claves como `app_title`, `panel_chord`, `mode_detection`, etc.), `SCALE_NAME_TEXTS` y otros que necesite la UI.
  - Idioma por defecto: `es`.

- **audio_engine.py**
  - Reproducción de audio: `PianoAudioEngine` con `note_on(note, velocity)` y `note_off(note)`; soporte para samples (piano, guitarra), clic de metrónomo, etc. Rutas de samples/config relativas a `PROJECT_ROOT`.

- **app_constants.py** / **app_config.py**
  - `PROJECT_ROOT`: raíz de recursos (en desarrollo = raíz del repo; en Flatpak puede ser `/app/share/midichords`). `CONFIG_PATH`, `DEFAULT_CONFIG`, listas de candidatos para imágenes (logo, clefs, piano, guitarra, metrónomo, etc.).

- **guitar_chord_cache.py**
  - Caché de variaciones de acordes de guitarra (posiciones); se puede cargar desde JSON en assets.

- **image_utils.py**
  - Utilidades para imágenes Tk (PhotoImage): redimensionar, padding, recoloring para modo oscuro.

### 4.2 `midichords/mixins/`

La app de escritorio es una clase Qt compuesta mediante varios mixins. Cada mixin aporta un bloque de funcionalidad (modo o subsistema):

- **UiMixin**: Construcción de ventana, paneles, pestañas, variables compatibles (`QtStringVar`, etc.) y selectores de modo.
- **RenderMixin**: Dibujo del teclado, guitarra y pentagrama mediante canvases adaptados sobre Qt; regiones interactivas.
- **InputDetectionMixin**: Conjunto de notas activas (ratón + MIDI), detección armónica del acorde (spelling), actualización de etiquetas “Notas”, “Notas sobrantes”, “Intervalos”, nombre del acorde. Usa `music_theory.analyze_chord_notes` y lógica de notas sobrantes.
- **GenerationMixin**: Generación de acordes (patrón, inversión), vista del acorde generado, reproducción.
- **ScalesMixin**: Escalas (patrón, tónica), vista y reproducción (opcional con metrónomo).
- **MetronomeMixin**: Metrónomo (BPM, compás, volumen, acento, presets).
- **TunerMixin**: Afinador (entrada de micrófono, detección de frecuencia, nota más cercana y cents).
- **MidiIOMixin**: Entrada/salida MIDI (listar dispositivos, abrir/cerrar, procesar mensajes note on/off, sustain).
- **OverlaysMixin**: Diálogos/overlays (selector de modo con tarjetas, etc.).

La clase principal combina los mixins de modos y subsistemas con `QtSchedulerMixin` y `QMainWindow`. Consultar `midichords/main_app.py` para el orden vigente, porque forma parte del contrato entre mixins.

### 4.3 `midichords/main_app.py`

- Una clase (`MidiChordAnalyzerApp`) que hereda de los mixins, `QtSchedulerMixin` y `QMainWindow`; en `__init__` inicializa estado (notas activas, MIDI, imágenes, config), construye la UI y enlaza eventos.
- Función `main()`: crea `QApplication`, construye la instancia y ejecuta el event loop de Qt.
- La app de escritorio se lanza desde `apps/desktop/main.py` importando y llamando a `main()` de `midichords.main_app`.

### 4.4 `midichords/ui/`

`widgets_qt.py` contiene los controles personalizados activos y
`desktop_ui_builders.py` las fronteras de construcción cubiertas por el smoke
contract de escritorio. La compatibilidad con la antigua API Tk vive en
`midichords/qt/`, sobre PySide6.

---

## 5. Aplicaciones

### 5.1 Escritorio

- **Entrada**: `python launch.py desktop` o `python app.py` (o `apps/desktop/main.py` con cwd/raíz). `launch.py` importa y ejecuta la función que arranca la app Qt.
- **Comportamiento**: ventana Qt principal con selector de modo (Detección, Intervalos, Generación, Círculo de quintas, Escalas, Metrónomo y Afinación cuando está habilitada); soporte de piano, guitarra, pentagrama, MIDI, audio y configuración persistente.

### 5.2 Web

- **Frontend**: HTML + JS + CSS en `apps/web/` (`index.html`, `static/app.js`, `static/style.css`, `templates/` si aplica). SPA con modos de pantalla: detección, generación de acordes, **círculo de quintas**, escalas, metrónomo, afinador. Carga inicial de datos desde la API (patrones de acordes y escalas, idioma).
- **Modo círculo de quintas**: interacción en canvas 2D (tónicas en quintas); clic para elegir tonalidad (anillo exterior = mayor, interior = menor relativa natural); **Mayús+clic** para un acorde diatónico de esa tonalidad; reproducción y pentagrama/guitarra reutilizan la misma generación que el modo generación vía `POST /api/generate/chord`. Implementación y convenciones de UI en `apps/web/static/app.js`; descripción orientativa en **`apps/web/README.md`** (*Frontend (modos SPA)*).
- **API (Cloudflare Worker)**: mismo contrato que la lógica de `music_service` + detección. Endpoints mínimos:
  - `GET /api/health` → `{ "status": "ok" }`
  - `GET /api/meta?language=es` → `{ "chord_patterns": [...], "scale_patterns": [...] }`
  - `POST /api/detect` → body `{ "notes": number[], "language", "accidental" }` → nombre del acorde y datos relacionados
  - `POST /api/generate/chord` → body `{ "root_pc", "suffix", "inversion", "language", "accidental" }` → acorde generado (notas, nombres, intervalos)
  - `POST /api/generate/scale` → body `{ "tonic_pc", "pattern_name", "language", "accidental" }` → escala generada
  - `POST /api/generate/guitar-variations` → variaciones de guitarra (puede devolver lista vacía si no hay implementación)
  - `POST /api/feedback` → reenvío de feedback por email (opcional, depende de env)
- El Worker puede reimplementar la lógica en JavaScript o invocar un backend; el frontend debe poder usar estos endpoints para replicar las pantallas de detección, generación y escalas.

### 5.3 Móvil (Flutter)

- Proyecto en `apps/mobile_flutter/`. Puede llamar a la API web o reimplementar detección/generación. Mismos modos conceptuales: detección, generación, escalas, metrónomo, afinador.
- Lanzamiento: `python launch.py mobile` (o `mobile -d <device_id>`); internamente ejecuta `flutter run` en el directorio del proyecto Flutter.

---

## 6. Assets y configuración

- **assets/**: imágenes (logo, iconos, clefs, teclado, guitarra, metrónomo) y muestras de audio (piano, guitarra). Formatos según necesidad (PNG, WAV, etc.).
- La configuración de la app de escritorio se persiste en un archivo (ruta definida en `app_constants`); opciones: idioma, dispositivo MIDI, salida de audio, preferencias de visualización (ej. etiquetas en teclas), opciones de metrónomo en escalas.

---

## 7. Tests

- **tests/**: tests unitarios Python (unittest o pytest). Descubrimiento desde la raíz: `python -m unittest discover -s tests` o `python -m pytest tests/`.
- Al menos un test que verifique que las inversiones generadas por `generate_chord` tienen el bajo correcto para cada patrón e inversión (raíz del acorde = nota más grave según el índice de inversión).
- Los tests importan `midichords.*`; el cwd o `PYTHONPATH` debe ser la raíz del repo.

---

## 8. Convenciones para regeneración

- **Nombres de notas**: consistentes con `i18n.NOTE_NAMES`; en español Do, Re, Mi, Fa, Sol, La, Si (con sostenidos/bemoles según preferencia).
- **Detección**: la “fuente de verdad” del nombre del acorde a partir de un conjunto de notas es la misma que usa `music_service.detect_chord` / `InputDetectionMixin` (p. ej. `analyze_chord_notes` + spelling armónico). Las “notas sobrantes” son las que no pertenecen al acorde detectado.
- **Generación de acordes**: intervalos en semitonos desde la fundamental; inversiones reordenando las notas de modo que la nota en la posición de inversión sea el bajo.
- **Escritorio**: PySide6/Qt es la UI de referencia. No confundir los adaptadores `tk_compat`, `ttk_compat` y `tkfont_compat` con una aplicación Tkinter independiente.
- **Web**: CORS habilitado para `/api/*` (OPTIONS + GET/POST); respuestas JSON; parámetros de idioma y accidental coherentes con el resto del producto.

---

## 9. Términos clave

- **root_pc** / **tonic_pc**: clase de pitch 0–11 (C=0, C#=1, …, B=11).
- **suffix**: variante del acorde (ej. `""`, `"m"`, `"7"`, `"maj7"`) según `ChordPattern.suffix`.
- **inversion**: índice de inversión (0 = fundamental en el bajo).
- **Notas sobrantes**: notas que no pertenecen al acorde detectado (según el mejor ajuste armónico).
- **PROJECT_ROOT**: raíz de recursos (assets, samples, config); en Flatpak puede ser `/app/share/midichords`.

---

## 10. Documentación relacionada

- **AGENTS.md**: guía para agentes IA que trabajan *dentro* del código existente (estructura, dónde está cada cosa, cómo ejecutar).
- **README.md**: resumen para humanos, instalación, ejecución unificada, despliegue web, firma/notarización macOS, etc.
- **apps/web/README.md**: despliegue a Cloudflare Pages y comprobaciones post-deploy.
- **Descargas**: ver la sección “Descargas” en `README.md` (por ejemplo, iOS en App Store).

---

*Este documento permite, en teoría, regenerar el proyecto MIDIChords: producto, stack, layout del monorepo, contrato del paquete `midichords`, APIs web, modos de la app y convenciones. Para detalles de implementación actual, usar el código y AGENTS.md.*
