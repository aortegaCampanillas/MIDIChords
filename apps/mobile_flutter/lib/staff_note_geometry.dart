double intervalStaffNoteX({
  required double startX,
  required int index,
  required bool compactWidth,
}) {
  final safeIndex = index < 0 ? 0 : index;
  final step = compactWidth ? 48.0 : 64.0;
  return startX + (safeIndex * step);
}
