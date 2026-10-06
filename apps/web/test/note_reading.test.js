const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/note_reading.js");

const {
  READING_RANGES,
  createReadingSession,
  createUtteranceTracker,
  generateReadingSequence,
  naturalNotesInRange,
  noteLabel,
  normalizeWord,
  recognizerVocabulary,
  stepForMidi,
  stepForWord,
} = globalThis.MidiChordsNoteReading;

function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) % 2147483648;
    return s / 2147483648;
  };
}

test("naturals are listed inside each clef range", () => {
  assert.deepEqual(naturalNotesInRange(...READING_RANGES.treble.staff), [64, 65, 67, 69, 71, 72, 74, 76, 77]);
  assert.deepEqual(naturalNotesInRange(...READING_RANGES.bass.staff), [43, 45, 47, 48, 50, 52, 53, 55, 57]);
  assert.equal(naturalNotesInRange(...READING_RANGES.treble.ledger)[0], 57);
  assert.equal(naturalNotesInRange(...READING_RANGES.bass.ledger).at(-1), 64);
});

test("sequences stay in range, use naturals and never repeat consecutively", () => {
  for (const clef of ["treble", "bass"]) {
    for (const range of ["staff", "ledger"]) {
      const [low, high] = READING_RANGES[clef][range];
      const notes = generateReadingSequence({ clef, range, length: 200, random: seededRandom(3) });
      assert.equal(notes.length, 200);
      notes.forEach((midi, i) => {
        assert.ok(midi >= low && midi <= high, `${midi} outside ${clef}/${range}`);
        assert.notEqual(stepForMidi(midi), null, `${midi} is not natural`);
        if (i) assert.notEqual(midi, notes[i - 1]);
      });
    }
  }
});

test("a new round never starts on the previous round's last note", () => {
  for (let seed = 1; seed < 50; seed += 1) {
    const [first] = generateReadingSequence({ length: 1, after: 64, random: seededRandom(seed) });
    assert.notEqual(first, 64);
  }
});

test("notes are labelled per language by pitch class", () => {
  const scale = [60, 62, 64, 65, 67, 69, 71];
  assert.deepEqual(scale.map((m) => noteLabel(m, "es")), ["do", "re", "mi", "fa", "sol", "la", "si"]);
  assert.deepEqual(scale.map((m) => noteLabel(m, "en")), ["C", "D", "E", "F", "G", "A", "B"]);
  assert.equal(noteLabel(48, "es"), "do");
  assert.equal(stepForMidi(61), null);
  assert.equal(noteLabel(61, "en"), null);
});

test("spoken words map to diatonic steps per language", () => {
  assert.deepEqual(recognizerVocabulary("es"), ["do", "re", "mi", "fa", "sol", "la", "si"]);
  assert.deepEqual(recognizerVocabulary("en"), ["see", "dee", "ee", "eff", "gee", "ay", "bee"]);
  assert.equal(stepForWord("Sol", "es"), 4);
  assert.equal(stepForWord("gee", "en"), 4);
  assert.equal(stepForWord("bee", "en"), 6);
  assert.equal(stepForWord("sol", "en"), null);
  assert.equal(stepForWord("[unk]", "es"), null);
});

test("words are normalized before matching", () => {
  assert.equal(normalizeWord(" Sí "), "si");
  assert.equal(normalizeWord("SOL"), "sol");
});

test("the tracker emits each word once across partial and final results", () => {
  const heard = [];
  const tracker = createUtteranceTracker((word, source) => heard.push(`${source}:${word}`));
  tracker.partial("do");
  tracker.partial("do re");
  tracker.partial("do re");
  tracker.final("do re mi");
  tracker.partial("fa");
  tracker.final("fa");
  assert.deepEqual(heard, ["partial:do", "partial:re", "final:mi", "partial:fa"]);
});

test("skipping mid-utterance drops the rest of that utterance only", () => {
  const heard = [];
  const tracker = createUtteranceTracker((word) => heard.push(word));
  tracker.partial("sol");
  tracker.skipCurrent();
  tracker.partial("sol");
  tracker.final("sol");
  tracker.partial("la");
  tracker.final("la");
  assert.deepEqual(heard, ["sol", "la"]);

  // Between utterances there is nothing to skip: the next word still counts.
  tracker.skipCurrent();
  tracker.partial("si");
  tracker.final("si");
  assert.deepEqual(heard, ["sol", "la", "si"]);
});

test("a session waits on wrong answers and advances on the right step", () => {
  const session = createReadingSession([60, 64, 67]);
  assert.deepEqual(session.answer(1), { result: "wrong", expected: 0, heard: 1, position: 0 });
  assert.equal(session.position, 0);
  assert.deepEqual(session.answer(0), { result: "correct", position: 0, done: false });
  assert.equal(session.answer(null).result, "ignored");
  session.answer(stepForWord("ee", "en"));
  assert.deepEqual(session.answer(stepForWord("sol", "es")), { result: "correct", position: 2, done: true });
  assert.equal(session.done, true);
  assert.equal(session.answer(0).result, "ignored");
  const { correct, wrong, missed } = session.stats;
  assert.equal(correct, 3);
  assert.equal(wrong, 1);
  assert.deepEqual([...missed], [0]);
});
