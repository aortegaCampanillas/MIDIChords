double intervalStaffNoteX({
  required double startX,
  required int index,
  required bool compactWidth,
}) {
  final safeIndex = index < 0 ? 0 : index;
  final step = compactWidth ? 48.0 : 64.0;
  return startX + (safeIndex * step);
}

/// Horizontal clearance after the last accidental in a key signature.
///
/// A note accidental is painted to the left of its note head, so the usual
/// control spacing is not enough to distinguish it from the signature.
double staffKeySignatureTrailingGap({required bool compactWidth}) =>
    compactWidth ? 20.0 : 32.0;

/// Small visual offset used when a chord is duplicated across both staves.
/// It keeps adjacent boundary notes (for example B♭3 and C4) from touching
/// while preserving each hand as a vertically aligned chord.
