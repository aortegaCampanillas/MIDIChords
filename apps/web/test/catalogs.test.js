const assert = require("node:assert/strict");
const test = require("node:test");

require("../static/ui_texts.js");
require("../static/music_notation.js");
require("../static/circle_theory.js");
require("../static/interval_theory.js");
require("../static/piano_fingering.js");
require("../static/key_signature.js");
require("../static/ui_lifecycle.js");
require("../static/staff_beam_geometry.js");
require("../static/scale_theory.js");
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
  assert.ok(Object.isFrozen(globalThis.MidiChordsCircleTheory));
  assert.ok(Object.isFrozen(globalThis.MidiChordsIntervalTheory));
  assert.ok(Object.isFrozen(globalThis.MidiChordsPianoFingering));
  assert.ok(Object.isFrozen(globalThis.MidiChordsKeySignature));
  assert.ok(Object.isFrozen(globalThis.MidiChordsUiLifecycle));
  assert.ok(Object.isFrozen(globalThis.MidiChordsStaffBeamGeometry));
  assert.ok(Object.isFrozen(globalThis.MidiChordsScaleTheory));
  assert.ok(Object.isFrozen(globalThis.MidiChordsChordHelp));
  assert.ok(Object.isFrozen(globalThis.MidiChordsHelpCallouts));
});

test("scale theory normalizes notes, octaves, aliases, and labels", () => {
  const {
    SCALE_BASIC_NAMES,
    scaleAliases,
    scaleDisplayLabel,
    scaleBaseNotes,
    scaleNotesForOctaves,
    scaleLabelWithoutOctave,
    scaleLabelForMidi,
  } = globalThis.MidiChordsScaleTheory;

  assert.ok(SCALE_BASIC_NAMES.has("Ionian"));
  assert.equal(scaleAliases("es").Aeolian, "Menor Natural");
  assert.equal(scaleAliases("en")["Super Locrian"], "Altered");
  assert.equal(scaleDisplayLabel("Ionian", "Jónica", "es"), "Mayor (Jónica) (I)");
  assert.equal(scaleDisplayLabel("Dorian", "Dórica", "es"), "Dórica (II)");
  assert.equal(scaleDisplayLabel("Locrian", "Locrian", "en"), "Locrian (VII)");
  assert.equal(scaleDisplayLabel("Chromatic", "Cromática", "es"), "Cromática");
  assert.deepEqual(scaleBaseNotes([67, 60, 64, 60]), [60, 64, 67]);
  assert.deepEqual(scaleBaseNotes([60, 64, 67], 72), [72, 76, 79]);
  assert.deepEqual(scaleBaseNotes([60, 64, 67], 73), [60, 64, 67]);
  assert.deepEqual(scaleNotesForOctaves([60, 64, 67], 3), [48, 52, 55, 60, 64, 67, 72, 76, 79]);
  assert.equal(scaleLabelWithoutOctave("Do#4"), "Do#");
  assert.equal(scaleLabelForMidi(72, [60, 64, 67], ["Do4", "Mi4", "Sol4"]), "Do");
  assert.equal(scaleLabelForMidi(84, [60, 72], ["Do4", "Do5"]), "Do");
  assert.equal(scaleLabelForMidi(61, [], []), null);
});

test("key signatures choose the shortest spelling and modal relative major", () => {
  const {
    MODE_RELATIVE_MAJOR_OFFSET,
    keySignatureCountForTonic,
    chordSymbolPreferFlat,
    applyFlatKeySignatureTie,
    keySignatureIndexForMidi,
    isMinorSuffix,
    scalePrefersMinor,
  } = globalThis.MidiChordsKeySignature;

  assert.deepEqual(keySignatureCountForTonic(0, false), { count: 0, preferFlats: false });
  assert.deepEqual(keySignatureCountForTonic(7, false), { count: 1, preferFlats: false });
  assert.deepEqual(keySignatureCountForTonic(5, false), { count: 1, preferFlats: true });
  assert.deepEqual(keySignatureCountForTonic(0, true), { count: 3, preferFlats: true });
  assert.deepEqual(keySignatureCountForTonic(6, false, false), { count: 6, preferFlats: false });
  assert.deepEqual(keySignatureCountForTonic(6, false, true), { count: 6, preferFlats: true });
  assert.equal(chordSymbolPreferFlat(6, false), true);
  assert.deepEqual(
    applyFlatKeySignatureTie({ count: 6, preferFlats: false }, 6, false, true),
    { count: 6, preferFlats: true },
  );
  assert.equal(MODE_RELATIVE_MAJOR_OFFSET.Dorian, 10);
  assert.equal(MODE_RELATIVE_MAJOR_OFFSET.Lydian, 7);
  assert.equal(isMinorSuffix("m7"), true);
  assert.equal(isMinorSuffix("maj7"), false);
  assert.equal(scalePrefersMinor("Dorian"), true);
  assert.equal(scalePrefersMinor("Mixolydian"), false);
  assert.equal(keySignatureIndexForMidi(66, { count: 3, preferFlats: false }), 0);
  assert.equal(keySignatureIndexForMidi(68, { count: 3, preferFlats: false }), 2);
  assert.equal(keySignatureIndexForMidi(70, { count: 3, preferFlats: true }), 0);
  assert.equal(keySignatureIndexForMidi(66, { count: 2, preferFlats: true }), -1);
});

