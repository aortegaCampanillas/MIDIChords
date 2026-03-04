# Local signing assets (not committed)

Use this folder to keep Apple signing material required to rebuild release artifacts.

Suggested structure:

- `local/certs/`: downloaded `.cer` certificates
- `local/profiles/`: `.provisionprofile` files
- `local/keys/`: exported `.p12` and App Store Connect `.p8` keys

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
