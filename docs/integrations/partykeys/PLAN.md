# Plan de integración PartyKeys 36 — web

Estado: **implementado en v1.0.14** (2026-10-05), probado con un PartyKeys 36 real. Protocolo y verificación con
hardware en [README.md](README.md).

## Objetivo

Que los LEDs del PartyKeys 36 reflejen lo que el piano de la pantalla resalta en cada
modo, sin cambiar nada para quien no tenga el teclado.

| Modo | LEDs |
|------|------|
| Generación / círculo de quintas | Acorde con los colores de la app según la mano seleccionada (derecha azul, izquierda naranja, tono suave); intensos durante ▶. Las teclas pulsadas no se recolorean: el firmware las pone en blanco y al soltar vuelven a su color |
| Escalas | Notas de la escala en tenue, tónica destacada y nota en curso en color vivo durante ▶ |
| Detección de notas / acordes | Teclas pulsadas; al reconocer el acorde, todas sus notas |
| Intervalos (generación / detección) | Nota que suena |
| Práctica de intervalos | Nota de referencia; al responder, verde (acierto) o rojo (fallo) |

## Decisiones tomadas

- **Sin controles en la interfaz**: los LEDs están siempre activos cuando hay un PartyKeys.
- El acceso MIDI se pide igual que antes; el permiso SysEx se pide **automáticamente al detectar
  un puerto PartyKeys** (o se reutiliza en silencio si ya estaba concedido). Si se deniega, no se
  vuelve a pedir en la sesión.
- La octava solo se sigue por los avisos del teclado (no hay selector manual).
- Notas fuera del rango físico: **trasladar de octava** en acordes/escalas/intervalos;
  en detección, **descartar** (mostrar la nota exacta o nada).
- Alcance de la primera versión: los cuatro grupos de modos de la tabla.
- Solo PartyKeys 36. PopuPiano queda fuera (protocolo distinto).

## Hechos de hardware que condicionan el diseño

- Usar **solo CMD 0x15** (RGB por índice físico) para encender y «apagar todo» (`71 00`) para limpiar.
  CMD 0x71 con nota MIDI depende de la octava del teclado: no usarlo.
- `índice = nota − 48 − 12·octava − transporte`. El teclado avisa de cambios con
  `F0 05 30 20 00 00 3F 18 <oct> <trans> F7` (7 bits con signo); al conectarse vuelve a 0/0
  y no informa de su estado.
- Sin eco: ni CMD 0x15 ni note-on generan entrada. No hace falta supresión de ecos.
- Colores: evitar naranja y magenta; «tenue» = canal 32–64; por debajo de 16 no se ve.
- Latencia LED ≈ 200 ms: aceptable para teoría; no se sincroniza con el audio en esta fase.

## Pasos

### 1. Módulo puro `apps/web/static/partykeys_leds.js`

Mismo patrón que `midi_output.js` (IIFE, `globalThis.MidiChordsPartyKeys`, sin DOM ni estado global).

- Constantes: cabecera, `ENTER_LED_MODE`, `ALL_OFF`, `KEY_COUNT = 36`, `BASE_NOTE = 48`.
- `encodeChannel(v)`, `buildRgbMessage(groups)` (agrupa teclas por color).
- `isPartyKeysPortName(name)` → `/partykey/i`.
- `parseDeviceMessage(data)` → `{ type: "octave", octave, transpose }` para `… 3F 18 …`, o `null`.
- `noteToKeyIndex(note, { octave, transpose, fold })`: con `fold`, traslada por octavas hasta
  caer en 0–35; sin `fold`, devuelve `null` si queda fuera.
- `createPartyKeysController({ getOutput })`:
  - `connect()` → envía `ENTER_LED_MODE` + `ALL_OFF`, resetea octava/transporte a 0 y el estado de LEDs.
  - `setDeviceShift({ octave, transpose })`.
  - `render(colorByNote, { fold })` → convierte notas a índices, calcula el delta contra lo
    encendido y envía un único CMD 0x15 con lo que cambia (apagados = negro). No envía nada si no hay cambios.
  - `clear()` → `ALL_OFF` y estado vacío.
