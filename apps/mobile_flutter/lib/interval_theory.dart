// Dart port of apps/web/static/interval_theory.js's chord/scale formula and
// construction helpers (mirrors midichords/core/music_theory.py on desktop).

// Grado (con alteración respecto a la escala mayor) por semitonos desde la
// tónica, hasta 24 semitonos (2 octavas) para cubrir 9a/11a/13a.
const Map<int, String> degreeBySemitone = <int, String>{
  0: '1',
  1: 'b2',
  2: '2',
  3: 'b3',
  4: '3',
  5: '4',
  6: 'b5',
  7: '5',
  8: '#5',
  9: '6',
  10: 'b7',
  11: '7',
  12: '8',
  13: 'b9',
  14: '9',
  15: '#9',
  17: '11',
  18: '#11',
  20: 'b13',
  21: '13',
};

// Grado diatónico (1-7) por semitonos desde la tónica, para escalas. A
// diferencia de degreeBySemitone (pensada para acordes, donde 8 semitonos se
// interpreta como quinta aumentada), aquí cada semitono siempre resuelve a una
// alteración del grado numérico correspondiente (8 semitonos -> b6, no #5).
const Map<int, String> scaleDegreeBySemitone = <int, String>{
  0: '1',
  1: 'b2',
  2: '2',
  3: 'b3',
  4: '3',
  5: '4',
  6: 'b5',
  7: '5',
  8: 'b6',
  9: '6',
  10: 'b7',
  11: '7',
  12: '8',
};

// Calidad abreviada de un intervalo (par de notas consecutivas de un acorde)
// por semitonos, en notación estándar: P=justo, M=mayor, m=menor, TT=tritono.
const Map<int, String> intervalQualityBySemitone = <int, String>{
  0: 'P1',
  1: 'm2',
  2: 'M2',
  3: 'm3',
  4: 'M3',
  5: 'P4',
  6: 'TT',
  7: 'P5',
  8: 'm6',
  9: 'M6',
  10: 'm7',
  11: 'M7',
  12: 'P8',
};

String intervalQualityAbbrev(int semitones) {
  final octaves = semitones ~/ 12;
  final remainder = semitones - octaves * 12;
  final base = intervalQualityBySemitone[remainder];
  if (base == null) return '${semitones}st';
  return octaves > 0 ? '$base+${octaves * 12}' : base;
}

List<int> _sortedUnique(List<int> notesMidi) {
  final ordered = notesMidi.toSet().toList()..sort();
  return ordered;
}

/// Fórmula de grados de un acorde: p. ej. rootPc=0 (Do), notesMidi=[60,64,67] -> "1 3 5".
String chordFormulaFromRoot(int rootPc, List<int> notesMidi) {
  final ordered = _sortedUnique(notesMidi);
  if (ordered.isEmpty) return '-';
  final rootMidi = ordered.first - (((ordered.first % 12) - rootPc) + 12) % 12;
  return ordered
      .map((n) => degreeBySemitone[n - rootMidi] ?? '${n - rootMidi}st')
      .join(' ');
}

/// Construcción de un acorde como intervalos apilados entre notas consecutivas:
/// p. ej. Do-Mi-Sol -> "M3 + m3".
String chordConstructionFromMidi(List<int> notesMidi) {
  final ordered = _sortedUnique(notesMidi);
  if (ordered.length < 2) return '-';
  final parts = <String>[
    for (var i = 1; i < ordered.length; i++)
      intervalQualityAbbrev(ordered[i] - ordered[i - 1]),
  ];
  return parts.join(' + ');
}

/// Reconstruye el voicing en posición fundamental (raíz en el bajo, resto
/// apilado ascendente) a partir de las pitch-classes presentes en un voicing
/// invertido.
List<int> rootPositionVoicing(int rootPc, List<int> notesMidi) {
  final root = ((rootPc % 12) + 12) % 12;
  final pcs = notesMidi.map((n) => ((n % 12) + 12) % 12).toSet().toList();
  final offsets = pcs.map((pc) => ((pc - root) + 12) % 12).toList()..sort();
  return offsets.map((offset) => 60 + offset).toList();
}

/// Rota una fórmula "1 - 3 - 5" tantas posiciones como indique el índice de
/// inversión: inversion=1 -> "3 - 5 - 1".
String rotateDegrees(String formula, int inversion) {
  final degrees = formula
      .split(' - ')
      .where((part) => part.isNotEmpty)
      .toList();
  if (degrees.isEmpty) return formula;
  final idx = inversion.clamp(0, degrees.length - 1);
  return <String>[
    ...degrees.sublist(idx),
    ...degrees.sublist(0, idx),
  ].join(' - ');
}

