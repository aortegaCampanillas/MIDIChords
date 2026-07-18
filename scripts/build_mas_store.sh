#!/usr/bin/env bash
# Carga signing/local/mas.env y ejecuta build_mas_pkg.sh con flags habituales App Store.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${MAS_ENV_FILE:-$ROOT_DIR/signing/local/mas.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  cat >&2 <<EOF
No se encuentra: $ENV_FILE

1) cp packaging/macos/mas-env.example signing/local/mas.env
2) Edita signing/local/mas.env (identidades, bundle id, perfil, versión, build)
3) Vuelve a ejecutar: ./scripts/build_mas_store.sh

Identidades: security find-identity -v -p codesigning
EOF
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${MAS_APP_DIST_IDENTITY:?Definir MAS_APP_DIST_IDENTITY en mas.env}"
: "${MAS_INSTALLER_IDENTITY:?Definir MAS_INSTALLER_IDENTITY en mas.env}"
: "${MAS_BUNDLE_ID:?Definir MAS_BUNDLE_ID en mas.env}"
: "${MAS_PROVISIONING_PROFILE:?Definir MAS_PROVISIONING_PROFILE en mas.env}"

EXTRA=()
if [[ -n "${MAS_VERSION:-}" ]]; then
  EXTRA+=(--version "$MAS_VERSION")
fi
if [[ -n "${MAS_BUILD_NUMBER:-}" ]]; then
  EXTRA+=(--build-number "$MAS_BUILD_NUMBER")
fi
if [[ "${MAS_SKIP_TK_CHECK:-1}" == "1" ]]; then
  EXTRA+=(--skip-tk-check)
fi
# installer -store suele colgarse o pedir autorización; Transporter valida al subir el .pkg
if [[ "${MAS_SKIP_STORE_VALIDATION:-1}" == "1" ]]; then
  EXTRA+=(--skip-store-validation)
fi
if [[ "${MAS_SKIP_BUILD:-0}" == "1" ]]; then
  EXTRA+=(--skip-build)
fi

exec "$ROOT_DIR/scripts/build_mas_pkg.sh" \
  --app-dist-identity "$MAS_APP_DIST_IDENTITY" \
  --installer-identity "$MAS_INSTALLER_IDENTITY" \
  --bundle-id "$MAS_BUNDLE_ID" \
  --provisioning-profile "$MAS_PROVISIONING_PROFILE" \
  --allow-network \
  --allow-file-access \
  "${EXTRA[@]}"
