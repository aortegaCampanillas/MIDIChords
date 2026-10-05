# PartyKeys LED Protocol — Developer Reference

> Firmware version tested: as shipped (2025)
> Transport: USB MIDI (Web MIDI API, Chrome / Edge)
> All values hexadecimal unless stated otherwise.

---

## 1. Connection

Request MIDI access **with SysEx enabled** — this is mandatory for LED control:

```js
const access = await navigator.requestMIDIAccess({ sysex: true });
```

Identify the device by scanning port names for `"partykeys"` (case-insensitive).
Fall back to the first available port if the name doesn't match.

---

## 2. Initialisation sequence

Every time the device connects or reconnects, send these two messages in order:

### 2-a. Enter lighting mode

```
F0 05 30 7F 7F 20 00 0F 01 F7
```

This switches the firmware into LED-control mode.
**Must be sent before any color command.** Sending color commands without it has no effect.

### 2-b. Clear all lights (optional but recommended)

Send a CMD 15 message that sets all 36 keys to black — see Section 4 for the format.
This ensures a clean known state after reconnect:

```
F0 05 30 7F 7F 20 00 15 01
  00 00  00 00  00 00  24
  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
  10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F
  20 21 22 23
F7
```

*(One group, color `[0,0,0]`, keyCount = 36 = `0x24`, keys 0–35)*

---

## 3. CMD 14 (0x14) — Per-key palette color

Sets individual keys to firmware-defined palette colors. Unlike CMD 71, this
command addresses keys by their zero-based key index rather than MIDI note.

### Frame structure

```
F0 05 30 7F 7F 20 00 14  <numKeys>
  <keyIndex_0>  <paletteIndex_0>
  <keyIndex_1>  <paletteIndex_1>
  …
F7
```

| Byte(s) | Value | Description |
|---------|-------|-------------|
| `F0` | — | SysEx start |
| `05 30 7F 7F 20 00` | — | Manufacturer / device header |
| `14` | 20 decimal | Command ID |
| `numKeys` | 0–36 | Number of key/palette pairs; `0` turns all lights off |
| `keyIndex` | 0–35 | Key index (`0` = leftmost key) |
| `paletteIndex` | 0–12 | Firmware-defined palette color |
| `F7` | — | SysEx end |

### Palette colors

CMD 14 uses the same 13 palette slots as CMD 71:

| Palette index | Color |
|---------------|-------|
| 0 | Off |
| 1 | Red |
| 2–11 | Orange → Cyan → Blue |
| 12 | Purple |

### Example — set key 0 red, key 12 blue

```
F0 05 30 7F 7F 20 00 14 02
  00 01
  0C 08
F7
```

---

## 4. CMD 15 — Per-key RGB color (primary command)

This is the main command for setting arbitrary colors on individual keys.

### Frame structure

```
F0 05 30 7F 7F 20 00 15  <numGroups>
  <group_0>
  <group_1>
  ...
  <group_N-1>
F7
```

| Byte(s) | Value | Description |
|---------|-------|-------------|
| `F0` | — | SysEx start |
| `05 30 7F 7F 20 00` | — | Manufacturer / device header |
| `15` | 21 decimal | Command ID |
| `numGroups` | 1–127 | How many color groups follow |
| *(groups)* | | See below |
| `F7` | — | SysEx end |

### Group format

Each group sets all listed keys to the same RGB color:

```
R_hi  R_lo   G_hi  G_lo   B_hi  B_lo   keyCount  key0  key1  …
```

| Field | Bytes | Range | Description |
|-------|-------|-------|-------------|
| `R_hi R_lo` | 2 | 0x00–0x01, 0x00–0x7F | Red channel (14-bit MIDI safe) |
| `G_hi G_lo` | 2 | same | Green channel |
| `B_hi B_lo` | 2 | same | Blue channel |
| `keyCount` | 1 | 1–36 | Number of key indices that follow |
| `key0…keyN` | N | 0–35 | Key indices (0 = leftmost, 35 = rightmost) |

### Color encoding

MIDI data bytes are 7-bit (0–127). Each 8-bit color channel (0–255) is split into two bytes:

```
high = floor(value / 128)   →  0 or 1
low  = value % 128          →  0–127

firmware reconstructs:  value = high × 128 + low
```

Examples:

| Color value | high | low | Hex bytes |
|-------------|------|-----|-----------|
| 0 (off) | `00` | `00` | `00 00` |
| 51 | `00` | `33` | `00 33` |
| 128 | `01` | `00` | `01 00` |
| 255 (max) | `01` | `7F` | `01 7F` |

### JavaScript encoder

```js
function encodeChannel(v) {
  return [Math.floor(v / 128), v % 128];
}
```

### Example — set key 0 red, keys 12 and 24 blue

```js
const msg = [
  0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00, 0x15,
  0x02,                             // numGroups = 2

  // Group 0 — red on key 0
  0x01, 0x7F,                       // R = 255
  0x00, 0x00,                       // G = 0
  0x00, 0x00,                       // B = 0
  0x01,                             // keyCount = 1
  0x00,                             // key 0

  // Group 1 — blue on keys 12 and 24
  0x00, 0x00,                       // R = 0
  0x00, 0x00,                       // G = 0
  0x01, 0x7F,                       // B = 255
  0x02,                             // keyCount = 2
  0x0C, 0x18,                       // keys 12, 24

  0xF7
];
outputPort.send(msg);
```

### Delta updates (recommended)

