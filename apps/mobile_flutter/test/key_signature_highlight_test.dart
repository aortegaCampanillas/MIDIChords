import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/key_signature_highlight.dart';

void main() {
  test('maps generated chord notes to sharp and flat key signatures', () {
    expect(
      keySignatureIndexForMidi(midi: 66, signatureCount: 3, preferFlats: false),
      0,
    );
    expect(
      keySignatureIndexForMidi(midi: 68, signatureCount: 3, preferFlats: false),
      2,
    );
    expect(
      keySignatureIndexForMidi(midi: 70, signatureCount: 3, preferFlats: true),
      0,
    );
    expect(
      keySignatureIndexForMidi(midi: 66, signatureCount: 2, preferFlats: true),
      -1,
    );
  });

  test('maps all seven sharp signature positions', () {
    final cases = <(String, int)>[
      ('Fa#', 66),
      ('Do#', 61),
      ('Sol#', 68),
      ('Re#', 63),
      ('La#', 70),
      ('Mi#', 65),
      ('Si#', 60),
    ];
    for (var index = 0; index < cases.length; index += 1) {
      expect(
        keySignatureIndexForScaleNote(
          label: cases[index].$1,
          midi: cases[index].$2,
          signatureCount: 7,
          preferFlats: false,
        ),
        index,
      );
    }
  });

  test('maps all seven flat signature positions', () {
    final cases = <(String, int)>[
      ('Si♭', 70),
      ('Mi♭', 63),
      ('La♭', 68),
      ('Re♭', 61),
      ('Sol♭', 66),
      ('Do♭', 59),
      ('Fa♭', 64),
    ];
    for (var index = 0; index < cases.length; index += 1) {
      expect(
        keySignatureIndexForScaleNote(
          label: cases[index].$1,
          midi: cases[index].$2,
          signatureCount: 7,
          preferFlats: true,
        ),
        index,
      );
    }
  });

  test('ignores absent, natural, and double accidentals', () {
    expect(
      keySignatureIndexForScaleNote(
        label: 'Do#',
        midi: 61,
        signatureCount: 1,
        preferFlats: false,
      ),
      -1,
    );
    expect(
      keySignatureIndexForScaleNote(
        label: 'Fa',
        midi: 65,
        signatureCount: 7,
        preferFlats: false,
      ),
      -1,
    );
    expect(
      keySignatureIndexForScaleNote(
        label: 'Fa##',
        midi: 67,
        signatureCount: 7,
        preferFlats: false,
      ),
      -1,
    );
  });

  test('manual scale release clears every current-note visual state', () {
    final source = File('lib/main.dart').readAsStringSync();
    final releaseBlock = source
        .split('void _endInputDrag(int pointer)')
        .last
        .split('void _syncPianoScrollToMiddleC')
        .first;

    expect(releaseBlock, contains('if (_tabIndex == 3 && !_scaleLoopRunning)'));
    expect(releaseBlock, contains('_scaleCurrentNote = null;'));
    expect(releaseBlock, contains('_scaleCurrentIsLeft = null;'));
    expect(releaseBlock, contains('_scaleInputRawNote = null;'));
  });
}
