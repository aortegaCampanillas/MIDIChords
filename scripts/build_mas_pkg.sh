#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Build and sign a Mac App Store package from the PyInstaller desktop app.

Usage:
  scripts/build_mas_pkg.sh \
    --app-dist-identity "Mac App Distribution: Your Name (TEAMID)" \
    --installer-identity "Mac Installer Distribution: Your Name (TEAMID)" \
    --bundle-id "com.yourcompany.midichords" \
    --provisioning-profile "/path/to/profile.provisionprofile"

Options:
  --app-dist-identity     macOS App Store signing identity for .app (required)
  --installer-identity    Installer signing identity for .pkg (required)
  --bundle-id             CFBundleIdentifier for MIDIChords.app (required)
  --provisioning-profile  Path to provisioning profile for this App ID (required)
  --app-name              App bundle name (default: MIDIChords)
  --display-name          App display name in Info.plist (default: MIDI Piano & Guitar Chords)
  --version               CFBundleShortVersionString (optional)
  --build-number          CFBundleVersion (optional)
  --entrypoint            Python entrypoint for PyInstaller (default: app.py)
  --output-pkg            Output package path (default: <APP_NAME>-macos-appstore.pkg)
  --category-uti          LSApplicationCategoryType (default: public.app-category.music)
  --min-system-version    LSMinimumSystemVersion (default: 12.0)
  --icon-png              Source PNG for AppIcon.icns (default: assets/app_logo.png)
  --skip-icon             Do not generate/embed AppIcon.icns
  --allow-network         Add com.apple.security.network.client entitlement
  --allow-file-access     Add user-selected read/write entitlement
  --skip-build            Do not run PyInstaller build
  --skip-store-validation Skip installer -store validation (recommended: often hangs; Transporter validates on upload)
  --skip-tk-check         No comprobar Tcl/Tk 8.6 (UI Qt; Python Homebrew 3.14+ suele traer Tk 9)
  -h, --help              Show this help

Notes:
  - This script is for Mac App Store submission, not Developer ID distribution.
  - Upload the resulting .pkg with Transporter or Xcode Organizer.
  - PyInstaller se invoca como: PYTHON_BIN -m PyInstaller (por defecto PYTHON_BIN=python3).
    Instala con: PYTHON_BIN -m pip install pyinstaller pyinstaller-hooks-contrib (y requirements del proyecto).
EOF
}

APP_NAME="MIDIChords"
DISPLAY_NAME="MIDI Piano & Guitar Chords"
ENTRYPOINT="app.py"
APP_DIST_IDENTITY=""
INSTALLER_IDENTITY=""
BUNDLE_ID=""
PROVISIONING_PROFILE=""
VERSION=""
BUILD_NUMBER=""
OUTPUT_PKG=""
CATEGORY_UTI="public.app-category.music"
MIN_SYSTEM_VERSION="12.0"
ICON_PNG="assets/app_logo.png"
SKIP_ICON=0
ALLOW_NETWORK=0
ALLOW_FILE_ACCESS=0
SKIP_BUILD=0
SKIP_STORE_VALIDATION=0
SKIP_TK_CHECK=0
PYTHON_BIN="${PYTHON_BIN:-python3}"

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
Avoid Homebrew Python 3.14 + Tk 9.0 for App Store submissions.
EOF
    exit 1
  fi
}

clear_quarantine_attrs() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    return 0
  fi
  xattr -cr "$path" 2>/dev/null || true
  xattr -dr com.apple.quarantine "$path" 2>/dev/null || true
}

# Tras borrar frameworks Qt (WebEngine, etc.) pueden quedar enlaces simbólicos rotos.
# codesign --verify --deep --strict entonces falla con "No such file or directory"
# mostrando solo la ruta del .app (mensaje poco claro).
remove_dead_symlinks_under() {
  local root="$1"
  [[ -d "$root" ]] || return 0
  find "$root" -type l ! -exec test -e {} \; -delete 2>/dev/null || true
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-dist-identity)
      APP_DIST_IDENTITY="${2:-}"
      shift 2
      ;;
    --installer-identity)
      INSTALLER_IDENTITY="${2:-}"
      shift 2
      ;;
    --bundle-id)
      BUNDLE_ID="${2:-}"
      shift 2
      ;;
    --provisioning-profile)
      PROVISIONING_PROFILE="${2:-}"
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
    --version)
      VERSION="${2:-}"
      shift 2
      ;;
    --build-number)
      BUILD_NUMBER="${2:-}"
      shift 2
      ;;
    --entrypoint)
      ENTRYPOINT="${2:-}"
      shift 2
      ;;
    --output-pkg)
      OUTPUT_PKG="${2:-}"
      shift 2
      ;;
    --category-uti)
      CATEGORY_UTI="${2:-}"
      shift 2
      ;;
    --min-system-version)
      MIN_SYSTEM_VERSION="${2:-}"
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
    --allow-network)
      ALLOW_NETWORK=1
      shift
      ;;
    --allow-file-access)
      ALLOW_FILE_ACCESS=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --skip-store-validation)
      SKIP_STORE_VALIDATION=1
      shift
      ;;
    --skip-tk-check)
      SKIP_TK_CHECK=1
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

