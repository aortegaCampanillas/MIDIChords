# PartyKeys Protocol — Developer Documentation (site snapshot)

> Snapshot of <https://protocol.partykeys.org/> converted to Markdown on 2026-10-05.
> Content kept as published (English). Only the HTML/UI chrome was removed.
> License: MIT. Spec repo: <https://github.com/allen4z/PartykeysProtocol>

*Light up any key, from anywhere.* The open MIDI + SysEx spec for PartyKeys
keyboards. Connect from a browser, a script, or hand it to your AI assistant.

---

## Quickstart

Plug in a PartyKeys 36, open Chrome DevTools on any page, and paste:

```js
const midi = await navigator.requestMIDIAccess({ sysex: true });
const out = [...midi.outputs.values()].find(p => /partykey/i.test(p.name));

// Enter LED mode (required once)
out.send([0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00, 0x0F, 0x01, 0xF7]);

// Light keys 17, 18, 19 red/green/blue
const enc = v => [Math.floor(v/128), v % 128];
out.send([
  0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00, 0x15, 0x03,
  ...enc(255), ...enc(0),   ...enc(0),   1, 17,
  ...enc(0),   ...enc(255), ...enc(0),   1, 18,
  ...enc(0),   ...enc(0),   ...enc(255), 1, 19,
  0xF7
]);
```

> **That's it.** Three things matter: (1) ask for SysEx access, (2) send the
> "enter LED mode" message once, (3) send CMD 15 per-key RGB messages whenever
> the lights should change. Everything else is convenience.

---

## Protocol

PartyKeys 36 — 36 keys, MIDI 48–83, USB. Three commands are all you need.

### PartyKeys 36

#### 1. Connect

SysEx must be explicitly enabled — without it every LED command is silently dropped.

```js
const access = await navigator.requestMIDIAccess({ sysex: true });
const out = [...access.outputs.values()].find(p => /partykey/i.test(p.name));
```

#### 2. Enter LED mode

Send once after each (re)connect. Color commands sent before this are no-ops.

```
F0 05 30 7F 7F 20 00 0F 01 F7
```

#### 3. CMD 15 — per-key RGB

Set any number of keys to any 24-bit RGB color in one message. Group keys that share a color.

```
F0 05 30 7F 7F 20 00 15 <numGroups>
  <group_0> <group_1> ...
F7

# Each group:
#   R_hi R_lo  G_hi G_lo  B_hi B_lo  keyCount  key0 key1 ...
```

| Field | Bytes | Range | Description |
|-------|-------|-------|-------------|
| `R_hi R_lo` | 2 | 0x00–0x01, 0x00–0x7F | Red channel (14-bit MIDI-safe) |
| `G_hi G_lo` | 2 | same | Green channel |
| `B_hi B_lo` | 2 | same | Blue channel |
| `keyCount` | 1 | 1–36 | Number of key indices that follow |
| `key0 … keyN` | N | 0–35 | Key indices (0 = leftmost C3, 35 = rightmost B5) |

Color encoding — MIDI is 7-bit, so each 0–255 channel splits into a pair:

```js
// v ∈ [0, 255]   →   [high, low]
const enc = v => [Math.floor(v / 128), v % 128];
// firmware reconstructs: value = high × 128 + low
```

| Color value | high | low | Hex bytes |
|-------------|------|-----|-----------|
| 0 (off) | `0x00` | `0x00` | `00 00` |
| 51 | `0x00` | `0x33` | `00 33` |
| 128 | `0x01` | `0x00` | `01 00` |
| 255 (max) | `0x01` | `0x7F` | `01 7F` |

#### 4. CMD 0x14 — Highlight / Darklight

Higher-level lighting that references a pre-loaded UI palette (`paletteUI_k[]`)
on the device. Two semantic states for guided-play scenarios (chord trainers,
sight-reading, sequencer playback) — Highlight for the key the player should
press now, Darklight as a dimmer preview of the upcoming key.

| State | Command | Palette slot | Brightness | Typical use |
|-------|---------|--------------|------------|-------------|
| Highlight (高亮) | `Send_LightUp (0x14)` | `paletteUI_k[n]` | × 1.0 | The key the player should press now |
| Darklight (预亮) | `Send_LightUp (0x14)` | `paletteUI_k[n+14]` | × 0.75 | Next upcoming key, dimmed as a preview |

**Palette layout (28 slots).** The UI palette is structured as:

| Slots | Color group |
|-------|-------------|
| 0 | Black (off) |
| 1 – 12 | Highlight colors — full brightness × 1.0 |
| 13 | Black (off) |
| 14 – 25 | Darklight colors — dim × 0.75 (same hues as 1–12) |
| 26, 27 | White |

