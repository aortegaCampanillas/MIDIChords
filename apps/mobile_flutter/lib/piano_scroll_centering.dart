bool modeUsesCenteredTheoryPiano(int tabIndex) =>
    tabIndex == 1 || tabIndex == 2 || tabIndex == 3;

class PianoScrollMemory {
  final Map<int, double> _offsets = <int, double>{};

  void remember(int tabIndex, double offset) {
    if (modeUsesCenteredTheoryPiano(tabIndex)) {
      _offsets[tabIndex] = offset;
    }
  }

  bool hasOffset(int tabIndex) => _offsets.containsKey(tabIndex);

  double? offsetFor(int tabIndex) => _offsets[tabIndex];
}
