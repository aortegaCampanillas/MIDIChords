const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/ui_texts.js");
require("../static/chord_help.js");

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
  assert.ok(Object.isFrozen(globalThis.MidiChordsChordHelp));
});
