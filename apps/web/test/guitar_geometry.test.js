const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/guitar_geometry.js");

const {
  findBarreSegments,
  calculateFretboardLayout,
  fretCenterX,
  scaleClientPoint,
  findCircularHitRegion,
} = globalThis.MidiChordsGuitarGeometry;

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

test("left-handed fretboard layout mirrors horizontal geometry", () => {
  const right = calculateFretboardLayout({
    width: 1000, height: 240, frets: 15, stringCount: 6, leftHanded: false,
  });
  const left = calculateFretboardLayout({
    width: 1000, height: 240, frets: 15, stringCount: 6, leftHanded: true,
  });

  assert.equal(right.nutX + left.nutX, 1000);
  assert.equal(right.boardEdgeX + left.boardEdgeX, 1000);
  assert.equal(right.openX + left.openX, 1000);
  assert.equal(right.dir, 1);
  assert.equal(left.dir, -1);
  assert.equal(fretCenterX(right, 7) + fretCenterX(left, 7), 1000);
  assert.equal(right.top, left.top);
  assert.equal(right.yGap, left.yGap);
});

test("fretboard vertical band clamps and open fret has its own center", () => {
  const short = calculateFretboardLayout({
    width: 1000, height: 180, frets: 15, stringCount: 6, leftHanded: false,
  });
  const tall = calculateFretboardLayout({
    width: 1000, height: 400, frets: 15, stringCount: 6, leftHanded: false,
  });
  assert.equal(short.stringBand, 116);
  assert.equal(tall.stringBand, 148);
  assert.equal(fretCenterX(short, 0), (short.openX + short.nutX) / 2);
});

test("canvas point scaling and circular hit testing are independent of the DOM", () => {
  const point = scaleClientPoint(60, 45, { left: 10, top: 20, width: 100, height: 50 }, 1000, 200);
  assert.deepEqual(point, { x: 500, y: 100 });
  const regions = [{ note: 60, x: 500, y: 100, r: 12 }];
  assert.equal(findCircularHitRegion(regions, 508, 108), regions[0]);
  assert.equal(findCircularHitRegion(regions, 513, 100), null);
  assert.equal(findCircularHitRegion(null, 0, 0), null);
});
