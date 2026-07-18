const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/music_notation.js");
require("../static/staff_geometry.js");

const {
  midiToDiatonicIndex,
  midiToTrebleY,
  midiToBassY,
  ledgerLineYs,
} = globalThis.MidiChordsStaffGeometry;

test("staff geometry maps reference notes to their bottom lines", () => {
  assert.equal(midiToTrebleY(64, 40, 12), 88); // E4
  assert.equal(midiToBassY(43, 120, 12), 168); // G2
});

test("enharmonic spelling changes the diatonic staff position", () => {
  assert.equal(midiToDiatonicIndex(61, false), 28); // C#4
  assert.equal(midiToDiatonicIndex(61, true), 29); // Db4
  assert.equal(midiToTrebleY(61, 40, 12, true), midiToTrebleY(61, 40, 12, false) - 6);
});

test("ledger geometry returns only complete lines beyond the staff", () => {
  assert.deepEqual(ledgerLineYs(15, 40, 10), [30, 20]);
  assert.deepEqual(ledgerLineYs(105, 40, 10), [90, 100]);
  assert.deepEqual(ledgerLineYs(60, 40, 10), []);
  assert.deepEqual(ledgerLineYs(20, 40, 0), []);
});
