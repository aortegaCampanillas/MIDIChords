import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/piano_scroll_centering.dart';

void main() {
  test('centers the piano when entering theory generation modes', () {
    expect(modeUsesCenteredTheoryPiano(1), isTrue);
    expect(modeUsesCenteredTheoryPiano(2), isTrue);
    expect(modeUsesCenteredTheoryPiano(3), isTrue);
  });

  test('does not recenter unrelated modes', () {
    expect(modeUsesCenteredTheoryPiano(0), isFalse);
    expect(modeUsesCenteredTheoryPiano(4), isFalse);
    expect(modeUsesCenteredTheoryPiano(5), isFalse);
    expect(modeUsesCenteredTheoryPiano(6), isFalse);
  });

  test('mode selection and piano toggle request a fresh centering', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(source, contains('if (modeUsesCenteredTheoryPiano(value))'));
    expect(source, contains('final switchingToCenteredPiano ='));
    expect(source, contains('_needsPianoScrollSync = true;'));
  });
}
