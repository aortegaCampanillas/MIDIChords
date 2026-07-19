const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/music_notation.js");
require("../static/staff_geometry.js");

const {
  midiToDiatonicIndex,
  midiToTrebleY,
  midiToBassY,
  ledgerLineYs,
  closestPitchClassMidi,
  mapPianoInputToStaffMidi,
  expandPianoPlayingNotesForStaff,
  mapPianoHeldNotesToStaff,
  buildScaleStaffEntries,
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

test("current scale note uses the closest displayed octave", () => {
  assert.equal(closestPitchClassMidi([55, 67, 79], 91), 79);
  assert.equal(closestPitchClassMidi([48, 72], 60), 48);
  assert.equal(closestPitchClassMidi([49, 61], 60), 60);
  assert.equal(closestPitchClassMidi([], 65), 65);
  assert.equal(closestPitchClassMidi([60], null), null);
});

test("piano input and playback notes map to displayed staff octaves", () => {
  assert.equal(mapPianoInputToStaffMidi([48, 60], 48), 48);
  assert.equal(mapPianoInputToStaffMidi([60], 48), 60);
  assert.equal(mapPianoInputToStaffMidi([72], 48), 48);
  assert.deepEqual(
    Array.from(expandPianoPlayingNotesForStaff([48, 60], new Set([60, 67]))).sort((a, b) => a - b),
    [48, 60, 67],
  );
  assert.deepEqual(
    Array.from(mapPianoHeldNotesToStaff([60, 64], new Set([48, 64]))).sort((a, b) => a - b),
    [60, 64],
  );
});

test("scale staff entries pair left and right hands by degree", () => {
  assert.deepEqual(
    buildScaleStaffEntries([60, 62, 64], [48, 50]),
    [
      { midi: 48, degree: 0 },
      { midi: 60, degree: 0 },
      { midi: 50, degree: 1 },
      { midi: 62, degree: 1 },
      { midi: 64, degree: 2 },
    ],
  );
});
