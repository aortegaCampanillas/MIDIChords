import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'interval generation uses a semitone table and a wider controls panel',
    () {
      final pages = File('lib/main_pages.dart').readAsStringSync();
      final main = File('lib/main.dart').readAsStringSync();
      final intervalPage = pages
          .split('Widget _buildIntervalGenerationPage()')
          .last
          .split('Widget _intervalGenerationPlayButton(')
          .first;

      expect(pages, contains('Widget _buildIntervalGenerationTable('));
      expect(pages, contains(r"'$label:'"));
      expect(intervalPage, contains('generatedIntervalName'));
      expect(intervalPage, contains('intervalGridDisplayNames('));
      expect(intervalPage, contains('selectedLabel: _intervalGenLabel'));
      expect(
        intervalPage,
        contains('final generatedIntervalName = _intervalGenSelected'),
      );
      expect(intervalPage, contains('_intervalGenSelected &&'));
      expect(intervalPage, isNot(contains('selectedCategory.name(_language)')));
      expect(pages, contains('for (var semitones = 0; semitones <= 12;'));
      expect(pages, contains('for (final category in intervalGridCategories)'));
      expect(
        intervalPage,
        contains('final compactPhone = _isCompactPhone(context);'),
      );
      expect(intervalPage, contains('? availableWidth'));
      expect(intervalPage, contains('compactPhone ? 0.0 : 3.0'));
      expect(intervalPage, contains('compactPhone ? 76.0 : 130.0'));
      expect(intervalPage, contains('height: cellHeight'));
      expect(intervalPage, isNot(contains('ChoiceChip(')));
      expect(
        intervalPage,
        contains("if (!_isCompactPhone(context)) ...<Widget>["),
      );
      expect(
        intervalPage,
        contains("_ui('Selecciona un intervalo', 'Select an interval')"),
      );
      expect(intervalPage, contains('icon: Icons.arrow_left'));
      expect(intervalPage, contains('icon: Icons.arrow_right'));
      expect(intervalPage, contains('compact: compactPhone'));
      expect(intervalPage, contains('hideLabel: compactPhone'));
      expect(pages, contains('width: compact ? 38 : 46'));
      expect(pages, contains('height: compact ? 40 : 48'));
      expect(intervalPage, isNot(contains("symbol: '▶↑'")));
      expect(intervalPage, isNot(contains("symbol: '▶↓'")));
      expect(
        intervalPage,
        contains('selected: _intervalGenLastPlayReversed == true'),
      );
      expect(
        intervalPage,
        contains('selected: _intervalGenLastPlayReversed == false'),
      );
      expect(
        main,
        contains('? 32\n                          : _tabIndex == 7\n                          ? 42\n                          : 57'),
      );
      expect(
        main,
        contains('? 68\n                          : _tabIndex == 7\n                          ? 58\n                          : 43'),
      );
      expect(
        main,
        contains('? 32\n                          : _tabIndex == 7\n                          ? 42\n                          : 56'),
      );
      expect(
        main,
        contains('? 68\n                          : _tabIndex == 7\n                          ? 58\n                          : 44'),
      );
      expect(main, contains("_instrumentView == 'guitar' ? 188.0 : 148.0"));
      expect(main, contains('value == 5 ||'));
      expect(main, contains('value == 7 ||'));
    },
  );
}