if [[ -z "$APP_DIST_IDENTITY" || -z "$INSTALLER_IDENTITY" || -z "$BUNDLE_ID" || -z "$PROVISIONING_PROFILE" ]]; then
  echo "Error: --app-dist-identity, --installer-identity, --bundle-id and --provisioning-profile are required." >&2
  usage
  exit 1
fi

if [[ ! -f "$PROVISIONING_PROFILE" ]]; then
  echo "Error: provisioning profile not found: $PROVISIONING_PROFILE" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="$ROOT_DIR/dist/${APP_NAME}.app"
ENTITLEMENTS_PATH="$ROOT_DIR/scripts/entitlements.mas.generated.plist"
ICONSET_TMP_DIR=""
PROFILE_PLIST_TMP=""
PROFILE_APP_IDENTIFIER=""
PROFILE_TEAM_ID=""

if [[ -z "$OUTPUT_PKG" ]]; then
  OUTPUT_PKG="$ROOT_DIR/${APP_NAME}-macos-appstore.pkg"
fi

if [[ "$ICON_PNG" != /* ]]; then
  ICON_PNG="$ROOT_DIR/$ICON_PNG"
fi

mkdir -p "$ROOT_DIR/build"
PROFILE_PLIST_TMP="$(mktemp "$ROOT_DIR/build/profile.XXXXXX.plist")"
trap 'if [[ -n "$ICONSET_TMP_DIR" && -d "$ICONSET_TMP_DIR" ]]; then rm -rf "$ICONSET_TMP_DIR"; fi; if [[ -n "$PROFILE_PLIST_TMP" && -f "$PROFILE_PLIST_TMP" ]]; then rm -f "$PROFILE_PLIST_TMP"; fi' EXIT

cd "$ROOT_DIR"

if [[ "$SKIP_BUILD" -eq 0 ]]; then
  if [[ "$SKIP_TK_CHECK" -eq 0 ]]; then
    check_supported_tk_runtime
  else
    echo "Skipping Tcl/Tk runtime check (--skip-tk-check). Using: $PYTHON_BIN"
  fi
  echo "Removing quarantine attributes from source assets before packaging..."
  clear_quarantine_attrs "$ROOT_DIR/assets"
  clear_quarantine_attrs "$ICON_PNG"
  echo "Building ${APP_NAME}.app with PyInstaller ($PYTHON_BIN -m PyInstaller)..."
  if ! "$PYTHON_BIN" -m PyInstaller --version >/dev/null 2>&1; then
    echo "Error: PyInstaller no está instalado para: $PYTHON_BIN" >&2
    echo "  Prueba: $PYTHON_BIN -m pip install pyinstaller pyinstaller-hooks-contrib" >&2
    echo "  O define PYTHON_BIN en signing/local/mas.env apuntando a un venv con dependencias (ver scripts/bootstrap_mas_build_env.sh)." >&2
    exit 1
  fi
  # --collect-all PySide6: a veces PyInstaller no vuelca Qt (aviso «not a package»);
  # --collect-submodules + hooks-contrib ayudan; mas_embed_pyside6_bundle.py cubre el hueco.
  # Qt WebEngine: sub-app QtWebEngineProcess.app firmada sin perfil MAS → TestFlight 90885.
  # MIDIChords no usa WebEngine; se excluye del análisis y se eliminan restos tras el build.
  "$PYTHON_BIN" -m PyInstaller --noconfirm --clean --windowed --name "$APP_NAME" \
    --collect-all PySide6 \
    --collect-submodules PySide6 \
    --exclude-module PySide6.QtWebEngineCore \
    --exclude-module PySide6.QtWebEngineWidgets \
    --exclude-module PySide6.QtWebEngineQuick \
    --exclude-module PySide6.QtWebView \
    --exclude-module PySide6.QtWebChannel \
    --exclude-module PySide6.QtSql \
    --add-data "assets:assets" \
    "$ENTRYPOINT"
fi

if [[ ! -d "$APP_PATH" ]]; then
  echo "Error: app bundle not found: $APP_PATH" >&2
  exit 1
fi

echo "Comprobando que el bundle incluye el plugin Qt (libqcocoa.dylib)…"
if ! "$PYTHON_BIN" "$ROOT_DIR/scripts/mas_embed_pyside6_bundle.py" "$APP_PATH"; then
  echo "Error: el .app no contiene libqcocoa.dylib; TestFlight/sandbox cerrará la app al abrir." >&2
  echo "  Instala en el venv MAS: pip install -r requirements.txt pyinstaller pyinstaller-hooks-contrib" >&2
  echo "  y vuelve a ejecutar este script (sin --skip-build salvo que ya hayas arreglado el .app)." >&2
  exit 1
fi

# PySide6 trae Assistant/Designer/Linguist como .app; PyInstaller los copia a Frameworks y/o
# Resources; symlinks rotos en esos sub-bundles hacen fallar codesign --verify --deep --strict.
for _pyside_root in "$APP_PATH/Contents/Frameworks/PySide6" "$APP_PATH/Contents/Resources/PySide6"; do
  if [[ -d "$_pyside_root" ]]; then
    echo "Quitando herramientas Qt anidadas (Assistant/Designer/Linguist) en ${_pyside_root##*/}…"
    for _tool in Assistant Designer Linguist; do
      rm -rf "$_pyside_root/${_tool}.app" "$_pyside_root/${_tool}__dot__app"
    done
  fi
done

# Cualquier resto de WebEngine (p. ej. si el hook volcó frameworks antes del exclude).
echo "Quitando Qt WebEngine / WebView / WebChannel del bundle (TestFlight 90885)…"
find "$APP_PATH/Contents/Frameworks" "$APP_PATH/Contents/Resources" \
  -type d \( -name 'QtWebEngine*.framework' -o -name 'QtWebView*.framework' -o -name 'QtWebChannel*.framework' \) \
  2>/dev/null | while IFS= read -r _fw; do rm -rf "$_fw"; done
find "$APP_PATH/Contents/Frameworks" "$APP_PATH/Contents/Resources" \
  -type d -name 'QtWebEngineProcess.app' 2>/dev/null | while IFS= read -r _hap; do rm -rf "$_hap"; done
for _pyside_root in "$APP_PATH/Contents/Frameworks/PySide6" "$APP_PATH/Contents/Resources/PySide6"; do
  if [[ -d "$_pyside_root" ]]; then
    rm -f "$_pyside_root"/QtWebEngine*.abi3.so "$_pyside_root"/QtWebEngine*.pyi 2>/dev/null || true
    rm -f "$_pyside_root"/QtWebView*.abi3.so "$_pyside_root"/QtWebView*.pyi 2>/dev/null || true
    rm -f "$_pyside_root"/QtWebChannel*.abi3.so "$_pyside_root"/QtWebChannel*.pyi 2>/dev/null || true
  fi
done

# TestFlight 90885: ejecutables Mach-O firmados (lupdate, rcc, uic, qmllint, …) y libexec de Qt
# tienen Identifier propio pero no perfil MAS embebido como el .app principal.
echo "Quitando Qt libexec y herramientas CLI en raíz PySide6 (90885)…"
for _root in "$APP_PATH/Contents/Frameworks/PySide6" "$APP_PATH/Contents/Resources/PySide6"; do
  if [[ -d "$_root" ]]; then
    rm -rf "$_root/Qt/libexec"
    find "$_root" -maxdepth 1 -type f 2>/dev/null | while IFS= read -r _f; do
      case "$(file -b "$_f" 2>/dev/null)" in
        *Mach-O*executable*) rm -f "$_f" ;;
      esac
    done
  fi
