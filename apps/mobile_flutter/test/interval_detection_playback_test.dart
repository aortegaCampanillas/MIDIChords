import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('descending interval playback highlights notes in reverse order', () {
    final source = File('lib/main.dart').readAsStringSync();
    final playback = source
        .split('void _playIntervalMelody({bool reversed = false})')
        .last
        .split('\n  void _playMelodySequence(')
        .first;
    final sequence = source
        .split('void _playMelodySequence(')
        .last
        .split('\n}')
        .first;

    expect(
      playback,
      contains('displayIndices: reversed ? const <int>[1, 0] : null'),
    );
    expect(
      sequence,
      contains('_intervalPlayingIdx = displayIndices?[index] ?? index'),
    );
    expect(sequence, contains('displayIndices: displayIndices'));
  });
}
