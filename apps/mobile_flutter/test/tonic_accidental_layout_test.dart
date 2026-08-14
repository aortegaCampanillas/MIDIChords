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
        .split('Widget _buildScaleFingeringRow')
        .first;

    expect(scales, contains('helpAnchorHeight: compactPhone ? 36 : 48'));
    expect(scales, contains("'scales_pattern'"));
    expect(scales, contains('height: compactPhone ? 36 : 48'));
  });

  test('wide chord generation gives tonic enough room beside variant', () {
    final source = File('lib/main_pages.dart').readAsStringSync();
    final generationStart = source.indexOf(
      'Widget _buildChordGenerationPage()',
    );
    final generationEnd = source.indexOf(
      'Widget _buildCircleOfFifthsPage()',
      generationStart,
    );
    final generation = source.substring(generationStart, generationEnd);

    expect(
      generation,
      contains(
        "flex: 4,\n                      child: _helpAnchor(\n                        'generation_tonic'",
      ),
    );
    expect(
      generation,
      contains(
        "flex: 5,\n                      child: _helpAnchor(\n                        'generation_variant'",
      ),
    );
    expect(
      'isExpanded: true'.allMatches(generation).length,
      greaterThanOrEqualTo(4),
    );
    expect(
      'overflow: TextOverflow.ellipsis'.allMatches(generation).length,
      greaterThanOrEqualTo(4),
    );
  });

  test('wide chord piano releases unused height for generation controls', () {
    final source = File('lib/main.dart').readAsStringSync();
    final panelHeight = source
        .split('final panelHeight = switch (_tabIndex)')
        .last
        .split('final chordVariations =')
        .first;

    expect(panelHeight, contains("_instrumentView == 'guitar'"));
    expect(panelHeight, contains(': 148.0'));
    expect(
      panelHeight,
      contains("_instrumentView == 'guitar' ? 188.0 : 148.0"),
    );
  });

  test('wide generation places inversion beside play and help', () {
    final source = File('lib/main_pages.dart').readAsStringSync();
    final generation = source
        .split('if (!compactGenerationLayout) ...<Widget>[')
        .last
        .split("const SizedBox(height: 8),\n              if (compactPhone)")
        .first;

    final play = generation.indexOf("'generation_play_button'");
    final help = generation.indexOf('_buildChordVariantTheoryButton()');
    final inversion = generation.indexOf("'generation_inversion'");
    final hand = generation.indexOf('_buildGenerationHandRow()');
    expect(play, greaterThanOrEqualTo(0));
    expect(help, greaterThan(play));
    expect(inversion, greaterThan(help));
    expect(hand, greaterThan(inversion));
  });
}