done
for _plugins in "$APP_PATH/Contents/Frameworks/PySide6/Qt/plugins" "$APP_PATH/Contents/Resources/PySide6/Qt/plugins"; do
  if [[ -d "$_plugins/webview" ]]; then
    rm -rf "$_plugins/webview"
  fi
done

# Guideline 2.5.1: libqsqlodbc.dylib (sqldrivers) enlaza ODBC; Apple lo rechaza como API no pública.
# MIDIChords no usa QtSql; se elimina toda la carpeta sqldrivers por si collect-all la volcó igualmente.
echo "Quitando plugins Qt SQL (sqldrivers)…"
find "$APP_PATH/Contents/Frameworks" "$APP_PATH/Contents/Resources" \
  -type d -path '*/Qt/plugins/sqldrivers' 2>/dev/null | while IFS= read -r _sd; do rm -rf "$_sd"; done

remove_dead_symlinks_under "$APP_PATH"

INFO_PLIST="$APP_PATH/Contents/Info.plist"

echo "Setting bundle identifier: $BUNDLE_ID"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$INFO_PLIST"

echo "Setting display name: $DISPLAY_NAME"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $DISPLAY_NAME" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $DISPLAY_NAME" "$INFO_PLIST"
/usr/libexec/PlistBuddy -c "Set :CFBundleName $DISPLAY_NAME" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleName string $DISPLAY_NAME" "$INFO_PLIST"

