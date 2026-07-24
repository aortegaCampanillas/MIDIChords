/// Interval detection data: names and reference melodies.
library;

const Map<String, Map<int, String>> intervalNames = {
  "es": {
    0: "Unísono justo",
    1: "Segunda menor",
    2: "Segunda mayor",
    3: "Tercera menor",
    4: "Tercera mayor",
    5: "Cuarta justa",
    6: "Cuarta aum. / Quinta dim.",
    7: "Quinta justa",
    8: "Sexta menor",
    9: "Sexta mayor",
    10: "Séptima menor",
    11: "Séptima mayor",
    12: "Octava justa",
  },
  "en": {
    0: "Perfect Unison",
    1: "Minor Second",
    2: "Major Second",
    3: "Minor Third",
    4: "Major Third",
    5: "Perfect Fourth",
    6: "Aug. Fourth / Dim. Fifth",
    7: "Perfect Fifth",
    8: "Minor Sixth",
    9: "Major Sixth",
    10: "Minor Seventh",
    11: "Major Seventh",
    12: "Perfect Octave",
  },
};

// Enharmonic alternative names per semitone (excluding the main name in
// intervalNames). Not every semitone count has a common alternative.
const Map<String, Map<int, List<String>>> intervalAltNames = {
  "es": {
    0: ["Segunda disminuida"],
    1: ["Unísono aumentado"],
    2: ["Tercera disminuida"],
    3: ["Segunda aumentada"],
    4: ["Cuarta disminuida"],
    5: ["Tercera aumentada"],
    6: ["Tritono"],
    7: ["Sexta disminuida"],
    8: ["Quinta aumentada"],
    9: ["Séptima disminuida"],
    10: ["Sexta aumentada"],
    11: ["Octava disminuida"],
    12: ["Séptima aumentada"],
  },
  "en": {
    0: ["Diminished Second"],
    1: ["Augmented Unison"],
    2: ["Diminished Third"],
    3: ["Augmented Second"],
    4: ["Diminished Fourth"],
    5: ["Augmented Third"],
    6: ["Tritone"],
    7: ["Diminished Sixth"],
    8: ["Augmented Fifth"],
    9: ["Diminished Seventh"],
    10: ["Augmented Sixth"],
    11: ["Diminished Octave"],
    12: ["Augmented Seventh"],
  },
};

class IntervalGridCell {
  final int semitones;
  final String label;

  const IntervalGridCell(this.semitones, this.label);
}

class IntervalGridCategory {
  final String key;
  final String nameEs;
  final String nameEn;
  final List<IntervalGridCell> cells;

  const IntervalGridCategory({
    required this.key,
    required this.nameEs,
    required this.nameEn,
    required this.cells,
  });

  String name(String language) => language == "en" ? nameEn : nameEs;
}

/// Same theoretical interval grid used by desktop and web.
const List<IntervalGridCategory> intervalGridCategories = [
  IntervalGridCategory(
    key: "diminished",
    nameEs: "Disminuidos",
    nameEn: "Diminished",
    cells: [
      IntervalGridCell(0, "d2"),
      IntervalGridCell(2, "d3"),
      IntervalGridCell(4, "d4"),
      IntervalGridCell(6, "d5"),
      IntervalGridCell(7, "d6"),
      IntervalGridCell(9, "d7"),
      IntervalGridCell(11, "d8"),
    ],
  ),
  IntervalGridCategory(
    key: "minor",
    nameEs: "Menores",
    nameEn: "Minor",
    cells: [
      IntervalGridCell(1, "m2"),
      IntervalGridCell(3, "m3"),
      IntervalGridCell(8, "m6"),
      IntervalGridCell(10, "m7"),
    ],
  ),
  IntervalGridCategory(
    key: "major",
    nameEs: "Mayores",
    nameEn: "Major",
    cells: [
      IntervalGridCell(2, "M2"),
      IntervalGridCell(4, "M3"),
      IntervalGridCell(9, "M6"),
      IntervalGridCell(11, "M7"),
    ],
  ),
  IntervalGridCategory(
    key: "perfect",
    nameEs: "Justos",
    nameEn: "Perfect",
    cells: [
      IntervalGridCell(0, "P1"),
      IntervalGridCell(5, "P4"),
      IntervalGridCell(7, "P5"),
      IntervalGridCell(12, "P8"),
    ],
  ),
  IntervalGridCategory(
    key: "augmented",
    nameEs: "Aumentados",
    nameEn: "Augmented",
    cells: [
      IntervalGridCell(1, "A1"),
      IntervalGridCell(3, "A2"),
      IntervalGridCell(5, "A3"),
      IntervalGridCell(6, "A4"),
      IntervalGridCell(8, "A5"),
      IntervalGridCell(10, "A6"),
      IntervalGridCell(12, "A7"),
    ],
  ),
];

