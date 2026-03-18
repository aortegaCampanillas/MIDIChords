#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_DIR="$ROOT_DIR/apps/mobile_flutter/android"
KEYSTORE_PATH_DEFAULT="$ANDROID_DIR/upload-keystore.jks"
KEY_PROPERTIES_PATH="$ANDROID_DIR/key.properties"

if ! command -v keytool >/dev/null 2>&1; then
  echo "keytool no está disponible en PATH."
  exit 1
fi

read -r -p "Ruta del keystore [$KEYSTORE_PATH_DEFAULT]: " KEYSTORE_PATH
KEYSTORE_PATH="${KEYSTORE_PATH:-$KEYSTORE_PATH_DEFAULT}"

read -r -p "Alias de la clave [upload]: " KEY_ALIAS
KEY_ALIAS="${KEY_ALIAS:-upload}"

read -r -s -p "Contraseña del keystore: " STORE_PASSWORD
echo
read -r -s -p "Repite la contraseña del keystore: " STORE_PASSWORD_CONFIRM
echo
if [[ "$STORE_PASSWORD" != "$STORE_PASSWORD_CONFIRM" ]]; then
  echo "Las contraseñas del keystore no coinciden."
  exit 1
fi

read -r -s -p "Contraseña de la clave [enter para reutilizar la del keystore]: " KEY_PASSWORD
echo
KEY_PASSWORD="${KEY_PASSWORD:-$STORE_PASSWORD}"

read -r -p "Nombre y apellidos [Antonio Ortega Gonzalez]: " DNAME_CN
DNAME_CN="${DNAME_CN:-Antonio Ortega Gonzalez}"
read -r -p "Organización [FPAlanTuring]: " DNAME_O
DNAME_O="${DNAME_O:-FPAlanTuring}"
read -r -p "Ciudad [Malaga]: " DNAME_L
DNAME_L="${DNAME_L:-Malaga}"
read -r -p "Provincia [Malaga]: " DNAME_ST
DNAME_ST="${DNAME_ST:-Malaga}"
read -r -p "País (2 letras) [ES]: " DNAME_C
DNAME_C="${DNAME_C:-ES}"

mkdir -p "$(dirname "$KEYSTORE_PATH")"

if [[ -f "$KEYSTORE_PATH" ]]; then
  echo "Ya existe un keystore en $KEYSTORE_PATH"
  exit 1
fi

keytool -genkeypair \
  -v \
  -keystore "$KEYSTORE_PATH" \
  -storetype JKS \
  -storepass "$STORE_PASSWORD" \
  -keypass "$KEY_PASSWORD" \
  -alias "$KEY_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -dname "CN=$DNAME_CN, O=$DNAME_O, L=$DNAME_L, ST=$DNAME_ST, C=$DNAME_C"

cat >"$KEY_PROPERTIES_PATH" <<EOF
storeFile=$KEYSTORE_PATH
storePassword=$STORE_PASSWORD
keyAlias=$KEY_ALIAS
keyPassword=$KEY_PASSWORD
EOF

echo
echo "Keystore creado en: $KEYSTORE_PATH"
echo "key.properties escrito en: $KEY_PROPERTIES_PATH"
echo "Siguiente paso:"
echo "  cd $ROOT_DIR/apps/mobile_flutter"
echo "  flutter build appbundle --release"
