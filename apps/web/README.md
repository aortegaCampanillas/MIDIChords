# MIDIChords Web

Aplicación web servida con Cloudflare Worker (`apps/web/worker/_worker.js`) y assets estáticos (`apps/web/index.html` + `apps/web/static`).

## Despliegue a Cloudflare Pages

La web se publica en Cloudflare Pages, no con un `wrangler.toml` local dentro del repo.

**Producción solo con etiquetas:** el workflow de producción (`deploy-cloudflare-on-tag.yml`) **no** se dispara con push a `main`; solo se ejecuta al hacer **push de una etiqueta** `v*` (p. ej. `v1.0.1`) o manualmente con *workflow_dispatch*.

El flujo real de despliegue es:

1. preparar un bundle estático temporal con:
   - `apps/web/index.html`
   - `apps/web/static/`
   - `apps/web/worker/_worker.js` copiado como `_worker.js`
2. desplegar ese bundle al proyecto de Pages configurado en GitHub:
   - variable: `CLOUDFLARE_PAGES_PROJECT`
   - valor actual: `midichords`

### Método recomendado

Usar GitHub Actions, porque ya reutiliza los secrets del repositorio:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- variable `CLOUDFLARE_PAGES_PROJECT`

Producción (se dispara al subir un tag; para lanzar a mano usa un tag existente o el botón Run workflow):

```bash
gh workflow run deploy-cloudflare-on-tag.yml --ref v1.0.1
```

Ese workflow no da el deploy por válido solo porque `wrangler` termine bien. Después:

- comprueba `https://freemidichords.com/api/meta?language=es`
- exige que la respuesta incluya `chord_patterns`
- si Cloudflare deja producción en un estado roto o incompleto, repite el deploy una vez
- si después del reintento sigue fallando, el workflow termina en error

Preview de una rama:

```bash
gh workflow run deploy-cloudflare-preview.yml --ref <tu-rama>
```

Ver estado del despliegue:

```bash
gh run list --workflow deploy-cloudflare-on-tag.yml
gh run watch <run_id>
```

### Cuándo usar cada workflow

- `deploy-cloudflare-preview.yml`: previews de ramas que no son `main`
- `deploy-cloudflare-on-tag.yml`: producción; **solo** se dispara con push a etiquetas `v*` (no con push a `main`). También puede lanzarse manualmente con *workflow_dispatch*. Siempre despliega el estado actual de la rama `main`.

### Despliegue manual con Wrangler

Solo úsalo si realmente necesitas publicar desde tu máquina y tienes credenciales locales válidas.

Hace falta:

- `wrangler` instalado
- `CLOUDFLARE_API_TOKEN` exportado en el entorno
- acceso al proyecto `midichords`

Preparación del bundle:

```bash
rm -rf /tmp/midichords-pages-dist
mkdir -p /tmp/midichords-pages-dist/static
cp apps/web/index.html /tmp/midichords-pages-dist/index.html
cp -R apps/web/static/. /tmp/midichords-pages-dist/static/
cp apps/web/worker/_worker.js /tmp/midichords-pages-dist/_worker.js
```

Deploy a producción:

```bash
wrangler pages deploy /tmp/midichords-pages-dist --project-name=midichords --branch=main
```

Comprobación manual recomendada después del deploy:

```bash
curl -fsS 'https://freemidichords.com/api/meta?language=es'
```

La respuesta debe ser JSON e incluir `chord_patterns` y `scale_patterns`. Si devuelve `404`, el frontend cargará pero los combos de generación y escalas quedarán vacíos.

Nota: si `wrangler` falla en entorno no interactivo pidiendo `CLOUDFLARE_API_TOKEN`, usa el workflow de GitHub Actions; es el camino más fiable en este repo.

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

El formulario de comentarios usa `Resend` si está configurado:

- `MIDICHORDS_FEEDBACK_PROVIDER=resend`
- `MIDICHORDS_FEEDBACK_TO=destino@dominio.com`
- `MIDICHORDS_FEEDBACK_FROM=MIDIChords <no-reply@tu-dominio-verificado.com>`
- `RESEND_API_KEY` (secret)

Comportamiento por entorno:

- Preview: envía correo automáticamente cuando `provider=resend`.
- Producción (`main`): envía correo automáticamente cuando `provider=resend`.
