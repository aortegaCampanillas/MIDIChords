const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/guitar_geometry.js");
require("../static/guitar_canvas.js");

const { calculateFretboardLayout } = globalThis.MidiChordsGuitarGeometry;
const { drawFretboardFrame } = globalThis.MidiChordsGuitarCanvas;

function recordingContext() {
  const calls = [];
  const target = { calls };
  return new Proxy(target, {
    set(object, property, value) {
      calls.push(["set", property, value]);
      object[property] = value;
      return true;
    },
    get(object, property) {
      if (property in object) return object[property];
      return (...args) => calls.push([property, ...args]);
    },
  });
}

test("frame paints background, board, nut, frets, and ordered labels", () => {
  const ctx = recordingContext();
  const layout = calculateFretboardLayout({
    width: 1000,
    height: 240,
    frets: 3,
    stringCount: 6,
    leftHanded: false,
  });

  drawFretboardFrame(ctx, { layout, width: 1000, height: 240, frets: 3 });

  assert.deepEqual(ctx.calls.find((call) => call[0] === "fillRect"), ["fillRect", 0, 0, 1000, 240]);
  assert.equal(ctx.calls.filter((call) => call[0] === "stroke").length, 7);
  assert.deepEqual(
    ctx.calls.filter((call) => call[0] === "fillText").map((call) => call[1]),
    ["0", "1", "2"],
  );
  assert.deepEqual(ctx.calls.slice(-2), [
    ["set", "textAlign", "start"],
    ["set", "textBaseline", "alphabetic"],
  ]);
});

test("left-handed frame mirrors fret and label coordinates", () => {
  const rightCtx = recordingContext();
  const leftCtx = recordingContext();
  const base = { width: 1000, height: 240, frets: 3, stringCount: 6 };
  const right = calculateFretboardLayout({ ...base, leftHanded: false });
  const left = calculateFretboardLayout({ ...base, leftHanded: true });

  drawFretboardFrame(rightCtx, { layout: right, width: 1000, height: 240, frets: 3 });
  drawFretboardFrame(leftCtx, { layout: left, width: 1000, height: 240, frets: 3 });

  const rightLabels = rightCtx.calls.filter((call) => call[0] === "fillText");
  const leftLabels = leftCtx.calls.filter((call) => call[0] === "fillText");
  rightLabels.forEach((call, index) => {
    assert.equal(call[2] + leftLabels[index][2], 1000);
  });
});
