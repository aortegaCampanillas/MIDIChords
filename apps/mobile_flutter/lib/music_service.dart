import 'dart:math' as math;

import 'music_catalog.dart';

const List<int> _rootLetterPcs = <int>[0, 2, 4, 5, 7, 9, 11];

class _ChordAnalysis {
  const _ChordAnalysis(this.rootPc, this.pattern, this.bassPc);

  final int? rootPc;
  final Map<String, dynamic>? pattern;
  final int? bassPc;
}

int positiveMod12(int value) {
  final m = value % 12;
  return m < 0 ? m + 12 : m;
}

String noteNameLocal(
  int midiNote, {
  required String language,
  required bool preferFlat,
  bool withOctave = true,
}) {
  const sharpEs = <String>[
    'Do',
    'Do#',
    'Re',
    'Re#',
    'Mi',
    'Fa',
    'Fa#',
    'Sol',
    'Sol#',
    'La',
    'La#',
    'Si',
  ];
  const sharpEn = <String>[
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
    'A',
    'A#',
    'B',
  ];
  const flatAliasesEs = <int, String>{
    1: 'Re♭',
    3: 'Mi♭',
    6: 'Sol♭',
    8: 'La♭',
    10: 'Si♭',
  };
  const flatAliasesEn = <int, String>{
    1: 'D♭',
    3: 'E♭',
    6: 'G♭',
    8: 'A♭',
    10: 'B♭',
  };
  final names = language == 'en' ? sharpEn : sharpEs;
  final flatAliases = language == 'en' ? flatAliasesEn : flatAliasesEs;
  final pc = positiveMod12(midiNote);
  final name = preferFlat ? (flatAliases[pc] ?? names[pc]) : names[pc];
  if (!withOctave) {
    return name;
  }
  final octave = (midiNote ~/ 12) - 1;
  return '$name$octave';
}

int _tonicLetterIndex(int tonicPc, bool preferFlats, [int? tonicLetterPc]) {
  if (tonicLetterPc != null) {
    final idx = _rootLetterPcs.indexOf(positiveMod12(tonicLetterPc));
    if (idx >= 0) return idx;
  }
  const mapSharp = <int, int>{
    0: 0,
    1: 0,
    2: 1,
    3: 1,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
    11: 6,
  };
  const mapFlat = <int, int>{
    0: 0,
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 4,
    7: 4,
    8: 5,
    9: 5,
    10: 6,
    11: 6,
  };
  final map = preferFlats ? mapFlat : mapSharp;
  return map[positiveMod12(tonicPc)] ?? 0;
}

String? _applyAccidental(String base, int diff) {
  switch (diff) {
    case 0:
      return base;
    case 1:
      return '$base#';
    case -1:
      return '$base♭';
    case 2:
      return '$base##';
    case -2:
      return '$base♭♭';
    default:
      return null;
  }
}

String _spellByDegree({
  required int rootPc,
  required int targetPc,
  required int degree,
  required String language,
  required bool preferFlats,
  int? midiNote,
  bool withOctave = false,
  int? tonicLetterPc,
}) {
  const letterEs = <String>['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si'];
  const letterEn = <String>['C', 'D', 'E', 'F', 'G', 'A', 'B'];
  const basePcs = <int>[0, 2, 4, 5, 7, 9, 11];
  final letters = language == 'en' ? letterEn : letterEs;
  final tonicLetter = _tonicLetterIndex(rootPc, preferFlats, tonicLetterPc);
  final letterIdx = (tonicLetter + degree) % 7;
  final naturalPc = basePcs[letterIdx];
  var diff = positiveMod12(targetPc - naturalPc);
  if (diff > 6) {
    diff -= 12;
  }
  final spelled = _applyAccidental(letters[letterIdx], diff);
  if (spelled == null) {
    final fallback = midiNote ?? targetPc;
    return noteNameLocal(
      fallback,
      language: language,
      preferFlat: preferFlats,
      withOctave: withOctave,
    );
  }
  if (!withOctave) {
    return spelled;
  }
  if (midiNote == null) {
    return spelled;
  }
  final octave = (midiNote ~/ 12) - 1;
  return '$spelled$octave';
}

int _chordIntervalDegree(int interval, String suffix) {
  final value = interval;
  if (value == 0 || value == 12) return 0;
  if (value == 1 || value == 2 || value == 13 || value == 14) return 1;
  if (value == 3 || value == 4 || value == 15) return 2;
  if (value == 5 || value == 17) return 3;
  if (value == 6 || value == 18) {
    if (suffix.contains('b5') || suffix.contains('dim')) return 4;
    return 3;
  }
  if (value == 7) return 4;
  if (value == 8) {
    if (suffix.contains('#5') || suffix.contains('aug')) return 4;
    return 5;
  }
  if (value == 9 || value == 21) return 5;
  if (value == 10 || value == 11) return 6;
  return math.max(0, math.min(6, value % 7));
}

