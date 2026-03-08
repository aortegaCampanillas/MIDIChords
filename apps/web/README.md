# MIDIChords Web

Aplicación web servida con Cloudflare Worker (`apps/web/worker/_worker.js`) y assets estáticos (`apps/web/index.html` + `apps/web/static`).

## Ejecutar en local (igual que Cloudflare)

Desde la raíz del repo:

```bash
python launch.py web --host 127.0.0.1 --port 8000
```

Este comando usa `wrangler dev` con el mismo Worker que producción.

## API

Rutas internas del Worker:

- `GET /api/health`
- `GET /api/meta`
- `POST /api/detect`
- `POST /api/generate/chord`
- `POST /api/generate/scale`
- `POST /api/generate/guitar-variations`
- `POST /api/feedback`

## Comentarios

El formulario de comentarios puede enviar email real solo en despliegues de preview.

Variables necesarias en Cloudflare Pages (Preview):

- `MIDICHORDS_FEEDBACK_PROVIDER=resend`
- `MIDICHORDS_FEEDBACK_TO=destino@dominio.com`
- `MIDICHORDS_FEEDBACK_FROM=MIDIChords Preview <no-reply@tu-dominio-verificado.com>`
- `RESEND_API_KEY` (secret)

En `main`/producción el endpoint `/api/feedback` queda en modo no-envío (mock).
