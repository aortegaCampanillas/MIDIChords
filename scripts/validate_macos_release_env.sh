#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Validate the local macOS release environment for desktop builds.

Usage:
  scripts/validate_macos_release_env.sh [--python /path/to/python] [--venv .venv-mas] [--profile path]

Options:
  --python   Python binary to validate.
             Default: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
  --venv     Virtualenv directory to inspect. Default: .venv-mas
  --profile  Provisioning profile path.
             Default: signing/local/profiles/Free_MIDI_Chords.provisionprofile
  -h, --help Show this help
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"
VENV_DIR="$ROOT_DIR/.venv-mas"
PROFILE_PATH="$ROOT_DIR/signing/local/profiles/Free_MIDI_Chords.provisionprofile"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_BIN="${2:-}"
      shift 2
      ;;
    --venv)
      VENV_DIR="${2:-}"
      shift 2
      ;;
    --profile)
      PROFILE_PATH="${2:-}"
      shift 2
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

failures=0

check_ok() {
  printf '[ok] %s\n' "$1"
}

check_warn() {
  printf '[warn] %s\n' "$1"
  failures=$((failures + 1))
}

if [[ -x "$PYTHON_BIN" ]]; then
  runtime_info="$("$PYTHON_BIN" - <<'PY'
import sys
import tkinter

print(f"{sys.executable}|{sys.version.split()[0]}|{tkinter.TclVersion}|{tkinter.TkVersion}")
PY
)"
  IFS='|' read -r py_exec py_ver tcl_ver tk_ver <<<"$runtime_info"
  if [[ "${tcl_ver%%.*}" -lt 9 && "${tk_ver%%.*}" -lt 9 ]]; then
    check_ok "Python runtime available: $py_exec (Python $py_ver, Tcl/Tk $tcl_ver/$tk_ver)"
  else
    check_warn "Python runtime uses unsupported Tcl/Tk: $py_exec (Tcl/Tk $tcl_ver/$tk_ver)"
  fi
else
  check_warn "Python runtime not found: $PYTHON_BIN"
fi

if [[ -x "$VENV_DIR/bin/python" ]]; then
  check_ok "Virtualenv present: $VENV_DIR"
else
  check_warn "Virtualenv missing: $VENV_DIR"
fi

if [[ -x "$VENV_DIR/bin/pyinstaller" ]]; then
  check_ok "PyInstaller installed in $VENV_DIR"
else
  check_warn "PyInstaller missing in $VENV_DIR"
fi

if [[ -f "$ROOT_DIR/signing/local/certs/mac_app.cer" ]]; then
  check_ok "Application certificate file present"
else
  check_warn "Missing application certificate file: signing/local/certs/mac_app.cer"
fi

if [[ -f "$ROOT_DIR/signing/local/certs/mac_installer.cer" ]]; then
  check_ok "Installer certificate file present"
else
  check_warn "Missing installer certificate file: signing/local/certs/mac_installer.cer"
fi

if find "$ROOT_DIR/signing/local/keys" -maxdepth 1 -type f \( -name '*.p12' -o -name '*.pfx' \) | grep -q .; then
  check_ok "Private key export found in signing/local/keys"
else
  check_warn "No .p12/.pfx private key export found in signing/local/keys"
fi

identity_count="$(security find-identity -v -p codesigning 2>/dev/null | sed -nE 's/^[[:space:]]*([0-9]+) valid identities found$/\1/p' | tail -n 1)"
identity_count="${identity_count:-0}"
if [[ "$identity_count" -ge 1 ]]; then
  check_ok "Keychain has $identity_count valid code signing identity/identities"
else
  check_warn "Keychain has no valid code signing identities"
fi

if [[ -f "$PROFILE_PATH" ]]; then
  tmp_plist="$(mktemp "$ROOT_DIR/build/profile-validate.XXXXXX.plist")"
  if openssl smime -inform der -verify -noverify -in "$PROFILE_PATH" -out "$tmp_plist" >/dev/null 2>&1; then
    profile_name="$(/usr/libexec/PlistBuddy -c 'Print :Name' "$tmp_plist" 2>/dev/null || true)"
    profile_app_id="$(/usr/libexec/PlistBuddy -c 'Print :Entitlements:com.apple.application-identifier' "$tmp_plist" 2>/dev/null || true)"
    profile_expiry="$(/usr/libexec/PlistBuddy -c 'Print :ExpirationDate' "$tmp_plist" 2>/dev/null || true)"
    check_ok "Provisioning profile decoded: ${profile_name:-unknown}"
    if [[ -n "$profile_app_id" ]]; then
      printf '      App ID: %s\n' "$profile_app_id"
    fi
    if [[ -n "$profile_expiry" ]]; then
      printf '      Expires: %s\n' "$profile_expiry"
    fi
  else
    check_warn "Provisioning profile could not be decoded: $PROFILE_PATH"
  fi
  rm -f "$tmp_plist"
else
  check_warn "Provisioning profile missing: $PROFILE_PATH"
fi

if [[ "$failures" -gt 0 ]]; then
  echo
  echo "Environment is not ready for a signed macOS release build."
  exit 1
fi

echo
echo "Environment is ready for a signed macOS release build."
