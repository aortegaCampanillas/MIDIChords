# TODO macOS verification — Qt shim `<Configure>` / wraplength fix

Contexto: bugs encontrados y corregidos en **Windows** (escritorio, backend Qt/PySide6 vía
`midichords/qt/tk_compat.py`). Pendiente de repetir la verificación visual en **macOS** antes
de dar el cambio por cerrado, porque el arreglo toca la clase base de la que heredan casi
todos los widgets (`Frame`, `Label`, `Button`, `Radiobutton`, `Entry`), no solo el widget
donde se detectó el síntoma.

## Síntoma original

Modo **Detección de acordes** → panel derecho: el texto de ayuda
("Pulsa notas en piano/guitarra para detectar acordes o usa un dispositivo MIDI.")
se recortaba/desbordaba en vez de ajustarse a 2 líneas dentro del panel.

## Causa raíz (dos bugs)

1. **`midichords/qt/tk_compat.py` — clase `Widget`** (base de `Frame`, `Label`, `Button`,
   `Radiobutton`, `Entry`): no implementaba `winfo_width()` / `winfo_height()` ni disparaba
   el evento `<Configure>` en `resizeEvent`. Solo `QtCanvas` (en `qt_primitives.py`) lo hacía.
   Consecuencia: cualquier `widget.winfo_width()` sobre un `Frame`/`Label` lanzaba excepción
   (capturada silenciosamente en el código llamante) y cualquier `bind("<Configure>", ...)`
   sobre esos widgets nunca se disparaba tras el layout inicial.
   - Fix: añadidos `winfo_width()`, `winfo_height()` y un `resizeEvent` que llama a
     `super().resizeEvent(event)` y luego dispara el binding `<Configure>` vía `_call_binding`.
   - `QtCanvas` es una clase independiente (no hereda de `Widget`), así que este cambio no
     la afecta ni duplica su despacho de `<Configure>` — bajo riesgo de regresión ahí.

2. **`midichords/mixins/ui_mixin.py` → `_refresh_right_panel_wraplengths`**: el `wraplength`
   de `detection_help_label` (que vive en el panel **derecho**, `chord_panel`) se calculaba
   usando el ancho del **panel izquierdo** (`staff_canvas`) en vez del propio `chord_panel`.
   Esto es lo que quedó "compensando" el bug (1): como `staff_canvas` sí disparaba
   `<Configure>` (por ser `Canvas`), se usó su ancho como sustituto, pero al ser mucho más
   ancho que el panel derecho real, el texto no se ajustaba dentro del espacio disponible.
   - Fix: revertido a usar `panel_width` (`chord_panel.winfo_width()`), igual que el resto
     de labels del panel derecho (`result_wrap`, etc.).

## Archivos tocados

- `midichords/qt/tk_compat.py` (clase `Widget`: `winfo_width`, `winfo_height`, `resizeEvent`)
- `midichords/mixins/ui_mixin.py` (`_refresh_right_panel_wraplengths`)

## Verificado en Windows

- [x] `python -m pytest tests/` → 766 passed, 12 subtests passed.
- [x] Captura de pantalla en modo Detección: el texto de ayuda se ve completo en 2 líneas
      dentro del panel derecho (antes se cortaba/desbordaba).

## Pendiente de verificar en macOS

- [ ] `python -m pytest tests/` sigue en verde (766 passed).
- [ ] Modo **Detección**: texto de ayuda del panel derecho en 2 líneas, sin cortarse ni
      desbordar, tanto al abrir la app como al redimensionar la ventana (antes el cálculo
      solo se hacía una vez al arrancar; ahora `<Configure>` se dispara en cada resize).
- [ ] Smoke test general por si el nuevo despacho de `<Configure>` en `Frame`/`Label`/
      `Button`/`Radiobutton`/`Entry` cambia algo en otros paneles que antes "vivían" sin él:
      - Generación (nombre de acorde generado, `staff_generated_chord_value`)
      - Escalas (fingering, sliders de metrónomo de escala)
      - Círculo de quintas
      - Metrónomo (sliders de volumen/BPM/compás, botones +/−)
      - Afinador (sliders de ganancia/rango de espectro)
      - Detección de intervalos (`interval_result_canvas`)
- [ ] Redimensionar la ventana en varios modos y comprobar que no aparecen saltos de layout,
      texto cortado o widgets que no se reajustan.
- [ ] Nada de esto debería afectar a `QtCanvas` (mantiene su propio despacho de `<Configure>`
      independiente), pero conviene confirmarlo igualmente arrastrando sliders/canvas del
      metrónomo y afinador.

## Cómo reproducir la verificación visual (igual que en Windows)

```bash
python -m pytest tests/ -q
python launch.py desktop
# Ir a modo "Detección de Acordes" y mirar el panel derecho.
```