if [[ -n "$VERSION" ]]; then
  echo "Setting marketing version: $VERSION"
  /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$INFO_PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$INFO_PLIST"
fi

if [[ -n "$BUILD_NUMBER" ]]; then
  echo "Setting build number: $BUILD_NUMBER"
  /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $BUILD_NUMBER" "$INFO_PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $BUILD_NUMBER" "$INFO_PLIST"
fi

echo "Setting NSMicrophoneUsageDescription..."
/usr/libexec/PlistBuddy -c "Set :NSMicrophoneUsageDescription This app uses the microphone for the chord and note tuner." "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string This app uses the microphone for the chord and note tuner." "$INFO_PLIST"

echo "Setting App Store category: $CATEGORY_UTI"
/usr/libexec/PlistBuddy -c "Set :LSApplicationCategoryType $CATEGORY_UTI" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :LSApplicationCategoryType string $CATEGORY_UTI" "$INFO_PLIST"

echo "Setting minimum macOS version: $MIN_SYSTEM_VERSION"
/usr/libexec/PlistBuddy -c "Set :LSMinimumSystemVersion $MIN_SYSTEM_VERSION" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :LSMinimumSystemVersion string $MIN_SYSTEM_VERSION" "$INFO_PLIST"

if [[ "$SKIP_ICON" -eq 0 ]]; then
  if [[ ! -f "$ICON_PNG" ]]; then
    echo "Error: icon source not found: $ICON_PNG" >&2
    exit 1
  fi
  if ! command -v iconutil >/dev/null 2>&1; then
    echo "Error: iconutil not found. Install Xcode command line tools." >&2
    exit 1
  fi
  if ! command -v sips >/dev/null 2>&1; then
    echo "Error: sips not found on this macOS system." >&2
    exit 1
  fi
  if ! command -v tiff2icns >/dev/null 2>&1; then
    echo "Error: tiff2icns not found on this macOS system." >&2
    exit 1
  fi
  if ! command -v tiffutil >/dev/null 2>&1; then
    echo "Error: tiffutil not found on this macOS system." >&2
    exit 1
  fi

  mkdir -p "$ROOT_DIR/build"
  ICONSET_TMP_DIR="$(mktemp -d "$ROOT_DIR/build/iconset.XXXXXX")"
  ICONSET_DIR="$ICONSET_TMP_DIR/AppIcon.iconset"
  mkdir -p "$ICONSET_DIR"

  echo "Generating AppIcon.icns from: $ICON_PNG"
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
    echo "iconutil failed; falling back to tiff2icns..."
    TIFF_TMP_DIR="$ICONSET_TMP_DIR/tiff"
    mkdir -p "$TIFF_TMP_DIR"
    for size in 16 32 128 256 512 1024; do
      sips -s format tiff -z "$size" "$size" "$ICON_PNG" --out "$TIFF_TMP_DIR/${size}.tiff" >/dev/null
    done
    tiffutil -cat "$TIFF_TMP_DIR"/*.tiff -out "$TIFF_TMP_DIR/multi.tiff" >/dev/null
    tiff2icns "$TIFF_TMP_DIR/multi.tiff" >/dev/null
    cp "$TIFF_TMP_DIR/multi.icns" "$APP_PATH/Contents/Resources/AppIcon.icns"
  fi
  /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "$INFO_PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "$INFO_PLIST"
fi

echo "Embedding provisioning profile..."
cp "$PROVISIONING_PROFILE" "$APP_PATH/Contents/embedded.provisionprofile"

echo "Removing quarantine attributes from packaged resources..."
clear_quarantine_attrs "$APP_PATH/Contents/Resources"
clear_quarantine_attrs "$APP_PATH/Contents/Frameworks"
clear_quarantine_attrs "$APP_PATH/Contents/embedded.provisionprofile"

echo "Reading provisioning profile entitlements..."
if ! security cms -D -i "$PROVISIONING_PROFILE" > "$PROFILE_PLIST_TMP" 2>/dev/null; then
  if ! openssl smime -inform der -verify -noverify -in "$PROVISIONING_PROFILE" -out "$PROFILE_PLIST_TMP" >/dev/null 2>&1; then
    echo "Error: unable to decode provisioning profile: $PROVISIONING_PROFILE" >&2
    exit 1
  fi
fi
PROFILE_APP_IDENTIFIER="$(/usr/libexec/PlistBuddy -c "Print :Entitlements:com.apple.application-identifier" "$PROFILE_PLIST_TMP" 2>/dev/null || true)"
if [[ -z "$PROFILE_APP_IDENTIFIER" ]]; then
  PROFILE_APP_IDENTIFIER="$(/usr/libexec/PlistBuddy -c "Print :ApplicationIdentifierPrefix:0" "$PROFILE_PLIST_TMP" 2>/dev/null || true).$BUNDLE_ID"
fi
PROFILE_TEAM_ID="$(/usr/libexec/PlistBuddy -c "Print :Entitlements:com.apple.developer.team-identifier" "$PROFILE_PLIST_TMP" 2>/dev/null || true)"
if [[ -z "$PROFILE_TEAM_ID" ]]; then
  PROFILE_TEAM_ID="$(/usr/libexec/PlistBuddy -c "Print :TeamIdentifier:0" "$PROFILE_PLIST_TMP" 2>/dev/null || true)"
fi
if [[ -z "$PROFILE_APP_IDENTIFIER" || -z "$PROFILE_TEAM_ID" ]]; then
  echo "Error: unable to extract application/team identifier from provisioning profile." >&2
  exit 1
fi

echo "Generating App Sandbox entitlements..."
cat > "$ENTITLEMENTS_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>com.apple.application-identifier</key>
  <string>$PROFILE_APP_IDENTIFIER</string>
  <key>com.apple.developer.team-identifier</key>
  <string>$PROFILE_TEAM_ID</string>
  <key>com.apple.security.app-sandbox</key>
  <true/>
EOF

if [[ "$ALLOW_NETWORK" -eq 1 ]]; then
  cat >> "$ENTITLEMENTS_PATH" <<'EOF'
  <key>com.apple.security.network.client</key>
  <true/>
EOF
fi

if [[ "$ALLOW_FILE_ACCESS" -eq 1 ]]; then
  cat >> "$ENTITLEMENTS_PATH" <<'EOF'
  <key>com.apple.security.files.user-selected.read-write</key>
  <true/>
EOF
fi

# Audio input (required for sounddevice tuner and for App Sandbox compliance)
cat >> "$ENTITLEMENTS_PATH" <<'EOF'
  <key>com.apple.security.device.audio-input</key>
  <true/>
</dict>
</plist>
EOF

echo "Removing quarantine attributes from app bundle..."
clear_quarantine_attrs "$APP_PATH"

remove_dead_symlinks_under "$APP_PATH"

echo "Signing app for Mac App Store..."
codesign --force --deep --timestamp \
  --entitlements "$ENTITLEMENTS_PATH" \
  --sign "$APP_DIST_IDENTITY" \
  "$APP_PATH"

echo "Verifying app signature..."
if ! codesign --verify --deep --strict --verbose=2 "$APP_PATH"; then
  echo "codesign --verify --deep --strict falló. Buscando symlinks rotos restantes…" >&2
  find "$APP_PATH" -type l ! -exec test -e {} \; -print 2>/dev/null | head -20 >&2 || true
  exit 1
fi

echo "Building signed installer package..."
rm -f "$OUTPUT_PKG"
productbuild \
  --component "$APP_PATH" /Applications \
  --sign "$INSTALLER_IDENTITY" \
  "$OUTPUT_PKG"

xattr -cr "$OUTPUT_PKG"
xattr -d com.apple.quarantine "$OUTPUT_PKG" 2>/dev/null || true

echo "Verifying installer signature..."
pkgutil --check-signature "$OUTPUT_PKG"

if [[ "$SKIP_STORE_VALIDATION" -eq 0 ]]; then
  cat >&2 <<'EOF'
Running Mac App Store installer validation (installer -store)…
This often hangs or waits for a system prompt. If it does not finish in 1–2 minutes, press Ctrl+C:
  • The .pkg is already built and signed — you can upload it with Transporter.
  • Re-run with --skip-store-validation, or set MAS_SKIP_STORE_VALIDATION=1 in mas.env
    (build_mas_store.sh skips this step by default).
EOF
  installer -store -pkg "$OUTPUT_PKG" -target /
else
  echo "Skipping installer -store validation (--skip-store-validation). Upload the PKG with Transporter; Apple validates on receipt."
fi

echo
echo "Done."
echo "App: $APP_PATH"
echo "Entitlements: $ENTITLEMENTS_PATH"
echo "PKG: $OUTPUT_PKG"
echo
echo "Next step: upload the PKG with Transporter or Xcode Organizer."
