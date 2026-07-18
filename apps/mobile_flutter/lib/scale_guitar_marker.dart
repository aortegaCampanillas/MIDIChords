enum ScaleGuitarMarkerStyle { current, selectedStart, tonic, degree }

ScaleGuitarMarkerStyle scaleGuitarMarkerStyle({
  required int note,
  required int tonicPitchClass,
  required Set<int> currentNotes,
  int? selectedStartNote,
}) {
  if (currentNotes.contains(note)) {
    return ScaleGuitarMarkerStyle.current;
  }
  final normalizedTonic = ((tonicPitchClass % 12) + 12) % 12;
  final isTonic = ((note % 12) + 12) % 12 == normalizedTonic;
  if (isTonic && selectedStartNote == note) {
    return ScaleGuitarMarkerStyle.selectedStart;
  }
  if (isTonic) {
    return ScaleGuitarMarkerStyle.tonic;
  }
  return ScaleGuitarMarkerStyle.degree;
}