/// Igual que `isMinorSuffix` / worker: `m…` pero no `maj…`.
bool isMinorChordSuffix(String suffix) {
  return suffix.startsWith('m') && !suffix.startsWith('maj');
}

/// Recuentos de #/♭ de armadura por tónica (misma tabla que la web).
({int? sharpCount, int? flatCount}) keySignatureSharpFlatCounts(
  int tonicPc,
  bool isMinor,
) {
  final pc = positiveMod12(tonicPc);
  final sharpMap = isMinor
      ? const <int, int>{4: 1, 11: 2, 6: 3, 1: 4, 8: 5, 3: 6, 10: 7}
      : const <int, int>{7: 1, 2: 2, 9: 3, 4: 4, 11: 5, 6: 6, 1: 7};
  final flatMap = isMinor
      ? const <int, int>{2: 1, 7: 2, 0: 3, 5: 4, 10: 5, 3: 6}
      : const <int, int>{5: 1, 10: 2, 3: 3, 8: 4, 1: 5, 6: 6};
  return (sharpCount: sharpMap[pc], flatCount: flatMap[pc]);
}

/// Misma regla que API/worker y `chordSymbolPreferFlat` en app.js: menos
/// alteraciones; empate enarmónico → bemoles.
bool chordSymbolPreferFlat(int rootPc, bool isMinor) {
  final c = keySignatureSharpFlatCounts(rootPc, isMinor);
  final sc = c.sharpCount;
  final fc = c.flatCount;
  if (sc == null && fc == null) {
    return false;
  }
  if (sc == null) {
    return true;
  }
  if (fc == null) {
    return false;
  }
  if (fc < sc) {
    return true;
  }
  if (sc < fc) {
    return false;
  }
  return true;
}

bool scalePrefersMinor(String patternName) {
  const minorNames = <String>{
    'Aeolian',
    'Dorian',
    'Phrygian',
    'Locrian',
    'Super Locrian',
    'Half Diminished',
    'Minor Pentatonic',
    'Minor Blues',
  };
  return patternName.contains('Minor') || minorNames.contains(patternName);
}

List<int> voicedIntervalsForInversion(List<int> intervals, int inversion) {
  if (intervals.isEmpty) {
    return <int>[];
  }
  final total = intervals.length;
  final inversionIdx = inversion.clamp(0, total - 1);
  final rotated = List<int>.generate(
    total,
    (i) => intervals[(inversionIdx + i) % total],
  );
  final voiced = <int>[];
  for (final raw in rotated) {
    var value = raw;
    if (voiced.isNotEmpty) {
      while (value <= voiced.last) {
        value += 12;
      }
    }
    voiced.add(value);
  }
  return voiced;
}

List<Map<String, dynamic>> chordPatternsForUi() {
  final priority = <String, int>{
    for (int i = 0; i < commonChordSuffixOrder.length; i += 1)
      commonChordSuffixOrder[i]: i,
  };
  final sorted = chordPatternDefs
      .map(
        (p) => <String, dynamic>{
          'suffix': p['suffix'],
          'intervals': List<int>.from(
            p['intervals'] as List<dynamic>? ?? const <dynamic>[],
          ),
        },
      )
      .toList();
  sorted.sort((a, b) {
    final aSuffix = (a['suffix'] as String? ?? '');
    final bSuffix = (b['suffix'] as String? ?? '');
    final aIntervals =
        (a['intervals'] as List<dynamic>? ?? const <dynamic>[]).length;
    final bIntervals =
        (b['intervals'] as List<dynamic>? ?? const <dynamic>[]).length;
    final aPrio = priority[aSuffix] ?? commonChordSuffixOrder.length;
    final bPrio = priority[bSuffix] ?? commonChordSuffixOrder.length;
    if (aPrio != bPrio) return aPrio.compareTo(bPrio);
    if (aIntervals != bIntervals) return aIntervals.compareTo(bIntervals);
    return aSuffix.compareTo(bSuffix);
  });
  return sorted;
}

