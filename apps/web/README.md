# MIDIChords Web

Aplicación web servida con Cloudflare Worker (`apps/web/worker/_worker.js`) y assets estáticos (`apps/web/index.html` + `apps/web/static`). El worker redirige (**307**) las peticiones a `/static/*` que llevan query o fragmento hacia la URL canónica sin ellos, para que CSS/JS sigan cargando aunque el HTML cacheado enlace con `?v=…`.

## Despliegue a Cloudflare Pages

La web se publica en Cloudflare Pages, no con un `wrangler.toml` local dentro del repo.

**Producción solo con etiquetas:** el workflow de producción (`deploy-cloudflare-on-tag.yml`) **no** se dispara con push a `main`; solo se ejecuta al hacer **push de una etiqueta** `v*` (p. ej. `v1.0.1`) o manualmente con *workflow_dispatch*.

El flujo real de despliegue es:

1. preparar un bundle estático temporal con:
   - `apps/web/index.html` y `apps/web/app.html` (en el bundle, los enlaces a **`ui_texts.js`**, **`chord_help.js`**, **`help_callouts.js`**, **`app.js`** y **`style.css`** se reescriben a nombres con **hash de contenido**, p. ej. `/static/app.a1b2c3d4e5f6.js`, para evitar cachés del edge en el dominio personalizado)
   - `apps/web/static/`
   - `apps/web/worker/_worker.js` copiado como `_worker.js`

   El script **`scripts/build_web_pages_dist.py`** (o `python launch.py deploy-web`) descubre automáticamente los JS/CSS enlazados desde `app.html` y aplica ese paso; en el repo siguen existiendo sus nombres estables para desarrollo local.
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
- `deploy-cloudflare-on-tag.yml`: producción; **solo** se dispara con push a etiquetas `v*` (no con push a `main`). También puede lanzarse manualmente con *workflow_dispatch*. Siempre despliega el estado actual de la rama `main`. Tras cada **`pages deploy`** espera **120 s** antes del smoke test de `/api/meta` (y lo mismo tras un redeploy de retry) para que el edge aplique el worker y **`_routes.json`** en el dominio personalizado.
- `web-production-health.yml`: **comprobación horaria** (cron, UTC) y **tras cada deploy exitoso** de `Deploy Cloudflare (Production)` (`workflow_run`), con **espera de 120 s** solo en ese caso para dar margen a propagación CDN/worker en el dominio personalizado. **`concurrency`** evita solapar dos chequeos (p. ej. cron + post-deploy). Comprueba HTML, CSS, `app.js` y `GET /api/meta?language=es`. Si **falla el primer chequeo**, el workflow **reconstruye el bundle**, hace **`wrangler pages deploy`** a producción desde **`main`** (requiere secrets **`CLOUDFLARE_API_TOKEN`** y **`CLOUDFLARE_ACCOUNT_ID`**, y variable **`CLOUDFLARE_PAGES_PROJECT`**), espera **120 s** y **vuelve a comprobar**. El correo **Resend** (si hay **`RESEND_API_KEY`**) se envía siempre que haya fallado el 1er chequeo: el **asunto** lleva **`[RESUELTO]`** si el 2º chequeo pasa tras el redeploy automático, o **`[ACCIÓN REQUERIDA]`** si la autocuración no deja la web sana. El paso de correo tiene **`continue-on-error`** (el job falla por el chequeo, pero verás errores de Resend en el log). **`scripts/send_resend_health_alert.py`**: **`User-Agent`**, remitentes en orden **`NOTIFY_FROM_EMAIL`**, **`notifications@freemidichords.com`**, **`onboarding@resend.dev`**. Para Gmail suele hacer falta dominio verificado en Resend. Destinatario por defecto **aortega98@gmail.com**; **`WEB_HEALTH_ALERT_TO`**. *Run workflow*. El **cron solo corre en la rama por defecto** (p. ej. `main`).

