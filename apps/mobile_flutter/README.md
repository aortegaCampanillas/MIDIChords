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
