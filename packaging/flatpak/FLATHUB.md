# Publicar MIDIChords en Flathub

## Requisitos previos

1. **Tag de release** en GitHub (p. ej. `v1.0.0`), para que el manifiesto apunte a código estable.
2. **Cuenta en GitHub** con 2FA activada (Flathub lo exige para darte acceso al repo de la app).
3. **Dominio** `freemidichords.com` accesible por HTTPS (para verificación opcional en Flathub).

## Pasos para enviar el PR a Flathub

### 1. Crear un release en GitHub

- En https://github.com/aortegaCampanillas/MIDIChords/releases → "Create a new release".
- Tag: `v1.0.0` (o la versión que uses).
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

En el repo `flathub` crea la carpeta de la app y copia los archivos necesarios:

```bash
mkdir -p com.freemidichords.MIDIChords
cp /ruta/a/MIDIChords/packaging/flatpak/com.freemidichords.MIDIChords.flathub.yml \
   com.freemidichords.MIDIChords/com.freemidichords.MIDIChords.yml
cp /ruta/a/MIDIChords/packaging/flatpak/flathub.json \
   com.freemidichords.MIDIChords/
cp /ruta/a/MIDIChords/packaging/flatpak/python-deps.json \
   com.freemidichords.MIDIChords/
```

**Importante:** En `com.freemidichords.MIDIChords.yml` (el que usa Flathub) el tag del módulo `midichords-launcher` debe coincidir con el release que creaste (p. ej. `v1.0.0`). Ábrelo y, si hace falta, cambia la ref/tag al tag real.

### 4. Commit y PR

```bash
git add com.freemidichords.MIDIChords/
git commit -m "Add com.freemidichords.MIDIChords"
git push origin add-com.freemidichords.MIDIChords
```

En GitHub: abre un **Pull Request** contra la rama **`new-pr`** del repo `flathub/flathub` (no contra `master`).

- Título del PR: **Add com.freemidichords.MIDIChords**

### 5. Comprobar build y linter (opcional pero recomendado)

En tu máquina, con el manifest que está en `com.freemidichords.MIDIChords/`:

```bash
flatpak install -y flathub org.flatpak.Builder
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest com.freemidichords.MIDIChords/com.freemidichords.MIDIChords.yml
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

No hace falta un nuevo PR. Editas los archivos en el repo **flathub/com.freemidichords.MIDIChords** (manifest, `python-deps.json`, etc.), subes los cambios y Flathub vuelve a construir. Para nuevas versiones, actualiza el tag en el manifiesto al nuevo release de GitHub.
