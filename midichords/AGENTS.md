# Instrucciones para `midichords/`

Estas reglas complementan el `AGENTS.md` de la raíz y se aplican al escritorio y al paquete Python compartido.

## Arquitectura real

- La aplicación de escritorio vigente usa **PySide6/Qt**.
- `midichords/main_app.py` crea `MidiChordAnalyzerApp`, que combina los mixins con `QtSchedulerMixin` y `QMainWindow`.
- `midichords/qt/tk_compat.py`, `ttk_compat.py` y `tkfont_compat.py` adaptan parte de la API histórica de Tk sobre Qt. Un import llamado `tk` no implica que se esté ejecutando Tkinter.
- Los widgets personalizados activos proceden de `midichords/ui/widgets_qt.py`;
  los builders estables están en `midichords/ui/desktop_ui_builders.py`.

## Límites de responsabilidad

- `core/music_theory.py` y `core/music_service.py`: lógica musical pura, sin Qt, widgets ni audio.
- `core/audio_engine.py`: reproducción y dispositivos de audio, sin construcción de UI.
- `mixins/`: coordinación de cada modo y de los subsistemas de escritorio.
- `ui/` y `qt/`: presentación y adaptación de APIs; no introducir aquí reglas musicales nuevas.
- `main_app.py`: composición, estado transversal y ciclo de vida. Evitar añadir lógica específica de un modo si puede vivir en su mixin.

## Archivos grandes

No leer ni reescribir completos `main_app.py`, `mixins/ui_mixin.py` o `mixins/render_mixin.py` sin necesidad. Localizar primero el método y sus llamadas.

Al extraer código:

1. Separar por responsabilidad, no por número arbitrario de líneas.
2. Mantener temporalmente la interfaz que esperan los mixins (`self.<atributo>` y callbacks).
3. Añadir tests de la lógica pura antes de cambiar coordinación o UI.
4. No sustituir globalmente la compatibilidad Tk por Qt directo como parte de un cambio funcional no relacionado.

## Verificación

Desde la raíz:

```bash
python scripts/check.py python
```

Si cambia un contrato musical, comprobar también Worker y Flutter según `docs/architecture/SOURCE_OF_TRUTH.md`.
