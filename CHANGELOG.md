# Changelog

Historial de versiones publicadas de MIDIChords.

## Unreleased

### Añadido

- **Flatpak / Flathub**: `com.freemidichords.MIDIChords.flathub.yml` usa el tag **`v1.0.1`**; `metainfo.xml` declara release **1.0.1** (2026-03-21). Guía `FLATHUB.md` alineada a ese tag de ejemplo.

- **Repo**: `.gitignore` ignora `.venv-build-dmg/` (venv local opcional para scripts de build DMG).
- macOS App Store: plantilla **`scripts/mas-env.example`**, script **`scripts/build_mas_store.sh`** (carga `signing/local/mas.env` y llama a `build_mas_pkg.sh` con red/archivos y opcionalmente **`--skip-tk-check`** para builds Qt sin Tcl/Tk 8.6), y flag **`--skip-tk-check`** en **`scripts/build_mas_pkg.sh`**.
- `.gitignore`: ignora capturas de depuración UI en `assets/` (patrones tipo `generation_full_*.png`, `overlay_mode_*.png`, `*_smoke.png`, …) y carpeta `assets/ui-debug-captures/` con `README.md` para uso local.
- Escritorio: modo trazas **`/verbose`**, **`--verbose`** o **`-v`** en `launch.py desktop` (y equivalente **`MIDICHORDS_VERBOSE=1`**); salida en **stderr** centrada en **audio** y **MIDI**. La configuración **Desktop: MIDIChords** en `.vscode/launch.json` arranca con `/verbose`.

### Documentado

- macOS App Store: `signing/README.md` y `README.md` — flujo **`mas.env`** + **`./scripts/build_mas_store.sh`**; ejemplo manual de `build_mas_pkg.sh` con **`--skip-tk-check`**.
- Escritorio (macOS): script **`scripts/build_mac_test_dmg.sh`** — genera **`MIDIChords-macos-test.dmg`** y `.app` para probar en un Mac sin certificado Developer ID; documentado en `README.md`.
- Repo: reglas de agente Cursor — **`release-changelog-agent.mdc`** (analizar diff, **CHANGELOG** Unreleased por app, `commit`/`push`; invocable con `@release-changelog-agent`) y **`github-update-triggers.mdc`** (`alwaysApply`, reacciona a «actualiza cambios», «commit y push», etc.); script manual `scripts/document_release_changes.py`; ver `AGENTS.md`.
- Móvil (Flutter): inventario operativo de dispositivos de prueba, ids confirmados de iPhone/iPad y tablet Android, y guía para arrancar simuladores/emuladores iOS y Android desde `apps/mobile_flutter/README.md`.
- Móvil (Flutter): nuevo script `scripts/select_mobile_emulator.py` para listar simuladores/emuladores disponibles en macOS y arrancar el elegido desde terminal.
- Móvil (Flutter): el selector de emuladores muestra por defecto solo los simuladores iOS documentados; `--all-ios` enseña el resto, y los AVD Android rotos ahora fallan con un mensaje claro antes de intentar arrancar.
- Móvil (Flutter): el selector interactivo añade la opción `m` para expandir la lista iOS sin reinvocar el comando.
- Móvil (Flutter): el selector añade la opción `d` y el modo `--devices` para listar dispositivos físicos móviles y lanzar la app directamente con `launch.py mobile -d <id>`.
- macOS App Store: guía MAS actualizada con los nombres reales de certificados usados en este proyecto, nota sobre `--skip-store-validation` en entornos no interactivos, necesidad de subir con `build-number` nuevo tras un rechazo, y advertencia sobre bundles previos creados por `root`.
- macOS App Store: la subida recomendada se documenta ahora con la app **Transporter** en modo manual (arrastrar `.pkg` y pulsar **Deliver**); `xcrun iTMSTransporter` queda como alternativa secundaria de diagnóstico.

### Corregido

