const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/playback_highlight.js");

const {
  isChordPlaybackMode,
  normalizePlaybackNotes,
  isPlaybackNoteActive,
  createPlaybackHighlighter,
} = globalThis.MidiChordsPlaybackHighlight;

test("generation and circle of fifths share chord playback highlighting", () => {
  assert.equal(isChordPlaybackMode("generation"), true);
  assert.equal(isChordPlaybackMode("circle_fifths"), true);
  assert.equal(isChordPlaybackMode("scales"), false);
});

test("playback notes support exact piano and pitch-class guitar matching", () => {
  const notes = normalizePlaybackNotes([60, "64", 67, 67, "invalid"]);

  assert.deepEqual([...notes], [60, 64, 67]);
  assert.equal(isPlaybackNoteActive(64, notes), true);
  assert.equal(isPlaybackNoteActive(76, notes), false);
  assert.equal(isPlaybackNoteActive(76, notes, { matchPitchClass: true }), true);
  assert.equal(isPlaybackNoteActive(61, notes, { matchPitchClass: true }), false);
});

test("timed playback renders immediately and clears every visual surface", () => {
  const changes = [];
  let renderCount = 0;
  let timer = null;
  const highlighter = createPlaybackHighlighter({
    onChange: (notes) => changes.push([...notes]),
    render: () => { renderCount += 1; },
    schedule: (callback, delay) => {
      timer = { callback, delay };
      return timer;
    },
    cancel: () => { timer = null; },
  });

  highlighter.showFor([60, 64, 67], 1500);
  assert.deepEqual(changes, [[60, 64, 67]]);
  assert.equal(renderCount, 1);
  assert.equal(timer.delay, 1500);

  timer.callback();
  assert.deepEqual(changes, [[60, 64, 67], []]);
  assert.equal(renderCount, 2);
});

test("held playback replaces pending timers and clear is idempotent", () => {
  const changes = [];
  const cancelled = [];
  let timerId = 0;
  const highlighter = createPlaybackHighlighter({
    onChange: (notes) => changes.push([...notes]),
    render: () => {},
    schedule: () => ++timerId,
    cancel: (id) => cancelled.push(id),
  });

  highlighter.showFor([60], 1000);
  highlighter.show([62]);
  highlighter.clear();
  highlighter.clear();

  assert.deepEqual(cancelled, [1]);
  assert.deepEqual(changes, [[60], [62], []]);
});
