const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/staff_beam_geometry.js");

const { commonStemUp } = globalThis.MidiChordsStaffBeamGeometry;

test("beamed notes on opposite sides choose one common stem direction", () => {
  assert.equal(commonStemUp([110, 70], 100), false);
  assert.equal(commonStemUp([130, 80], 100), true);
});

test("empty and invalid groups use a safe upward default", () => {
  assert.equal(commonStemUp([], 100), true);
  assert.equal(commonStemUp([NaN], 100), true);
});
