(function initPianoFingering(global) {
  "use strict";

function pianoFingeringForCount(count, hand) {
  const n = Math.max(1, Number(count) || 1);
  if (hand === "right") {
    const templates = {
      1: [1],
      2: [1, 3],
      3: [1, 3, 5],
      4: [1, 2, 4, 5],
      5: [1, 2, 3, 4, 5],
    };
    if (templates[n]) return templates[n];
    return Array.from({ length: n }, (_, i) => Math.min(5, i + 1));
  }
  const templates = {
    1: [5],
    2: [5, 3],
    3: [5, 3, 1],
    4: [5, 3, 2, 1],
    5: [5, 4, 3, 2, 1],
  };
  if (templates[n]) return templates[n];
  return Array.from({ length: n }, (_, i) => Math.max(1, 5 - i));
}

// Documented one-octave piano scale fingerings. Do not add fallback patterns
// for unsupported scales/tonics unless they are backed by a piano fingering source.

// Major Pentatonic (6 notes/oct).
const MAJOR_PENT_RH = {
  0:[1,2,3,1,2,3], 1:[2,3,1,2,3,4], 2:[1,2,3,1,2,4], 3:[2,1,2,3,1,2],
  4:[1,2,3,1,2,3], 5:[1,2,3,1,2,4], 6:[1,2,3,1,2,3], 7:[1,2,3,1,2,4],
  8:[2,3,1,2,1,2], 9:[1,2,3,1,2,1], 10:[3,1,2,1,2,3], 11:[1,2,3,4,5,1],
};
const MAJOR_PENT_LH = {
  0:[3,2,1,2,1,3], 1:[3,2,1,4,3,2], 2:[2,1,3,2,1,2], 3:[3,2,1,2,1,3],
  4:[4,3,2,1,2,1], 5:[3,2,1,2,1,3], 6:[3,2,1,3,2,1], 7:[3,2,1,2,1,3],
  8:[3,2,1,2,1,3], 9:[2,1,2,1,3,2], 10:[3,2,1,2,1,3], 11:[1,5,4,3,2,1],
};

// Minor Pentatonic (6 notes/oct).
const MINOR_PENT_RH = {
  0:[1,2,3,1,2,3], 1:[2,1,2,3,1,2], 2:[1,2,3,1,2,3], 3:[1,2,3,1,2,3],
  4:[1,2,3,1,2,3], 5:[1,2,3,1,2,3], 6:[2,1,2,3,1,2], 7:[1,2,1,2,3,1],
  8:[2,1,2,3,4,5], 9:[1,2,3,1,2,3], 10:[2,3,4,1,2,3], 11:[2,1,2,3,1,2],
};
const MINOR_PENT_LH = {
  0:[1,3,2,1,2,1], 1:[2,1,3,2,1,2], 2:[3,2,1,3,2,1], 3:[3,2,1,3,2,1],
  4:[3,2,1,3,2,1], 5:[4,3,2,1,2,1], 6:[3,2,1,2,1,3], 7:[1,3,2,1,2,1],
  8:[2,1,5,4,3,2], 9:[3,2,1,3,2,1], 10:[4,3,2,1,4,3], 11:[3,2,1,3,2,1],
};

// Minor Blues (7 notes/oct). C blues is documented in beginner piano sheets.
// Other tonics are intentionally not synthesized here.
const MINOR_BLUES_RH = {
  0:[1,2,3,4,1,2,3],
};
const MINOR_BLUES_LH = {
  0:[3,2,1,4,3,2,1],
};

// Whole Tone (7 notes/oct).
const WHOLE_TONE_RH = {
  0:[1,2,1,2,3,4,5], 1:[2,3,1,2,3,1,2], 2:[2,1,2,3,4,1,2],
  3:[4,1,2,1,2,3,4], 4:[1,2,3,4,1,2,3], 5:[1,2,3,1,2,3,4],
  6:[2,3,4,1,2,3,4], 7:[1,2,1,2,3,4,5], 8:[2,3,1,2,1,2,3],
  9:[1,2,3,4,1,2,3], 10:[4,1,2,1,2,3,4], 11:[1,2,3,1,2,3,4],
};
const WHOLE_TONE_LH = {
  0:[3,2,1,4,3,2,1], 1:[3,2,1,3,2,1,3], 2:[2,1,4,3,2,1,2],
  3:[4,3,2,1,4,3,2], 4:[5,4,3,2,1,3,2], 5:[4,3,2,1,3,2,1],
  6:[4,3,2,1,3,1,2], 7:[3,2,1,4,3,2,1], 8:[3,2,1,2,1,3,2],
  9:[2,1,3,2,1,2,3], 10:[4,3,2,1,4,3,2], 11:[4,3,2,1,3,2,1],
};

// Chromatic (13 notes/oct). Same for all keys.
const CHROMATIC_RH = [1,3,1,3,1,2,3,1,3,1,3,1,2];
const CHROMATIC_LH = [1,3,1,3,2,1,3,1,3,1,3,2,1];

// Natural Minor / Aeolian fingerings.
const NATURAL_MINOR_RH = {
  0:[1,2,3,1,2,3,4,5], 1:[3,4,1,2,3,1,2,3], 2:[1,2,3,1,2,3,4,5],
  3:[3,1,2,3,4,1,2,3], 4:[1,2,3,1,2,3,4,5], 5:[1,2,3,4,1,2,3,4],
  6:[2,3,1,2,3,1,2,3], 7:[1,2,3,1,2,3,4,5], 8:[3,4,1,2,3,1,2,3],
  9:[1,2,3,1,2,3,4,5], 10:[2,1,2,3,1,2,3,4], 11:[1,2,3,1,2,3,4,5],
};
const NATURAL_MINOR_LH = {
  0:[5,4,3,2,1,3,2,1], 1:[3,2,1,4,3,2,1,3], 2:[5,4,3,2,1,3,2,1],
  3:[2,1,4,3,2,1,3,2], 4:[5,4,3,2,1,3,2,1], 5:[5,4,3,2,1,3,2,1],
  6:[4,3,2,1,3,2,1,4], 7:[5,4,3,2,1,3,2,1], 8:[3,2,1,3,2,1,4,3],
  9:[5,4,3,2,1,3,2,1], 10:[2,1,3,2,1,4,3,2], 11:[4,3,2,1,4,3,2,1],
};

// Harmonic Minor fingerings.
const HARMONIC_MINOR_RH = {
  0:[1,2,3,1,2,3,4,5], 1:[3,4,1,2,3,1,2,3], 2:[1,2,3,1,2,3,4,5],
  3:[3,1,2,3,4,1,2,3], 4:[1,2,3,1,2,3,4,5], 5:[1,2,3,4,1,2,3,4],
  6:[2,3,1,2,3,1,2,3], 7:[1,2,3,1,2,3,4,5], 8:[2,3,1,2,3,1,2,3],
  9:[1,2,3,1,2,3,4,5], 10:[2,1,2,3,1,2,3,4], 11:[1,2,3,1,2,3,4,5],
};
const HARMONIC_MINOR_LH = {
  0:[5,4,3,2,1,3,2,1], 1:[3,2,1,4,3,2,1,3], 2:[5,4,3,2,1,3,2,1],
  3:[2,1,4,3,2,1,3,2], 4:[5,4,3,2,1,3,2,1], 5:[5,4,3,2,1,3,2,1],
  6:[4,3,2,1,3,2,1,4], 7:[5,4,3,2,1,3,2,1], 8:[3,2,1,4,3,2,1,3],
  9:[5,4,3,2,1,3,2,1], 10:[2,1,3,2,1,4,3,2], 11:[4,3,2,1,4,3,2,1],
};

// Melodic Minor fingerings, ascending/jazz form.
const MELODIC_MINOR_RH = {
  0:[1,2,3,1,2,3,4,5], 1:[2,3,1,2,3,4,1,2], 2:[1,2,3,1,2,3,4,5],
  3:[3,1,2,3,4,1,2,3], 4:[1,2,3,1,2,3,4,5], 5:[1,2,3,4,1,2,3,4],
  6:[2,3,1,2,3,4,1,2], 7:[1,2,3,4,1,2,3,4], 8:[3,4,1,2,3,1,2,3],
  9:[1,2,3,1,2,3,4,5], 10:[4,1,2,3,1,2,3,4], 11:[1,2,3,1,2,3,4,5],
};
const MELODIC_MINOR_LH = {
  0:[5,4,3,2,1,3,2,1], 1:[3,2,1,4,3,2,1,3], 2:[5,4,3,2,1,3,2,1],
  3:[2,1,4,3,2,1,3,2], 4:[5,4,3,2,1,3,2,1], 5:[5,4,3,2,1,3,2,1],
  6:[4,3,2,1,3,2,1,4], 7:[5,4,3,2,1,3,2,1], 8:[3,2,1,4,3,2,1,3],
  9:[5,4,3,2,1,3,2,1], 10:[2,1,4,3,2,1,3,2], 11:[4,3,2,1,4,3,2,1],
};

// LH Ionian fingerings (1 octave = 8 notes). No sharp/flat distinction needed for LH.
const IONIAN_LH = {
  0:  [5,4,3,2,1,3,2,1], // C
  7:  [5,4,3,2,1,3,2,1], // G
  2:  [5,4,3,2,1,3,2,1], // D
  9:  [5,4,3,2,1,3,2,1], // A
  4:  [5,4,3,2,1,3,2,1], // E
  5:  [5,4,3,2,1,3,2,1], // F
  11: [4,3,2,1,4,3,2,1], // B
  6:  [4,3,2,1,3,2,1,4], // F# / Gb
  10: [3,2,1,4,3,2,1,3], // Bb
  3:  [3,2,1,4,3,2,1,3], // Eb
  8:  [3,2,1,4,3,2,1,3], // Ab
  1:  [3,2,1,4,3,2,1,3], // C# / Db
};

// RH Ionian fingerings (1 octave = 8 notes). Multi-octave: period of 7 + last note = pattern[7].
const IONIAN_RH = {
  sharp: {
    0:  [1,2,3,1,2,3,4,5], // C
    2:  [1,2,3,1,2,3,4,5], // D
    4:  [1,2,3,1,2,3,4,5], // E
    5:  [1,2,3,4,1,2,3,4], // F
    7:  [1,2,3,1,2,3,4,5], // G
    9:  [1,2,3,1,2,3,4,5], // A
    11: [1,2,3,1,2,3,4,5], // B
    1:  [2,3,1,2,3,4,1,2], // C#
    6:  [2,3,4,1,2,3,1,2], // F# (same as Gb)
    10: [2,1,2,3,1,2,3,4], // Bb/A#
    3:  [3,1,2,3,4,1,2,3], // Eb/D#
    8:  [3,4,1,2,3,1,2,3], // Ab/G#
  },
  flat: {
    0:  [1,2,3,1,2,3,4,5], // C
    2:  [1,2,3,1,2,3,4,5], // D
    4:  [1,2,3,1,2,3,4,5], // E
    5:  [1,2,3,4,1,2,3,4], // F
    7:  [1,2,3,1,2,3,4,5], // G
    9:  [1,2,3,1,2,3,4,5], // A
    11: [1,2,3,1,2,3,4,5], // B
    1:  [2,3,1,2,3,4,1,2], // Db
    6:  [2,3,4,1,2,3,1,2], // Gb
    10: [2,1,2,3,1,2,3,4], // Bb
    3:  [3,1,2,3,4,1,2,3], // Eb
    8:  [3,4,1,2,3,1,2,3], // Ab
  },
};

function fingerArrayToResult(fingers) {
  return fingers.map((f, i) => ({
    finger: f,
    crossover: i > 0 && i < fingers.length - 1 && Math.abs(f - fingers[i - 1]) > 1,
  }));
}

function extendFingerPattern(pattern, n) {
  const len = pattern.length;
  if (n <= len) return pattern.slice(0, n);
  if (len === 8) {
    // 8-note scales: octave boundary = thumb if pattern starts on thumb, else ending finger
    const ob = pattern[0] === 1 ? 1 : pattern[7];
    const period = pattern.slice(0, 7);
    const fingers = [];
    for (let i = 0; i < n - 1; i++) {
      fingers.push(i > 0 && i % 7 === 0 ? ob : period[i % 7]);
    }
    fingers.push(pattern[7]);
    return fingers;
  }
  const period = len - 1;
  const out = [];
  for (let i = 0; i < n - 1; i++) out.push(pattern[i % period]);
  out.push(pattern[len - 1]);
  return out;
}

// Returns [{finger: 1-5, crossover: bool}] for each note in midiNotes (ascending).
// crossover=true marks a "paso de dedo" (thumb passing under for RH, finger-3 crossing over for LH).
// ctx: optional { tonicPc, patternName, preferFlat } for scale-specific overrides.
function computeScaleFingering(midiNotes, hand, ctx = {}) {
  const n = midiNotes.length;
  if (n === 0) return [];

  if (ctx.patternName === "Ionian") {
    if (hand === "right") {
      const table = ctx.preferFlat ? IONIAN_RH.flat : IONIAN_RH.sharp;
      const pattern8 = table[ctx.tonicPc];
      if (pattern8) return fingerArrayToResult(extendFingerPattern(pattern8, n));
    } else {
      const pattern8 = IONIAN_LH[ctx.tonicPc];
      if (pattern8) return fingerArrayToResult(extendFingerPattern(pattern8, n));
    }
  }

  if (ctx.patternName === "Aeolian" && ctx.tonicPc != null) {
    const p = hand === "right" ? NATURAL_MINOR_RH[ctx.tonicPc] : NATURAL_MINOR_LH[ctx.tonicPc];
    if (p) return fingerArrayToResult(extendFingerPattern(p, n));
  }

  if (ctx.patternName === "Harmonic Minor" && ctx.tonicPc != null) {
    const p = hand === "right" ? HARMONIC_MINOR_RH[ctx.tonicPc] : HARMONIC_MINOR_LH[ctx.tonicPc];
    if (p) return fingerArrayToResult(extendFingerPattern(p, n));
  }

  if (ctx.patternName === "Melodic Minor" && ctx.tonicPc != null) {
    const p = hand === "right" ? MELODIC_MINOR_RH[ctx.tonicPc] : MELODIC_MINOR_LH[ctx.tonicPc];
    if (p) return fingerArrayToResult(extendFingerPattern(p, n));
  }

  if (ctx.patternName === "Minor Blues" && ctx.tonicPc != null) {
    const p = hand === "right" ? MINOR_BLUES_RH[ctx.tonicPc] : MINOR_BLUES_LH[ctx.tonicPc];
    if (p) return fingerArrayToResult(extendFingerPattern(p, n));
  }

  for (const [names, rh, lh] of [
    [["Major Pentatonic"], MAJOR_PENT_RH, MAJOR_PENT_LH],
    [["Minor Pentatonic", "Blues Pentatonic"], MINOR_PENT_RH, MINOR_PENT_LH],
    [["Whole Tone (WT)"], WHOLE_TONE_RH, WHOLE_TONE_LH],
  ]) {
    if (names.includes(ctx.patternName) && ctx.tonicPc != null) {
      const p = hand === "right" ? rh[ctx.tonicPc] : lh[ctx.tonicPc];
      if (p) return fingerArrayToResult(extendFingerPattern(p, n));
    }
  }

  if (ctx.patternName === "Chromatic") {
    const p = hand === "right" ? CHROMATIC_RH : CHROMATIC_LH;
    return fingerArrayToResult(extendFingerPattern(p, n));
  }

  return [];
}


global.MidiChordsPianoFingering = Object.freeze({
  pianoFingeringForCount,
  computeScaleFingering,
});
})(globalThis);
