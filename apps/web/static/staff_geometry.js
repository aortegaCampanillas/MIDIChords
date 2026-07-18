(function initStaffGeometry(global) {
  "use strict";

  const {
    PC_TO_DIATONIC_LETTER,
    PC_TO_DIATONIC_FLAT,
  } = global.MidiChordsMusicNotation;

  function midiToDiatonicIndex(midi, preferFlat = false) {
    const note = Number(midi);
    if (!Number.isFinite(note)) return null;
    const pc = ((note % 12) + 12) % 12;
    const octave = Math.floor(note / 12) - 1;
    const map = preferFlat ? PC_TO_DIATONIC_FLAT : PC_TO_DIATONIC_LETTER;
    return (octave * 7) + map[pc];
  }

  function midiToTrebleY(midi, trebleTop, gap, preferFlat = false) {
    const diatonicIndex = midiToDiatonicIndex(midi, preferFlat);
    if (diatonicIndex == null) return Number(trebleTop);
    const trebleBottomLineDiatonic = (4 * 7) + 2; // E4
    return Number(trebleTop) + (4 * Number(gap))
      - ((diatonicIndex - trebleBottomLineDiatonic) * (Number(gap) / 2));
  }

  function midiToBassY(midi, bassTop, gap, preferFlat = false) {
    const diatonicIndex = midiToDiatonicIndex(midi, preferFlat);
    if (diatonicIndex == null) return Number(bassTop);
    const bassBottomLineDiatonic = (2 * 7) + 4; // G2
    return Number(bassTop) + (4 * Number(gap))
      - ((diatonicIndex - bassBottomLineDiatonic) * (Number(gap) / 2));
  }

  function ledgerLineYs(noteY, staffTop, gap) {
    const y = Number(noteY);
    const top = Number(staffTop);
    const spacing = Number(gap);
    if (![y, top, spacing].every(Number.isFinite) || spacing <= 0) return [];
    const bottom = top + (spacing * 4);
    const lines = [];
    if (y < top - 1) {
      for (let lineY = top - spacing; lineY >= y - 1; lineY -= spacing) lines.push(lineY);
    } else if (y > bottom + 1) {
      for (let lineY = bottom + spacing; lineY <= y + 1; lineY += spacing) lines.push(lineY);
    }
    return lines;
  }

  function closestPitchClassMidi(notes, currentMidi) {
    if (currentMidi == null) return currentMidi;
    const current = Number(currentMidi);
    const currentPc = ((current % 12) + 12) % 12;
    const matches = (Array.isArray(notes) ? notes : [])
      .map(Number)
      .filter((note) => ((note % 12) + 12) % 12 === currentPc);
    if (!matches.length) return current;
    return matches.reduce((best, note) => (
      Math.abs(note - current) < Math.abs(best - current) ? note : best
    ), matches[0]);
  }

  function mapPianoInputToStaffMidi(staffNotes, inputMidi) {
    if (inputMidi == null) return inputMidi;
    const note = Number(inputMidi);
    const staffSet = new Set((Array.isArray(staffNotes) ? staffNotes : []).map(Number));
    return !staffSet.has(note) && staffSet.has(note + 12) ? note + 12 : note;
  }

  function expandPianoPlayingNotesForStaff(staffNotes, playingNotes) {
    const staffSet = new Set((Array.isArray(staffNotes) ? staffNotes : []).map(Number));
    const display = new Set(Array.from(playingNotes || []).map(Number));
    Array.from(display).forEach((note) => {
      if (staffSet.has(note - 12)) display.add(note - 12);
    });
    return display;
  }

  function mapPianoHeldNotesToStaff(staffNotes, heldNotes) {
    const staffSet = new Set((Array.isArray(staffNotes) ? staffNotes : []).map(Number));
    const display = new Set(Array.from(heldNotes || []).map(Number));
    Array.from(display).forEach((note) => {
      if (!staffSet.has(note) && staffSet.has(note + 12)) {
        display.delete(note);
        display.add(note + 12);
      }
    });
    return display;
  }

  function buildScaleStaffEntries(rightHand, leftHand) {
    const rh = Array.isArray(rightHand) ? rightHand.map(Number) : [];
    const lh = Array.isArray(leftHand) ? leftHand.map(Number) : [];
    const lhSet = new Set(lh);
    const entries = [];
    const pairCount = Math.min(rh.length, lh.length);
    for (let index = 0; index < pairCount; index += 1) {
      const bass = rh[index] - 12;
      if (lhSet.has(bass)) entries.push({ midi: bass, degree: index });
      entries.push({ midi: rh[index], degree: index });
    }
    for (let index = pairCount; index < rh.length; index += 1) {
      entries.push({ midi: rh[index], degree: index });
    }
    return entries;
  }

  global.MidiChordsStaffGeometry = Object.freeze({
    midiToDiatonicIndex,
    midiToTrebleY,
    midiToBassY,
    ledgerLineYs,
    closestPitchClassMidi,
    mapPianoInputToStaffMidi,
    expandPianoPlayingNotesForStaff,
    mapPianoHeldNotesToStaff,
    buildScaleStaffEntries,
  });
})(globalThis);
