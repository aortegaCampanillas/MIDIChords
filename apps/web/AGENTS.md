# Instrucciones para `apps/web/`

Estas reglas complementan el `AGENTS.md` de la raíz.

## Fuentes editables

- SPA: `static/app.js` y `static/style.css`.
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

## Verificación

Desde la raíz:

```bash
python scripts/check.py web
```

El perfil comprueba la sintaxis de la SPA y del Worker con Node, y construye `pages-dist/`. No hay todavía una suite JavaScript dedicada; los cambios de lógica deben acompañarse de tests cuando se introduzca esa infraestructura.