List<Map<String, dynamic>> scalePatternsLocal(String language) {
  return scalePatternDefs
      .map((pattern) {
        final name = pattern['name'] as String? ?? 'Ionian';
        final localized = language == 'es' ? (scaleNameEs[name] ?? name) : name;
        return <String, dynamic>{
          'name': name,
          'localized_name': localized,
          'intervals': List<int>.from(
            pattern['intervals'] as List<dynamic>? ?? const <dynamic>[],
          ),
        };
      })
      .toList(growable: false);
}

_ChordAnalysis _analyzeChordNotes(Set<int> notes) {
  if (notes.isEmpty) {
    return const _ChordAnalysis(null, null, null);
  }
  final pcs = notes.map(positiveMod12).toSet();
  final bassPc = notes.reduce(math.min) % 12;
  final suffixPriority = <String, int>{
    for (int i = 0; i < commonChordSuffixOrder.length; i += 1)
      commonChordSuffixOrder[i]: i,
  };
  var bestScore = -999;
  var bestComplexity = -999;
  var bestRootIsBass = false;
  var bestPriority = commonChordSuffixOrder.length;
  int? bestRoot;
  Map<String, dynamic>? bestPattern;
  for (int root = 0; root < 12; root += 1) {
    for (final pattern in chordPatternDefs) {
      final intervals =
          (pattern['intervals'] as List<dynamic>? ?? const <dynamic>[])
              .map((e) => e as int)
              .toList(growable: false);
      final template = intervals.map((i) => (root + i) % 12).toSet();
      final extra = pcs.difference(template).length;
      final missing = template.difference(pcs).length;
      int score;
      if (extra == 0 && missing == 0) {
        score = 100;
      } else if (missing == 0) {
        score = 70 - extra;
      } else if (extra == 0) {
        score = 40 - missing;
      } else {
        continue;
      }
      final complexity = -intervals.length;
      // Distintos acordes pueden compartir exactamente las mismas notas
      // (p. ej. Do sus2 = Do-Re-Sol y Sol sus4 = Sol-Do-Re son el mismo
      // conjunto de pitch-classes). En ese empate exacto, la nota más
      // grave realmente tocada (bassPc) es la señal más fuerte de cuál
      // es la raíz percibida, y debe primar sobre la prioridad fija de
      // sufijos (que si no, siempre elegía "sus4" sobre "sus2").
      final rootIsBass = root == bassPc;
      final suffix = pattern['suffix'] as String? ?? '';
      final priority = suffixPriority[suffix] ?? commonChordSuffixOrder.length;
      final better =
          score > bestScore ||
          (score == bestScore && complexity > bestComplexity) ||
          (score == bestScore &&
              complexity == bestComplexity &&
              rootIsBass &&
              !bestRootIsBass) ||
          (score == bestScore &&
              complexity == bestComplexity &&
              rootIsBass == bestRootIsBass &&
              priority < bestPriority);
      if (better) {
        bestScore = score;
        bestComplexity = complexity;
        bestRootIsBass = rootIsBass;
        bestPriority = priority;
        bestRoot = root;
        bestPattern = pattern;
      }
    }
  }
  return _ChordAnalysis(bestRoot, bestPattern, bassPc);
}

