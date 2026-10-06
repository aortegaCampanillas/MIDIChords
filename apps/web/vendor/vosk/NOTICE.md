# Vosk (lectura de notas por voz)

Terceros redistribuidos sin modificar. No editar: para actualizar, sustituir los
archivos y cambiar el número de versión en el nombre (las rutas se sirven con
caché inmutable, ver `apps/web/_headers`).

| Archivo | Origen | Licencia |
|---------|--------|----------|
| `vosk-browser-0.0.8.js` | npm `vosk-browser@0.0.8` (`dist/vosk.js`), <https://github.com/ccoreilly/vosk-browser> | Apache-2.0 |
| `vosk-model-small-es-0.42.tar.gz.part0` + `.part1` | `vosk-model-small-es-0.42.zip` de <https://alphacephei.com/vosk/models>, reempaquetado como `.tar.gz` y partido en dos trozos | Apache-2.0, Copyright 2022-2050 AC Technologies LLC |
| `vosk-model-small-en-us-0.15.tar.gz.part0` + `.part1` | `vosk-model-small-en-us-0.15.zip` de <https://alphacephei.com/vosk/models>, mismo reempaquetado | Apache-2.0, Copyright 2020 Alpha Cephei Inc |

El modelo se parte porque Cloudflare Pages no admite archivos de más de 25 MiB;
`note_speech.js` descarga los trozos, los concatena en el navegador y pasa el
resultado a `Vosk.createModel`. Para regenerarlo:

```bash
unzip vosk-model-small-es-0.42.zip
tar -czf model.tar.gz vosk-model-small-es-0.42
split -b 20000000 -a 1 -d model.tar.gz vosk-model-small-es-0.42.tar.gz.part
# inglés: igual con vosk-model-small-en-us-0.15 y -b 21000000
```
