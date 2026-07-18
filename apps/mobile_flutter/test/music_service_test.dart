import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/music_service.dart';

void main() {
  test('normalizes pitch classes and note names', () {
    expect(positiveMod12(-1), 11);
    expect(positiveMod12(13), 1);
    expect(noteNameLocal(61, language: 'es', preferFlat: true), 'Re♭4');
    expect(
      noteNameLocal(61, language: 'en', preferFlat: false, withOctave: false),
      'C#',
    );
  });

  test('generates chord inversions with the expected bass', () {
    final chord = generateChordLocal(
      rootPc: 0,
      suffix: '',
      inversion: 1,
      language: 'es',
      preferFlat: false,
    );

    expect(chord['name'], 'Do/Mi');
    expect(chord['notes_midi'], <int>[64, 67, 72]);
    expect(chord['intervals'], <int>[4, 7, 12]);
    expect(chord['description'], 'Mayor, primera inversión');
  });

  test('detects root position and inverted major chords', () {
    final root = detectChordLocal(
      notes: <int>[60, 64, 67],
      language: 'es',
      preferFlat: false,
    );
    final inverted = detectChordLocal(
      notes: <int>[64, 67, 72],
      language: 'es',
      preferFlat: false,
    );

    expect(root['name'], 'Do');
    expect(root['suffix'], '');
    expect(inverted['name'], 'Do/Mi');
    expect(inverted['inversion'], 1);
  });

  test('spells scale degrees from the selected tonic letter', () {
    final scale = generateScaleLocal(
      tonicPc: 8,
      patternName: 'Ionian',
      language: 'es',
      preferFlat: false,
      tonicLetterPc: 7,
    );

    expect(scale['pattern_localized_name'], 'Jónica');
    expect(scale['notes'], <String>[
      'Sol#4',
      'La#4',
      'Si#5',
      'Do#5',
      'Re#5',
      'Mi#5',
      'Fa##5',
      'Sol#5',
    ]);
  });

  test('lists UI patterns without exposing mutable catalog lists', () {
    final chords = chordPatternsForUi();
    final scales = scalePatternsLocal('es');

    expect(chords.first['suffix'], '');
    expect(chords[1]['suffix'], 'm');
    expect(scales.first['localized_name'], 'Jónica');

    (chords.first['intervals']! as List<int>).add(99);
    expect(chordPatternsForUi().first['intervals'], isNot(contains(99)));
  });
}
