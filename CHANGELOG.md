# Changelog

Historial de versiones publicadas de MIDIChords.

## Unreleased

### Añadido

- Escritorio: modo trazas **`/verbose`**, **`--verbose`** o **`-v`** en `launch.py desktop` (y equivalente **`MIDICHORDS_VERBOSE=1`**); salida en **stderr** centrada en **audio** y **MIDI**. La configuración **Desktop: MIDIChords** en `.vscode/launch.json` arranca con `/verbose`.

### Documentado

- Móvil (Flutter): inventario operativo de dispositivos de prueba, ids confirmados de iPhone/iPad y tablet Android, y guía para arrancar simuladores/emuladores iOS y Android desde `apps/mobile_flutter/README.md`.
- Móvil (Flutter): nuevo script `scripts/select_mobile_emulator.py` para listar simuladores/emuladores disponibles en macOS y arrancar el elegido desde terminal.
- Móvil (Flutter): el selector de emuladores muestra por defecto solo los simuladores iOS documentados; `--all-ios` enseña el resto, y los AVD Android rotos ahora fallan con un mensaje claro antes de intentar arrancar.
- Móvil (Flutter): el selector interactivo añade la opción `m` para expandir la lista iOS sin reinvocar el comando.
- Móvil (Flutter): el selector añade la opción `d` y el modo `--devices` para listar dispositivos físicos móviles y lanzar la app directamente con `launch.py mobile -d <id>`.

### Corregido

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
