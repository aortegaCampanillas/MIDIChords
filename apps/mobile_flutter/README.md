# MIDIChords Mobile (Flutter)

Base Flutter para tablets iOS/Android del proyecto MIDIChords.

## Estado

- Estructura de navegación por módulos:
  - Detección
  - Generación de acordes
  - Escalas
  - Metrónomo
  - Afinador
- Integración con backend Python web:
  - `/api/meta`
  - `/api/detect`
  - `/api/generate/chord`
  - `/api/generate/scale`
- Detección con teclado táctil en pantalla + entrada manual de notas MIDI.
- Metrónomo nativo implementado (BPM, compás, start/stop, pulso visual).
- Afinador nativo implementado (captura de micrófono + estimación de pitch + cents).

## Ejecutar

Arranque recomendado en emulador Android:

```bash
# Desde la raíz del repo
flutter emulators
flutter emulators --launch Medium_Tablet
flutter devices
python launch.py mobile -d emulator-5554
```

Si solo hay un dispositivo Android activo, también puedes usar:

```bash
python launch.py mobile
```

Puedes ejecutar Flutter directamente desde este directorio:

```bash
cd apps/mobile_flutter
flutter run -d emulator-5554
```

Comando unificado (sin elegir device explícitamente):

```bash
python launch.py mobile
```

Para ejecutar directamente en iPad (arranca backend web en LAN y configura la app móvil con la URL automática):

```bash
python launch.py mobile-ipad --device "<ID_O_NOMBRE_IPAD>"
```

Puedes listar dispositivos con:

```bash
flutter devices
```

También puedes usar el selector interactivo del repo para lanzar un simulador/emulador desde macOS:

```bash
python scripts/select_mobile_emulator.py
```

Por defecto, en iOS solo muestra los simuladores recomendados y documentados en este repo. En el menú interactivo aparece la opción `m` para mostrar más dispositivos iOS y `d` para cambiar a la lista de dispositivos físicos móviles y lanzar la app directamente en uno de ellos. Para verlos directamente desde línea de comandos:

```bash
python scripts/select_mobile_emulator.py --all-ios
```

Solo listar:

```bash
python scripts/select_mobile_emulator.py --list
python scripts/select_mobile_emulator.py --platform ios --list
python scripts/select_mobile_emulator.py --platform ios --all-ios --list
python scripts/select_mobile_emulator.py --platform android --list
python scripts/select_mobile_emulator.py --devices
python scripts/select_mobile_emulator.py --devices --list
```

## Dispositivos y emuladores de prueba

Inventario verificado en esta máquina el **2026-03-20**.

### Dispositivos físicos

| Tipo | Nombre detectado | Identificador | Estado |
|------|-------------------|---------------|--------|
| iPhone | iPhone de Antonio (2) | `00008101-0014452401F0001E` | Detectado por `flutter devices` (wireless) |
| iPad | iPad de Antonio | `00008101-0011294A1EA3A01E` | Detectado por `flutter devices` (wireless) |
| Tablet Android | Samsung Galaxy Tab S10 FE+ (`SM_X620`) | `R52YA01ZP4B` | Detectado por `adb devices -l` (USB) |
| Teléfono Android | Pendiente de conectar | `TODO` | Completar al conectarlo |

Notas:

- El id Android físico útil para `flutter run -d ...` suele coincidir con el serial de `adb`.
- Si un dispositivo iOS aparece por Wi-Fi, Flutter permite usar directamente ese identificador con `-d`.

### Emuladores / simuladores disponibles

| Plataforma | Tipo | Nombre | Identificador | Cómo se usa |
|-----------|------|--------|---------------|-------------|
| iOS | Genérico Flutter | iOS Simulator | `apple_ios_simulator` | Arranca la app en el simulador iOS por defecto |
| iOS | Teléfono recomendado | iPhone 17 (iOS 26.2) | `F2AEE231-DF98-4373-9BA8-6725D7355ADF` | Boot explícito con `xcrun simctl boot ...` |
| iOS | Tablet recomendada | iPad Air 11-inch (M3) (iOS 26.2) | `B3E6EBB0-F8E5-4221-A3F6-CAE536B665D8` | Boot explícito con `xcrun simctl boot ...` |
| Android | Genérico Flutter / AVD | Medium Tablet | `Medium_Tablet` | `flutter emulators --launch Medium_Tablet` |
| Android | Dispositivo ya arrancado | Pixel Tablet | `emulator-5554` | Id visible una vez el emulador está en ejecución |
| Android | Teléfono | No existe AVD creado ahora mismo | `TODO` | Crear AVD y documentar su nombre/id |

### Cómo lanzar cada emulador recomendado

