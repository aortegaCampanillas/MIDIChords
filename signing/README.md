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

Example command using a local profile from this folder:

```bash
scripts/build_mas_pkg.sh \
  --app-dist-identity "3rd Party Mac Developer Application: Antonio Ortega González (977G5A733H)" \
  --installer-identity "3rd Party Mac Developer Installer: Antonio Ortega González (977G5A733H)" \
  --bundle-id "com.FPAlanTuring.FreeMIDIChords" \
  --provisioning-profile "signing/local/profiles/Free_MIDI_Chords.provisionprofile" \
  --version "1.0.0" \
  --build-number "1" \
  --allow-network \
  --allow-file-access
```