/// Paso entre dos notas consecutivas de una escala en tonos (T) y semitonos
/// (S): 1 -> "S", 2 -> "T", 3 -> "T+S", 4 -> "T+T", etc.
String scaleStepLabel(int semitones) {
  if (semitones <= 0) return '';
  final tones = semitones ~/ 2;
  final hasSemitone = semitones % 2 == 1;
  final parts = <String>[for (var i = 0; i < tones; i++) 'T'];
  if (hasSemitone) parts.add('S');
  return parts.join('+');
}

/// Patrón T/S de una escala a partir de sus notas MIDI ordenadas:
/// p. ej. Do jónico [60,62,64,65,67,69,71,72] -> "T T S T T T S".
String scalePatternFromMidi(List<int> notesMidi) {
  final ordered = _sortedUnique(notesMidi);
  if (ordered.length < 2) return '-';
  final parts = <String>[
    for (var i = 1; i < ordered.length; i++)
      scaleStepLabel(ordered[i] - ordered[i - 1]),
  ];
  return parts.join(' ');
}

/// Fórmula de grados de una escala a partir de sus notas MIDI ordenadas:
/// p. ej. Do jónico -> "1 2 3 4 5 6 7".
String scaleFormulaFromMidi(List<int> notesMidi) {
  final ordered = _sortedUnique(notesMidi);
  if (ordered.isEmpty) return '-';
  final rootMidi = ordered.first;
  // La nota final (octava) no se cuenta como grado nuevo en la fórmula.
  final degreeNotes = ordered.length > 1 && ordered.last - rootMidi == 12
      ? ordered.sublist(0, ordered.length - 1)
      : ordered;
  return degreeNotes
      .map((n) => scaleDegreeBySemitone[n - rootMidi] ?? '${n - rootMidi}st')
      .join(' ');
}

String _appendInversionDetail(
  String baseValue,
  int inversionIndex,
  String invertedValue,
  Map<String, dynamic> catalog,
  String language,
) {
  if (inversionIndex <= 0) return baseValue;
  final lang = language == 'en' ? 'en' : 'es';
  final names =
      ((catalog['inversion_names'] as Map?)?[lang] as List<dynamic>? ??
              const <dynamic>[])
          .map((value) => value.toString())
          .toList(growable: false);
  final label = inversionIndex < names.length
      ? names[inversionIndex]
      : (lang == 'en'
            ? 'Inversion $inversionIndex'
            : 'Inversión $inversionIndex');
  return '$baseValue (${label.toLowerCase()}: $invertedValue)';
}

/// Fórmula y construcción de un acorde (con detalle de inversión entre
/// paréntesis si aplica), para detección o generación. chordMidi debe ser el
/// voicing ya ordenado tal como se toca/genera (refleja la inversión).
({String formula, String construction}) chordFormulaAndConstruction({
  required Map<String, dynamic> catalog,
  required int? rootPc,
  required String? suffix,
  required int inversion,
  required List<int> chordMidi,
  required String language,
}) {
  if (rootPc == null || chordMidi.isEmpty) {
    return (formula: '-', construction: '-');
  }
  final theoryMap = (catalog['theory'] as Map?) ?? const <dynamic, dynamic>{};
  final curatedEntry = suffix != null ? theoryMap[suffix] as Map? : null;
  final curatedFormula = curatedEntry?['formula']?.toString();
  final rootFormula = (curatedFormula != null && curatedFormula.isNotEmpty)
      ? curatedFormula
      : chordFormulaFromRoot(rootPc, chordMidi);
  final inversionIndex = inversion < 0 ? 0 : inversion;
  final formula = _appendInversionDetail(
    rootFormula,
    inversionIndex,
    rotateDegrees(rootFormula, inversionIndex),
    catalog,
    language,
  );
  final String construction;
  if (inversionIndex > 0) {
    final rootPositionMidi = rootPositionVoicing(rootPc, chordMidi);
    final rootConstruction = chordConstructionFromMidi(rootPositionMidi);
    final inversionConstruction = chordConstructionFromMidi(chordMidi);
    construction = _appendInversionDetail(
      rootConstruction,
      inversionIndex,
      inversionConstruction,
      catalog,
      language,
    );
  } else {
    construction = chordConstructionFromMidi(chordMidi);
  }
  return (formula: formula, construction: construction);
}
