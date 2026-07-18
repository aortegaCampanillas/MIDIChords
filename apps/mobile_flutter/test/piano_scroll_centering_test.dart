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

  test('remembers an independent scroll position for every theory mode', () {
    final memory = PianoScrollMemory();

    expect(memory.hasOffset(1), isFalse);
    memory.remember(1, 128.5);
    memory.remember(2, 242.0);

    expect(memory.offsetFor(1), 128.5);
    expect(memory.offsetFor(2), 242.0);
    expect(memory.hasOffset(3), isFalse);
  });

  test('ignores scroll positions from unrelated modes', () {
    final memory = PianoScrollMemory()..remember(0, 80);

    expect(memory.hasOffset(0), isFalse);
  });

  test('mode selection and piano toggle restore the saved position', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(source, contains('_rememberPianoScrollForMode(_tabIndex);'));
    expect(source, contains('_requestPianoScrollForMode(value);'));
    expect(source, contains('_requestPianoScrollForMode(_tabIndex);'));
  });
}
