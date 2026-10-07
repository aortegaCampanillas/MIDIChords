# Integración PartyKeys — protocolo de LEDs

Documentación de referencia para integrar MIDIChords con los teclados
**PartyKeys 36** (y su variante **PopuPiano 29**), que tienen un LED RGB direccionable
por tecla controlable por MIDI SysEx.

Plan de integración web: [PLAN.md](PLAN.md).

## Fuentes (copiadas el 2026-10-05)

| Archivo | Origen | Notas |
|---------|--------|-------|
| [upstream/protocol-site.md](upstream/protocol-site.md) | <https://protocol.partykeys.org/> | Web oficial convertida a Markdown. Incluye quickstart, ejemplos JS/Python/Node/Swift y FAQ. |
| [upstream/LED_PROTOCOL.md](upstream/LED_PROTOCOL.md) | [allen4z/PartykeysProtocol](https://github.com/allen4z/PartykeysProtocol) @ `2ea97de` (2026-07-22) | Referencia más completa de PartyKeys 36: CMD 14, eco de note-on, timing, hooks. |
| [upstream/popupiano_LED_PROTOCOL.md](upstream/popupiano_LED_PROTOCOL.md) | mismo repo y commit | PopuPiano 29, incluye CMD 0x23 (modo enseñanza) que no aparece en la web. |

Licencia upstream: MIT. Los archivos de `upstream/` se mantienen tal cual (en inglés);
no editarlos a mano. Para actualizarlos, volver a descargarlos y anotar aquí el nuevo commit y la fecha.

## Resumen del protocolo — PartyKeys 36

- 36 teclas, MIDI 48–83 (C3–B5), USB MIDI class-compliant. `key_index = midi_note − 48`.
- Detección: nombre de puerto que contenga `partykey` (sin distinguir mayúsculas).
- Cabecera de fabricante: `05 30 7F 7F 20 00`.
- **SysEx obligatorio**: `navigator.requestMIDIAccess({ sysex: true })`. Sin él los
  comandos de LED se descartan en silencio.

| Objetivo | Mensaje |
|----------|---------|
| Entrar en modo LED (una vez tras cada (re)conexión) | `F0 05 30 7F 7F 20 00 0F 01 F7` |
| RGB por tecla (**CMD 0x15**, comando principal) | `F0 05 30 7F 7F 20 00 15 <numGroups> [R_hi R_lo G_hi G_lo B_hi B_lo keyCount key…]× F7` |
| Apagar todo | `F0 05 30 7F 7F 20 00 71 00 F7` |
| Paleta por índice de tecla (CMD 0x14) | `F0 05 30 7F 7F 20 00 14 <N> [keyIndex palette]× F7` |
| Paleta por nota MIDI (CMD 0x71) | `F0 05 30 7F 7F 20 00 71 <N> [midiNote palette]× F7` |

Codificación de color de CMD 0x15: cada canal 0–255 se divide en dos bytes de 7 bits,
`high = floor(v / 128)`, `low = v % 128` (255 → `01 7F`).

Reglas prácticas:

- Usar CMD 0x15 y **no** note-on (`90 nn 40`) para encender LEDs: según upstream el firmware
  devuelve el note-on como eco (en nuestro teclado, simplemente no hace nada; ver verificación).
- Actualizaciones delta: enviar solo las teclas que cambian (las que se apagan, con color 0).
- La latencia física del LED es ≈150–250 ms. Para sincronizar con audio, enviar el SysEx en el
  tiempo del beat y retrasar audio y visuales ≈200 ms (no adelantar el SysEx).
- En Web MIDI, `output.send(data, timestamp)` permite programar el envío; `output.clear()` cancela lo pendiente (p. ej. al pulsar Stop).
- Al cerrar la app o desconectar, enviar «apagar todo».
- Navegadores: Chrome/Edge (Web MIDI + SysEx). Safari/iOS no tienen Web MIDI.

## Resumen del protocolo — PopuPiano 29

- 29 teclas, MIDI 48–76 (C3–E5), USB o BLE MIDI. Detección por `popupiano`. Cabecera `03`.
- No hay comando de «entrar en modo».
- `F0 03 1E <numColors> 01 [R G B]× F7`: sube la paleta a partir del slot 1 (colores de 7 bits, `min(127, round(v/2))`).
- `F0 03 20 <numPairs> [lampID slot]× F7`: asigna un slot a cada tecla (slot 0 = apagada).
- `F0 03 23 …`: mismo formato, pero en modo enseñanza (la tecla se ilumina solo mientras se mantiene pulsada).
- La paleta persiste hasta apagar el dispositivo; para refrescar basta reenviar CMD 0x20.

## Discrepancias entre fuentes (verificar con hardware)

1. **CMD 0x14.** La web lo describe como `Send_LightUp` con paleta UI de 28 slots
   (Highlight = slots 1–12 a brillo ×1.0; Darklight = slots 14–25 a ×0.75; 26–27 blanco) y dice
   que en el cable se emite como **CMD 0x71** con pares `nota MIDI / slot`. `LED_PROTOCOL.md`
   lo define como comando propio `0x14` con pares `índice de tecla / paleta 0–12`.
2. **Cabecera en los ejemplos de Highlight/Darklight.** La web usa `F0 05 30 7F **3F** 20 00 71 …`,
   mientras que el resto de mensajes usa `7F 7F`. Puede ser una errata o un sub-ID distinto.
3. **Paleta de CMD 0x71.** `LED_PROTOCOL.md` documenta 13 slots (0 apagado, 1 rojo … 12 morado);
   la web habla de 28 slots. Solo se detallan los colores de los extremos.

Ver la sección siguiente para lo que se ha comprobado con hardware real.

## Verificación con hardware (PartyKeys 36, macOS, 2026-10-05)

Pruebas hechas con python-rtmidi; el puerto aparece como `PartyKeys` (entrada y salida).

| Prueba | Resultado |
|--------|-----------|
| Entrar en modo LED + CMD 0x15 | ✅ Funciona; índices 0–35 = posición física de izquierda a derecha. |
| Apagar todo (`71 00`) | ✅ Funciona. |
| Actualización delta con CMD 0x15 | ✅ Poner una tecla a negro no afecta a las demás. |
| Brillo (canal rojo 255 → 1) | Gradiente visible; por debajo de ~16 apenas se distingue. Usar 32–64 para «tenue». |
| Colores | Blanco, amarillo, cian, violeta bien distinguibles; **naranja (255,128,0) se confunde con amarillo** y magenta tira a violeta. |
| CMD 0x14 (`keyIndex palette`) | ✅ Funciona como dice `LED_PROTOCOL.md`: índice físico, paleta 1–12. |
| CMD 0x71 (`midiNote palette`) | ⚠️ Funciona, pero la nota se interpreta **con la octava/transporte activos del teclado** (con OCT−1, las notas 60–71 encendieron las teclas 24–35). Notas fuera del rango actual se ignoran. |
| Cabecera `7F 3F` (web) en CMD 0x71 | ✅ También funciona (equivale a `7F 7F` a efectos prácticos). Darklight no verificado. |
| Note-on legacy (`90 nn 40`) | ❌ No enciende LED ni produce eco con este firmware. |
| Eco por la entrada de CMD 0x14/0x15/0x71 | Ninguno. |
| LEDs al cambiar octava | Se mantienen (van ligados a la posición física). |

### Resaltado al pulsar y modos de LED (no documentado upstream)

El firmware ilumina en **blanco** la tecla mientras se mantiene pulsada, con o sin app
conectada, y ese blanco **tiene prioridad** sobre los colores de CMD 0x15 en el modo
documentado (`0F 01`). Probando otros valores del byte de modo:

| Mensaje | Tecla pulsada | Al soltar |
|---------|---------------|-----------|
| `F0 05 30 7F 7F 20 00 0F 00 F7` | blanco | queda naranja (efecto del firmware) |
| `F0 05 30 7F 7F 20 00 0F 01 F7` (upstream) | blanco | vuelve al color previo |
| `F0 05 30 7F 7F 20 00 0F 02 F7` | blanco | queda naranja |
| `F0 05 30 7F 7F 20 00 0F 03 F7` | color propio del firmware por nota (do rojo, mi naranja…) | se apaga (negro) |

En ningún modo gana el color del host mientras la tecla está pulsada (enviarlo 200 ms
después de la pulsación tampoco). Con `0F 01` el color enviado se guarda y aparece al
soltar, sin parpadeo. La web usa `0F 01`; el feedback de color solo es visible en
teclas no pulsadas o tras soltarlas.

### Octava y transporte (no documentado upstream)

Al pulsar OCT± o Fn+OCT± el teclado **envía** un SysEx con el estado actual:

```
F0 05 30 20 00 <canal> 3F 18 <octava> <transporte> F7
```

`<canal>` es el canal MIDI configurado en el teclado (`00` en el canal 1, `01` en el
canal 2…, visto el 2026-10-07 con el teclado en canal 2: las notas llegaban como `91`/`81`).

Ambos valores son enteros con signo en 7 bits (`00` = 0, `01` = +1, `7F` = −1).
Pulsar Fn envía además `F0 05 30 10 00 00 3F 16 F7`.

Las notas que envía el teclado se desplazan con ambos valores:

```
nota_recibida = 48 + índice_físico + 12·octava + transporte
índice_físico = nota − 48 − 12·octava − transporte
```

Reconexión USB (desenchufar y volver a enchufar con OCT−1 activo):

- El teclado **no envía** ningún SysEx de estado al conectarse.
- Vuelve a octava 0 / transporte 0 (se apaga el indicador OCT y la tecla izquierda envía 48).
- CMD 0x15 funciona inmediatamente **sin** reenviar «entrar en modo LED». Aun así se
  envía tras cada conexión, por seguir la spec (es inocuo).
- Otra app con el puerto abierto (p. ej. la web de producción) no interfiere: CoreMIDI
  reparte la entrada a todos los clientes.

Por tanto: al detectar la conexión, asumir octava 0 / transporte 0 y actualizar al
recibir el aviso `… 3F 18 …`. Caso no cubierto: si la página se recarga con el teclado
ya conectado y transpuesto, el estado es desconocido hasta el siguiente cambio de octava;
no se conoce ningún mensaje para consultarlo.

Conclusión: usar CMD 0x15 (índice físico) para todo, convirtiendo nota → índice con
la octava/transporte conocidos; CMD 0x71 solo para «apagar todo».

## Encaje en MIDIChords

Puntos de partida en el código actual (aún no hay integración):

- **Web**: `requestMidiAccessWithCaching()` en `apps/web/static/app.js` llama a
  `navigator.requestMIDIAccess()` **sin** `sysex: true`; habrá que pedirlo (lanza un
  permiso adicional en el navegador). La salida MIDI de bajo nivel está en
  `apps/web/static/midi_output.js` y el resaltado de teclas durante la reproducción en
  `apps/web/static/playback_highlight.js`.
- **Escritorio**: la E/S MIDI está en `midichords/mixins/midi_io_mixin.py` (python-rtmidi); el
  ejemplo de upstream con `mido` se traduce directamente a mensajes SysEx de rtmidi.
- **Móvil**: requeriría un plugin MIDI con soporte SysEx (USB/BLE) en Flutter.

Usos naturales: iluminar el acorde o la escala seleccionada, resaltar las notas durante la
reproducción y, en modos de práctica, mostrar «nota actual» frente a «siguiente nota»
(el par Highlight/Darklight está pensado justo para eso).
