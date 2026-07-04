#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/sign_notarize_macos.sh --identity "Developer ID Application: Your Name (TEAMID)" --bundle-id "com.yourcompany.midichords" --notary-profile "AC_NOTARY"

Options:
  --identity        Developer ID Application identity (required)
  --bundle-id       CFBundleIdentifier for MIDIChords.app (required)
  --notary-profile  notarytool keychain profile name (required)
  --app-name        App name (default: MIDIChords)
  --display-name    App display name in Info.plist (default: MIDI Piano & Guitar Chords)
  --icon-png        Source PNG for AppIcon.icns (default: assets/app_logo.png)
  --skip-icon       Do not generate/embed AppIcon.icns
  --skip-build      Do not run PyInstaller build
  --skip-notarize   Do not notarize/staple (sign only)
  -h, --help        Show this help

Notes:
  1) You need Xcode command line tools installed.
  2) You need to create the notary profile once, for example:
     xcrun notarytool store-credentials "AC_NOTARY" --apple-id "<APPLE_ID>" --team-id "<TEAM_ID>" --password "<APP_SPECIFIC_PASSWORD>"
EOF
}

APP_NAME="MIDIChords"
DISPLAY_NAME="MIDI Piano & Guitar Chords"
IDENTITY=""
BUNDLE_ID=""
NOTARY_PROFILE=""
SKIP_BUILD=0
SKIP_NOTARIZE=0
PYTHON_BIN="${PYTHON_BIN:-python3}"
ICON_PNG="assets/app_logo.png"
SKIP_ICON=0

check_supported_tk_runtime() {
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Error: Python runtime not found: $PYTHON_BIN" >&2
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
Error: unsupported Tcl/Tk runtime detected for macOS packaging.
Python: $py_exec
Tcl: $tcl_ver
Tk: $tk_ver

Build the macOS app with a Python runtime linked against Tcl/Tk 8.6.
Avoid Homebrew Python 3.14 + Tk 9.0 for signed macOS releases.
EOF
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --identity)
      IDENTITY="${2:-}"
      shift 2
      ;;
    --bundle-id)
      BUNDLE_ID="${2:-}"
      shift 2
      ;;
    --notary-profile)
      NOTARY_PROFILE="${2:-}"
      shift 2
      ;;
    --app-name)
      APP_NAME="${2:-}"
      shift 2
      ;;
    --display-name)
      DISPLAY_NAME="${2:-}"
      shift 2
      ;;
    --icon-png)
      ICON_PNG="${2:-}"
      shift 2
      ;;
    --skip-icon)
      SKIP_ICON=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --skip-notarize)
      SKIP_NOTARIZE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$IDENTITY" || -z "$BUNDLE_ID" ]]; then
  echo "Error: --identity and --bundle-id are required." >&2
  usage
  exit 1
fi

if [[ "$SKIP_NOTARIZE" -eq 0 && -z "$NOTARY_PROFILE" ]]; then
  echo "Error: --notary-profile is required unless --skip-notarize is set." >&2
  usage
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="$ROOT_DIR/dist/${APP_NAME}.app"
DMG_PATH="$ROOT_DIR/${APP_NAME}-macos.dmg"
DMG_ROOT="$ROOT_DIR/dmg-root"
ICONSET_TMP_DIR=""