Map<String, dynamic> generateChordLocal({
  required int rootPc,
  required String suffix,
  required int inversion,
  required String language,
  required bool preferFlat,
  int? tonicLetterPc,
}) {
  final selected = chordPatternDefs.firstWhere(
    (p) => (p['suffix'] as String? ?? '') == suffix,
    orElse: () => chordPatternDefs.first,
  );
  final intervals = List<int>.from(
    selected['intervals'] as List<dynamic>? ?? const <dynamic>[],
  );
  if (intervals.isEmpty) {
    return <String, dynamic>{
      'root_pc': positiveMod12(rootPc),
      'suffix': selected['suffix'] as String? ?? '',
      'inversion': 0,
      'name': '-',
      'notes_midi': <int>[],
      'notes': <String>[],
    };
  }
  final safeInversion = inversion.clamp(0, intervals.length - 1);
  final rootMidi = 60 + positiveMod12(rootPc);
  final voicedIntervals = voicedIntervalsForInversion(intervals, safeInversion);
  final notesMidi = voicedIntervals.map((i) => rootMidi + i).toList();
  final noteLabels = <String>[];
  final noteLabelsNoOct = <String>[];
  for (int i = 0; i < notesMidi.length; i += 1) {
    final interval = voicedIntervals[i];
    final midiNote = notesMidi[i];
    final degree = _chordIntervalDegree(interval, suffix);
    final pc = positiveMod12(midiNote);
    noteLabels.add(
      _spellByDegree(
        rootPc: rootPc,
        targetPc: pc,
        degree: degree,
        language: language,
        preferFlats: preferFlat,
        midiNote: midiNote,
        withOctave: true,
        tonicLetterPc: tonicLetterPc,
      ),
    );
    noteLabelsNoOct.add(
      _spellByDegree(
        rootPc: rootPc,
        targetPc: pc,
        degree: degree,
        language: language,
        preferFlats: preferFlat,
        midiNote: midiNote,
        withOctave: false,
        tonicLetterPc: tonicLetterPc,
      ),
    );
  }
  final rootName = _spellByDegree(
    rootPc: rootPc,
    targetPc: positiveMod12(rootPc),
    degree: 0,
    language: language,
    preferFlats: preferFlat,
    midiNote: rootPc,
    withOctave: false,
    tonicLetterPc: tonicLetterPc,
  );
  var chordName = '$rootName$suffix';
  String? bassName;
  if (safeInversion > 0 && noteLabelsNoOct.isNotEmpty) {
    bassName = noteLabelsNoOct.first;
    chordName = '$chordName/$bassName';
  }
  final suffixNames = language == 'es'
      ? chordSuffixNamesEs
      : chordSuffixNamesEn;
  final inversionNames = language == 'es' ? inversionNamesEs : inversionNamesEn;
  final baseDesc = suffixNames[suffix];
  String? description;
  if (baseDesc != null) {
    if (bassName != null) {
      description = safeInversion > 0 && safeInversion < inversionNames.length
          ? '$baseDesc, ${inversionNames[safeInversion]}'
          : '$baseDesc, ${language == 'es' ? 'bajo en' : 'bass on'} $bassName';
    } else {
      description = baseDesc;
    }
  }
  return <String, dynamic>{
    'root_pc': positiveMod12(rootPc),
    'suffix': suffix,
    'inversion': safeInversion,
    'name': chordName,
    'notes_midi': notesMidi,
    'notes': noteLabels,
    'notes_no_octave': noteLabelsNoOct,
    'intervals': voicedIntervals,
    if (description case final String d) 'description': d,
  };
}

