(function initPartyKeysLeds(global) {
  "use strict";

  // Protocol and hardware findings: docs/integrations/partykeys/README.md.
  const HEADER = Object.freeze([0xF0, 0x05, 0x30, 0x7F, 0x7F, 0x20, 0x00]);
  // While a key is held the firmware paints it white over any host color; the
  // host color is kept and shows again on release (see README, LED modes).
  const ENTER_LED_MODE = Object.freeze([...HEADER, 0x0F, 0x01, 0xF7]);
  const ALL_OFF = Object.freeze([...HEADER, 0x71, 0x00, 0xF7]);
  const CMD_RGB = 0x15;
  const KEY_COUNT = 36;
  const BASE_NOTE = 48;
  // Sent by the keyboard on OCT± / Fn+OCT±: F0 05 30 20 00 00 3F 18 <octave> <transpose> F7.
  const OCTAVE_NOTICE_PREFIX = Object.freeze([0xF0, 0x05, 0x30, 0x20, 0x00, 0x00, 0x3F, 0x18]);

  // Chosen on real hardware: orange/magenta are hard to tell apart and
  // channel values below ~16 are barely visible.
  const COLORS = Object.freeze({
    // Hands follow the app's piano colors (right = blue, left = orange): a
    // dim idle tone and the same hue at full intensity while played.
    rightIdle: Object.freeze([0, 24, 72]),
    rightPlayed: Object.freeze([0, 110, 255]),
    leftIdle: Object.freeze([72, 20, 0]),
    leftPlayed: Object.freeze([255, 80, 0]),
    // Badge marks shared by scales and intervals: tonic/first note green,
    // other notes amber/orange; dim while idle, full intensity while sounding.
    markTonic: Object.freeze([0, 64, 0]),
    markTonicPlayed: Object.freeze([0, 255, 0]),
    markNote: Object.freeze([80, 24, 0]),
    markNotePlayed: Object.freeze([255, 90, 0]),
    // Note detection: last detected note, brighter while ▶ is held.
    noteIdle: Object.freeze([0, 40, 110]),
    notePlayed: Object.freeze([0, 160, 255]),
    active: Object.freeze([0, 160, 255]),
    correct: Object.freeze([0, 255, 0]),
    wrong: Object.freeze([255, 0, 0]),
  });

  const BLACK = Object.freeze([0, 0, 0]);

  function isPartyKeysPortName(name) {
    return /partykey/i.test(String(name || ""));
  }

  function clampChannel(value) {
    const v = Math.round(Number(value) || 0);
    return Math.min(255, Math.max(0, v));
  }

  function encodeChannel(value) {
    const v = clampChannel(value);
    return [Math.floor(v / 128), v % 128];
  }

  function buildRgbMessage(groups) {
    const message = [...HEADER, CMD_RGB, groups.length];
    for (const group of groups) {
      const [r, g, b] = group.rgb;
      message.push(...encodeChannel(r), ...encodeChannel(g), ...encodeChannel(b));
      message.push(group.keys.length, ...group.keys);
    }
    message.push(0xF7);
    return message;
  }

  function signed7(value) {
    return value >= 64 ? value - 128 : value;
  }

  function parseDeviceMessage(data) {
    const bytes = Array.from(data || []);
    if (bytes.length !== OCTAVE_NOTICE_PREFIX.length + 3) return null;
    if (!OCTAVE_NOTICE_PREFIX.every((byte, idx) => bytes[idx] === byte)) return null;
    if (bytes[bytes.length - 1] !== 0xF7) return null;
    return {
      type: "octave",
      octave: signed7(bytes[8]),
      transpose: signed7(bytes[9]),
    };
  }

  function noteToKeyIndex(note, { octave = 0, transpose = 0, fold = false } = {}) {
    const midi = Number(note);
    if (!Number.isFinite(midi)) return null;
    let idx = Math.round(midi) - BASE_NOTE - 12 * octave - transpose;
    if (fold) {
      while (idx < 0) idx += 12;
      while (idx >= KEY_COUNT) idx -= 12;
    }
    return idx >= 0 && idx < KEY_COUNT ? idx : null;
  }

  function colorKey(rgb) {
    return rgb.map(clampChannel).join(",");
  }

  function createPartyKeysController({ getOutput }) {
    let shift = { octave: 0, transpose: 0 };
    // keyIndex -> "r,g,b" of what the device currently shows.
    let lit = new Map();

    function send(message) {
      const output = getOutput();
      if (!output) return false;
      try {
        output.send(message);
        return true;
      } catch (_error) {
        return false;
      }
    }

    function connect() {
      shift = { octave: 0, transpose: 0 };
      lit = new Map();
      const entered = send(Array.from(ENTER_LED_MODE));
      send(Array.from(ALL_OFF));
      return entered;
    }

    function setDeviceShift({ octave = 0, transpose = 0 } = {}) {
      const next = { octave: Number(octave) || 0, transpose: Number(transpose) || 0 };
      const changed = next.octave !== shift.octave || next.transpose !== shift.transpose;
      shift = next;
      return changed;
    }

    function getDeviceShift() {
      return { ...shift };
    }

    // colorByNote: iterable of [midiNote, [r, g, b]]; later entries win when
    // several notes fold onto the same key, so pass them in rising priority.
    function render(colorByNote, { fold = false } = {}) {
      const target = new Map();
      for (const [note, rgb] of colorByNote || []) {
        const idx = noteToKeyIndex(note, { ...shift, fold });
        if (idx == null || !rgb) continue;
        const key = colorKey(rgb);
        if (key === colorKey(BLACK)) target.delete(idx);
        else target.set(idx, key);
      }

      const changes = new Map();
      for (const [idx, key] of target) {
        if (lit.get(idx) !== key) changes.set(idx, key);
      }
      for (const idx of lit.keys()) {
        if (!target.has(idx)) changes.set(idx, colorKey(BLACK));
      }
      if (!changes.size) return true;

      const keysByColor = new Map();
      for (const [idx, key] of changes) {
        if (!keysByColor.has(key)) keysByColor.set(key, []);
        keysByColor.get(key).push(idx);
      }
      const groups = Array.from(keysByColor, ([key, keys]) => ({
        rgb: key.split(",").map(Number),
        keys: keys.sort((a, b) => a - b),
      }));
      if (!send(buildRgbMessage(groups))) {
        lit = new Map();
        return false;
      }
      lit = target;
      return true;
    }

    function clear() {
      const hadOutput = send(Array.from(ALL_OFF));
      lit = new Map();
      return hadOutput;
    }

    return Object.freeze({ connect, setDeviceShift, getDeviceShift, render, clear });
  }

  global.MidiChordsPartyKeys = Object.freeze({
    ALL_OFF,
    BASE_NOTE,
    COLORS,
    ENTER_LED_MODE,
    KEY_COUNT,
    buildRgbMessage,
    createPartyKeysController,
    encodeChannel,
    isPartyKeysPortName,
    noteToKeyIndex,
    parseDeviceMessage,
  });
})(globalThis);
