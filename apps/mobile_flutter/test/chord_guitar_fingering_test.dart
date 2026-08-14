import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('chord guitar markers display cached fingering numbers', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(source, contains("selectedVariation?['fingers']"));
    expect(source, contains('final selectedFingers = !leftHanded'));
    expect(source, contains('chordMode && useFrets'));
    expect(
      source,
      contains("'\${f == 0 ? 0 : (selectedFinger > 0 ? selectedFinger : 1)}'"),
    );
    expect(source, contains("child: Text(\n                            'X'"));
    expect(source, contains('color: Color(0xFFFF5A5A)'));
  });
}
