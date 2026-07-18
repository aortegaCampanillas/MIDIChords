(function initMidiOutput(global) {
  "use strict";

  function createMidiOutputController(options = {}) {
    const getOutput = typeof options.getOutput === "function" ? options.getOutput : () => null;
    const schedule = typeof options.schedule === "function" ? options.schedule : setTimeout;
    const heldNotes = options.heldNotes instanceof Set ? options.heldNotes : new Set();
    const velocity = Number.isFinite(Number(options.velocity)) ? Number(options.velocity) : 64;

    function sendNote(note, durationMs) {
      const output = getOutput();
      if (!output) return false;
      output.send([0x90, note, velocity]);
      schedule(() => {
        try {
          output.send([0x80, note, 0]);
        } catch (_error) {}
      }, durationMs);
      return true;
    }

    function noteOn(note) {
      const output = getOutput();
      if (!output) return false;
      output.send([0x90, note, velocity]);
      heldNotes.add(note);
      return true;
    }

    function noteOff(note) {
      const output = getOutput();
      if (output) {
        try {
          output.send([0x80, note, 0]);
        } catch (_error) {}
      }
      heldNotes.delete(note);
      return !!output;
    }

    function stopAll() {
      for (const note of Array.from(heldNotes)) noteOff(note);
    }

    function programChange(instrument) {
      const output = getOutput();
      if (!output) return false;
      // General MIDI: 0 = Acoustic Grand Piano, 24 = Acoustic Guitar (nylon).
      output.send([0xC0, instrument === "guitar" ? 24 : 0]);
      return true;
    }

    return Object.freeze({
      heldNotes,
      sendNote,
      noteOn,
      noteOff,
      stopAll,
      programChange,
    });
  }

  global.MidiChordsMidiOutput = Object.freeze({ createMidiOutputController });
})(globalThis);