List<int> generateIntervalNotes(int rootPc, int semitones) {
  final normalizedRoot = rootPc % 12;
  final rootMidi = 60 + normalizedRoot;
  return <int>[rootMidi, rootMidi + semitones.clamp(0, 12)];
}

class IntervalMelody {
  final String nameEs;
  final String nameEn;
  final int beatsPerBar;
  final double? anacrusis;
  final int? jumpAt;
  final int? playbackStepMs;
  final bool? setupSlur;
  final int? highlightUntil;
  final List<int?> offsets;
  final List<String> durations;

  const IntervalMelody({
    required this.nameEs,
    required this.nameEn,
    required this.beatsPerBar,
    this.anacrusis,
    this.jumpAt,
    this.playbackStepMs,
    this.setupSlur,
    this.highlightUntil,
    required this.offsets,
    required this.durations,
  });
}

// Duration codes: w=redonda h=blanca q=negra e=corchea s=semicorchea
// Add "." for dotted. null=rest
const Map<int, IntervalMelody> intervalMelodies = {
  1: IntervalMelody(
    nameEs: "Tiburón (Jaws)",
    nameEn: "Jaws Theme",
    beatsPerBar: 4,
    offsets: [0, 1, 0, 1, 0, 1, 0, 1],
    durations: ["e", "e", "e", "e", "e", "e", "e", "e"],
  ),
  2: IntervalMelody(
    nameEs: "Cumpleaños feliz",
    nameEn: "Happy Birthday",
    beatsPerBar: 3,
    anacrusis: 1,
    jumpAt: 1,
    offsets: [0, 0, 2, 0, 5, 4],
    durations: ["e.", "s", "q", "q", "q", "h"],
  ),
  3: IntervalMelody(
    nameEs: "Smoke on the Water",
    nameEn: "Smoke on the Water",
    beatsPerBar: 4,
    offsets: [0, 3, 5, null, 0, null, 3, 6, 5],
    durations: ["q", "q", "q", "e", "e", "e", "q", "e", "h"],
  ),
  4: IntervalMelody(
    nameEs: "When the Saints Go Marching In",
    nameEn: "When the Saints Go Marching In",
    beatsPerBar: 4,
    anacrusis: 1,
    playbackStepMs: 320,
    offsets: [0, 4, 5, 7],
    durations: ["q", "q", "q", "w"],
  ),
  5: IntervalMelody(
    nameEs: "Here Comes the Bride",
    nameEn: "Here Comes the Bride",
    beatsPerBar: 4,
    jumpAt: 3,
    setupSlur: false,
    highlightUntil: 1,
    offsets: [0, 5, 5, 5, 0, 7, 4, 5],
    durations: ["q", "e.", "s", "h", "q", "e.", "s", "h"],
  ),
  6: IntervalMelody(
    nameEs: "María (West Side Story)",
    nameEn: "Maria (West Side Story)",
    beatsPerBar: 3,
    setupSlur: false,
    offsets: [0, 6, 7, 4, 0, -5],
    durations: ["q.", "e", "h", "q", "q", "h"],
  ),
  7: IntervalMelody(
    nameEs: "Star Wars",
    nameEn: "Star Wars",
    beatsPerBar: 4,
    offsets: [0, 7, 5, 4, 2, 12, 7],
    durations: ["h", "h", "et", "et", "et", "h", "q"],
  ),
  8: IntervalMelody(
    nameEs: "Love Story",
    nameEn: "Love Story",
    beatsPerBar: 4,
    anacrusis: 1,
    playbackStepMs: 520,
    highlightUntil: 2,
    offsets: [0, 0, 8, 8, 0, 1, 0, -2],
    durations: ["e", "e", "e", "e", "e", "e", "e", "e"],
  ),
  9: IntervalMelody(
    nameEs: "My Way",
    nameEn: "My Way",
    beatsPerBar: 4,
    anacrusis: 1.5,
    offsets: [0, 9, 7, 9],
    durations: ["e", "e", "e", "h"],
  ),
  10: IntervalMelody(
    nameEs: "Somewhere (West Side Story)",
    nameEn: "Somewhere (West Side Story)",
    beatsPerBar: 4,
    offsets: [0, 10, 9, 5, 2],
    durations: ["h", "h", "q.", "e", "h"],
  ),
  11: IntervalMelody(
    nameEs: "Take On Me",
    nameEn: "Take On Me",
    beatsPerBar: 4,
    offsets: [0, 11, 12],
    durations: ["h", "h", "h"],
  ),
  12: IntervalMelody(
    nameEs: "Somewhere Over the Rainbow",
    nameEn: "Somewhere Over the Rainbow",
    beatsPerBar: 4,
    offsets: [0, 12, 11, 7, 9, 11, 12],
    durations: ["h", "h", "q", "e", "e", "q", "q"],
  ),
};

