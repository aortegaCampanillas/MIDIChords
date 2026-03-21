# MIDIChords Web

Aplicación web servida con Cloudflare Worker (`apps/web/worker/_worker.js`) y assets estáticos (`apps/web/index.html` + `apps/web/static`). El worker redirige (**307**) las peticiones a `/static/*` que llevan query o fragmento hacia la URL canónica sin ellos, para que CSS/JS sigan cargando aunque el HTML cacheado enlace con `?v=…`.

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

### Desplegar sin GitHub Actions (local)

Puedes publicar producción desde tu máquina con el mismo resultado que el workflow.

**Opción recomendada: fichero de secretos (no se sube al repo)**

1. Copia el ejemplo y rellena tus valores (el fichero real `.env.deploy` está en .gitignore):
   ```bash
   cp env.deploy.example .env.deploy
   # Edita .env.deploy con tu CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID y CLOUDFLARE_PAGES_PROJECT
   ```
   También se busca `apps/web/.env.deploy`.
2. Despliega (el comando lee las variables desde `.env.deploy`):
   ```bash
   python launch.py deploy-web
   ```

También se busca `.env.deploy` en la raíz del repo. Las variables de entorno ya definidas tienen prioridad sobre el fichero.

**Sin fichero:** puedes exportar las variables en la shell y ejecutar `python launch.py deploy-web`, o usar `--project-name midichords` si solo falta el nombre del proyecto.

El comando prepara el bundle en `apps/web/pages-dist` y ejecuta `wrangler pages deploy`. Los estáticos se sirven con `Cache-Control: no-store` vía `_headers` y el worker (no se usan querystrings `?v=` en el HTML: en Pages rompían la resolución de assets). No hace smoke test; comprueba tú la URL de producción después.

### Método recomendado (GitHub Actions)

Usar GitHub Actions reutiliza los secrets del repositorio:

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
- `web-production-health.yml`: **comprobación horaria** (cron, UTC) y **tras cada deploy exitoso** de `Deploy Cloudflare (Production)` (`workflow_run`), con **espera de 90 s** solo en ese caso para dar margen a la CDN. **`concurrency`** evita solapar dos chequeos (p. ej. cron + post-deploy). Comprueba HTML, CSS, `app.js` y `GET /api/meta?language=es`. Si falla, intenta correo vía **Resend** (**secret `RESEND_API_KEY`**; si falta, aviso en el log). El paso de correo tiene **`continue-on-error`**: si Resend devuelve error, el job **sigue marcado como fallido por el chequeo web**, pero en el log verás el **cuerpo de respuesta de Resend**. El script **`scripts/send_resend_health_alert.py`** envía con **`User-Agent`** (evita 403/1010) y prueba remitentes en orden: variable **`NOTIFY_FROM_EMAIL`**, luego **`notifications@freemidichords.com`**, luego **`onboarding@resend.dev`**. Para Gmail suele hacer falta un **dominio verificado** en Resend; configura **`NOTIFY_FROM_EMAIL`** con algo tipo `MIDIChords <noreply@tudominio.com>`. Destinatario por defecto **aortega98@gmail.com**; variable **`WEB_HEALTH_ALERT_TO`**. *Run workflow*. El **cron solo corre en la rama por defecto** (p. ej. `main`).

### Monitorización local

```bash
python3 scripts/check_production_web_health.py
# Otra URL:
WEB_BASE_URL=https://staging.ejemplo.com python3 scripts/check_production_web_health.py
```

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
[ -f apps/web/robots.txt ] && cp apps/web/robots.txt /tmp/midichords-pages-dist/robots.txt
[ -f apps/web/sitemap.xml ] && cp apps/web/sitemap.xml /tmp/midichords-pages-dist/sitemap.xml
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
