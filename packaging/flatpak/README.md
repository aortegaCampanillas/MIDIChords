# Flatpak / Flathub

Este directorio prepara la base para publicar MIDIChords en Flathub.

## Archivos incluidos

- `com.freemidichords.MIDIChords.yml`: manifiesto base Flatpak
- `com.freemidichords.MIDIChords.desktop`: lanzador exportado
- `com.freemidichords.MIDIChords.metainfo.xml`: metainfo AppStream
- `python-deps.json`: dependencias Python fijadas para Flatpak
- `flathub.json`: limita la build a `x86_64` por ahora

## Estado actual

La base ya está preparada para una build Flatpak reproducible:

- el manifiesto principal está en `com.freemidichords.MIDIChords.yml`
- las dependencias Python se generan en `python-deps.json`
- el build empaqueta el binario Linux con `PyInstaller` dentro del sandbox de Flatpak

El archivo `python-deps.json` se regenera con:

```bash
python3 scripts/generate_flatpak_python_deps.py
```

## Recomendación práctica

La vía más realista es:

1. construir un Flatpak que empaquete un binario PyInstaller reproducible
2. regenerar `python-deps.json` cuando cambien versiones
3. en el **PR de nueva app**, el manifiesto y `flathub.json` van en la **raíz** de la rama (no en subcarpeta)
4. verificar el ID `com.freemidichords.MIDIChords` desde `freemidichords.com`

## ID elegido

Se usa `com.freemidichords.MIDIChords` para que la app pueda verificarse en Flathub a partir del dominio `freemidichords.com`.

## Publicar en Flathub

Guía paso a paso: **[FLATHUB.md](FLATHUB.md)**. Incluye crear el release en GitHub, fork de flathub, uso del manifiesto `com.freemidichords.MIDIChords.flathub.yml` (origen Git) y apertura del PR contra la rama `new-pr`.
