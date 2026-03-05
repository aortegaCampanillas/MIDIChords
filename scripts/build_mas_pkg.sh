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
  --skip-store-validation Skip installer -store validation
  -h, --help              Show this help

Notes:
  - This script is for Mac App Store submission, not Developer ID distribution.
  - Upload the resulting .pkg with Transporter or Xcode Organizer.
EOF
}

APP_NAME="MIDIChords"
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
  echo "Building ${APP_NAME}.app with PyInstaller..."
  pyinstaller --noconfirm --clean --windowed --name "$APP_NAME" --add-data "assets:assets" "$ENTRYPOINT"
fi

if [[ ! -d "$APP_PATH" ]]; then
  echo "Error: app bundle not found: $APP_PATH" >&2
  exit 1
fi

INFO_PLIST="$APP_PATH/Contents/Info.plist"

echo "Setting bundle identifier: $BUNDLE_ID"
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$INFO_PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$INFO_PLIST"

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
  iconutil -c icns "$ICONSET_DIR" -o "$APP_PATH/Contents/Resources/AppIcon.icns"
  /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile AppIcon" "$INFO_PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string AppIcon" "$INFO_PLIST"
fi

echo "Embedding provisioning profile..."
cp "$PROVISIONING_PROFILE" "$APP_PATH/Contents/embedded.provisionprofile"

echo "Reading provisioning profile entitlements..."
security cms -D -i "$PROVISIONING_PROFILE" > "$PROFILE_PLIST_TMP"
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

cat >> "$ENTITLEMENTS_PATH" <<'EOF'
</dict>
</plist>
EOF

echo "Removing quarantine attributes from app bundle..."
xattr -cr "$APP_PATH"
xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || true

echo "Signing app for Mac App Store..."
codesign --force --deep --timestamp \
  --entitlements "$ENTITLEMENTS_PATH" \
  --sign "$APP_DIST_IDENTITY" \
  "$APP_PATH"

echo "Verifying app signature..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

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
  echo "Running Mac App Store installer validation..."
  installer -store -pkg "$OUTPUT_PKG" -target /
fi

echo
echo "Done."
echo "App: $APP_PATH"
echo "Entitlements: $ENTITLEMENTS_PATH"
echo "PKG: $OUTPUT_PKG"
echo
echo "Next step: upload the PKG with Transporter or Xcode Organizer."
