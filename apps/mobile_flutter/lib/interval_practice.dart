import 'dart:math' as math;

class IntervalPracticeChoice {
  const IntervalPracticeChoice({
    required this.root,
    required this.semitones,
    required this.direction,
  });

  final int root;
  final int semitones;
  final int direction;

  int get target => root + direction * semitones;
}

class IntervalPracticeDeck {
  IntervalPracticeDeck({math.Random? random})
    : _random = random ?? math.Random();

  final math.Random _random;
  final List<int> _deck = <int>[];
  int? _lastSemitones;

  void reset() {
    _deck.clear();
    _lastSemitones = null;
  }

  IntervalPracticeChoice? draw({
    required Set<int> allowedSemitones,
    required bool randomTonic,
    required bool ascendingOnly,
  }) {
    final distances =
        allowedSemitones.where((value) => value >= 0 && value <= 12).toList()
          ..sort();
    if (distances.isEmpty) return null;
    _deck.removeWhere((value) => !allowedSemitones.contains(value));
    if (_deck.isEmpty) {
      _deck
        ..addAll(distances)
        ..shuffle(_random);
      if (_deck.length > 1 && _deck.first == _lastSemitones) {
        final first = _deck.removeAt(0);
        _deck.insert(1, first);
      }
    }
    final semitones = _deck.removeAt(0);
    _lastSemitones = semitones;
    final root = randomTonic ? 60 + _random.nextInt(12) : 60;
    final direction = ascendingOnly || semitones == 0
        ? 1
        : (_random.nextBool() ? 1 : -1);
    return IntervalPracticeChoice(
      root: root,
      semitones: semitones,
      direction: direction,
    );
  }
}