#### iOS teléfono

```bash
open -a Simulator
xcrun simctl boot F2AEE231-DF98-4373-9BA8-6725D7355ADF
python launch.py mobile -d F2AEE231-DF98-4373-9BA8-6725D7355ADF
```

Alternativa rápida si te vale el simulador iOS por defecto:

```bash
python launch.py mobile -d apple_ios_simulator
```

#### iOS tablet

```bash
open -a Simulator
xcrun simctl boot B3E6EBB0-F8E5-4221-A3F6-CAE536B665D8
python launch.py mobile -d B3E6EBB0-F8E5-4221-A3F6-CAE536B665D8
```

Si prefieres el flujo preparado para iPad con backend web en LAN:

```bash
python launch.py mobile-ipad --device B3E6EBB0-F8E5-4221-A3F6-CAE536B665D8
```

#### Android tablet

Antes de lanzar emuladores Android fuera de Android Studio, exporta el SDK:

```bash
export ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export PATH="$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$PATH"
```

Comprobación rápida:

```bash
echo "$ANDROID_SDK_ROOT"
$ANDROID_SDK_ROOT/emulator/emulator -list-avds
```

En esta máquina, el AVD `Medium_Tablet` está creado pero actualmente apunta a esta imagen:

```text
system-images/android-35/google_apis_playstore_tablet/arm64-v8a/
```

Si esa carpeta no existe, el emulador falla aunque `flutter emulators` liste el AVD. El error típico es:

```text
Cannot find AVD system path. Please define ANDROID_SDK_ROOT
```

o, después de exportar la variable, un fallo equivalente por imagen de sistema ausente.

Primero asegúrate de que la imagen exista en el SDK. Puedes instalarla desde Android Studio o por línea de comandos:

```bash
sdkmanager "system-images;android-35;google_apis_playstore_tablet;arm64-v8a"
```

Después:

```bash
flutter emulators --launch Medium_Tablet
flutter devices
python launch.py mobile -d emulator-5554
```

También puedes arrancarlo directamente con el binario del SDK:

```bash
$HOME/Library/Android/sdk/emulator/emulator -avd Medium_Tablet
```

Si quieres forzar el SDK en una sola línea:

```bash
ANDROID_SDK_ROOT="$HOME/Library/Android/sdk" \
ANDROID_HOME="$HOME/Library/Android/sdk" \
"$HOME/Library/Android/sdk/emulator/emulator" -avd Medium_Tablet
```

#### Android teléfono

Ahora mismo **no hay AVD de teléfono Android creado** en esta máquina. Cuando se cree uno, documentar:

```bash
flutter emulators
flutter emulators --launch <ID_AVD_TELEFONO>
flutter devices
python launch.py mobile -d <ID_FLUTTER_O_EMULATOR-XXXX>
```

### Comandos de inventario útiles

```bash
python scripts/select_mobile_emulator.py --list
python scripts/select_mobile_emulator.py --all-ios --list
flutter devices
flutter emulators
xcrun simctl list devices available
$HOME/Library/Android/sdk/platform-tools/adb devices -l
$HOME/Library/Android/sdk/emulator/emulator -list-avds
```

### Pendientes cuando conectes el teléfono Android

1. Ejecutar `adb devices -l`.
2. Anotar el serial real del teléfono Android.
3. Sustituir `TODO` en esta guía.

## Nota de arquitectura

El objetivo es compartir lógica musical a través del backend Python (`apps/web` + `midichords/core/music_service.py`) y consumirla desde Flutter por HTTP.

## Publicar en iOS (App Store Connect)

Esta app se publica subiendo una **IPA** a App Store Connect (por ejemplo con **Transporter**).

### 1) Subir versión/build

En Flutter, el build number de iOS sale de `pubspec.yaml` (campo `version:`):

- `build-name` → `CFBundleShortVersionString`
- `build-number` → `CFBundleVersion`

Ejemplo:

- `version: 1.0.1+3` → App Store Connect verá **1.0.1 (3)**.

### 2) Generar la IPA

Desde este directorio:

```bash
flutter pub get
flutter build ipa --release
```

Salida típica:

- `build/ios/archive/Runner.xcarchive`
- `build/ios/ipa/*.ipa`

### 3) Subir a Apple (Transporter)

1. Abre Transporter.
2. Arrastra el `.ipa` generado (en `build/ios/ipa/`).
3. Sube y espera a que App Store Connect lo procese.

### 4) Documentar la subida (obligatorio)

- Actualiza `CHANGELOG.md` en **Unreleased** con los cambios que entran en la próxima subida.
- Indica la build publicada (ej: **iOS 1.0.1 (3)**) cuando corresponda.
