bool beamGroupStemUp(Iterable<double> noteYs, double staffMiddleY) {
  final values = noteYs.toList(growable: false);
  if (values.isEmpty) return true;
  final averageY = values.reduce((a, b) => a + b) / values.length;
  return averageY >= staffMiddleY;
}
