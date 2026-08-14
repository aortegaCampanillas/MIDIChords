import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('circle of fifths omits the mobile instrument panel', () {
    final source = File('lib/main_pages.dart').readAsStringSync();
    final circlePage = source
        .split('Widget _buildCircleOfFifthsPage()')
        .last
        .split('Widget _buildScaleGenerationPage()')
        .first;

    expect(circlePage, contains('showInstrument: false'));
  });

  test('interval generation omits the mobile piano panel', () {
    final source = File('lib/main_pages.dart').readAsStringSync();
    final intervalGenerationPage = source
        .split('Widget _buildIntervalGenerationPage()')
        .last
        .split('Widget _buildMetronomePage()')
        .first;

    expect(intervalGenerationPage, contains('showInstrument: false'));
  });

  test('modes without an instrument use the full compact height', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(
      source,
      contains(
        '!showInstrument && bottomPanel == null\n'
        '                      ? constraints.maxHeight',
      ),
    );
  });
}
