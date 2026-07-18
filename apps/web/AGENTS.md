# Instrucciones para `apps/web/`

Estas reglas complementan el `AGENTS.md` de la raíz.

## Fuentes editables

- SPA: `static/app.js`, `static/ui_texts.js`, `static/music_notation.js`, `static/circle_theory.js`, `static/interval_theory.js`, `static/piano_fingering.js`, `static/chord_help.js`, `static/help_callouts.js` y `static/style.css`.
- HTML público: `index.html`, `app.html` y `fp30x.html`.
- API: `worker/_worker.js`.
- Assets web: `static/`.

`pages-dist/` es salida generada por `python scripts/build_web_pages_dist.py` o por el flujo de despliegue. No editarla como fuente ni incluirla en cambios manuales.

## Contratos

- El frontend consume `/api/meta`, `/api/detect`, `/api/generate/chord`, `/api/generate/scale`, `/api/generate/guitar-variations` y `/api/feedback`.
- Si cambia un nombre de campo, actualizar en el mismo cambio Worker, SPA, tests y documentación.
- El Worker reimplementa en JavaScript parte de `midichords/core/music_service.py`; no ejecuta el paquete Python.
- Los patrones musicales todavía están duplicados entre Python, Worker y Flutter. Tratar `midichords/core/music_theory.py` como referencia funcional y verificar paridad antes de cambiar una copia.

## Archivos grandes

`static/app.js` contiene estado, API, audio, MIDI, renderers y modos. Antes de modificarlo, localizar la función concreta y sus llamadas. Las extracciones futuras deben hacerse por subsistema o modo y conservar primero el comportamiento observable.

`static/chord_help.js` contiene el catálogo bilingüe, grupos de variantes y textos de inversiones de la ayuda de acordes. Se carga antes de `app.js` y publica `globalThis.MidiChordsChordHelp`; conservar ese orden y actualizar las pruebas de paridad al modificarlo.

`static/ui_texts.js` contiene los textos generales ES/EN y publica `globalThis.MidiChordsUiTexts`. Cada clave debe existir en ambos idiomas; `tests/test_web_ui_texts.py` comprueba esa paridad y el orden de carga.

`static/music_notation.js` contiene nombres de notas, letras de tónica, alteraciones, armaduras y conversiones puras de pitch class. La UI debe consumir estas funciones en vez de duplicar normalización o tablas.

`static/circle_theory.js` contiene orden de quintas, grados, tríadas diatónicas, armaduras y geometría pura del círculo. El renderizado con estado y DOM permanece en `app.js`; mantener esa frontera para que la teoría pueda probarse directamente con Node.

`static/interval_theory.js` contiene nombres bilingües, cálculo de semitonos y catálogo/mapeo de melodías mnemotécnicas. La cola de notas, temporizadores y reproducción permanecen en `app.js`.

`static/piano_fingering.js` contiene patrones documentados y resolución pura de digitaciones de acordes y escalas. No añadir fallbacks inventados para tonalidades sin fuente; el resultado vacío indica que no hay referencia documentada.

`static/help_callouts.js` define los selectores, claves de texto y posiciones de la ayuda contextual por modo. La suite Node comprueba que cada clave exista en ambos idiomas; mantener aquí configuración declarativa, no manipulación del DOM.

Los scripts y hojas CSS enlazados desde `app.html` se descubren automáticamente para comprobar sintaxis, aplicar fingerprint en `pages-dist/` y validar producción. Al añadir un módulo estático, mantener el orden de sus `<script>` en `app.html`; no hay que registrar su nombre en los scripts Python.

## Verificación

Desde la raíz:

```bash
python scripts/check.py web
```

El perfil comprueba la sintaxis de la SPA y del Worker, ejecuta las pruebas nativas de Node en `test/` y construye `pages-dist/`. Añadir casos JavaScript directos cuando se extraiga lógica ejecutable; mantener los tests Python para contratos y paridad multiplataforma.
