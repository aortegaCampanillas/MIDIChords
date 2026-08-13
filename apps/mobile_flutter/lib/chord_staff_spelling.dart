Map<int, bool> chordStaffNotePreferFlats({
  required Map<String, dynamic>? chord,
  required Map<int, int> displayToSourceNote,
  Iterable<int> additionalDisplayNotes = const <int>[],
}) {
  if (chord == null) return const <int, bool>{};
  final midi = (chord['notes_midi'] as List<dynamic>? ?? const <dynamic>[])
      .whereType<num>()
      .map((note) => note.toInt())
      .toList();
  final labels = (chord['notes'] as List<dynamic>? ?? const <dynamic>[])
      .map((label) => '$label')
      .toList();
  final exact = <int, bool>{};
  final byPitchClass = <int, bool>{};
  for (var index = 0; index < midi.length && index < labels.length; index++) {
    final label = labels[index];
    final bool? preferFlat = label.contains('♭')
        ? true
        : label.contains('#')
        ? false
        : null;
    if (preferFlat == null) continue;
    exact[midi[index]] = preferFlat;
    byPitchClass[((midi[index] % 12) + 12) % 12] = preferFlat;
  }

  final result = <int, bool>{};
  for (final entry in displayToSourceNote.entries) {
    final preference =
        exact[entry.value] ?? byPitchClass[((entry.value % 12) + 12) % 12];
    if (preference != null) result[entry.key] = preference;
  }
  for (final note in additionalDisplayNotes) {
    final preference = byPitchClass[((note % 12) + 12) % 12];
    if (preference != null) result[note] = preference;
  }
  return result;
}
