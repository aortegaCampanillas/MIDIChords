# MIDIChords Web

Aplicación web en Python con FastAPI y frontend JS.

## Ejecutar

Desde la raíz del repo:

```bash
python launch.py web --host 127.0.0.1 --port 8000 --reload
```

## Funcionalidades incluidas

- Detección de acordes por notas activas
- Generación de acordes (tónica/variante/inversión)
- Generación de escalas
- Metrónomo básico en navegador
- Afinador básico con micrófono (WebAudio)

## API

- `GET /api/meta`
- `POST /api/detect`
- `POST /api/generate/chord`
- `POST /api/generate/scale`

