import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/interval_data.dart';

void main() {
  test('interval generation catalog matches the shared theoretical grid', () {
    expect(intervalGridCategories.map((category) => category.key), <String>[
      'diminished',
      'minor',
      'major',
      'perfect',
      'augmented',
    ]);
    expect(
      intervalGridCategories
          .expand((category) => category.cells)
          .map((cell) => cell.label)
          .toSet(),
      containsAll(<String>['2d', '3m', '3M', '5J', '4A', '7A']),
    );
  });

  test('generated interval notes use C4 octave and selected distance', () {
    expect(generateIntervalNotes(0, 7), <int>[60, 67]);
    expect(generateIntervalNotes(11, 12), <int>[71, 83]);
    expect(generateIntervalNotes(13, 3), <int>[61, 64]);
  });

  test('generated interval distance is clamped to one octave', () {
    expect(generateIntervalNotes(0, -1), <int>[60, 60]);
    expect(generateIntervalNotes(0, 20), <int>[60, 72]);
  });
}
