# Changelog

Historial de versiones publicadas de MIDIChords.

## [1.0.0] - 2026-03-14

Primera versión 1.x publicada del proyecto.

> Nota (trazabilidad iOS): esta etiqueta `v1.0.0` apunta al commit con el que se subió a App Store Connect la build de iOS **1.0.0 (2)**.

Disponible en:

- App Store en iOS
- Mac App Store en escritorio macOS
- Google Play en Android

### Añadido

- Aplicación Flutter para tablet con detección, generación de acordes, escalas y metrónomo.
- Modo ayuda contextual en móvil con zonas interactivas por pantalla y por control.
- Flujo documentado de despliegue web en Cloudflare Pages.

### Mejorado

- Resaltado del pentagrama en generación de acordes para respetar mejor la mano activa.
- Comportamiento del metrónomo y del audio nativo iOS en iPhone/iPad.
- Ayudas contextuales y distribución visual en iPad.

### Corregido

- Envío del formulario de comentarios en producción web.
- Verificación del despliegue de producción web para detectar estados rotos donde faltaba `/api/meta`.
- Varios problemas de enlace y configuración del proyecto iOS Flutter.

## [Unreleased] - Cambios desde [1.0.0]

Estos cambios son los que entrarán en la **próxima subida** respecto a `v1.0.0` (iOS **1.0.0 (2)**).

### iOS (Flutter)

- Audio del piano menos “cortado” al soltar la tecla (release más natural).
- Reducción de saturación/clipping percibido en iOS (atenuación de ganancia, especialmente en piano).
- Preparada la próxima build de iOS: **1.0.1 (3)**.

### Web (Cloudflare Pages)

- Nuevo panel **Descargas** (PC/Mac y móvil) con ventana/modal y enlaces actualizados.
- Enlaces de descarga directos para artefactos en GitHub (`/releases/latest/download/...`).
- Endurecimiento del despliegue para evitar caché de CSS/JS:
  - `Cache-Control: no-store` para HTML y `/static/*`.
  - Cache-busting en `index.html` con `?v=${GITHUB_SHA}` en `style.css` y `app.js`.
- Ajuste de responsive: mantener **3 columnas** del panel inferior hasta 700px.

### CI / Releases (desktop)

- Firma y notarización de macOS en CI (opcional vía `SIGN_MACOS=true`) con import de certificado, keychain y `notarytool`.
- Fixes de creación de DMG en macOS CI (`hdiutil` “Resource busy” y nombre temporal `.tmp.dmg`).
- Deploy de Cloudflare producción solo con **tags `v*`** (no en cada push a `main`).
- Publicación de instaladores en GitHub Releases y sincronización al repo público `FreeMIDIChords_Releases`.

### Repo / mantenimiento

- Eliminado el submódulo roto `flathub-submission` y añadido a `.gitignore` como carpeta local.

[1.0.0]: https://github.com/aortegaCampanillas/MIDIChords/releases/tag/v1.0.0