test("piano fingering resolves documented scales without synthetic fallbacks", () => {
  const { pianoFingeringForCount, computeScaleFingering } =
    globalThis.MidiChordsPianoFingering;

  assert.deepEqual(pianoFingeringForCount(3, "right"), [1, 3, 5]);
  assert.deepEqual(pianoFingeringForCount(3, "left"), [5, 3, 1]);

  const cMajor = computeScaleFingering(
    [60, 62, 64, 65, 67, 69, 71, 72],
    "right",
    { patternName: "Ionian", tonicPc: 0, preferFlat: false },
  );
  assert.deepEqual(cMajor.map((item) => item.finger), [1, 2, 3, 1, 2, 3, 4, 5]);
  assert.equal(cMajor[3].crossover, true);

  const chromatic = computeScaleFingering(
    Array.from({ length: 13 }, (_, index) => 60 + index),
    "left",
    { patternName: "Chromatic", tonicPc: 0 },
  );
  assert.equal(chromatic.length, 13);
  assert.deepEqual(
    computeScaleFingering([61, 64, 67, 70, 72, 73, 76], "right", {
      patternName: "Minor Blues",
      tonicPc: 1,
    }),
    [],
  );
});

test("interval theory identifies intervals and preserves melody timing", () => {
  const {
    INTERVAL_MELODIES,
    formatIntervalsFromMidi,
    intervalName,
    intervalSemitones,
    intervalMelodyNotes,
    intervalMelodySongName,
  } = globalThis.MidiChordsIntervalTheory;

  assert.equal(Object.keys(INTERVAL_MELODIES).length, 12);
  assert.equal(intervalSemitones([60, 60]), 0);
  assert.equal(intervalSemitones([60, 72]), 12);
  assert.equal(intervalSemitones([72, 60]), 12);
  assert.equal(intervalSemitones([60, 67]), 7);
  assert.equal(intervalName("es", 7), "Quinta justa");
  assert.equal(intervalName("en", 3), "Minor Third");
  assert.equal(intervalName("unknown", 3), "Tercera menor");
  assert.equal(formatIntervalsFromMidi([67, 60, 64, 64]), "0 +4 +3");
  assert.equal(intervalMelodySongName("es", [60, 62]), "Cumpleaños feliz");

  const smoke = intervalMelodyNotes([60, 63]);
  assert.equal(smoke.length, INTERVAL_MELODIES[3].durations.length);
  assert.equal(smoke[3], null);
  assert.deepEqual(intervalMelodyNotes([64]), [64]);
});

test("circle of fifths theory maps keys and diatonic triads", () => {
  const {
    CIRCLE_FIFTHS_ORDER,
    diatonicTriadSuffixMajorKey,
    diatonicTriadSuffixNaturalMinorKey,
    circleSignatureLabelForSliceIndex,
    relativeMinorPcFromMajorPc,
    circleSliceIndexForPitchClass,
    chordRootPcForMajorScaleDegree,
    circleSliceAngles,
    pitchClassFromCircleClick,
    circleChordRootPcFromClick,
    circleChordShiftClickIsDiatonic,
    circleFifthsClickInnerMinorBand,
    circleChordHighlightGeom,
  } = globalThis.MidiChordsCircleTheory;

  assert.equal(CIRCLE_FIFTHS_ORDER.length, 12);
  assert.equal(new Set(CIRCLE_FIFTHS_ORDER).size, 12);
  assert.deepEqual(CIRCLE_FIFTHS_ORDER, [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]);
  assert.deepEqual(diatonicTriadSuffixMajorKey(0, 7), { suffix: "", degree: 7 });
  assert.deepEqual(diatonicTriadSuffixMajorKey(0, 2), { suffix: "m", degree: 2 });
  assert.deepEqual(diatonicTriadSuffixNaturalMinorKey(9, 11), {
    suffix: "dim",
    interval: 2,
    roman: "ii°",
  });
  assert.equal(relativeMinorPcFromMajorPc(0), 9);
  assert.equal(circleSliceIndexForPitchClass(10), 10);
  assert.equal(chordRootPcForMajorScaleDegree(0, 11), 11);
  assert.equal(circleSignatureLabelForSliceIndex(0), "0");
  assert.equal(circleSignatureLabelForSliceIndex(8), "4♭");
  assert.ok(Math.abs(circleSliceAngles(0).mid + (Math.PI / 2)) < 1e-12);
  assert.equal(pitchClassFromCircleClick(200, 200, 200, 40), 0);
  assert.equal(circleChordRootPcFromClick(400, 400, 200, 200, 200, 50), 0);
  assert.equal(circleChordRootPcFromClick(400, 400, 200, 200, 200, 130), 9);
  assert.equal(circleChordRootPcFromClick(400, 400, 200, 200, 200, 200), null);
  assert.equal(circleFifthsClickInnerMinorBand(400, 400, 200, 200, 200, 130), true);
  assert.equal(circleFifthsClickInnerMinorBand(400, 400, 200, 200, 200, 50), false);
  assert.equal(circleChordShiftClickIsDiatonic(0, 400, 400, 200, 200, 200, 50), true);
  assert.equal(circleChordShiftClickIsDiatonic(0, 400, 400, 200, 200, 338, 120), false);
  assert.deepEqual(circleChordHighlightGeom(0, 9, { suffix: "m" }), {
    sliceIdx: 0,
    band: "minor",
  });
  assert.deepEqual(circleChordHighlightGeom(0, 11, { suffix: "dim" }), {
    sliceIdx: 2,
    band: "minor",
  });
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