**Wire format.** Both states are emitted as CMD 0x71 palette assignment. To
light an entire C3 octave (keys 48–59) at Highlight or Darklight:

```
# Highlight one C3 octave — palette slots 1–12 (full brightness × 1.0)
F0 05 30 7F 3F 20 00 71 0C
  30 01  31 02  32 03  33 04  34 05  35 06
  36 07  37 08  38 09  39 0A  3A 0B  3B 0C
F7

# Darklight the same keys — palette slots 14–25 (dim × 0.75, same hues)
F0 05 30 7F 3F 20 00 71 0C
  30 0E  31 0F  32 10  33 11  34 12  35 13
  36 14  37 15  38 16  39 17  3A 18  3B 19
F7
```

#### 5. All off

```
F0 05 30 7F 7F 20 00 71 00 F7
```

#### 6. Key layout

| Key index | MIDI note | Note name | Position |
|-----------|-----------|-----------|----------|
| 0 | 48 | C3 | Leftmost |
| 17 | 65 | F4 | Middle |
| 35 | 83 | B5 | Rightmost |

General formula: `midi_note = key_index + 48`. 36 keys total, 3 octaves C3–B5.

> **Note-on echo.** The legacy way to light a key (`0x90 note 0x40`) makes the
> firmware echo a note-on back as if the player pressed it. Use CMD 15 — it
> doesn't echo.

> **LED latency ≈ 200 ms.** Don't pre-fire the SysEx. Send it at the beat and
> delay your audio + visuals by the same constant.

### PopuPiano 29 (alt device)

29 keys, MIDI 48–76, USB or BLE. Two-step: upload palette, assign slots. No
"enter mode" needed.

#### 1. Upload a palette (CMD 0x1E)

Uploads N colors into the device palette starting at slot 1. Colors are 7-bit
RGB — scale 8-bit by `min(127, round(v / 2))`.

```
F0 03 1E <numColors> 01  <R G B> × N  F7

# Example: upload red, green, blue into slots 1–3
F0 03 1E 03 01  7F 00 00  00 7F 00  00 00 7F  F7
```

#### 2. Assign palette slots to keys (CMD 0x20)

Assigns a palette slot to each of the 29 keys. `lampID` is 0–28; `paletteSlot` 0
turns a key off.

```
F0 03 20 <numPairs>  <lampID paletteSlot> × N  F7
```

> **Tip.** Slot 0 is reserved as "off" and cannot be overwritten. The palette
> persists on the device until power-cycle, so live color updates only need to
> re-send CMD 0x20 — at audio rate if needed.

---

## SDK Examples

Same task in four languages: connect, init, light keys 17–19 red/green/blue.

### JavaScript (Browser · Web MIDI)

```js
const MFR = [0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00];
const enc = v => [Math.floor(v / 128), v % 128];

const access = await navigator.requestMIDIAccess({ sysex: true });
const out = [...access.outputs.values()].find(p => /partykey/i.test(p.name));
out.send([...MFR, 0x0F, 0x01, 0xF7]);   // enter LED mode

function setLEDs(groups) {
  const msg = [...MFR, 0x15, groups.length];
  for (const g of groups) {
    msg.push(...enc(g.rgb[0]), ...enc(g.rgb[1]), ...enc(g.rgb[2]));
    msg.push(g.keys.length, ...g.keys);
  }
  msg.push(0xF7);
  out.send(msg);
}

setLEDs([
  { rgb: [255, 0,   0  ], keys: [17] },
  { rgb: [0,   255, 0  ], keys: [18] },
  { rgb: [0,   0,   255], keys: [19] },
]);
```

### Python (mido)

`pip install mido python-rtmidi`

```python
import mido

MFR = [0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00]
enc = lambda v: [v // 128, v % 128]

out = mido.open_output(next(n for n in mido.get_output_names()
                            if 'partykey' in n.lower()))
out.send(mido.Message('sysex', data=MFR + [0x0F, 0x01]))   # enter LED mode

def set_leds(groups):
    payload = MFR + [0x15, len(groups)]
    for rgb, keys in groups:
        payload += enc(rgb[0]) + enc(rgb[1]) + enc(rgb[2])
        payload += [len(keys)] + list(keys)
    out.send(mido.Message('sysex', data=payload))

set_leds([
    ((255, 0,   0  ), [17]),
    ((0,   255, 0  ), [18]),
    ((0,   0,   255), [19]),
])
```

