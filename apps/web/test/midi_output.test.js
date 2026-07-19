const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/midi_output.js");

const { createMidiOutputController } = globalThis.MidiChordsMidiOutput;

test("timed notes send matching note-on and note-off messages", () => {
  const messages = [];
  const timers = [];
  const output = { send: (message) => messages.push(message) };
  const controller = createMidiOutputController({
    getOutput: () => output,
    schedule: (callback, delay) => timers.push({ callback, delay }),
  });

  assert.equal(controller.sendNote(64, 350), true);
  assert.deepEqual(messages, [[0x90, 64, 64]]);
  assert.equal(timers[0].delay, 350);
  timers[0].callback();
  assert.deepEqual(messages, [[0x90, 64, 64], [0x80, 64, 0]]);
});

test("held notes are tracked and stopAll releases every note", () => {
  const messages = [];
  const heldNotes = new Set();
  const output = { send: (message) => messages.push(message) };
  const controller = createMidiOutputController({
    getOutput: () => output,
    heldNotes,
    velocity: 90,
  });

  controller.noteOn(60);
  controller.noteOn(67);
  assert.deepEqual([...heldNotes], [60, 67]);
  controller.stopAll();
  assert.equal(heldNotes.size, 0);
  assert.deepEqual(messages, [
    [0x90, 60, 90],
    [0x90, 67, 90],
    [0x80, 60, 0],
    [0x80, 67, 0],
  ]);
});

test("program changes follow General MIDI instrument numbers", () => {
  const messages = [];
  let output = { send: (message) => messages.push(message) };
  const controller = createMidiOutputController({ getOutput: () => output });

  assert.equal(controller.programChange("piano"), true);
  assert.equal(controller.programChange("guitar"), true);
  assert.deepEqual(messages, [[0xC0, 0], [0xC0, 24]]);
  output = null;
  assert.equal(controller.noteOn(60), false);
  assert.equal(controller.heldNotes.size, 0);
});
