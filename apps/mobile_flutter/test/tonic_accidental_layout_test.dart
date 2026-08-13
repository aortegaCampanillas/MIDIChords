import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('compact accidental selector leaves room for value and arrow', () {
    final source = File('lib/main.dart').readAsStringSync();
    final selector = source
        .split('Widget _buildTonicLetterAccidentalDropdowns')
        .last
        .split('List<InlineSpan> _splitPitchClassLabelSpans')
        .first;

    expect(selector, contains('width: 64'));
    expect('isExpanded: true'.allMatches(selector), hasLength(2));
    expect('horizontal: 8'.allMatches(selector), hasLength(2));
    expect('isDense: true'.allMatches(selector), hasLength(2));
    expect(selector, contains('double helpAnchorHeight = 56'));
    expect(selector, contains('height: helpAnchorHeight'));
  });

  test('scales uses compact tonic and type selectors', () {
    final source = File('lib/main_pages.dart').readAsStringSync();
    final scales = source
        .split('Widget _buildScaleGenerationPage()')
        .last
        .split('Widget _buildScaleFingeringRow()')
        .first;

    expect(scales, contains('helpAnchorHeight: 48'));
    expect(scales, contains("'scales_pattern'"));
    expect(scales, contains('height: 48'));
  });
}
