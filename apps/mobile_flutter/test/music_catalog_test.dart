import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/music_catalog.dart';

void main() {
  test('chord catalog is complete and internally consistent', () {
    expect(chordPatternDefs, hasLength(52));

    final suffixes = chordPatternDefs
        .map((pattern) => pattern['suffix']! as String)
        .toList(growable: false);
    expect(suffixes.toSet(), hasLength(suffixes.length));
    expect(chordSuffixNamesEs.keys, containsAll(suffixes));
    expect(chordSuffixNamesEn.keys, containsAll(suffixes));
    expect(suffixes, containsAll(commonChordSuffixOrder));

    for (final pattern in chordPatternDefs) {
      final intervals = pattern['intervals']! as List<int>;
      expect(intervals, isNotEmpty, reason: '${pattern['suffix']}');
      expect(intervals.first, 0, reason: '${pattern['suffix']}');
      expect(
        intervals,
        orderedEquals(intervals.toList()..sort()),
        reason: '${pattern['suffix']}',
      );
    }
  });

  test('scale catalog is complete and internally consistent', () {
    expect(scalePatternDefs, hasLength(53));

    final names = scalePatternDefs
        .map((pattern) => pattern['name']! as String)
        .toList(growable: false);
    expect(names.toSet(), hasLength(names.length));
    expect(scaleNameEs.keys, containsAll(names));
    expect(names, containsAll(scaleBasicNames));

    for (final pattern in scalePatternDefs) {
      final intervals = pattern['intervals']! as List<int>;
      expect(intervals, isNotEmpty, reason: '${pattern['name']}');
      expect(intervals.first, 0, reason: '${pattern['name']}');
      expect(intervals.last, 12, reason: '${pattern['name']}');
      expect(
        intervals,
        orderedEquals(intervals.toList()..sort()),
        reason: '${pattern['name']}',
      );
    }
  });

  test('inversion labels remain aligned between languages', () {
    expect(inversionNamesEs, hasLength(inversionNamesEn.length));
    expect(inversionNamesEs.first, isEmpty);
    expect(inversionNamesEn.first, isEmpty);
  });
}
