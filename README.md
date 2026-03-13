# MIDIChords Monorepo

Repositorio reorganizado para albergar varias versiones de la app con librerías compartidas:

- `apps/desktop`: aplicación de escritorio (Tkinter, Python)
- `apps/web`: aplicación web (Cloudflare Worker + frontend JS)
- `apps/mobile_flutter`: aplicación tablet (Flutter para iOS/Android)
- `midichords`: librería Python común (teoría musical, audio y lógica compartida)
- `assets`: recursos gráficos y muestras de audio compartidas

## Estructura

```text
.
├── apps/
│   ├── desktop/
│   │   └── main.py
│   ├── web/
│   │   ├── worker/
│   │   ├── index.html
│   │   └── static/
│   └── mobile_flutter/
├── midichords/
├── assets/
├── launch.py
├── app.py
└── requirements.txt
```

## Requisitos

- Python 3.10+
- Dependencias desktop: `requirements.txt`
- Node.js + `wrangler` para web local
- Flutter (solo para móvil): 3.38+

## Instalación (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm i -g wrangler
```

## Ejecución unificada

### Desktop

```bash
python launch.py desktop
```

También sigue funcionando:

```bash
python app.py
```

### Web

```bash
python launch.py web --host 127.0.0.1 --port 8000 --reload
```

Abrir: `http://127.0.0.1:8000`

Nota: `launch.py web` usa el mismo Worker de Cloudflare que producción (`wrangler dev`), para evitar diferencias entre local y Cloudflare.

Despliegue a Cloudflare Pages:

```bash
gh workflow run deploy-cloudflare-on-tag.yml --ref main
```

Seguimiento:

```bash
gh run list --workflow deploy-cloudflare-on-tag.yml
gh run watch <run_id>
```

La documentación operativa completa del despliegue web está en `apps/web/README.md`.

## Flutter (tablets iOS/Android)

Proyecto base creado en `apps/mobile_flutter`.

Para ejecutar en emulador Android:

```bash
# 1) Listar emuladores disponibles
flutter emulators

# 2) Arrancar Medium_Tablet con el SDK que contiene su system image
ANDROID_SDK_ROOT=/Users/aortega/.buildozer/android/platform/android-sdk \
ANDROID_HOME=/Users/aortega/.buildozer/android/platform/android-sdk \
/Users/aortega/.buildozer/android/platform/android-sdk/emulator/emulator -avd Medium_Tablet

# 3) Confirmar device id activo (ej: emulator-5554)
flutter devices

# 4) Lanzar la app en ese emulador
python launch.py mobile -d emulator-5554
```

Nota: en esta máquina `Medium_Tablet` usa la imagen en
`/Users/aortega/.buildozer/android/platform/android-sdk/system-images/...`.
Si se intenta arrancar con `/Users/aortega/Library/Android/sdk`, puede fallar
con error de `Broken AVD system path`.

Si ya tienes un único dispositivo Android activo, también funciona:

```bash
python launch.py mobile
```

Opcional, para pasar argumentos a Flutter:

```bash
python launch.py mobile -- -d <device_id>
```

Nota: la app Flutter ya incluye detección, generación de acordes, generación de escalas, metrónomo y afinador.

## Firmar y notarizar macOS (Apple Developer)

Para ejecutar la app de escritorio "normalmente" en macOS (sin avisos de app no confiable), firma con `Developer ID Application` y notariza.

1. Crear perfil de credenciales para notarización (una sola vez):

```bash
xcrun notarytool store-credentials "AC_NOTARY" --apple-id "<TU_APPLE_ID>" --team-id "<TU_TEAM_ID>" --password "<APP_SPECIFIC_PASSWORD>"
```

2. Compilar + firmar + crear DMG + notarizar + staple:

```bash
scripts/sign_notarize_macos.sh \
  --identity "Developer ID Application: Tu Nombre (TEAMID)" \
  --bundle-id "com.tudominio.midichords" \
  --notary-profile "AC_NOTARY"
```

