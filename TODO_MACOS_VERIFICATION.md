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

## Archivos tocados (estado final)

- `midichords/qt/tk_compat.py`: clase `Widget` — solo `winfo_width()` / `winfo_height()`
  (getters puros, sin `resizeEvent` nuevo).
- `midichords/mixins/ui_mixin.py`: `_refresh_right_panel_wraplengths` usa `panel_width`
  en vez de `left_w`; se quitó el bind muerto `chord_panel.bind("<Configure>", ...)`
  (redundante, `staff_canvas` ya dispara el refresco).

## Verificado en Windows

- [x] `python -m pytest tests/` → 766 passed, 12 subtests passed.
- [x] `python launch.py desktop` arranca de forma estable (4/4 intentos sin crash tras
      el fix final; antes del fix final, crash reproducible 100% de las veces).
- [x] Captura de pantalla en modo Detección: el texto de ayuda se ve completo en 2 líneas
      dentro del panel derecho (antes se cortaba/desbordaba).

## Pendiente de verificar en macOS

- [ ] `python -m pytest tests/` sigue en verde (766 passed).
- [ ] `python launch.py desktop` arranca varias veces seguidas sin crash (no solo una vez).
- [ ] Modo **Detección**: texto de ayuda del panel derecho en 2 líneas, sin cortarse ni
      desbordar, tanto al abrir la app como al redimensionar la ventana.
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
