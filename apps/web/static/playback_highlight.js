(function initPlaybackHighlight(global) {
  "use strict";

  function normalizePlaybackNotes(notes) {
    return new Set((notes || []).map((note) => Number(note)).filter((note) => Number.isFinite(note)));
  }

  function isChordPlaybackMode(mode) {
    return mode === "generation" || mode === "circle_fifths";
  }

  function isPlaybackNoteActive(note, playingNotes, { matchPitchClass = false } = {}) {
    const midi = Number(note);
    if (!Number.isFinite(midi)) return false;
    const normalized = playingNotes instanceof Set ? playingNotes : normalizePlaybackNotes(playingNotes);
    if (!matchPitchClass) return normalized.has(midi);
    const pitchClass = ((midi % 12) + 12) % 12;
    return Array.from(normalized).some((playing) => ((playing % 12) + 12) % 12 === pitchClass);
  }

  function createPlaybackHighlighter({
    onChange,
    render,
    schedule = global.setTimeout,
    cancel = global.clearTimeout,
  }) {
    let notes = new Set();
    let clearTimer = null;

    function cancelPendingClear() {
      if (clearTimer == null) return;
      cancel(clearTimer);
      clearTimer = null;
    }

    function publish(nextNotes) {
      notes = normalizePlaybackNotes(nextNotes);
      onChange(new Set(notes));
      render();
    }

    function show(nextNotes) {
      cancelPendingClear();
      publish(nextNotes);
    }

    function showFor(nextNotes, durationMs) {
      show(nextNotes);
      if (!notes.size) return;
      clearTimer = schedule(() => {
        clearTimer = null;
        publish([]);
      }, Math.max(0, Number(durationMs) || 0));
    }

    function clear() {
      cancelPendingClear();
      if (notes.size) publish([]);
    }

    return Object.freeze({ show, showFor, clear });
  }

  global.MidiChordsPlaybackHighlight = Object.freeze({
    isChordPlaybackMode,
    normalizePlaybackNotes,
    isPlaybackNoteActive,
    createPlaybackHighlighter,
  });
})(globalThis);
