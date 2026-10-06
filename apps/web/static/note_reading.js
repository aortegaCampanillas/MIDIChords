(function initNoteReading(global) {
  "use strict";

  // Notes are compared by diatonic step (C/do = 0 … B/si = 6). `words` are the
  // recognizer's vocabulary: English letters use their spelled pronunciation,
  // which measured clearly better with Vosk than the bare letters.
  const NOTE_NAMES = Object.freeze({
    es: Object.freeze({
      labels: Object.freeze(["do", "re", "mi", "fa", "sol", "la", "si"]),
      words: Object.freeze({ do: 0, re: 1, mi: 2, fa: 3, sol: 4, la: 5, si: 6 }),
    }),
    en: Object.freeze({
      labels: Object.freeze(["C", "D", "E", "F", "G", "A", "B"]),
      words: Object.freeze({ see: 0, dee: 1, ee: 2, eff: 3, gee: 4, ay: 5, bee: 6 }),
    }),
  });
  const NATURAL_PCS = Object.freeze([0, 2, 4, 5, 7, 9, 11]);

  // MIDI bounds per clef: "staff" stays on the five lines; "ledger" adds up to
  // two ledger lines above and below.
  const READING_RANGES = Object.freeze({
    treble: Object.freeze({ staff: Object.freeze([64, 77]), ledger: Object.freeze([57, 84]) }),
    bass: Object.freeze({ staff: Object.freeze([43, 57]), ledger: Object.freeze([36, 64]) }),
  });

  const DEFAULT_LENGTH = 8;

  function isNatural(midi) {
    return NATURAL_PCS.includes(((Number(midi) % 12) + 12) % 12);
  }

  function naturalNotesInRange(low, high) {
    const notes = [];
    for (let midi = Math.ceil(low); midi <= high; midi += 1) {
      if (isNatural(midi)) notes.push(midi);
    }
    return notes;
  }

  function readingRange(clef, range) {
    const byClef = READING_RANGES[clef] || READING_RANGES.treble;
    return byClef[range] || byClef.staff;
  }

  // Random naturals within the range, never repeating the previous note so
  // every step is a new reading. `after` is the note shown just before this
  // sequence (the end of the previous round), which the first note avoids too.
  function generateReadingSequence({
    clef = "treble",
    range = "staff",
    length = DEFAULT_LENGTH,
    after = null,
    random = Math.random,
  } = {}) {
    const [low, high] = readingRange(clef, range);
    const pool = naturalNotesInRange(low, high);
    const notes = [];
    for (let i = 0; i < length; i += 1) {
      const previous = i === 0 ? after : notes[i - 1];
      const options = pool.filter((midi) => midi !== previous);
      notes.push(options[Math.min(options.length - 1, Math.floor(random() * options.length))]);
    }
    return notes;
  }

  function noteNames(language) {
    return NOTE_NAMES[language] || NOTE_NAMES.es;
  }

  function recognizerVocabulary(language) {
    return Object.keys(noteNames(language).words);
  }

  function stepForMidi(midi) {
    const step = NATURAL_PCS.indexOf(((Number(midi) % 12) + 12) % 12);
    return step < 0 ? null : step;
  }

  function labelForStep(step, language) {
    return noteNames(language).labels[step] ?? null;
  }

  function noteLabel(midi, language) {
    const step = stepForMidi(midi);
    return step == null ? null : labelForStep(step, language);
  }

  function stepForWord(word, language) {
    const step = noteNames(language).words[normalizeWord(word)];
    return step == null ? null : step;
  }

  function normalizeWord(word) {
    return String(word || "")
      .trim()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  // Partial results grow word by word and the final result repeats them, so
  // only words beyond those already handled in the current utterance are emitted.
  function createUtteranceTracker(onWord) {
    let consumed = 0;
    // True between the first partial word of an utterance and its final result.
    let inUtterance = false;
    const wordsOf = (text) => String(text || "").trim().split(/\s+/).filter(Boolean);

    function emitFrom(words, source) {
      while (consumed < words.length) onWord(normalizeWord(words[consumed++]), source);
    }

    return Object.freeze({
      partial(text) {
        const words = wordsOf(text);
        if (words.length) inUtterance = true;
        emitFrom(words, "partial");
      },
      final(text) {
        emitFrom(wordsOf(text), "final");
        consumed = 0;
        inUtterance = false;
      },
      // Drop whatever is left of the utterance in progress (its final result
      // repeats words already handled), e.g. when the exercise moves on.
      skipCurrent() {
        if (inUtterance) consumed = Infinity;
      },
      reset() {
        consumed = 0;
        inUtterance = false;
      },
    });
  }

  // Waits on each note until it is read correctly; wrong answers are counted
  // and remembered per position.
  // answer() takes a diatonic step (see stepForWord), so the session does not
  // depend on the spoken language.
  function createReadingSession(notes) {
    const sequence = Array.from(notes || [], Number);
    let position = 0;
    let correct = 0;
    let wrong = 0;
    const missed = new Set();

    function answer(step) {
      if (!Number.isInteger(step) || step < 0 || step > 6) return { result: "ignored" };
      if (position >= sequence.length) return { result: "ignored" };
      const expected = stepForMidi(sequence[position]);
      if (step !== expected) {
        wrong += 1;
        missed.add(position);
        return { result: "wrong", expected, heard: step, position };
      }
      correct += 1;
      position += 1;
      return { result: "correct", position: position - 1, done: position >= sequence.length };
    }

    return Object.freeze({
      notes: Object.freeze(sequence),
      answer,
      get position() { return position; },
      get done() { return position >= sequence.length; },
      get stats() { return { correct, wrong, missed: new Set(missed) }; },
    });
  }

  global.MidiChordsNoteReading = Object.freeze({
    DEFAULT_LENGTH,
    NOTE_NAMES,
    READING_RANGES,
    createReadingSession,
    createUtteranceTracker,
    generateReadingSequence,
    labelForStep,
    naturalNotesInRange,
    noteLabel,
    normalizeWord,
    readingRange,
    recognizerVocabulary,
    stepForMidi,
    stepForWord,
  });
})(globalThis);
