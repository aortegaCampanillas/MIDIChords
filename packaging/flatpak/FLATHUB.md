# Publicar MIDIChords en Flathub

## Requisitos previos

1. **Tag de release** en GitHub (p. ej. `v1.0.1`), para que el manifiesto apunte a código estable.
2. **Cuenta en GitHub** con 2FA activada (Flathub lo exige para darte acceso al repo de la app).
3. **Dominio** `freemidichords.com` accesible por HTTPS (para verificación opcional en Flathub).

## Prueba local con `flatpak-builder` (Debian / Ubuntu)

El manifiesto usa **org.freedesktop.Sdk 24.08** y **`appstream-compose: true`**. Si al final del build aparece:

`bwrap: execvp appstream-compose: No such file or directory`

suele ser porque el **`flatpak-builder` del sistema es antiguo** (p. ej. Debian Bookworm ≈ 1.2.x): aún intenta ejecutar el binario `appstream-compose` dentro del entorno de build, pero **en el SDK 24.08 ese comando ya no va empaquetado** así. GitHub Actions usa Ubuntu reciente y no reproduce el fallo.

**Opción recomendada — `org.flatpak.Builder` de Flathub** (no depende de la versión del `.deb`):

1. Asegura el remoto **Flathub en instalación de usuario** (`~/.local/share/flatpak`), que es donde el wrapper del Builder apunta:

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install -y --user flathub org.flatpak.Builder
```

(`--user` en `install` evita el menú “system vs user” si tienes `flathub` duplicado.)

2. Lanza el build **sin** `--command=flatpak-builder`. Si fuerzas ese comando, te saltas `flatpak-builder-wrapper`, que exporta `FLATPAK_USER_DIR=$HOME/.local/share/flatpak`; entonces `flatpak --user install` mira el directorio aislado de la app (`~/.var/app/org.flatpak.Builder/...`), donde **no** está `flathub`, y aparece `No remote refs found for 'flathub'`.

```bash
cd /ruta/al/clon/MIDIChords
flatpak run --filesystem=home org.flatpak.Builder \
  --force-clean --user --install-deps-from=flathub --install \
  build-dir packaging/flatpak/com.freemidichords.MIDIChords.yml
```

(`--filesystem=home` permite leer el repo; el módulo `type: dir` del manifiesto apunta a `../../` desde `packaging/flatpak/`.)

Equivalente explícito: `--command=flatpak-builder-wrapper` (mismo efecto que el comando por defecto de la app). Flathub documenta también `flatpak run --command=flathub-build org.flatpak.Builder --install <manifiesto>` ([guía de envío](https://docs.flathub.org/docs/for-app-authors/submission#build-and-install)), con otras opciones por defecto (`repo/`, `builddir`, etc.).

**Opción alternativa — paquetes del sistema más nuevos:** en Debian, **`flatpak-builder` desde bookworm-backports** (≥ 1.4) y, en la misma línea que el CI del repo, `appstream` y `appstream-compose`:

```bash
sudo apt-get install -y flatpak flatpak-builder desktop-file-utils appstream appstream-compose
```

(El workflow [validate-flatpak.yml](../../.github/workflows/validate-flatpak.yml) del repo usa esa lista sobre `ubuntu-latest`.)

**Solo para una prueba rápida en local:** en una copia del YAML (no el que subes a Flathub), puedes poner `appstream-compose: false`; la app suele instalarse igual porque el metainfo ya se copia en el módulo `midichords-launcher`.

## Pasos para enviar el PR a Flathub

### 1. Crear un release en GitHub

- En https://github.com/aortegaCampanillas/MIDIChords/releases → "Create a new release".
- Tag: `v1.0.1` (o la versión que uses; debe coincidir con `tag:` en el manifiesto Flathub).
- Título y descripción opcionales. Publicar.

### 2. Fork y rama de Flathub

```bash
# Clonar tu fork de flathub (crea el fork en GitHub si no lo tienes)
git clone --branch new-pr git@github.com:TU_USUARIO_GITHUB/flathub.git
cd flathub

# Rama para esta app
git checkout -b add-com.freemidichords.MIDIChords new-pr
```

### 3. Añadir los archivos de la app

Los requisitos de Flathub exigen el **manifiesto y `flathub.json` en la raíz** de la rama del PR (no dentro de una subcarpeta). Copia los tres archivos **al toplevel** del clon de `flathub`:

```bash
cp /ruta/a/MIDIChords/packaging/flatpak/com.freemidichords.MIDIChords.flathub.yml \
   ./com.freemidichords.MIDIChords.yml
cp /ruta/a/MIDIChords/packaging/flatpak/flathub.json ./
cp /ruta/a/MIDIChords/packaging/flatpak/python-deps.json ./
cp /ruta/a/MIDIChords/packaging/flatpak/pyside6.json ./
```

**Importante:** En `com.freemidichords.MIDIChords.yml` el módulo `midichords-launcher` debe tener **`tag`** y **`commit`** (el linter de Flathub lo exige). El `commit` es el SHA al que apunta el tag en GitHub, p. ej.:

`git ls-remote https://github.com/aortegaCampanillas/MIDIChords 'refs/tags/v1.0.1^{}'`

En el repo MIDIChords el template `com.freemidichords.MIDIChords.flathub.yml` deja el `commit` como comentario: cópialo al YAML del PR y rellena el SHA antes de abrir o actualizar el PR.

### 4. Commit y PR

```bash
git add com.freemidichords.MIDIChords.yml flathub.json python-deps.json pyside6.json
git commit -m "Add com.freemidichords.MIDIChords"
git push origin add-com.freemidichords.MIDIChords
```

En GitHub: abre un **Pull Request** contra la rama **`new-pr`** del repo `flathub/flathub` (no contra `master`).

- Título del PR: **Add com.freemidichords.MIDIChords**

### 5. Comprobar build y linter (opcional pero recomendado)

En tu máquina, con el manifest en la **raíz** del clon:

```bash
flatpak install -y flathub org.flatpak.Builder
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest com.freemidichords.MIDIChords.yml
```

Si hay errores, corrígelos antes de abrir el PR o en el PR según indiquen los revisores.

### 6. Revisión y build de prueba

- Los revisores de Flathub revisan el PR.
- Para lanzar un build de prueba en el PR, comenta: **`bot, build`**.
- Responde a todos los comentarios y aplica los cambios que pidan.

### 7. Después del merge

- Flathub crea el repo **flathub/com.freemidichords.MIDIChords** y te invita como mantenedor. Acepta la invitación en GitHub.
- El build oficial se publica en 1–2 horas. Luego la app aparece en https://flathub.org/apps/com.freemidichords.MIDIChords .
- Para verificación por dominio (badge “Verified”): en https://flathub.org/developer-portal puedes enlazar el dominio `freemidichords.com` y colocar el archivo que te indiquen en `https://freemidichords.com/.well-known/org.flathub.VerifiedApps.txt`.

## Actualizar la app en Flathub (después de publicada)

No hace falta un nuevo PR. Editas los archivos en el repo **flathub/com.freemidichords.MIDIChords** (manifest, `python-deps.json`, `pyside6.json`, etc.), subes los cambios y Flathub vuelve a construir. Para nuevas versiones, actualiza el tag en el manifiesto al nuevo release de GitHub.