- **CI / Flatpak**: workflow **Validate Flatpak** — `flatpak remote-add` usa **`--user`** y URL `dl.flathub.org` (en GitHub Actions el remoto de sistema fallaba con *ConfigureRemote not allowed*); `appstreamcli validate` con **`--no-net`** para evitar falsos positivos de URL desde los runners; `.desktop` con **`Categories=AudioVideo;Audio;Music;`** (requisito de `desktop-file-validate`); disparador **`push` de etiquetas `v*`** además de `main` y PRs (alineado con **Build Installers**).
- **Flatpak / Flathub**: guía `FLATHUB.md` y comentarios del manifiesto — en el PR de nueva app los archivos van en la **raíz** de la rama (requisito Flathub para `detect-appid`); presentación Flathub [#8160](https://github.com/flathub/flathub/pull/8160) (PR [#8089](https://github.com/flathub/flathub/pull/8089) anterior cerrado por revisores). Manifiesto: sin `finish-args` de filesystem innecesarios (linter Flathub); fuente git con **`commit`** además del tag (documentado en `FLATHUB.md`). `python-deps.json`: **setuptools-scm** desde wheel PyPI (evita fallo del sdist con setuptools del SDK); **metainfo** con `<screenshots>` (URL en GitHub) para el linter de repo Flathub. **`appstream-compose: true`** para generar el catálogo AppStream y evitar `appstream-missing-appinfo-file` en el build de Flathub; CI instala **`appstream-compose`**. Iconos en **48/128/256/512** px bajo `hicolor` para que `appstreamcli compose` no falle con `icon-not-found`.
- macOS App Store: `build_mas_store.sh` **omite por defecto** `installer -store` (`MAS_SKIP_STORE_VALIDATION` por defecto `1`); aviso en `build_mas_pkg.sh` si se ejecuta y se queda colgado.
- macOS App Store: `scripts/build_mas_pkg.sh` usa **`$PYTHON_BIN -m PyInstaller`** en lugar del comando `pyinstaller` en PATH; mensaje claro si falta el módulo.
- macOS App Store / **Escritorio (Qt)**: arranque del `.app` PyInstaller — se fija **`QT_PLUGIN_PATH`** antes de importar PySide6 (`apps/desktop/darwin_frozen_bootstrap.py`) y **`PROJECT_ROOT`** usa **`sys._MEIPASS`** en binario `frozen` para localizar `assets/`; evita el cierre inmediato en Dock sin crash log que suele dar Qt sin plugins en bundle firmado/sandbox.
- Móvil (Flutter): **Generación** (piano) — digitación de acordes alineada al escritorio: tríada mano derecha **1-3-5** y mano izquierda **5-3-1** (notas ordenadas de grave a agudo); antes se asignaban dedos por índice (1-2-3 / 5-4-3).
- macOS App Store: `scripts/build_mas_pkg.sh` limpia atributos `com.apple.quarantine` también en `assets/` y en los recursos empaquetados del `.app` antes de firmar, evitando rechazos de App Store Connect como `code 91109`.
- macOS release env: `scripts/validate_macos_release_env.sh` detecta de forma más robusta las identidades válidas del llavero.
- Escritorio (Qt): **Ajustes** — al refrescar la lista de dispositivos al abrir el combo de **entrada MIDI** o **salida de audio**, el otro combo parecía perder la selección: tras `clear()`/`addItems()` el `QComboBox` no se re-sincronizaba con el `StringVar` (solo existía enlace combo→var). `ttk.Combobox.configure(values=…)` vuelve a aplicar `setCurrentText` desde la variable si el valor sigue en la lista; el refresco de Ajustes usa la config como respaldo si la var va vacía.
- Escritorio (Qt): **Metrónomo** — fila **Temporizador** en dos líneas (checkbox + título / minutos y segundos) para que etiquetas y spinboxes no se pisen en paneles estrechos; figuras con **tresillo** dibujan el **"3"** en una franja superior y el rectángulo de color por debajo (sin invadir el borde del botón).
- Escritorio (Qt): **Metrónomo** — la fila del play y el botón de sonido MIDI dejaban de lado a lado y se solapaban; la fila usa `grid` con columna extensible (como los sliders de volumen/tempo) en lugar de `pack` en un `QHBoxLayout` poco fiable aquí.
- Escritorio: **Escalas** (piano) — al tocar con MIDI, la nota se marcaba en el teclado pero no en el pentagrama: `staff_pressed_scale_notes` solo se actualizaba con clic en teclado/pentagrama. Tras cada refresco de notas activas se sincroniza el pentagrama con MIDI/ratón/sostenido (sin interferir mientras se arrastra en el pentagrama).
- Escritorio: **Generación** — al mantener notas por MIDI (o varias a la vez), el resaltado en teclado/pentagrama dejaba de mostrarse o solo quedaba una nota: `_update_generation_preview()` trataba cualquier `generated_playing_notes` como “reproducir acorde” y llamaba a `_stop_generated_playback()` al refrescar la vista previa (p. ej. al actualizar combos en Qt). Solo se interrumpe ahora el play mantenido con botón o barra espaciadora; añadidas salidas tempranas si raíz/variante/inversión no cambian.
- Escritorio (Qt): **Ajustes** — el combo de entrada MIDI podía quedar vacío aunque el teclado sonara: el refresco en segundo plano usaba un probe MIDI por subprocess donde `sys.gettrace()` no refleja el depurador, fallaba y vaciaba la lista; el listado de puertos pasa a hacerse siempre con `mido.get_input_names()` en proceso. El `Combobox` Qt ahora ejecuta `postcommand` al desplegar (como Tk), para refrescar al abrir la lista.
- Escritorio (Qt): **Escalas** — el slider de BPM entre **−** y **+** no se veía: con `sticky="ew"` el grid Qt usaba una alineación que dejaba el canvas al ancho mínimo (1 px). Sticky `ew` / `ns` (relleno) ahora usa alineación 0 para estirar a la celda (afecta a otros sliders con el mismo patrón).
- Escritorio (Qt): sliders del **metrónomo** (tempo, volumen, compás) y similares — `QtCanvas` ya no usa `setFixedSize` con `width`+`height` (solo tamaño mínimo), de modo que la franja entre **−** y **+** puede ocupar todo el ancho del panel.
- Escritorio: en **Generación**, al mantener pulsada una tecla MIDI el resaltado del teclado ya no desaparece a los ~520 ms; solo se quita al **soltar** la nota (`note_off`). Los clics en teclado/pentagrama siguen usando el timeout corto.
- Escritorio: en **Generación** con MIDI, al pulsar varias notas del acorde se resaltan y suenan **todas** a la vez (cada una hasta su `note_off`); el ratón sigue sustituyendo la vista previa y envía `note_off` en piano a las notas que dejan de mostrarse.
- Escritorio (migración Qt): aviso `QObject::startTimer: Timers can only be used with threads started with QThread` — `after()` y el refresco de dispositivos en **Configuración** ya no crean `QTimer` desde hilos `threading` (se reenvía al hilo GUI con `run_on_main_thread`).
- Escritorio (migración Qt): el shim `place()` ahora respeta `x` / `y` / `width` / `height` como Tk, de modo que los paneles izquierdo y derecho sobre el canvas superior vuelven a posicionarse y mostrarse (antes solo se usaba `relx`/`relwidth`).
- Escritorio (migración Qt): `pack_forget` quita el widget del `QLayout` del padre (no solo `hide()`); pestañas de modo no empaquetadas se ocultan al inicio para que no tapen el panel derecho; `RoundedPanel` expone `sizeHint`/`minimumSizeHint` para que el panel inferior (piano) reciba altura en el `QVBoxLayout`.
- Escritorio (migración Qt): `QtCanvas.itemconfigure` aplica `width`/`height` a ventanas de `create_window` (panel de resultados de detección); `Label` aplica `fg`/`font` y tamaño mínimo (icono ⚙); se ocultan al inicio los canvas de afinador/guitarra que no están en `pack` para no tapar el teclado.
- Escritorio (migración Qt): `QtCanvas.create_arc` y constantes `tk.PIESLICE`/`ARC`/`CHORD` para dibujar el teclado (`redraw_keyboard`).
- Escritorio (migración Qt): clics en canvas alineados con Tk (`<ButtonPress-1>` / `<ButtonRelease-1>`) y `mouseReleaseEvent` vuelve a notificar para teclado/pentagrama/guitarra.
- Escritorio (migración Qt): play de detección sin `command` al soltar (evita segundo `_start_detection_hold` con `PlayTransportButton`).
- Escritorio (migración Qt): `tk.Label` enlaza `textvariable` (`StringVar`) con el `QLabel` para notas/intervalos/acorde en detección (y similares).
- Escritorio (migración Qt): botones #/♭ de la barra superior centrados y altura 40 px alineada al selector de modo; `Widget` respeta `<ButtonPress-1>` si está enlazado antes que `<Button-1>`.
- Escritorio (migración Qt): botones personalizados (`RoundedChoiceButton`, `GrayRoundedButton`, `GreenRoundedButton`) usan `ui_font_family` y tamaños alineados al resto de la UI; #/♭ en barra superior a **12 pt bold** como `widgets.py` (Tk); `GreenRoundedButton` dibuja **♭** compuesto como en Tk.
- Escritorio (migración Qt): `pack(padx=…/pady=…)` usa huecos por widget (`addSpacing` / `insertSpacing`) en lugar de `setSpacing` global, y los widgets Qt (`widgets_qt`) respetan `padx`; corrige separación #/♭ y el margen antes de ⚙.
- Escritorio (migración Qt): panel derecho — `tk.Label` aplica `configure(wraplength=…)` (antes ignorado), alinea `anchor`/`justify`, y el tamaño mínimo con texto multilínea usa `TextWordWrap` (evita métricas de una sola línea enormes). Textos de resultados en **Generación** y **Escalas** unificados a **13 pt** como **Detección**. `ttk` usa `qt_pack_attach` para `pack`; `Combobox`, `Spinbox` y `Checkbutton` respetan `font=(familia, tamaño…)`.
- Escritorio (migración Qt): fila **Detección** (play / Limpiar / Reproducir entrada MIDI) — `pack(fill=X)` en la fila, botón MIDI con `expand_h` + `pack(fill=X, expand=True)` para repartir el ancho; `pack(anchor=…)` en vertical respeta alineación (`AlignLeft`, etc.). Misma idea en la fila play + MIDI del **metrónomo** (`sticky=ew`).
- Escritorio (migración Qt): panel derecho más legible — títulos **20 pt**, ayuda **15 pt**, resultado acorde **38 pt**, notas/intervalos **15 pt** (mono); menos `pady` entre bloques, `RoundedPanel` derecho con padding vertical **8**; generación/escalas alineados al mismo criterio.
- Escritorio (migración Qt): icono **⚙** — el `QLabel` interno ya no intercepta el ratón (`WA_TransparentForMouseEvents`); `bind_all('<ButtonPress-1>')` se despacha vía `QApplication.installEventFilter`; `_is_widget_inside` sube por `parentWidget` y `Widget.master` para cerrar overlays al pulsar fuera.
- Escritorio (migración Qt): selector de modo — `tk.Frame` aplica `bg` y borde `highlightthickness`/`highlightbackground` con `WA_StyledBackground` + `stylesheet`; `tk.Label` reenvía esas opciones al `Widget` para que el panel modal y las tarjetas tengan fondo visible (no solo iconos/texto).
- Escritorio (migración Qt): `ttk.Frame(..., padding=…)` — el shim ya no pasa `padding` a `QWidget`; se traduce a `setContentsMargins` del `pack`/`grid` interno (p. ej. diálogo de ajustes).
- Escritorio (migración Qt): selector de modo en canvas — `QtCanvas.coords()` actualiza posición de ítems `text`/`line`/`rect`/`oval`/`image` (antes solo ventanas; la flecha quedaba en x=0 y no se veía). Dibujo de texto con anclaje tipo Tk (`w`/`e`/…) vía `drawText(QRectF, flags)` + centrado vertical; fuente Tk con tamaño negativo → `setPixelSize`. Flecha **▼** y texto del modo a **15 pt bold**.
- Escritorio (migración Qt): **Configuración (⚙)** — el `eventFilter` de la app despacha `bind_all('<ButtonPress-1>')` por cada ancestro del widget pulsado; tras abrir el overlay, el siguiente receptor era el `Frame` padre del icono y `_on_global_click_press` cerraba el diálogo al instante. Se ignora el cierre automático durante ~0,28 s tras abrir (`_settings_overlay_opened_ts`), como el selector de modo.
- Escritorio (migración Qt): selector de modo (rejilla) — `rowconfigure` solo en filas con tarjetas (4 modos ya no dejan una fila vacía estirada abajo); icono y texto con `anchor="center"` y `pack(anchor="center")` para igualar el centrado de Tk y no pegar el glifo a la izquierda.

## [1.0.0] - 2026-03-14

Primera versión 1.x publicada del proyecto.

> Nota (trazabilidad iOS): esta etiqueta `v1.0.0` apunta al commit con el que se subió a App Store Connect la build de iOS **1.0.0 (2)**.

Disponible en:

- App Store en iOS
- Mac App Store en escritorio macOS
- Google Play en Android

### Añadido

- Aplicación Flutter para tablet con detección, generación de acordes, escalas y metrónomo.
- Modo ayuda contextual en móvil con zonas interactivas por pantalla y por control.
- Flujo documentado de despliegue web en Cloudflare Pages.

### Mejorado

- Resaltado del pentagrama en generación de acordes para respetar mejor la mano activa.
- Comportamiento del metrónomo y del audio nativo iOS en iPhone/iPad.
- Ayudas contextuales y distribución visual en iPad.

### Corregido

- Envío del formulario de comentarios en producción web.
- Verificación del despliegue de producción web para detectar estados rotos donde faltaba `/api/meta`.
- Varios problemas de enlace y configuración del proyecto iOS Flutter.

## [1.0.1] - 2026-02-20

Cambios respecto a `v1.0.0` (iOS **1.0.0 (2)**).

### iOS (Flutter)

- Audio del piano menos “cortado” al soltar la tecla (release más natural).
- Reducción de saturación/clipping percibido en iOS (atenuación de ganancia, especialmente en piano).
- Build de iOS: **1.0.1 (3)** / **1.0.1 (4)**.

### Android (Flutter)

- Corregido el panel izquierdo del metrónomo en Android 14 (ej. UMIDIGI G9C).

### Web (Cloudflare Pages)

- Nuevo panel **Descargas** (PC/Mac y móvil) con ventana/modal y enlaces actualizados.
- Enlaces de descarga directos para artefactos en GitHub (`/releases/latest/download/...`).
- Endurecimiento del despliegue para evitar caché de CSS/JS:
  - `Cache-Control: no-store` para HTML y `/static/*`.
  - Cache-busting en `index.html` con `?v=${GITHUB_SHA}` en `style.css` y `app.js`.
- Ajuste de responsive: mantener **3 columnas** del panel inferior hasta 700px.

### CI / Releases (desktop)

- Firma y notarización de macOS en CI (opcional vía `SIGN_MACOS=true`) con import de certificado, keychain y `notarytool`.
- Fixes de creación de DMG en macOS CI (`hdiutil` “Resource busy” y nombre temporal `.tmp.dmg`).
- Deploy de Cloudflare producción solo con **tags `v*`** (no en cada push a `main`).
- Publicación de instaladores en GitHub Releases y sincronización al repo público `FreeMIDIChords_Releases`.
- Notificación por correo al mantener cuando falla un workflow (Resend).

### Repo / mantenimiento

- Eliminado el submódulo roto `flathub-submission` y añadido a `.gitignore` como carpeta local.

## [Unreleased] - Cambios desde [1.0.1]

_(Próximos cambios.)_

### Corregido

- Escritorio (migración Qt): variaciones de guitarra cacheadas ahora se filtran/reordenan para que acordes como **SolM** no dibujen una cejilla con notas por delante (mezcla incoherente con cuerdas abiertas).
- Escritorio (migración Qt): en **Escalas**, el panel derecho de “Notas/Intervalos” ahora muestra correctamente el subpanel (el shim ajusta también la altura del `create_window` interno del `scale_result_canvas`).
- Escritorio (migración Qt): en **Generación** (modo guitarra) el panel inferior ya no recorta el `guitar_canvas`; `_fit_instrument_panel_height()` ajusta correctamente la altura en Qt (usa `self.height()` y fija el alto del panel).

[1.0.0]: https://github.com/aortegaCampanillas/MIDIChords/releases/tag/v1.0.0
[1.0.1]: https://github.com/aortegaCampanillas/MIDIChords/releases/tag/v1.0.1