### Node.js (JZZ)

`npm install jzz`

```js
import JZZ from 'jzz';

const MFR = [0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00];
const enc = v => [Math.floor(v / 128), v % 128];

const engine = await JZZ();
const name = engine.info().outputs.find(p => /partykey/i.test(p.name)).name;
const out = JZZ().openMidiOut(name);

out.send([...MFR, 0x0F, 0x01, 0xF7]);   // enter LED mode

function setLEDs(groups) {
  const msg = [...MFR, 0x15, groups.length];
  for (const g of groups) {
    msg.push(...enc(g.rgb[0]), ...enc(g.rgb[1]), ...enc(g.rgb[2]));
    msg.push(g.keys.length, ...g.keys);
  }
  msg.push(0xF7);
  out.send(msg);
}

setLEDs([
  { rgb: [255, 0,   0  ], keys: [17] },
  { rgb: [0,   255, 0  ], keys: [18] },
  { rgb: [0,   0,   255], keys: [19] },
]);
```

### Swift (CoreMIDI)

Link `CoreMIDI.framework` — no third-party deps.

```swift
import CoreMIDI

let MFR: [UInt8] = [0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00]
func enc(_ v: UInt8) -> [UInt8] { [v / 128, v % 128] }

var client = MIDIClientRef(); var port = MIDIPortRef()
MIDIClientCreate("PK" as CFString, nil, nil, &client)
MIDIOutputPortCreate(client, "out" as CFString, &port)

var dest: MIDIEndpointRef = 0
for i in 0..<MIDIGetNumberOfDestinations() {
    let d = MIDIGetDestination(i)
    var n: Unmanaged<CFString>?
    MIDIObjectGetStringProperty(d, kMIDIPropertyName, &n)
    if ((n?.takeRetainedValue() as String?) ?? "").lowercased().contains("partykey") {
        dest = d; break
    }
}

func sendSysEx(_ data: [UInt8]) {
    var pkt = MIDIPacketList()
    let p = MIDIPacketListInit(&pkt)
    _ = MIDIPacketListAdd(&pkt, 1024, p, 0, data.count, data)
    MIDISend(port, dest, &pkt)
}

sendSysEx(MFR + [0x0F, 0x01, 0xF7])      // enter LED mode

func setLEDs(_ groups: [(rgb: (UInt8, UInt8, UInt8), keys: [UInt8])]) {
    var msg = MFR + [0x15, UInt8(groups.count)]
    for g in groups {
        msg += enc(g.rgb.0) + enc(g.rgb.1) + enc(g.rgb.2)
        msg += [UInt8(g.keys.count)] + g.keys
    }
    msg.append(0xF7)
    sendSysEx(msg)
}

setLEDs([
    (rgb: (255, 0,   0  ), keys: [17]),
    (rgb: (0,   255, 0  ), keys: [18]),
    (rgb: (0,   0,   255), keys: [19]),
])
```

---

## AI Assistant

The site also publishes a one-click LLM prompt and a `CLAUDE.md` /
`.cursorrules` template. Both only restate the protocol above (plus these
conventions), so they are summarised here instead of duplicated:

- Use a single helper `setLEDs(groups)` — never craft raw SysEx at call sites.
- Use delta updates: only send keys whose color is changing.
- Prefer CMD 15 over legacy note-on LEDs (those echo back as fake input).
- Hardware LED latency ≈ 200 ms; if syncing to audio, delay audio + visuals by
  `HW_LATENCY_MS` instead of pre-firing SysEx.
- Always `allOff()` on app teardown.
- Don't send 8-bit color on the wire — must be 7-bit encoded.
- PopuPiano: manufacturer header `03`, detect by port name `/popupiano/i`,
  custom colors in slots 1–127.

---

## FAQ

**My color commands do nothing.**
Three checks: (1) `{sysex: true}` in `requestMIDIAccess`, (2) sent "enter LED
mode" after connect, (3) you encoded each 8-bit channel as two 7-bit bytes.
That's 99% of cases.

**LEDs trail my audio.**
Hardware delay is ~150–250 ms. Don't pre-fire SysEx — send at the beat, then
delay your audio + visuals by ~200 ms (one constant).

**My input handler fires when I light a key.**
You're using legacy note-on LEDs (`0x90 note 0x40`). The firmware echoes those
as fake player input. Switch to CMD 15 — it doesn't echo.

**Which browsers / OSes work?**
PartyKeys 36 needs Chrome or Edge (Web MIDI + SysEx). For Safari/iOS use the
Swift example. The device is class-compliant USB MIDI — no driver install.