Map<String, dynamic> detectChordLocal({
  required List<int> notes,
  required String language,
  required bool preferFlat,
}) {
  final midiNotes = notes.toSet().toList()..sort();
  if (midiNotes.isEmpty) {
    return <String, dynamic>{
      'name': '-',
      'extras_midi': <int>[],
      'notes_midi': <int>[],
      'notes': <String>[],
      'extras': <String>[],
    };
  }
  final pcs = midiNotes.map(positiveMod12).toSet();
  if (pcs.length == 1) {
    final single = midiNotes.first;
    final namePf = chordSymbolPreferFlat(positiveMod12(single), false);
    return <String, dynamic>{
      'name': noteNameLocal(
        single,
        language: language,
        preferFlat: namePf,
        withOctave: false,
      ),
      'notes_midi': midiNotes,
      'notes': midiNotes
          .map(
            (n) => noteNameLocal(
              n,
              language: language,
              preferFlat: preferFlat,
              withOctave: true,
            ),
          )
          .toList(),
      'extras_midi': <int>[],
      'extras': <String>[],
    };
  }
  final analysis = _analyzeChordNotes(midiNotes.toSet());
  final root = analysis.rootPc;
  final pattern = analysis.pattern;
  final bassPc = analysis.bassPc;
  if (root == null || pattern == null) {
    return <String, dynamic>{
      'name': midiNotes
          .map(
            (n) => noteNameLocal(
              n,
              language: language,
              preferFlat: preferFlat,
              withOctave: false,
            ),
          )
          .join(' + '),
      'notes_midi': midiNotes,
      'notes': midiNotes
          .map(
            (n) => noteNameLocal(
              n,
              language: language,
              preferFlat: preferFlat,
              withOctave: true,
            ),
          )
          .toList(),
      'extras_midi': <int>[],
      'extras': <String>[],
    };
  }
  final suffix = pattern['suffix'] as String? ?? '';
  final intervals = List<int>.from(
    pattern['intervals'] as List<dynamic>? ?? const <dynamic>[],
  );
  final inversionIndex = bassPc == null
      ? 0
      : math
            .max(
              0,
              intervals.indexWhere(
                (interval) => positiveMod12(root + interval) == bassPc,
              ),
            )
            .toInt();
  final degreeByPc = <int, int>{};
  for (final interval in intervals) {
    final pc = positiveMod12(root + interval);
    degreeByPc.putIfAbsent(pc, () => _chordIntervalDegree(interval, suffix));
  }
  final namePf = chordSymbolPreferFlat(root, isMinorChordSuffix(suffix));
  final rootName = _spellByDegree(
    rootPc: root,
    targetPc: root,
    degree: 0,
    language: language,
    preferFlats: namePf,
    midiNote: root,
    withOctave: false,
  );
  var chordName = '$rootName$suffix';
  String? resolvedBassName;
  if (bassPc != null && bassPc != root) {
    final bassDegree = degreeByPc[bassPc];
    resolvedBassName = bassDegree == null
        ? noteNameLocal(
            bassPc,
            language: language,
            preferFlat: namePf,
            withOctave: false,
          )
        : _spellByDegree(
            rootPc: root,
            targetPc: bassPc,
            degree: bassDegree,
            language: language,
            preferFlats: namePf,
            midiNote: bassPc,
            withOctave: false,
          );
    chordName = '$chordName/$resolvedBassName';
  }
  final suffixNames = language == 'es'
      ? chordSuffixNamesEs
      : chordSuffixNamesEn;
  final inversionNames = language == 'es' ? inversionNamesEs : inversionNamesEn;
  final baseDesc = suffixNames[suffix];
  String? description;
  if (baseDesc != null) {
    if (bassPc != null && bassPc != root && resolvedBassName != null) {
      if (inversionIndex > 0 && inversionIndex < inversionNames.length) {
        description = '$baseDesc, ${inversionNames[inversionIndex]}';
      } else {
        final bassWord = language == 'es' ? 'bajo en' : 'bass on';
        description = '$baseDesc, $bassWord $resolvedBassName';
      }
    } else {
      description = baseDesc;
    }
  }
  final expectedPcs = intervals.map((i) => positiveMod12(root + i)).toSet();
  final extras = midiNotes.where((n) => !expectedPcs.contains(n % 12)).toList();
  // Notas dentro del acorde reconocido: ortografía diatónica fija respecto a
  // su tónica (p. ej. la 3ª de Mi mayor siempre es Sol#, nunca Lab) — el
  // ajuste #/♭ del usuario solo decide notas "extra" fuera del acorde.
  final noteLabels = midiNotes.map((n) {
    final pc = positiveMod12(n);
    final degree = degreeByPc[pc];
    return degree == null
        ? noteNameLocal(
            n,
            language: language,
            preferFlat: preferFlat,
            withOctave: true,
          )
        : _spellByDegree(
            rootPc: root,
            targetPc: pc,
            degree: degree,
            language: language,
            preferFlats: namePf,
            midiNote: n,
            withOctave: true,
          );
  }).toList();
  return <String, dynamic>{
    'name': chordName,
    'notes_midi': midiNotes,
    'notes': noteLabels,
    'extras_midi': extras,
    'extras': extras
        .map(
          (n) => noteNameLocal(
            n,
            language: language,
            preferFlat: preferFlat,
            withOctave: true,
          ),
        )
        .toList(),
    'root_pc': root,
    'suffix': suffix,
    'inversion': inversionIndex,
    if (description case final String d) 'description': d,
  };
}

Map<String, dynamic> generateScaleLocal({
  required int tonicPc,
  required String patternName,
  required String language,
  required bool preferFlat,
  int? tonicLetterPc,
}) {
  final selected = scalePatternDefs.firstWhere(
    (p) => (p['name'] as String? ?? '') == patternName,
    orElse: () => scalePatternDefs.first,
  );
  final intervals = List<int>.from(
    selected['intervals'] as List<dynamic>? ?? const <dynamic>[],
  );
  final rootMidi = 60 + positiveMod12(tonicPc);
  final notesMidi = intervals.map((i) => rootMidi + i).toList();
  final names = <String>[];
  for (int idx = 0; idx < notesMidi.length; idx += 1) {
    final midiNote = notesMidi[idx];
    names.add(
      _spellByDegree(
        rootPc: tonicPc,
        targetPc: positiveMod12(midiNote),
        degree: idx,
        language: language,
        preferFlats: preferFlat,
        midiNote: midiNote,
        withOctave: true,
        tonicLetterPc: tonicLetterPc,
      ),
    );
  }
  final selectedName = selected['name'] as String? ?? patternName;
  final localized = language == 'es'
      ? (scaleNameEs[selectedName] ?? selectedName)
      : selectedName;
  return <String, dynamic>{
    'tonic_pc': positiveMod12(tonicPc),
    'pattern_name': selectedName,
    'pattern_localized_name': localized,
    'notes_midi': notesMidi,
    'notes': names,
    'intervals': intervals,
  };
}
