const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/partykeys_leds.js");

const {
  ALL_OFF,
  ENTER_LED_MODE,
  buildRgbMessage,
  createPartyKeysController,
  encodeChannel,
  isPartyKeysPortName,
  noteToKeyIndex,
  parseDeviceMessage,
} = globalThis.MidiChordsPartyKeys;

function hex(message) {
  return message.map((b) => b.toString(16).toUpperCase().padStart(2, "0")).join(" ");
}

function fakeController() {
  const messages = [];
  let output = { send: (message) => messages.push(Array.from(message)) };
  const controller = createPartyKeysController({ getOutput: () => output });
  return { controller, messages, setOutput: (next) => { output = next; } };
}

test("color channels split into two 7-bit bytes", () => {
  assert.deepEqual(encodeChannel(0), [0, 0]);
  assert.deepEqual(encodeChannel(51), [0, 0x33]);
  assert.deepEqual(encodeChannel(128), [1, 0]);
  assert.deepEqual(encodeChannel(255), [1, 0x7F]);
  assert.deepEqual(encodeChannel(999), [1, 0x7F]);
});

test("RGB message matches the bytes verified on hardware", () => {
  const message = buildRgbMessage([
    { rgb: [255, 0, 0], keys: [0] },
    { rgb: [0, 255, 0], keys: [17] },
    { rgb: [0, 0, 255], keys: [35] },
  ]);
  assert.equal(
    hex(message),
    "F0 05 30 7F 7F 20 00 15 03 01 7F 00 00 00 00 01 00 00 00 01 7F 00 00 01 11 00 00 00 00 01 7F 01 23 F7",
  );
  assert.equal(hex(ENTER_LED_MODE), "F0 05 30 7F 7F 20 00 0F 01 F7");
  assert.equal(hex(ALL_OFF), "F0 05 30 7F 7F 20 00 71 00 F7");
});

test("port names are matched case-insensitively", () => {
  assert.equal(isPartyKeysPortName("PartyKeys"), true);
  assert.equal(isPartyKeysPortName("partykeys 36 MIDI 1"), true);
  assert.equal(isPartyKeysPortName("IAC Driver Bus 1"), false);
  assert.equal(isPartyKeysPortName(null), false);
});

test("octave notices decode signed 7-bit octave and transpose", () => {
  const notice = (oct, trans) => [0xF0, 0x05, 0x30, 0x20, 0x00, 0x00, 0x3F, 0x18, oct, trans, 0xF7];
  assert.deepEqual(parseDeviceMessage(notice(0x00, 0x00)), { type: "octave", octave: 0, transpose: 0 });
  assert.deepEqual(parseDeviceMessage(notice(0x7F, 0x00)), { type: "octave", octave: -1, transpose: 0 });
  assert.deepEqual(parseDeviceMessage(new Uint8Array(notice(0x00, 0x01))), { type: "octave", octave: 0, transpose: 1 });
  // Byte 5 follows the keyboard's MIDI channel (seen as 01 on channel 2).
  const onChannel2 = [0xF0, 0x05, 0x30, 0x20, 0x00, 0x01, 0x3F, 0x18, 0x7F, 0x00, 0xF7];
  assert.deepEqual(parseDeviceMessage(onChannel2), { type: "octave", octave: -1, transpose: 0 });
  assert.equal(parseDeviceMessage([0xF0, 0x05, 0x30, 0x10, 0x00, 0x00, 0x3F, 0x16, 0xF7]), null);
  assert.equal(parseDeviceMessage([0x90, 60, 64]), null);
});

test("notes map to physical keys using octave and transpose", () => {
  assert.equal(noteToKeyIndex(48), 0);
  assert.equal(noteToKeyIndex(83), 35);
  assert.equal(noteToKeyIndex(84), null);
  assert.equal(noteToKeyIndex(47), null);
  // OCT-1: the leftmost key sends 36 (observed on hardware).
  assert.equal(noteToKeyIndex(36, { octave: -1 }), 0);
  // Transpose +1: the leftmost key sends 49.
  assert.equal(noteToKeyIndex(49, { transpose: 1 }), 0);
  assert.equal(noteToKeyIndex(90, { fold: true }), 30);
  assert.equal(noteToKeyIndex(30, { fold: true }), 6);
  assert.equal(noteToKeyIndex(Number.NaN, { fold: true }), null);
});

test("connect enters LED mode and clears the keyboard", () => {
  const { controller, messages } = fakeController();
  assert.equal(controller.connect(), true);
  assert.deepEqual(messages, [Array.from(ENTER_LED_MODE), Array.from(ALL_OFF)]);
});

test("render only sends the keys that change", () => {
  const { controller, messages } = fakeController();
  const green = [0, 255, 0];
  controller.render(new Map([[48, green], [52, green], [55, green]]));
  assert.deepEqual(messages.at(-1), buildRgbMessage([{ rgb: green, keys: [0, 4, 7] }]));

  const sent = messages.length;
  controller.render(new Map([[48, green], [52, green], [55, green]]));
  assert.equal(messages.length, sent, "identical frame sends nothing");

  controller.render(new Map([[52, green], [55, green]]));
  assert.deepEqual(messages.at(-1), buildRgbMessage([{ rgb: [0, 0, 0], keys: [0] }]));

  controller.render(new Map([[52, [255, 0, 0]], [55, green], [60, green]]));
  assert.deepEqual(messages.at(-1), buildRgbMessage([
    { rgb: [255, 0, 0], keys: [4] },
    { rgb: green, keys: [12] },
  ]));
});

test("later entries win when folded notes share a key", () => {
  const { controller, messages } = fakeController();
  // 36 folds up onto key 0, the same key as 48.
  controller.render([[48, [0, 0, 255]], [36, [255, 255, 255]]], { fold: true });
  assert.deepEqual(messages.at(-1), buildRgbMessage([{ rgb: [255, 255, 255], keys: [0] }]));
});

test("device shift changes move the lit keys", () => {
  const { controller, messages } = fakeController();
  const blue = [0, 0, 255];
  controller.render([[48, blue]]);
  assert.equal(controller.setDeviceShift({ octave: -1, transpose: 0 }), true);
  assert.equal(controller.setDeviceShift({ octave: -1, transpose: 0 }), false);
  controller.render([[48, blue]]);
  assert.deepEqual(messages.at(-1), buildRgbMessage([
    { rgb: blue, keys: [12] },
    { rgb: [0, 0, 0], keys: [0] },
  ]));
  controller.connect();
  assert.deepEqual(controller.getDeviceShift(), { octave: 0, transpose: 0 });
});

test("missing output forgets the lit state so the next frame is resent", () => {
  const { controller, messages, setOutput } = fakeController();
  const red = [255, 0, 0];
  setOutput(null);
  assert.equal(controller.render([[48, red]]), false);
  assert.equal(messages.length, 0);
  setOutput({ send: (message) => messages.push(Array.from(message)) });
  assert.equal(controller.render([[48, red]]), true);
  assert.deepEqual(messages.at(-1), buildRgbMessage([{ rgb: red, keys: [0] }]));
  assert.equal(controller.clear(), true);
  assert.deepEqual(messages.at(-1), Array.from(ALL_OFF));
});
