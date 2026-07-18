const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/ui_texts.js");
require("../static/music_notation.js");
require("../static/chord_help.js");
require("../static/help_callouts.js");

const { UI_TEXTS } = globalThis.MidiChordsUiTexts;
const {
  CHORD_VARIANT_GROUPS,
  CHORD_VARIANT_THEORY,
  MAJOR_CHORD_INVERSION_THEORY,
  chordInversionTheory,
} = globalThis.MidiChordsChordHelp;

test("the interface catalogs expose the same keys in Spanish and English", () => {
  const spanishKeys = Object.keys(UI_TEXTS.es).sort();
  const englishKeys = Object.keys(UI_TEXTS.en).sort();

  assert.ok(spanishKeys.length > 100);
  assert.deepEqual(spanishKeys, englishKeys);
  for (const key of spanishKeys) {
    assert.ok(UI_TEXTS.es[key].trim(), `empty Spanish text: ${key}`);
    assert.ok(UI_TEXTS.en[key].trim(), `empty English text: ${key}`);
  }
});

test("every chord theory variant belongs to exactly one selector group", () => {
  const theorySuffixes = Object.keys(CHORD_VARIANT_THEORY).sort();
  const groupedSuffixes = CHORD_VARIANT_GROUPS
    .flatMap((group) => group.suffixes)
    .sort();

  assert.equal(theorySuffixes.length, 52);
  assert.equal(new Set(groupedSuffixes).size, groupedSuffixes.length);
  assert.deepEqual(groupedSuffixes, theorySuffixes);
});

test("generic inversion help follows the selected bass degree", () => {
  assert.match(chordInversionTheory("1 - 3 - 5", 0, "es"), /^Posición fundamental:/);
  assert.match(chordInversionTheory("1 - 3 - 5", 1, "en"), /^First inversion:/);
  assert.match(chordInversionTheory("1 - 3 - 5", 2, "es"), /la quinta justa está en el bajo/);
  assert.equal(MAJOR_CHORD_INVERSION_THEORY.length, 3);
});

test("catalog entry points are immutable", () => {
  assert.ok(Object.isFrozen(globalThis.MidiChordsUiTexts));
  assert.ok(Object.isFrozen(globalThis.MidiChordsMusicNotation));
  assert.ok(Object.isFrozen(globalThis.MidiChordsChordHelp));
  assert.ok(Object.isFrozen(globalThis.MidiChordsHelpCallouts));
});

test("music notation normalizes pitch classes and accidentals", () => {
  const {
    NOTE_LABELS,
    ROOT_LETTERS,
    ROOT_LETTER_ACCIDENTALS,
    rootPcFromLetterAccidental,
    noteLabelFromPc,
  } = globalThis.MidiChordsMusicNotation;

  assert.equal(ROOT_LETTERS.length, 7);
  assert.equal(new Set(NOTE_LABELS.es.sharp).size, 12);
  assert.equal(new Set(NOTE_LABELS.en.flat).size, 12);
  assert.equal(rootPcFromLetterAccidental(0, "flat"), 11);
  assert.equal(rootPcFromLetterAccidental(11, "sharp"), 0);
  assert.equal(noteLabelFromPc("es", -1, false), "Si");
  assert.equal(noteLabelFromPc("en", 13, true), "D♭");
  for (const root of ROOT_LETTERS) {
    assert.ok(ROOT_LETTER_ACCIDENTALS[root.pc]?.includes("natural"));
  }
});

test("every contextual help item has bilingual text", () => {
  const { helpCalloutsForMode, isHelpAvailableForMode } =
    globalThis.MidiChordsHelpCallouts;
  const modes = [
    "detection",
    "interval_detection",
    "generation",
    "circle_fifths",
    "scales",
    "metronome",
  ];

  for (const mode of modes) {
    const callouts = helpCalloutsForMode(mode);
    assert.ok(isHelpAvailableForMode(mode));
    assert.ok(callouts.length > 0);
    for (const callout of callouts) {
      assert.ok(callout.selector);
      assert.ok(UI_TEXTS.es[callout.textKey], `${mode}: ${callout.textKey} missing in es`);
      assert.ok(UI_TEXTS.en[callout.textKey], `${mode}: ${callout.textKey} missing in en`);
    }
  }
  assert.deepEqual(helpCalloutsForMode("tuner"), []);
  assert.equal(isHelpAvailableForMode("tuner"), false);
});
