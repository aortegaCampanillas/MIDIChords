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
IDENTITY=""
BUNDLE_ID=""
NOTARY_PROFILE=""
SKIP_BUILD=0
SKIP_NOTARIZE=0

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

cd "$ROOT_DIR"

if [[ "$SKIP_BUILD" -eq 0 ]]; then
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

echo "Signing app bundle..."
codesign --force --deep --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH"

echo "Verifying app signature..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

echo "Building DMG..."
rm -rf "$DMG_ROOT" "$DMG_PATH"
mkdir -p "$DMG_ROOT"
cp -R "$APP_PATH" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_ROOT" -ov -format UDZO "$DMG_PATH"

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

