# Local signing assets (not committed)

Use this folder to keep Apple signing material required to rebuild release artifacts.

Suggested structure:

- `local/certs/`: downloaded `.cer` certificates
- `local/profiles/`: `.provisionprofile` files
- `local/keys/`: exported `.p12` and App Store Connect `.p8` keys

Important:

- `.cer` files are not enough to sign. You also need the matching private key, typically exported as `.p12`, and imported into your login keychain.
- If `security find-identity -v -p codesigning` shows `0 valid identities found`, the keychain is missing the private key even if the `.cer` files exist.
- You can validate the full environment with `scripts/validate_macos_release_env.sh`.

Recommended setup flow:

```bash
# 1) Use the official python.org runtime with Tcl/Tk 8.6
scripts/bootstrap_mas_build_env.sh \
  --python /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13

# 2) Validate runtime, virtualenv, profile and keychain state
scripts/validate_macos_release_env.sh

# 3) If identities are missing, export the signing certificate + private key
#    from Keychain Access as .p12 and copy it into signing/local/keys/
#    Then import it into the login keychain.
```

These files are ignored by git via:

- repository `.gitignore`
- `signing/.gitignore`

### Flujo recomendado: `signing/local/mas.env` + `build_mas_store.sh`

1. `cp scripts/mas-env.example signing/local/mas.env`
2. Edita `mas.env` (identidades, `MAS_BUNDLE_ID`, ruta del `.provisionprofile`, **versión** y **build** nuevos tras un rechazo).
3. Desde la raíz del repo:

```bash
chmod +x scripts/build_mas_store.sh
./scripts/build_mas_store.sh
```

El wrapper pasa `--allow-network`, `--allow-file-access` y por defecto **`--skip-tk-check`** (la app usa Qt; el chequeo Tcl/Tk era para builds antiguos). Para forzar el chequeo Tcl/Tk 8.6: `MAS_SKIP_TK_CHECK=0` en `mas.env`.

Salida: `MIDIChords-macos-appstore.pkg` (y `dist/MIDIChords.app`). Sube el `.pkg` con **Transporter**.

### Revisión MAS: icono en Dock y la app se cierra sin ventana

Suele ser **Qt sin el plugin de plataforma `cocoa`** en el bundle firmado. El arranque escribe **`mas_bootstrap_last.txt`** (y errores Python en **`python-startup-error.log`**) bajo *Application Support* de la app: en sandbox suele ser  
`~/Library/Containers/<TU_BUNDLE_ID>/Data/Library/Application Support/MIDIChords/`.  
Ahí verás `_MEIPASS`, `QT_PLUGIN_PATH` y el ejecutable. El script de build usa **`--collect-all PySide6`**, **`--collect-submodules PySide6`**, **`pyinstaller-hooks-contrib`** en el venv y, si hace falta, **`scripts/mas_embed_pyside6_bundle.py`** (copia **PySide6**/**shiboken6** a **`Contents/Frameworks`**) porque a veces **`collect-all` no vuelca Qt** y el `.app` **no contiene `libqcocoa.dylib`** — síntoma: **TestFlight o sandbox cierra la app al abrir** sin crash útil. El build **falla** si tras eso sigue faltando el plugin. Tras un rechazo, **sube un build nuevo** (`--build-number` distinto) y un `.pkg` regenerado con `./scripts/build_mas_store.sh`.

### TestFlight / validación: error **90885** (`QtWebEngineProcess.app`)

Apple exige que los **ejecutables anidados** con *application identifier* lleven **provisioning profile** alineado con MAS. **Qt WebEngine** incluye **`QtWebEngineProcess.app`** dentro de **`QtWebEngineCore.framework`**, lo que dispara **90885**. MIDIChords **no usa WebEngine**; **`build_mas_pkg.sh`** excluye esos módulos en PyInstaller y **elimina** frameworks `QtWebEngine*`, `QtWebView*` y `QtWebChannel*` (y cualquier `QtWebEngineProcess.app` suelto) antes de firmar.

Además, el wheel de **PySide6** incluye **herramientas Qt** (`lupdate`, `rcc`, `uic`, `qmllint`, …) y **`Qt/libexec/*`**: son **Mach-O ejecutables** que `codesign --deep` firma con **Team ID** e **identifier** propios pero **sin** el mismo perfil que el `.app` → Apple los rechaza con **90885** (a veces el mensaje solo muestra plantillas `${executable}` / `${bundle}`). El script **borra** `Qt/libexec` y esos binarios en la raíz de **PySide6**, y la carpeta de plugins **`webview`** (incluye `libqtwebview_webengine.dylib`).

### Revisión MAS: **Guideline 2.5.1** — `libqsqlodbc.dylib` (plugins **sqldrivers**)

Apple puede rechazar el binario si detecta referencias a APIs consideradas no públicas. El driver Qt **`libqsqlodbc.dylib`** enlaza símbolos ODBC (`SQLAllocHandle`, …). MIDIChords **no usa bases de datos Qt**; **`build_mas_pkg.sh`** excluye **`PySide6.QtSql`** en PyInstaller y **elimina** `Qt/plugins/sqldrivers` del `.app` antes de firmar.

### Comando largo (equivalente manual)

Example command using a local profile from this folder:

```bash
scripts/build_mas_pkg.sh \
  --app-dist-identity "3rd Party Mac Developer Application: …" \
  --installer-identity "3rd Party Mac Developer Installer: …" \
  --bundle-id "com.example.midichords" \
  --provisioning-profile "signing/local/profiles/TuPerfil.provisionprofile" \
  --version "1.0.1" \
  --build-number "1" \
  --allow-network \
  --allow-file-access \
  --skip-tk-check
```

Operational notes:

- `installer -store` (validación local MAS) often hangs or waits for authorization. **`./scripts/build_mas_store.sh` skips it by default** (`MAS_SKIP_STORE_VALIDATION=1`). The `.pkg` is already signed; **Transporter** validates on upload. To force local validation: `MAS_SKIP_STORE_VALIDATION=0` in `mas.env` or `--skip-store-validation` omitted when calling `build_mas_pkg.sh` directly.
- If App Store Connect rejects a build, bump `--build-number` before re-uploading. Reusing the same failed build number can leave Transporter stuck on the previous failed processing state.
- If App Store Connect reports `com.apple.quarantine` inside the package payload, clear extended attributes and rebuild. `scripts/build_mas_pkg.sh` now cleans `assets/`, the generated `.app`, and the final `.pkg` automatically.
- Recommended upload flow for this repo: open the **Transporter** macOS app, sign in, drag `MIDIChords-macos-appstore.pkg`, and click **Deliver**. Keep `xcrun iTMSTransporter` only as a fallback/debug path.
