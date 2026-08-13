import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/interval_practice.dart';

void main() {
  test('balanced deck covers every enabled interval before repeating', () {
    final deck = IntervalPracticeDeck(random: math.Random(7));
    final draws = List<IntervalPracticeChoice>.generate(
      3,
      (_) => deck.draw(
        allowedSemitones: <int>{1, 4, 7},
        randomTonic: false,
        ascendingOnly: true,
      )!,
    );
    expect(draws.map((choice) => choice.semitones).toSet(), <int>{1, 4, 7});
    expect(draws.every((choice) => choice.root == 60), isTrue);
    expect(draws.every((choice) => choice.direction == 1), isTrue);
  });

  test('filter and descending option constrain generated choices', () {
    final deck = IntervalPracticeDeck(random: math.Random(2));
    for (var index = 0; index < 12; index += 1) {
      final choice = deck.draw(
        allowedSemitones: <int>{6},
        randomTonic: true,
        ascendingOnly: false,
      )!;
      expect(choice.semitones, 6);
      expect(choice.root, inInclusiveRange(60, 71));
      expect(choice.target, anyOf(choice.root - 6, choice.root + 6));
    }
  });

  test('empty filter cannot produce an exercise', () {
    final deck = IntervalPracticeDeck(random: math.Random(1));
    expect(
      deck.draw(
        allowedSemitones: <int>{},
        randomTonic: false,
        ascendingOnly: true,
      ),
      isNull,
    );
  });
}
