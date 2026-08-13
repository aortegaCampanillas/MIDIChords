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
      expect(intervalPage, isNot(contains('selectedCategory.name(_language)')));
      expect(pages, contains('for (var semitones = 0; semitones <= 12;'));
      expect(pages, contains('for (final category in intervalGridCategories)'));
      expect(intervalPage, isNot(contains('ChoiceChip(')));
      expect(intervalPage, contains('icon: Icons.arrow_left'));
      expect(intervalPage, contains('icon: Icons.arrow_right'));
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
      expect(main, contains('_tabIndex == 7 || _tabIndex == 9 ? 42 : 57'));
      expect(main, contains('_tabIndex == 7 || _tabIndex == 9 ? 58 : 43'));
      expect(
        main,
        contains('flex: _tabIndex == 7 || _tabIndex == 9 ? 42 : 56'),
      );
      expect(
        main,
        contains('flex: _tabIndex == 7 || _tabIndex == 9 ? 58 : 44'),
      );
      expect(main, contains("_instrumentView == 'guitar' ? 188.0 : 148.0"));
      expect(main, contains('value == 5 ||'));
      expect(main, contains('value == 7 ||'));
    },
  );
}
