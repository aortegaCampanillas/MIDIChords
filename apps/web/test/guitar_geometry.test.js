const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/guitar_geometry.js");

const { findBarreSegments } = globalThis.MidiChordsGuitarGeometry;

test("full barre spans the first and last sounding strings", () => {
  assert.deepEqual(
    findBarreSegments([1, 1, 3, 3, 1, 1], [1, 1, 3, 4, 1, 1]),
    {
      segments: [{ fret: 1, finger: 1, start: 0, end: 5, covered: [0, 1, 4, 5] }],
      coveredIndexes: [0, 1, 4, 5],
    },
  );
});

test("partial barres require contiguous runs and can produce separate segments", () => {
  assert.deepEqual(
    findBarreSegments([3, 5, 5, 7, 5, 5], [2, 1, 1, 3, 1, 1]),
    {
      segments: [
        { fret: 5, finger: 1, start: 1, end: 2, covered: [1, 2] },
        { fret: 5, finger: 1, start: 4, end: 5, covered: [4, 5] },
      ],
      coveredIndexes: [1, 2, 4, 5],
    },
  );
});

test("muted strings set sounding boundaries and invalid input is safe", () => {
  assert.deepEqual(
    findBarreSegments([-1, 3, 3, 5, 4, 3], [0, 1, 1, 3, 2, 1]),
    {
      segments: [{ fret: 3, finger: 1, start: 1, end: 5, covered: [1, 2, 5] }],
      coveredIndexes: [1, 2, 5],
    },
  );
  assert.deepEqual(findBarreSegments([1, 1], [1]), { segments: [], coveredIndexes: [] });
  assert.deepEqual(findBarreSegments([-1, -1], [0, 0]), { segments: [], coveredIndexes: [] });
});
