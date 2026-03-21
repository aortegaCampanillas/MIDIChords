#!/usr/bin/env bash
# Genera MIDIChords.app + DMG para probar en un Mac local (no Mac App Store).
# No requiere certificado "Developer ID". Opcional: firma ad hoc (-) para menos fricción al abrir.
set -euo pipefail

usage() {
  cat <<'EOF'
Uso:
  scripts/build_mac_test_dmg.sh [opciones]

Opciones:
  --skip-build       No ejecutar PyInstaller (usa dist/MIDIChords.app existente)
  --no-ad-hoc        No firmar con identidad ad hoc (totalmente sin firmar)
  --bundle-id ID     CFBundleIdentifier (default: com.midichords.desktop.localtest)
  --app-name NAME    Nombre del bundle (default: MIDIChords)
  --output-dmg PATH  Ruta del .dmg (default: <repo>/MIDIChords-macos-test.dmg)
  --strict-tk        Exigir Tcl/Tk 8.6 en el Python de build (como el script de firma)
  -h, --help         Ayuda

Salida:
  dist/<AppName>.app
  MIDIChords-macos-test.dmg (o --output-dmg)

Primer arranque en macOS: si Gatekeeper avisa, clic derecho en la app > Abrir.
Para ver errores de consola: dist/MIDIChords.app/Contents/MacOS/MIDIChords
EOF
}

APP_NAME="MIDIChords"
DISPLAY_NAME="MIDI Piano & Guitar Chords"
BUNDLE_ID="com.midichords.desktop.localtest"
SKIP_BUILD=0
AD_HOC_SIGN=1
OUTPUT_DMG=""
STRICT_TK=0
PYTHON_BIN="${PYTHON_BIN:-python3}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DMG_ROOT="$ROOT_DIR/dmg-root-test"

check_supported_tk_runtime() {
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: Python no encontrado: $PYTHON_BIN" >&2
    exit 1
  fi
  local runtime_info py_exec tcl_ver tk_ver
  runtime_info="$("$PYTHON_BIN" - <<'PY'
import sys
import tkinter
print(f"{sys.executable}|{tkinter.TclVersion}|{tkinter.TkVersion}")
PY
)"
  IFS='|' read -r py_exec tcl_ver tk_ver <<<"$runtime_info"
  if [[ "${tcl_ver%%.*}" -ge 9 || "${tk_ver%%.*}" -ge 9 ]]; then
    cat >&2 <<EOF
Error: Tcl/Tk >= 9 en este Python ($py_exec). Usa python.org 3.12/3.13 o pasa sin --strict-tk.
EOF
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-build) SKIP_BUILD=1; shift ;;
    --no-ad-hoc) AD_HOC_SIGN=0; shift ;;
    --bundle-id) BUNDLE_ID="${2:-}"; shift 2 ;;
    --app-name) APP_NAME="${2:-}"; shift 2 ;;
    --output-dmg) OUTPUT_DMG="${2:-}"; shift 2 ;;
    --strict-tk) STRICT_TK=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opción desconocida: $1" >&2; usage; exit 1 ;;
  esac
done

APP_PATH="$ROOT_DIR/dist/${APP_NAME}.app"
if [[ -z "$OUTPUT_DMG" ]]; then
  OUTPUT_DMG="$ROOT_DIR/${APP_NAME}-macos-test.dmg"
else
  OUTPUT_DMG="$(cd "$(dirname "$OUTPUT_DMG")" && pwd)/$(basename "$OUTPUT_DMG")"
fi

if [[ "$SKIP_BUILD" -eq 0 && -d "$APP_PATH" && ! -w "$APP_PATH" ]]; then
  echo "Error: $APP_PATH existe y no es escribible (p. ej. propiedad root)." >&2
  echo "  sudo rm -rf \"$APP_PATH\"   o   ./scripts/build_mac_test_dmg.sh --app-name MIDIChordsTest" >&2
  exit 1
fi

cd "$ROOT_DIR"

if [[ "$STRICT_TK" -eq 1 ]]; then
  check_supported_tk_runtime
fi

if [[ "$SKIP_BUILD" -eq 0 ]]; then
  if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Error: pyinstaller no está en PATH. Prueba: pip install pyinstaller" >&2
    exit 1
  fi
  echo "PyInstaller → ${APP_NAME}.app ..."
  pyinstaller --noconfirm --clean --windowed --name "$APP_NAME" --add-data "assets:assets" app.py
fi

if [[ ! -d "$APP_PATH" ]]; then
  echo "Error: no existe $APP_PATH" >&2
  exit 1
fi

echo "Info.plist (bundle id de prueba, no MAS)..."
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleName string $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist"

if [[ "$AD_HOC_SIGN" -eq 1 ]]; then
  echo "Firma ad hoc (identidad '-') — solo para pruebas locales..."
  codesign --force --deep -s - "$APP_PATH"
  codesign --verify --verbose=2 "$APP_PATH" 2>/dev/null || true
fi

echo "Creando DMG..."
hdiutil detach "/Volumes/$APP_NAME" 2>/dev/null || true
rm -rf "$DMG_ROOT" "$OUTPUT_DMG"
mkdir -p "$DMG_ROOT"
cp -R "$APP_PATH" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"
DMG_TMP="${OUTPUT_DMG%.dmg}.tmp"
rm -f "$DMG_TMP" "$DMG_TMP.dmg"
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_ROOT" -ov -format UDZO "$DMG_TMP"
mv -f "$DMG_TMP.dmg" "$OUTPUT_DMG"
rm -rf "$DMG_ROOT"

echo
echo "Listo."
echo "  App:  $APP_PATH"
echo "  DMG:  $OUTPUT_DMG"
echo "Monta el DMG, arrastra la app a Aplicaciones (o ejecuta el binario desde Terminal para ver errores)."
