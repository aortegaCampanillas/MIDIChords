import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/staff_beam_geometry.dart';

void main() {
  test('beamed notes on opposite sides share one stem direction', () {
    expect(beamGroupStemUp(<double>[110, 70], 100), isFalse);
    expect(beamGroupStemUp(<double>[130, 80], 100), isTrue);
  });

  test('empty beam groups have a safe upward default', () {
    expect(beamGroupStemUp(const <double>[], 100), isTrue);
  });
}
