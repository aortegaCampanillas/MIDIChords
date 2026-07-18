(function initScaleTheory(global) {
  "use strict";

  const SCALE_BASIC_NAMES = new Set([
    "Ionian", "Aeolian", "Harmonic Minor", "Melodic Minor",
    "Dorian", "Phrygian", "Lydian", "Mixolydian", "Locrian",
    "Major Pentatonic", "Minor Pentatonic",
    "Blues Pentatonic", "Minor Blues",
    "Chromatic", "Whole Tone (WT)",
  ]);
  const MODAL_SCALE_DEGREES = Object.freeze({
    Ionian: "I",
    Dorian: "II",
    Phrygian: "III",
    Lydian: "IV",
    Mixolydian: "V",
    Aeolian: "VI",
    Locrian: "VII",
  });
  const MODAL_SCALE_NAMES = Object.freeze(Object.keys(MODAL_SCALE_DEGREES));
  const SCALE_FAMILY_GROUPS = Object.freeze([
    ["scale_group_greek_modes", MODAL_SCALE_NAMES],
    ["scale_group_minor", ["Harmonic Minor", "Melodic Minor", "Romanian Minor", "Hawaiian"]],
    ["scale_group_altered_modes", [
      "Locrian #2", "Half Diminished", "Super Locrian", "Neapolitan Major", "Neapolitan Minor",
      "Lydian Minor", "Lydian Augmented", "Lydian Diminished", "Lydian Augmented #6",
      "Hungarian Major", "Hungarian Minor",
    ]],
    ["scale_group_pentatonic_blues", [
      "Major Pentatonic", "Minor Pentatonic", "Blues Pentatonic", "Neutral Pentatonic", "Minor Blues",
    ]],
    ["scale_group_bebop", ["Bebop", "Bebop Major", "Bebop Minor"]],
    ["scale_group_symmetric_synthetic", [
      "Chromatic", "Diminished", "Whole Tone (WT)", "Diminished WT", "Enigmatic",
      "Prometheus", "Prometheus Neapolitan", "Six Tone Symmetric",
    ]],
    ["scale_group_world", [
      "Spanish Gypsy", "Eight Tone Spanish", "Pelog", "Ichikosucho", "Persian", "Flamenco",
      "Maqam", "Oriental", "Iwato", "Raga Malakosh", "Balinese", "Kafi Raga", "Todi Raga",
      "Purvi Raga", "In Sen",
    ]],
  ]);

  function scaleAliases(language) {
    return language === "en"
      ? { Ionian: "Major", Aeolian: "Natural Minor", "Super Locrian": "Altered" }
      : { Ionian: "Mayor", Aeolian: "Menor Natural", "Super Locrian": "Alterada" };
  }

  function scaleDisplayLabel(patternName, localizedName, language) {
    const alias = scaleAliases(language)[patternName];
    const label = alias ? `${alias} (${localizedName})` : String(localizedName);
    const degree = MODAL_SCALE_DEGREES[patternName];
    return degree ? `${label} (${degree})` : label;
  }

  function groupScalePatterns(patterns) {
    const available = new Map((patterns || []).map((pattern) => [pattern.name, pattern]));
    return SCALE_FAMILY_GROUPS.map(([labelKey, names]) => ({
      labelKey,
      patterns: names.map((name) => available.get(name)).filter(Boolean),
    })).filter((group) => group.patterns.length);
  }

  function scaleBaseNotes(notesMidi, guitarStartNote = null) {
    if (!Array.isArray(notesMidi)) return [];
    const base = Array.from(new Set(notesMidi.map((note) => Number(note))))
      .filter((note) => Number.isFinite(note))
      .sort((a, b) => a - b);
    if (!base.length || guitarStartNote == null) return base;
    const start = Number(guitarStartNote);
    if (!Number.isFinite(start)) return base;
    const first = base[0];
    if (((start % 12) + 12) % 12 !== ((first % 12) + 12) % 12) return base;
    const delta = start - first;
    return base.map((note) => note + delta);
  }

  function scaleNotesForOctaves(baseNotes, octaves = 1) {
    const base = Array.isArray(baseNotes) ? baseNotes : [];
    if (!base.length || Number(octaves) <= 1) return [...base];
    const result = new Set(base);
    if (Number(octaves) >= 2) {
      for (const note of base) result.add(Number(note) - 12);
    }
    if (Number(octaves) >= 3) {
      for (const note of base) result.add(Number(note) + 12);
    }
    return Array.from(result).sort((a, b) => a - b);
  }

  function scaleLabelWithoutOctave(label) {
    return String(label || "").replace(/-?\d+$/g, "");
  }

  function scaleLabelForMidi(midi, notesMidi, labels) {
    const target = Number(midi);
    if (!Number.isFinite(target) || !Array.isArray(notesMidi) || !Array.isArray(labels)) {
      return null;
    }
    const targetPc = ((target % 12) + 12) % 12;
    let best = null;
    notesMidi.forEach((baseMidi, index) => {
      const base = Number(baseMidi);
      if (!Number.isFinite(base) || ((base % 12) + 12) % 12 !== targetPc) return;
      const label = scaleLabelWithoutOctave(labels[index]);
      if (!label) return;
      const distance = Math.abs(target - base);
      if (!best || distance < best.distance) best = { label, distance };
    });
    return best ? best.label : null;
  }

  global.MidiChordsScaleTheory = Object.freeze({
    SCALE_BASIC_NAMES,
    MODAL_SCALE_DEGREES,
    MODAL_SCALE_NAMES,
    SCALE_FAMILY_GROUPS,
    scaleAliases,
    scaleDisplayLabel,
    groupScalePatterns,
    scaleBaseNotes,
    scaleNotesForOctaves,
    scaleLabelWithoutOctave,
    scaleLabelForMidi,
  });
})(globalThis);