Salida esperada:
- `dist/MIDIChords.app` firmado
- `MIDIChords-macos.dmg` firmado y notarizado

Opciones útiles:
- `--skip-build`: reutiliza `dist/MIDIChords.app` ya generado.
- `--skip-notarize`: solo firma localmente (sin envío a Apple).

## Empaquetar para Mac App Store (MAS)

Para subir a la Mac App Store, no uses DMG con `Developer ID`. Debes generar un `PKG` firmado para App Store con sandbox.

Requisitos previos:

- Certificado `Mac App Distribution`
- Certificado `Mac Installer Distribution`
- Provisioning profile de macOS App Store para tu `Bundle ID`
- Python enlazado con `Tcl/Tk 8.6` para el build de escritorio. No uses Homebrew `python@3.14` con `Tk 9.0` para generar el binario de la Mac App Store.

Script disponible:

```bash
scripts/build_mas_pkg.sh \
  --app-dist-identity "Mac App Distribution: Tu Nombre (TEAMID)" \
  --installer-identity "Mac Installer Distribution: Tu Nombre (TEAMID)" \
  --bundle-id "com.tudominio.midichords" \
  --provisioning-profile "/ruta/a/TuPerfil.provisionprofile" \
  --version "1.0.0" \
  --build-number "1" \
  --allow-network \
  --allow-file-access
```

Salida esperada:

- `dist/MIDIChords.app` firmado para Mac App Store
- `MIDIChords-macos-appstore.pkg` listo para subir a App Store Connect

Notas:

- Entitlements base en `scripts/entitlements.mas.plist`.
- El script genera un archivo temporal: `scripts/entitlements.mas.generated.plist`.
- Si no necesitas red o acceso a archivos seleccionados por usuario, omite `--allow-network` y/o `--allow-file-access`.
- El script también configura automáticamente claves requeridas por App Store:
  - `LSApplicationCategoryType` (por defecto: `public.app-category.music`)
  - `LSMinimumSystemVersion` (por defecto: `12.0`)
  - `CFBundleIconFile` + `AppIcon.icns` generado desde `assets/app_logo.png`
- El script elimina automáticamente atributos `com.apple.quarantine` del `.app` y del `.pkg`.
- El script extrae del provisioning profile:
  - `com.apple.application-identifier`
  - `com.apple.developer.team-identifier`
  y los incluye en los entitlements de firma.
- Si App Review rechaza el binario por `libtcl9tk9.0.dylib` o símbolos no públicos, reconstruye con otro runtime de Python para macOS que use `Tcl/Tk 8.6`.
- El nombre visible en App Store no debe incluir referencias a precio como `Free`; ese cambio se hace en App Store Connect, no en el bundle.
- Si instalas el Python oficial de `python.org` para evitar Homebrew `Tk 9.0`, puedes preparar un entorno limpio con `scripts/bootstrap_mas_build_env.sh`.
- Antes de firmar o subir a App Store, valida el entorno completo con `scripts/validate_macos_release_env.sh`.
- Puedes ajustar estos valores con:
  - `--category-uti`
  - `--min-system-version`
  - `--icon-png` (o `--skip-icon` si ya lo gestionas externamente)
- Para guardar certificados/perfiles/keys dentro del proyecto sin subirlos a git, usa `signing/local/` (documentado en `signing/README.md`).

## VS Code launch

Se añadieron dos configuraciones:

- `Desktop: MIDIChords`
- `Web: MIDIChords`

Archivo: `.vscode/launch.json`

Extensiones recomendadas para este proyecto (archivo `.vscode/extensions.json`):

- `ms-python.python` (soporte Python en VS Code)
- `ms-python.debugpy` (depuración de configuraciones `launch.json`)

## Librerías compartidas

- La lógica musical reutilizable en Python está en `midichords/core/music_service.py`.
- Esta capa expone:
  - detección armónica de acordes
  - generación de acordes
  - generación de escalas
  - listados de patrones