### Monitorización local

```bash
python3 scripts/check_production_web_health.py
# Otra URL:
WEB_BASE_URL=https://staging.ejemplo.com python3 scripts/check_production_web_health.py
# Más reintentos si el edge aún propaga (por defecto 2; en Actions el workflow usa 4):
WEB_HEALTH_RETRIES=5 python3 scripts/check_production_web_health.py
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
cp apps/web/_routes.json /tmp/midichords-pages-dist/_routes.json
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

### API en producción: `404` con cuerpo vacío (dominio personalizado)

Si `curl -sSI 'https://freemidichords.com/api/meta?language=es'` devuelve **404**, **`content-length: 0`** y **no** hay `content-type: application/json`, la petición **no está llegando** al `_worker.js` de Pages: el edge intenta servir `/api/meta` como **estático** y al no existir fichero responde vacío. El worker del repo sí devolvería JSON (aunque sea error) con `content-type`.

Qué hacer:

1. **Vuelve a desplegar** el bundle actual (incluye **`_routes.json`** en la raíz del deploy junto a `_worker.js`, con `"include": ["/*"]`, para que **todas** las rutas pasen por el worker).
2. En **Cloudflare Dashboard** → **Workers & Pages** → proyecto **Pages** (`midichords`) → **Custom domains**: confirma que **`freemidichords.com`** está enlazado a **este** proyecto (no a otro sitio ni a un Worker suelto).
3. En el **mismo zona DNS** (`freemidichords.com`), revisa **Workers Routes**: ninguna ruta del tipo `*freemidichords.com/*` debe capturar el tráfico **antes** que Pages y devolver 404 sin pasar por el proyecto.
4. Comprueba de nuevo: `python3 scripts/check_production_web_health.py`

### Dominio personalizado: JS/CSS antiguos (caché del zona)

Si **`*.pages.dev`** muestra el comportamiento nuevo pero tu dominio (p. ej. `freemidichords.com`) no, casi siempre es **caché en el edge del zona** con TTL largo para `/static/*` (verás `cf-cache-status: HIT` y `cache-control: public, max-age=…` en `curl -sI https://tudominio/static/app.js`).

1. **Cloudflare Dashboard** del dominio → **Caching** → **Configuration** → **Purge Everything** (o *Custom Purge* con URL/prefijo `https://tudominio/static/`).
2. Revisa **Caching** → **Cache Rules**: si hay una regla tipo *Cache Everything* o TTL fijo para `/static/*`, cámbiala para **respetar cabeceras de origen** o excluir esas rutas; el worker ya envía `Cache-Control: no-store` y `CDN-Cache-Control: no-store` en HTML y estáticos.

Comparación rápida:

```bash
curl -sI 'https://midichords.pages.dev/static/app.js' | grep -i cache-control
curl -sI 'https://freemidichords.com/static/app.js' | grep -i cache-control
```

En el host de Pages debería verse `no-store`; en el dominio custom, tras purgar o corregir reglas, igual.

Nota: si `wrangler` falla en entorno no interactivo pidiendo `CLOUDFLARE_API_TOKEN`, usa el workflow de GitHub Actions; es el camino más fiable en este repo.

## Google Search Console

Estos pasos los ejecuta **quien administra el dominio** en [Google Search Console](https://search.google.com/search-console); no hay automatización en el repo más allá de tener ya **`robots.txt`**, **`sitemap.xml`** y metas en **`index.html`** (tras un deploy con etiqueta `v*`).

### 1. Dar de alta la propiedad

1. Entra en Search Console → **Añadir propiedad**.
2. Elige uno de estos modos (recomendación según tu caso):
   - **Prefijo de URL** `https://freemidichords.com/` — suele ser lo más rápido si solo importa la web HTTPS.
   - **Dominio** `freemidichords.com` — incluye todas las variantes (http/https, subdominios); la verificación suele ser por **registro DNS TXT** en el proveedor del dominio (p. ej. Cloudflare).

### 2. Verificar la propiedad

Sigue el asistente de Google. Métodos habituales:

| Método | Notas |
|--------|--------|
| **Etiqueta HTML** | Google te da un `<meta name="google-site-verification" content="…" />`. Colócalo en el `<head>` de **`apps/web/index.html`**, despliega de nuevo (tag `v*`) y pulsa *Verificar* en GSC. |
| **Fichero HTML** | Sube el fichero que indique Google a la **raíz del bundle** de Pages (junto a `index.html`), igual que `robots.txt`, y vuelve a desplegar. |
| **DNS** | Registro TXT en el DNS del dominio; obligatorio si elegiste propiedad tipo **Dominio**. |

Hasta que la verificación no sea correcta, no podrás enviar el sitemap de forma fiable.

### 3. Enviar el sitemap

1. En la propiedad verificada, menú **Sitemaps**.
2. En *Añadir un sitemap nuevo*, escribe: `sitemap.xml` (o la URL completa `https://freemidichords.com/sitemap.xml` si la interfaz lo pide así).
3. Comprueba que el estado pase a **Correcto** (puede tardar horas el primer procesamiento).

Comprobación rápida desde terminal (debe devolver XML, no error):

```bash
curl -fsSI 'https://freemidichords.com/sitemap.xml'
curl -fsS 'https://freemidichords.com/robots.txt'
```

### 4. Revisar cobertura

1. **Indexación** → **Páginas** (o *Cobertura* en vistas antiguas).
2. Revisa **Correctas**, **Excluidas** y **Con errores**. Para una SPA de una sola URL relevante, lo normal es ver la **página principal** indexada; las exclusiones por *duplicado*, *canonical* o *redirección* pueden ser esperables según la configuración.
3. Si aparece **No se ha podido rastrear** o **404**, confirma que el último deploy de producción incluye `index.html` y que `https://freemidichords.com/` responde **200**.

### 5. Consultas y rendimiento

1. **Rendimiento** (o **Resultados de la búsqueda**): consultas, impresiones, clics y posición media (con retraso de unos días).
2. Usa filtros por **página** (`https://freemidichords.com/`) y por **consulta** para ver por qué términos aparece el sitio.
3. **Experiencia de página** / **Core Web Vitals** (si está disponible en tu cuenta): sirve para detectar problemas de UX en dispositivos móviles o escritorio.

### Comprobaciones previas al alta

- El **sitemap** en producción lista la URL canónica: `https://freemidichords.com/`.
- **`robots.txt`** no bloquea el rastreo de `/` y enlaza al sitemap (ya configurado en el repo).

## Ejecutar en local (igual que Cloudflare)

Desde la raíz del repo:

```bash
python launch.py web --host 127.0.0.1 --port 8000
```

Este comando usa `wrangler dev` con el mismo Worker que producción.

Si necesitas HTTPS local, usa el mismo launcher con `--https`:

```bash
python launch.py web --host 127.0.0.1 --port 8443 --https
```

Esto también usa `wrangler dev`; no arranca proxy ni backend adicional. Wrangler puede usar certificados propios con `--https-key-path` y `--https-cert-path` si hace falta.

## Frontend (modos SPA)

El cliente es una **SPA** en **`static/app.js`** y **`static/style.css`**, cargada desde **`app.html`**. Los textos generales viven en **`static/ui_texts.js`**, las tablas y conversiones de notación en **`static/music_notation.js`**, la teoría y geometría pura del círculo en **`static/circle_theory.js`**, la teoría de intervalos y melodías mnemotécnicas en **`static/interval_theory.js`**, la ayuda teórica de acordes en **`static/chord_help.js`** y la configuración de ayuda contextual por modo en **`static/help_callouts.js`**; estos módulos se cargan antes de `app.js`. El selector de modo (`#modeSelect`) alterna entre: detección de acordes, **detección de intervalos**, generación de acordes, **círculo de quintas**, escalas, metrónomo y afinador.

Las pruebas JavaScript sin dependencias externas están en **`test/`** y se ejecutan con `node --test`; `python scripts/check.py web` incluye esta suite, la comprobación de sintaxis y la construcción del bundle.

El perfil web y el chequeo de salud de producción validan automáticamente todos los scripts y hojas CSS locales enlazados por `app.html`; no mantienen una lista paralela de nombres de assets.

### Detección de intervalos (`interval_detection`)

- **Ubicación en código**: `apps/web/static/interval_theory.js` contiene nombres, cálculo y melodías; `apps/web/static/app.js` conserva estado `state.mode === "interval_detection"`, cola, reproducción, panel y renderizado.
- **Funcionamiento**: registra las **últimas 2 notas** pulsadas (teclado interactivo o MIDI), ordena ascendentemente para el pentagrama y muestra nombre del intervalo, semitonos y una **canción mnemotécnica** (`INTERVAL_MELODIES`). Las notas se guardan en orden de inserción para que `shift()` descarte siempre la más antigua.
- **Melodía mnemotécnica** (botón «Recordar»): activa `state.intervalMelodyActive`; el pentagrama pasa a mostrar la melodía completa (`getIntervalMelodyNotes()`). Las dos notas del intervalo aparecen en blanco, el resto en gris. Algunas canciones usan `jumpAt > 0` cuando el salto del intervalo ocurre en la 2.ª→3.ª nota (p. ej. «Cumpleaños feliz»); en ese caso las notas de preparación llevan ligadura. El botón ▶ toca la melodía con duraciones reales (`DURATION_BEATS`); el botón ◀ toca el intervalo en orden inverso.
- **Duraciones**: `DURATION_BEATS` mapea `"w"/"h"/"h."/"q"/"q."/"e"/"e."/"s"/"s."` a tiempos; `playIntervalNoteSequence` calcula tiempos acumulados para respetar el ritmo y usa `state.intervalPlayingIdx` para resaltar la nota exacta en curso (no todas las del mismo pitch).
- **Silencios**: `null` en el array de offsets de `INTERVAL_MELODIES` → silencio; se dibuja el símbolo de silencio correspondiente con `drawRest()`.
- **Ayuda**: `HELP_CALLOUTS_INTERVAL_DETECTION` cubre todos los controles del panel.

### Círculo de quintas (`circle_fifths`)

- **Ubicación en código**: `apps/web/static/app.js` conserva estado, canvas y renderizado (`renderCircleFifths`, `runGenerateChordCircle`); `apps/web/static/circle_theory.js` contiene orden, grados, tríadas diatónicas y geometría pura.
- **Interacción**: **clic** para fijar la **tonalidad** según la banda (anillo exterior = acordes mayores del sector → modo mayor; anillo interior = fundamental menor relativa → modo menor natural; misma armadura). **Mayús+clic** para elegir un **acorde diatónico** (triada) de esa tonalidad sin cambiar la tónica; solo se acepta la combinación banda/sector coherente con la escala.
- **Datos**: el acorde mostrado y reproducido se obtiene con **`POST /api/generate/chord`** (mismo cuerpo conceptual que el modo generación: `root_pc`, `suffix`, `inversion`, `language`, `accidental`).
- **UI**: colores por función en el anillo; en modo menor, numerales tipo **♭III / ♭VI / ♭VII** (bemol en superíndice en canvas); botón **▶** superpuesto en la esquina superior izquierda del área del canvas (no ocupa una fila aparte). Textos y traducciones ES/EN están en los objetos de strings de `app.js` (`tr()`).
- **Ayuda (modo Ayuda)**: los globos de ayuda contextual incluyen el canvas del círculo (explicación del círculo de tónicas y clic/Mayús); el párrafo de ayuda fijo bajo el pentagrama **no** tiene callout asociado.

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