To avoid redundant redraws, track which keys are currently lit and only send:
- New keys with their target color
- Previously lit keys that should now go dark (send with `[00 00 00 00 00 00]`)

This keeps messages small — typically 1–2 groups per chord change.

---

## 5. CMD 113 (0x71) — All lights off

Dedicated command to extinguish all LEDs immediately:

```
F0 05 30 7F 7F 20 00 71 00 F7
```

---

## 6. CMD 113 (0x71) — Palette mode (alternative)

Sets keys to firmware-defined palette colors (13 slots):

```
F0 05 30 7F 7F 20 00 71  <numKeys>
  <midiNote_0>  <paletteIndex_0>
  <midiNote_1>  <paletteIndex_1>
  …
F7
```

| Palette index | Color |
|---------------|-------|
| 0 | Off |
| 1 | Red |
| 2–11 | Orange → Cyan → Blue |
| 12 | Purple |

`midiNote` = key index + 48 (keyboard starts at MIDI 48 = C3).

> Note: all-off and palette mode share the same command byte (`0x71`).
> The firmware distinguishes them by content: `numKeys = 0` with no pairs = all-off;
> `numKeys > 0` with note/palette pairs = palette mode.

---

## 7. Note-on LED (legacy, avoid in new code)

The firmware also accepts standard MIDI note-on messages to light keys.
**Always use velocity = 64 (`0x40`) on channel 0:**

```
90 <midiNote> 40   →  key lights up
80 <midiNote> 00   →  key turns off
```

**Critical caveat — echo suppression required:**
The keyboard firmware echoes every note-on back to the host. A LED note-on at velocity 64 will be echoed as a note-on at velocity 64, which is indistinguishable from the player pressing the same key. You must suppress these echoes in your MIDI input handler:

```js
const pendingEchoes = new Map();  // midiNote → count

// Before sending a LED note-on:
pendingEchoes.set(note, (pendingEchoes.get(note) || 0) + 1);
outputPort.send([0x90, note, 0x40]);

// In your MIDI input handler:
function onMIDI(msg) {
  const [status, note, velocity] = msg.data;
  if ((status & 0xF0) === 0x90 && velocity === 64 && pendingEchoes.has(note)) {
    const n = pendingEchoes.get(note) - 1;
    if (n <= 0) pendingEchoes.delete(note); else pendingEchoes.set(note, n);
    return;  // drop the echo — do not treat as player input
  }
  // ... handle real player input ...
}
```

**Prefer CMD 15 (Section 4) over note-on LEDs** — CMD 15 does not echo.

---

## 8. Key layout

```
Key index:  0  1  2  3  4  5  6  7  8  9  10 11 12 ... 35
MIDI note: 48 49 50 51 52 53 54 55 56 57 58  59 60 ... 83
Note name: C3 C#3 D3 D#3 E3 F3 F#3 G3 G#3 A3 A#3 B3 C4 ... B5
```

- 36 keys total, 3 octaves (C3 – B5)
- Index 0 = leftmost key (C3), Index 35 = rightmost key (B5)
- White/black pattern per octave (C=0): `W B W B W W B W B W B W`

---

## 9. Precise timing (Web MIDI)

`outputPort.send(data, domTimestamp)` schedules the message to fire at a specific
`performance.now()` timestamp, bypassing JS event-loop jitter:

```js
const msUntilBeat = (audioCtxTime - audioContext.currentTime) * 1000;
const domTs = performance.now() + msUntilBeat;
outputPort.send(msg, Math.max(performance.now(), domTs));
```

Use this when synchronising LED changes to audio playback.
To cancel pre-scheduled messages (e.g. on Stop): `outputPort.clear()`.

---

## 10. Hardware latency note

Physical LED changes lag behind the moment the firmware receives the MIDI message by
approximately **150–250 ms** (varies by unit). When synchronising to audio:

- Fire the SysEx at the scheduled beat time (no advance)
- Delay the audio and any on-screen visuals by `HW_LATENCY_MS` (≈ 200 ms)
- All three (physical LED, audio, screen) then appear to coincide

---

## 11. Page-level hooks (PartyKeys web runtime)

If you build on top of `audio.js`, two `window` hooks are available:

| Hook | When called | Typical use |
|------|-------------|-------------|
| `window._pkMidiHook(msg)` | Every real (non-echo) MIDI input event | Chord detection, custom input handling |
| `window._pkOnMidiConnect()` | After device reconnect clears LEDs | Restore current LED state |

```js
// Example: restore chord LEDs after reconnect
window._pkOnMidiConnect = function() {
  window._pkSendColorSysEx(currentChordGroups);
};

// Example: detect held notes
window._pkMidiHook = function(msg) {
  const [status, note, velocity] = msg.data;
  if ((status & 0xF0) === 0x90 && velocity > 0) {
    heldNotes.add(note);
  } else {
    heldNotes.delete(note);
  }
};
```

---

## Quick reference

| Goal | Command |
|------|---------|
| Enter LED mode (required first) | `F0 05 30 7F 7F 20 00 0F 01 F7` |
| All lights off | `F0 05 30 7F 7F 20 00 71 00 F7` |
| Set palette colors by key index | CMD 14: `F0 05 30 7F 7F 20 00 14 <N> <index pal>× F7` |
| Set per-key RGB colors | CMD 15: `F0 05 30 7F 7F 20 00 15 <groups> F7` |
| Set palette colors | CMD 71: `F0 05 30 7F 7F 20 00 71 <N> <note pal>× F7` |
| Light single key (legacy) | Note-on ch0 vel=64; suppress echo |