String getIntervalName(int semitones, String language) {
  final lang = intervalNames.containsKey(language) ? language : "es";
  return intervalNames[lang]?[semitones] ?? "-";
}

String getIntervalAltNames(int semitones, String language) {
  final lang = intervalAltNames.containsKey(language) ? language : "es";
  final names = intervalAltNames[lang]?[semitones] ?? const <String>[];
  return names.isEmpty ? "-" : names.join(", ");
}

IntervalMelody? getIntervalMelody(int semitones) {
  return intervalMelodies[semitones];
}

String getIntervalMelodyName(int semitones, String language) {
  final melody = getIntervalMelody(semitones);
  if (melody == null) return "-";
  return language == "en" ? melody.nameEn : melody.nameEs;
}

List<int?> getIntervalMelodyNotes(List<int> intervalNotes) {
  if (intervalNotes.length < 2) {
    return List<int>.from(intervalNotes);
  }

  final raw = (intervalNotes[1] - intervalNotes[0]).abs();
  final mod = raw % 12;
  final semitones = (mod == 0 && raw > 0) ? 12 : mod;

  final melody = getIntervalMelody(semitones);
  if (melody == null) {
    return List<int>.from(intervalNotes)..sort();
  }

  final base = intervalNotes.reduce((a, b) => a < b ? a : b);
  final notes = <int?>[
    for (final offset in melody.offsets)
      if (offset == null)
        null
      else
        (base + offset >= 0 && base + offset <= 127) ? base + offset : null,
  ];
  return notes;
}

int durationToMs(String durationCode) {
  const baseMs = 500; // quarter note = 500ms (120 BPM)

  final isDotted = durationCode.endsWith(".");
  final code = isDotted
      ? durationCode.substring(0, durationCode.length - 1)
      : durationCode;

  final durations = {
    "w": baseMs * 4.0,
    "h": baseMs * 2.0,
    "q": baseMs * 1.0,
    "e": baseMs / 2.0,
    "s": baseMs / 4.0,
    "t": baseMs / 3.0,
    "et": baseMs / 3.0,
  };

  var ms = durations[code] ?? baseMs;
  if (isDotted) {
    ms = ms * 1.5;
  }

  return ms.toInt();
}
