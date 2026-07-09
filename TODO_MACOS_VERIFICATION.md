# TODO macOS verification — Qt shim wraplength fix (panel Detección)

Contexto: bug encontrado y corregido en **Windows** (escritorio, backend Qt/PySide6 vía
`midichords/qt/tk_compat.py` y `midichords/mixins/ui_mixin.py`). Pendiente de repetir la
verificación visual en **macOS** antes de dar el cambio por cerrado.

## Síntoma original

Modo **Detección de acordes** → panel derecho: el texto de ayuda
("Pulsa notas en piano/guitarra para detectar acordes o usa un dispositivo MIDI.")
se recortaba/desbordaba en vez de ajustarse a 2 líneas dentro del panel.

## Causa raíz

`midichords/mixins/ui_mixin.py` → `_refresh_right_panel_wraplengths`: el `wraplength`
de `detection_help_label` (que vive en el panel **derecho**, `chord_panel`) se calculaba
usando el ancho del **panel izquierdo** (`staff_canvas`) en vez del propio `chord_panel`.
Al ser `staff_canvas` mucho más ancho que el panel derecho real, el texto no se ajustaba
al espacio disponible.

- Fix: usar `panel_width` (`chord_panel.winfo_width()`), igual que el resto de labels
  del panel derecho (`result_wrap`, etc.).
- Para que `chord_panel.winfo_width()` funcione (antes lanzaba excepción, capturada
  silenciosamente, y devolvía siempre 0), se añadió `winfo_width()` / `winfo_height()`
  a la clase base `Widget` en `midichords/qt/tk_compat.py` (antes solo `QtCanvas` los
  tenía). Estos son **getters puros** (`max(1, int(self.width()))`), sin efectos
  secundarios — seguros de añadir.
- El refresco se sigue disparando desde `staff_canvas.bind("<Configure>", ...)` (ya
  existía y es seguro, `QtCanvas` despacha `<Configure>` de forma nativa). `chord_panel` y
  `staff_canvas` se redimensionan en el mismo layout pass, así que el ancho leído en el
  handler ya es válido.

## ⚠️ Intento fallido a evitar: no despachar `<Configure>` desde la clase base `Widget`

Un primer intento añadió también un `resizeEvent` a la clase base `Widget` (de la que
heredan `Frame`, `Label`, `Button`, `Radiobutton`, `Entry`) que llamaba a
`self._call_binding("<Configure>", event)` en cada resize, para que `chord_panel.bind("<Configure>", ...)`
funcionara igual que en un `Canvas`. **Esto provocó un crash nativo reproducible al
arrancar** (`Segmentation fault` / `Windows fatal exception: access violation`, confirmado
con `python -X faulthandler`), incluso con el handler vaciado a un `return` inmediato — es
decir, el crash no dependía de la lógica del handler, sino de invocar cualquier callback
Python en un `resizeEvent` genérico sobre `Frame`/`Label`/etc. La única `resizeEvent` segura
en este shim es la ya existente en la **ventana principal** (`ui_mixin.py`, método
`resizeEvent` de `MidiChordAnalyzerApp`, usado para el overlay de ayuda), porque
`MidiChordAnalyzerApp` hereda `QMainWindow` directamente, no `Widget`.

**No reintroducir** un `resizeEvent`/despacho de `<Configure>` genérico en la clase `Widget`
de `tk_compat.py` sin probar antes con `python -X faulthandler launch.py desktop` varias
veces seguidas (el crash fue 100% reproducible en 3-4 intentos, no intermitente).

## Segundo bug igual: Detección de Intervalos