if [[ "$ICON_PNG" != /* ]]; then
  ICON_PNG="$ROOT_DIR/$ICON_PNG"
fi

cd "$ROOT_DIR"

if [[ "$SKIP_BUILD" -eq 0 ]]; then
  check_supported_tk_runtime
  echo "Building ${APP_NAME}.app with PyInstaller..."
  pyinstaller --noconfirm --clean --windowed --name "$APP_NAME" --add-data "assets:assets" app.py
fi

if [[ ! -d "$APP_PATH" ]]; then
  echo "Error: app bundle not found: $APP_PATH" >&2
  exit 1
fi

echo "Setting bundle identifier: $BUNDLE_ID"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$APP_PATH/Contents/Info.plist"

echo "Setting display name: $DISPLAY_NAME"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleName string $DISPLAY_NAME" "$APP_PATH/Contents/Info.plist"

if [[ "$SKIP_ICON" -eq 0 ]]; then
  if [[ ! -f "$ICON_PNG" ]]; then
    echo "Error: icon source not found: $ICON_PNG" >&2
    exit 1
  fi
  if ! command -v iconutil >/dev/null 2>&1 || ! command -v sips >/dev/null 2>&1 || ! command -v tiff2icns >/dev/null 2>&1 || ! command -v tiffutil >/dev/null 2>&1; then
    echo "Error: macOS icon generation tools missing." >&2
    exit 1
  fi
  ICONSET_TMP_DIR="$(mktemp -d "$ROOT_DIR/build/iconset-notary.XXXXXX")"
  trap 'if [[ -n "$ICONSET_TMP_DIR" && -d "$ICONSET_TMP_DIR" ]]; then rm -rf "$ICONSET_TMP_DIR"; fi' EXIT
  ICONSET_DIR="$ICONSET_TMP_DIR/AppIcon.iconset"
  mkdir -p "$ICONSET_DIR"
  sips -z 16 16 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
  sips -z 64 64 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null
  mkdir -p "$APP_PATH/Contents/Resources"
  if ! iconutil -c icns "$ICONSET_DIR" -o "$APP_PATH/Contents/Resources/AppIcon.icns" >/dev/null 2>&1; then
    TIFF_TMP_DIR="$ICONSET_TMP_DIR/tiff"
    mkdir -p "$TIFF_TMP_DIR"
    for size in 16 32 128 256 512 1024; do
      sips -s format tiff -z "$size" "$size" "$ICON_PNG" --out "$TIFF_TMP_DIR/${size}.tiff" >/dev/null
    done
    tiffutil -cat "$TIFF_TMP_DIR"/*.tiff -out "$TIFF_TMP_DIR/multi.tiff" >/dev/null
    tiff2icns "$TIFF_TMP_DIR/multi.tiff" >/dev/null
    cp "$TIFF_TMP_DIR/multi.icns" "$APP_PATH/Contents/Resources/AppIcon.icns"
  fi
  /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "$APP_PATH/Contents/Info.plist"
fi

echo "Cleaning bundle before signing..."
# Remove all nested .app bundles inside PySide6 (Assistant, Designer, etc.)
# PyInstaller encodes them as *__dot__app or *.app directories
find "$APP_PATH/Contents/Frameworks/PySide6" -maxdepth 1 -type d \( -name "*.app" -o -name "*__dot__app" \) -exec rm -rf {} + 2>/dev/null || true
# Remove Qt tools and drivers that break notarization
rm -rf "$APP_PATH/Contents/Frameworks/PySide6/Qt/libexec"
rm -rf "$APP_PATH/Contents/Frameworks/PySide6/Qt/plugins/sqldrivers"
# Do NOT remove .dist-info dirs — some packages (mido, etc.) read their own version from them at runtime
find "$APP_PATH" -name 'QtWebEngine*' -exec rm -rf {} + 2>/dev/null || true
find "$APP_PATH" -name 'QtWebView*' -exec rm -rf {} + 2>/dev/null || true
find "$APP_PATH" -name 'QtWebChannel*' -exec rm -rf {} + 2>/dev/null || true

echo "Signing app bundle (inside-out, no --deep)..."
# --deep is unreliable with PyInstaller+PySide6 bundles.
# Sign every Mach-O binary inside-out, then the top-level bundle.

# Remove Qt tools that are not needed and cannot be notarized easily
find "$APP_PATH/Contents/Frameworks/PySide6" -maxdepth 1 -type f \
  \( -name "balsam" -o -name "balsamui" -o -name "lrelease" -o -name "lupdate" \
     -o -name "qmlformat" -o -name "qmllint" -o -name "qmlls" -o -name "qsb" \
     -o -name "svgtoqml" \) -delete 2>/dev/null || true

# Sign all Mach-O binaries inside Frameworks/ (deepest first)
while IFS= read -r f; do
  if file "$f" | grep -qE "Mach-O|executable|dynamically linked|bundle"; then
    codesign --force --options runtime --timestamp --sign "$IDENTITY" "$f" 2>/dev/null || true
  fi
done < <(find "$APP_PATH/Contents/Frameworks" -type f ! -name "*.py" ! -name "*.pyi" ! -name "*.txt" ! -name "*.plist" ! -name "CodeResources" ! -name "*.json" ! -name "*.qml" ! -name "*.qmlc" ! -name "*.png" ! -name "*.icns")

# Sign the main executable
codesign --force --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH/Contents/MacOS/MIDIChords"

# Sign the top-level bundle (no --deep)
codesign --force --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH"

echo "Verifying app signature..."
codesign --verify --verbose=2 "$APP_PATH"

echo "Building DMG..."
# Evitar "Resource busy": desmontar si el volumen ya está montado y crear DMG en temp
hdiutil detach "/Volumes/$APP_NAME" 2>/dev/null || true
rm -rf "$DMG_ROOT" "$DMG_PATH"
mkdir -p "$DMG_ROOT"
cp -R "$APP_PATH" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"
DMG_TMP="${DMG_PATH}.tmp"
rm -f "$DMG_TMP" "$DMG_TMP.dmg"
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_ROOT" -ov -format UDZO "$DMG_TMP"
# hdiutil añade .dmg al path si no termina en .dmg
mv -f "$DMG_TMP.dmg" "$DMG_PATH"

echo "Signing DMG..."
codesign --force --timestamp --sign "$IDENTITY" "$DMG_PATH"
codesign --verify --verbose=2 "$DMG_PATH"

if [[ "$SKIP_NOTARIZE" -eq 0 ]]; then
  echo "Submitting DMG for notarization..."
  xcrun notarytool submit "$DMG_PATH" --keychain-profile "$NOTARY_PROFILE" --wait

  echo "Stapling notarization ticket..."
  xcrun stapler staple "$APP_PATH"
  xcrun stapler staple "$DMG_PATH"
  xcrun stapler validate "$DMG_PATH"
fi

echo
echo "Done."
echo "App: $APP_PATH"
echo "DMG: $DMG_PATH"