- Tests: `apps/web/test/partykeys_leds.test.js` con salida falsa (codificación, mensaje con los
  bytes verificados en hardware, delta, plegado de octavas, parseo de `3F 18` con 00/01/7F).
- Añadir el `<script>` en `app.html` antes de `app.js` (junto a `midi_output.js`).

### 2. Permiso y dispositivo (`app.js`)

- Estado en `state.midi`: `sysex` (el `MIDIAccess` actual tiene SysEx), `sysexDenied`,
  `partyKeysConnected`. La octava/transporte viven en el controlador.
- `enableMidiInput`: si el permiso SysEx ya está concedido, pedir el acceso con `{ sysex: true }`;
  si no, el acceso normal.
- `refreshPartyKeysConnection()` (al activar MIDI y en `access.onstatechange`): si hay puerto
  PartyKeys y el acceso no tiene SysEx → `requestSysexForPartyKeys()`, que sustituye
  `state.midi.access` por uno con SysEx (la entrada sin SysEx tampoco recibe los avisos de octava)
  y reengancha los handlers. Con SysEx, al aparecer el puerto → `controller.connect()` y resincronizar.
- `getPartyKeysOutput()` busca por nombre; `getMidiOutput()` (sonido MIDI) no cambia.

### 3. Entrada: avisos de octava

- En `handleMidiMessage`, antes de filtrar note-on/off, pasar los SysEx a
  `parseDeviceMessage`; si es de octava, `setDeviceShift` y forzar resincronización.

### 4. Sincronización

- `syncPartyKeysLeds()` en `app.js`:
  - Si está desactivado o el modo no tiene instrumento → `clear()`.
  - Si no, construir `Map(nota → color)` desde `getActiveMidiForMode()` más el contexto del modo
    (raíz `generatedChord.root_pc`, tónica de escala, `scaleCurrentNote`, respuesta de práctica).
  - Llamar a `controller.render(map, { fold: !isDetectionMode })`.
- Llamarla al final de `renderInstrument()` **antes** de la bifurcación piano/guitarra, para que
  funcione aunque se muestre la guitarra.
- Práctica de intervalos: `getActiveMidiForMode()` devuelve vacío; usar sus propias notas
  (`intervalPracticeStaffNotes()`) y `intervalPracticeAnswer` para verde/rojo.
- Limpiar en: `disableMidiInput`, cambio a modo sin teclado (metrónomo,
  afinador) y `pagehide`.

### 5. Paleta

Constante en `partykeys_leds.js`, ajustable tras probar:

| Rol | RGB |
|-----|-----|
| Nota activa / acorde | (0, 160, 255) azul |
| Fundamental / tónica | (255, 0, 0) rojo |
| Nota de escala (tenue) | (0, 48, 48) cian tenue |
| Nota en curso (▶) | (255, 255, 255) blanco |
| Acierto | (0, 255, 0) verde |
| Fallo | (255, 0, 0) rojo |

### 6. UI y textos

Ninguno. Riesgo conocido: si se recarga la página con el teclado ya transpuesto, los LEDs quedan
desplazados hasta el siguiente OCT/Fn+OCT.

### 7. Verificación

- `python scripts/check.py web` (descubre el test nuevo).
- Manual en Chrome/Edge con el teclado: cada modo de la tabla, cambio de OCT±/Fn+OCT± con
  acorde encendido (debe moverse correctamente), desconexión/reconexión, recarga de la página,
  desactivar MIDI (todo apagado), denegar el permiso SysEx (la app sigue funcionando sin LEDs)
  y convivencia con salida de sonido MIDI.

## Fuera de alcance (fases posteriores)

- Modo guiado «ahora / siguiente» (Highlight/Darklight) para escalas y arpegios.
- Sincronía fina LED/audio (`output.send(msg, timestamp)` y retraso de audio ≈ 200 ms).
- PopuPiano 29, escritorio (Python) y móvil (Flutter).