Mismo síntoma, panel distinto: en **Detección de Intervalos** ("Pulsa dos notas
(ratón, teclado o MIDI) para detectar el intervalo.") el label se creaba **bajo
demanda** (`_setup_interval_ui`, solo la primera vez que se entra en el modo) con
`wraplength=800` fijo y sin ningún mecanismo que lo recalculara — a diferencia de
`detection_help_label`, que se crea eagerly durante el setup inicial y sí recibía
(aunque con el bug del ancho equivocado) un cálculo dinámico.

- Fix: el label ahora se guarda como `self.interval_help_label` y se registra en
  `_refresh_right_panel_wraplengths` (mismo `help_wrap` que `detection_help_label`,
  basado en `chord_panel.winfo_width()`). Además, `_setup_interval_ui` llama a
  `_refresh_right_panel_wraplengths()` justo al terminar de construir el panel, para
  que quede bien ajustado desde la primera vez que se entra en el modo (no depende
  de que el usuario redimensione la ventana después).
- **Ojo con otros paneles creados "bajo demanda"** (patrón `if hasattr(self,
  '_xxx_panel_created'): return` + flag al final): si alguno tiene un label de ayuda
  con `wraplength` fijo, sufre el mismo bug. Revisar `scales`, `metronome`, `tuner`
  si en algún momento se les añade un texto de ayuda similar.

## Tercer bug: Generación de Acordes — Notas/Intervalos recortados por abajo

Reportado directamente en **macOS**: en modo **Generación de Acordes**, las filas
**Notas** e **Intervalos** dentro del bloque de resultado se veían recortadas por
abajo, y en general los textos parecían más grandes que en Windows.

Causa: `generation_result_canvas` (el `Canvas` que dibuja el fondo redondeado del
bloque acorde/notas/intervalos) se crea con **alto fijo `height=160`**
(`ui_mixin.py`). El contenido real (`generation_result_inner`, con 3 filas de texto)
no está limitado a esa altura — si necesita más (p. ej. notas/intervalos con muchas
notas que hacen wrap a 2 líneas por el `wraplength=420`), simplemente se recorta
porque el `Canvas` no crece. En **macOS**, las fuentes del sistema elegidas por
`_pick_font_family` (`Avenir Next` / `SF Pro Text`) tienen métricas más altas que
`Segoe UI`/`Helvetica` en Windows, así que el mismo contenido necesita más alto con
más frecuencia — de ahí que el bug sea más visible allí, aunque en teoría también
puede reproducirse en Windows con un acorde con muchas notas (p. ej. acordes de
9/11/13 con varias inversiones).

- Fix: nuevo método `_refresh_generation_result_height()` (`ui_mixin.py`) que lee
  `self.generation_result_inner.winfo_reqheight()` (alto real que pide el contenido)
  y llama a `self.generation_result_canvas.setMinimumHeight(...)` si hace falta más
  que el mínimo de 160px. Enganchado vía `trace_add("write", ...)` a
  `generated_notes_var` y `generated_intervals_var`, así se recalcula cada vez que
  cambian las notas/intervalos mostrados (no solo al arrancar).
- Para que `winfo_reqheight()` funcione, se añadieron `winfo_reqwidth()` /
  `winfo_reqheight()` (getters puros basados en `sizeHint()`) a la clase base
  `Widget` del shim Qt (`tk_compat.py`) — mismo patrón seguro que `winfo_width()` /
  `winfo_height()`, sin tocar `resizeEvent` (ver el crash documentado arriba).
- **Importante**: `Canvas.configure(height=...)` en este shim es un no-op (solo
  llama a `self.update()`, `midichords/qt/tk_compat.py` línea ~1188) — para
  redimensionar un Canvas hay que usar el método nativo Qt `setMinimumHeight()`
  directamente, `.configure()` no sirve.
- Verificado con un script aislado (fuera de la app) que crea un `Frame`+`Label`
  igual que `generation_result_inner`, confirmando que `winfo_reqheight()` crece de
  61 a 84 cuando el texto pasa a necesitar 2 líneas.
- **Mismo patrón de riesgo en otros paneles**: `detection_result_canvas` (height=180)
  y `scale_result_canvas` (height=220) tienen el mismo alto fijo. No se ha reportado
  el bug ahí todavía, pero si en el futuro se reporta recorte en Detección de
  Acordes o Escalas, aplicar el mismo fix (leer `winfo_reqheight()` del `*_inner` y
  `setMinimumHeight()` en el canvas correspondiente).

## Cuarto bug: Círculo de quintas — no cabe en el panel, texto sobredimensionado

Reportado directamente en **macOS**, "sobre todo al elegir guitarra": el círculo de
quintas no cabía en el panel derecho, y el texto de los acordes del anillo interior
se salía de sus sectores.

Causa: `circle_canvas` (`ui_mixin.py`) se creaba con `width=480, height=480`, que en
el shim Qt (`Canvas.__init__` → `QtCanvas.__init__`) se traduce en
`setMinimumSize(480, 480)` — un **mínimo forzado**, no un tamaño inicial que pueda
encogerse. El `tab_circle_frame` vive en el panel derecho (`chord_panel`), cuyo
ancho puede ser bastante menor que 480px en ventanas compactas, y cuya altura
depende del espacio que quede libre arriba tras el panel de instrumento inferior
(piano/guitarra comparten esa fila; el fretboard de guitarra usa una altura fija de
196px frente a 156px del teclado — 40px menos disponibles para el círculo cuando se
selecciona guitarra, lo que **agrava** el problema aunque no es la causa raíz). Con
el canvas forzado a 480×480, `_circle_redraw_canvas` lee ese tamaño "inflado" vía
`winfo_width()/winfo_height()` y `draw_circle_of_fifths` calcula radios y tamaños de
fuente proporcionalmente a esos 480px (`fs_sig = 0.026 * w`, etc.), aunque el
espacio realmente visible sea menor — de ahí el desbordamiento y el texto
sobredimensionado.

- Fix: reducido a `width=260, height=260` en la creación de `circle_canvas`, el
  mismo valor que `_circle_redraw_canvas` ya usaba como suelo (`max(260, ...)`).
  Así el canvas puede encoger hasta ese mínimo razonable en vez de forzar 480, y el
  dibujo (que ya es proporcional al tamaño real) se ajusta correctamente al espacio
  disponible.
- Verificado con captura de pantalla en modo Círculo de quintas (vista piano): el
  círculo cabe completo dentro del panel derecho, sin desbordar, con texto legible
  y proporcionado.
- **No se pudo verificar visualmente con la vista de guitarra activa** en esta
  sesión (la automatización de clicks de UI resultó poco fiable, y forzar el modo
  vía `config.json` con `instrument_view`/`generation_instrument_view` en
  `"guitar"` se revertía solo a `"piano"` entre una edición y el siguiente
  arranque, por una razón no identificada — no parece un proceso duplicado, ver
  nota abajo). Pendiente confirmar en macOS que el caso "sobre todo con guitarra"
  también queda arreglado.

### Nota rara: `config.json` con `instrument_view: "guitar"` se revierte a `"piano"` solo

Al intentar forzar el arranque en vista de guitarra (editando `instrument_view` y
`generation_instrument_view` a `"guitar"` en `config.json`) para probar el bug de
guitarra en el círculo de quintas, el valor volvía a `"piano"` — confirmado incluso
con un `print()` de depuración justo tras `load_config_file()` en `main_app.py`, que
mostró `"piano"` aunque el archivo en disco decía `"guitar"` momentos antes. Una
prueba aislada con `load_config_file(CONFIG_PATH, DEFAULT_CONFIG)` fuera de la app
sí devolvió `"guitar"` correctamente, así que el propio cargador de config no tiene
la culpa. No se llegó a la causa (se abandonó la investigación por fricción de
permisos en la sesión) — **si esto se reproduce en macOS o vuelve a aparecer**,
revisar si algo restaura `instrument_view`/`generation_instrument_view` a `"piano"`
durante el arranque en modo `circle_fifths` específicamente (el código de
`_on_mode_combo_changed` en `ui_mixin.py` no parecía forzarlo tras revisión manual,
pero el comportamiento observado sugiere lo contrario).

## Archivos tocados (estado final)

- `midichords/qt/tk_compat.py`: clase `Widget` — `winfo_width()` / `winfo_height()` /
  `winfo_reqwidth()` / `winfo_reqheight()` (todos getters puros, sin `resizeEvent`
  nuevo).
- `midichords/mixins/ui_mixin.py`: `_refresh_right_panel_wraplengths` usa
  `panel_width` en vez de `left_w`; se quitó el bind muerto
  `chord_panel.bind("<Configure>", ...)` (redundante, `staff_canvas` ya dispara el
  refresco); ahora también actualiza `interval_help_label`. Nuevo
  `_refresh_generation_result_height()` enganchado a los `StringVar` de notas/
  intervalos de Generación. `circle_canvas` creado con `width=260, height=260` en
  vez de `480, 480`.
- `midichords/mixins/interval_mixin.py`: `interval_help_label` guardado como atributo
  de instancia; `_setup_interval_ui` refresca el wraplength al terminar de construir
  el panel.
- `midichords/mixins/render_mixin.py`: se oculta el hint de Shift en Detección de
  Intervalos (`interval_tab_active`).

## Verificado en Windows

- [x] `python -m pytest tests/` → 766 passed, 12 subtests passed.
- [x] `python launch.py desktop` arranca de forma estable (4/4 intentos sin crash tras
      el fix final; antes del fix final, crash reproducible 100% de las veces).
- [x] Captura de pantalla en modo Detección de Acordes: el texto de ayuda se ve
      completo en 2 líneas dentro del panel derecho (antes se cortaba/desbordaba).
- [x] Captura de pantalla en modo Detección de Intervalos: el texto de ayuda se ve
      completo en 2 líneas dentro del panel derecho (antes se cortaba/desbordaba), y
      ya no aparece el hint de Shift bajo el pentagrama.
- [x] Modo Generación de Acordes: caso simple (acorde de 3 notas) se ve bien; el
      mecanismo de crecimiento dinámico (`winfo_reqheight` + `setMinimumHeight`) se
      verificó de forma aislada (script fuera de la app), pero **no se ha podido
      verificar visualmente dentro de la app con un acorde que realmente fuerce el
      wrap a 2 líneas** (automatización de clicks de UI poco fiable en este entorno)
      — pendiente también en macOS.
- [x] Captura de pantalla en modo Círculo de quintas (vista piano): el círculo cabe
      completo en el panel derecho, sin desbordar, texto proporcionado. **No
      verificado con vista de guitarra** (ver nota sobre `config.json` arriba).

## Pendiente de verificar en macOS

- [ ] `python -m pytest tests/` sigue en verde (766 passed).
- [ ] `python launch.py desktop` arranca varias veces seguidas sin crash (no solo una vez).
- [ ] Modo **Detección de Acordes**: texto de ayuda del panel derecho en 2 líneas, sin
      cortarse ni desbordar, tanto al abrir la app como al redimensionar la ventana.
- [ ] Modo **Detección de Intervalos**: mismo texto de ayuda ("Pulsa dos notas...") en
      2 líneas, entrando por primera vez en el modo (no solo si arranca ya en ese modo);
      y confirmar que ya NO aparece el hint de Shift bajo el pentagrama en este modo.
- [ ] Modo **Generación de Acordes**: probar un acorde con muchas notas/inversión que
      fuerce Notas/Intervalos a 2 líneas (p. ej. un acorde de 9ª o 13ª con varias
      notas) y confirmar que el bloque crece sin recortar el texto por abajo — este es
      el caso que originalmente falló en macOS y que en Windows no se pudo reproducir
      con un click real de UI.
- [ ] Modo **Círculo de quintas**: el círculo cabe completo en el panel derecho, sin
      desbordar, con texto legible dentro de sus sectores — tanto con vista de
      **piano** como con vista de **guitarra** (el reporte original decía que era
      "sobre todo" con guitarra donde se notaba peor).
- [ ] Redimensionar la ventana en varios modos (generación, escalas, círculo de quintas,
      metrónomo, afinador, intervalos) y comprobar que no hay regresiones de layout —
      el cambio en `tk_compat.py` es mínimo (dos getters) pero toca una clase base muy
      compartida.

## Cómo reproducir la verificación visual (igual que en Windows)

```bash
python -m pytest tests/ -q
python launch.py desktop
# Ir a modo "Detección de Acordes" y mirar el panel derecho.
# Repetir el arranque varias veces para descartar crashes intermitentes.
```
