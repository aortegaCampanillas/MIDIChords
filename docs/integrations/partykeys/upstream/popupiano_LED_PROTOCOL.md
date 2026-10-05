# PopuPiano LED Protocol

PopuPiano uses a two-step SysEx protocol to control per-key RGB lighting over MIDI.
No special mode-entry message is required — send the commands directly after connecting.

---

## Overview

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `CMD 0x1E` | Upload a color palette to the device |
| 2 | `CMD 0x20` | Map each key to a palette slot |

Colors are stored on the device after step 1. Step 2 can then reassign all 29 keys
in a single message, making live color updates fast and efficient.

---

## Key Layout

PopuPiano has **29 keys** spanning C3 to E5 (MIDI notes 48–76).

| Key Index | Note | MIDI |
|-----------|------|------|
| 0  | C3  | 48 |
| 1  | C#3 | 49 |
| 2  | D3  | 50 |
| … | … | … |
| 28 | E5  | 76 |

Key index 0 is the leftmost key (C3). Index 28 is the rightmost key (E5).

---

## Color Encoding

All RGB values are **7-bit** (0–127). Scale down from standard 8-bit (0–255):

```
value_7bit = min(127, round(value_8bit / 2))
```

**Palette slot 0 is reserved as "off"** and cannot be overwritten.
Custom colors occupy slots 1–127.

---

## CMD 0x1E — Set Palette

Uploads N colors into the device palette starting at slot 1.

### Format

```
F0 03 1E [numColors] 01 [R G B] × N F7
```

| Byte | Value | Description |
|------|-------|-------------|
| `F0` | — | SysEx start |
| `03` | — | Manufacturer ID |
| `1E` | — | Command: Set Palette |
| `[numColors]` | 1–127 | Number of colors being uploaded |
| `01` | — | Palette start slot (always 1) |
| `[R G B]` | 0–127 each | Color entries, repeated N times |
| `F7` | — | SysEx end |

### Example — upload 3 colors (red, green, blue)

```
F0 03 1E 03 01
   7F 00 00    ← slot 1: red   (r=127, g=0,   b=0)
   00 7F 00    ← slot 2: green (r=0,   g=127, b=0)
   00 00 7F    ← slot 3: blue  (r=0,   g=0,   b=127)
F7
```

---

## CMD 0x20 — Set Key Lamps

Assigns a palette slot to each of the 29 keys. Slot 0 turns a key off.

### Format

```
F0 03 20 [numPairs] [lampID paletteSlot] × N F7
```

| Byte | Value | Description |
|------|-------|-------------|
| `F0` | — | SysEx start |
| `03` | — | Manufacturer ID |
| `20` | — | Command: Set Key Lamps |
| `[numPairs]` | 1–29 | Number of key–slot pairs |
| `[lampID]` | 0–28 | Key index (0 = C3, 28 = E5) |
| `[paletteSlot]` | 0–127 | Palette slot (0 = off) |
| `F7` | — | SysEx end |

### Example — light keys 0, 7, 14 with red (slot 1), turn rest off

Send CMD 0x20 with all 29 pairs:

```
F0 03 20 1D
   00 01   ← key 0  (C3)  → red
   01 00   ← key 1  (C#3) → off
   02 00   ← key 2  (D3)  → off
   ...
   07 01   ← key 7  (G3)  → red
   ...
   0E 01   ← key 14 (D4)  → red
   ...
   1C 00   ← key 28 (E5)  → off
F7
```

---

## CMD 0x23 — Set Key Lamps (Teaching Mode)

Same wire format as CMD 0x20, but saves lamp assignments for **teaching mode**:
a configured key lights up only while held and turns off on release. Use this for
lesson recording / guided play, where each key should light on press and go dark on
release. Keys not listed in the message are left unmodified.

### Format

```
F0 03 23 [numPairs] [lampID paletteSlot] × N F7
```

| Byte | Value | Description |
|------|-------|-------------|
| `F0` | — | SysEx start |
| `03` | — | Manufacturer ID |
| `23` | — | Command: Set Key Lamps (Teaching Mode) |
| `[numPairs]` | 1–29 | Number of key–slot pairs |
| `[lampID]` | 0–28 | Key index (0 = C3, 28 = E5) |
| `[paletteSlot]` | 0–127 | Palette slot (0 = off) |
| `F7` | — | SysEx end |

### Example — single key

```
F0 03 23 01 00 03 F7   ← key 0 (C3) saved to palette slot 3; other keys unchanged
```

### Example — set all 29 keys to palette slot 5

```
F0 03 23 1D
   00 05   ← key 0  (C3)  → slot 5
   01 05   ← key 1  (C#3) → slot 5
   02 05   ← key 2  (D3)  → slot 5
   ...
   1C 05   ← key 28 (E5)  → slot 5
F7
```

> Unlike CMD 0x20, CMD 0x23 does **not** light keys immediately — each configured
> key lights only while physically held. To turn a teaching-mode key off permanently,
> assign it slot 0.

---

## Typical Flow

```
1. Connect to PopuPiano over BLE MIDI or USB MIDI.

2. Send CMD 0x1E to upload your color palette.
   (Only needed once, or when colors change.)

3. Send CMD 0x20 to assign palette slots to all 29 keys.
   (Repeat this message any time you want to update the lighting.)
```

---

## JavaScript Example (Web MIDI API)

```js
function scale7(v) { return Math.min(127, Math.round(v / 2)); }

// Step 1: upload palette — [red, green, blue]
const palette = [
  [255, 0,   0  ],  // slot 1: red
  [0,   255, 0  ],  // slot 2: green
  [0,   0,   255],  // slot 3: blue
];
const paletteMsg = [0xF0, 0x03, 0x1E, palette.length, 0x01];
for (const [r, g, b] of palette) paletteMsg.push(scale7(r), scale7(g), scale7(b));
paletteMsg.push(0xF7);
output.send(paletteMsg);

// Step 2: assign slots to keys (slot 0 = off)
const keySlots = new Array(29).fill(0);
keySlots[0]  = 1; // C3  → red
keySlots[7]  = 2; // G3  → green
keySlots[14] = 3; // D4  → blue

const lampMsg = [0xF0, 0x03, 0x20, 29];
for (let i = 0; i < 29; i++) lampMsg.push(i, keySlots[i]);
lampMsg.push(0xF7);
output.send(lampMsg);
```

---

## Notes

- There is no "enter LED mode" command. Send CMD 0x1E and CMD 0x20 directly.
- Palette slots persist on the device until overwritten or power-cycled.
- Sending CMD 0x20 with all slots set to 0 turns all lights off.
- The device name visible in the Web MIDI API contains `"popupiano"` (case-insensitive).

---

## License

MIT — see repository root.
