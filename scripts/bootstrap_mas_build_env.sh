#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Create a clean virtualenv for Mac App Store desktop builds.

Usage:
  scripts/bootstrap_mas_build_env.sh [--python /path/to/python3.13] [--venv .venv-mas]

Options:
  --python  Python binary to use. Default:
            /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
  --venv    Virtualenv directory. Default: .venv-mas
  -h, --help
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"
VENV_DIR="$ROOT_DIR/.venv-mas"

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

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Error: Python binary not found or not executable: $PYTHON_BIN" >&2
  exit 1
fi

runtime_info="$("$PYTHON_BIN" - <<'PY'
import sys
import tkinter

print(f"{sys.executable}|{sys.version.split()[0]}|{tkinter.TclVersion}|{tkinter.TkVersion}")
PY
)"
IFS='|' read -r py_exec py_ver tcl_ver tk_ver <<<"$runtime_info"

if [[ "${tcl_ver%%.*}" -ge 9 || "${tk_ver%%.*}" -ge 9 ]]; then
  cat >&2 <<EOF
Error: unsupported Tcl/Tk runtime for Mac App Store builds.
Python: $py_exec
Version: $py_ver
Tcl: $tcl_ver
Tk: $tk_ver
EOF
  exit 1
fi

echo "Using Python: $py_exec"
echo "Version: $py_ver"
echo "Tcl/Tk: $tcl_ver / $tk_ver"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt" pyinstaller pyinstaller-hooks-contrib

echo
echo "Done."
echo "Virtualenv: $VENV_DIR"
echo "Python: $VENV_DIR/bin/python"
