const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/staff_beam_geometry.js");

const { commonStemUp, beamSegments } = globalThis.MidiChordsStaffBeamGeometry;

test("beamed notes on opposite sides choose one common stem direction", () => {
  assert.equal(commonStemUp([110, 70], 100), false);
  assert.equal(commonStemUp([130, 80], 100), true);
});

test("empty and invalid groups use a safe upward default", () => {
  assert.equal(commonStemUp([], 100), true);
  assert.equal(commonStemUp([NaN], 100), true);
});

test("secondary sixteenth beams remain parallel to the primary beam", () => {
  const segments = beamSegments([
    { stemX: 10, stemEndY: 30, stemUp: true, base: "e" },
    { stemX: 50, stemEndY: 42, stemUp: true, base: "s" },
  ]);
  assert.equal(segments.length, 2);
  const primarySlope = (segments[0].yb - segments[0].ya) / (segments[0].xb - segments[0].xa);
  const secondarySlope = (segments[1].yb - segments[1].ya) / (segments[1].xb - segments[1].xa);
  assert.equal(secondarySlope, primarySlope);
});

test("eighth-note groups expose only the primary segment", () => {
  assert.equal(beamSegments([
    { stemX: 10, stemEndY: 30, stemUp: false, base: "e" },
    { stemX: 50, stemEndY: 42, stemUp: false, base: "e" },
  ]).length, 1);
});
