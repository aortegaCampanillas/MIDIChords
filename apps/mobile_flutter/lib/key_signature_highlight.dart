int keySignatureIndexForScaleNote({
  required String? label,
  required int midi,
  required int signatureCount,
  required bool preferFlats,
}) {
  if (label == null || signatureCount <= 0) return -1;
  final text = label.replaceAll(RegExp(r'-?\d+$'), '');
  final accidentalCount = preferFlats
      ? '♭'.allMatches(text).length
      : '#'.allMatches(text).length + '♯'.allMatches(text).length;
  if (accidentalCount != 1) return -1;
  final pc = ((midi % 12) + 12) % 12;
  final naturalPc = preferFlats ? (pc + 1) % 12 : (pc - 1 + 12) % 12;
  const sharpNaturalPcOrder = <int>[5, 0, 7, 2, 9, 4, 11];
  const flatNaturalPcOrder = <int>[11, 4, 9, 2, 7, 0, 5];
  final order = preferFlats ? flatNaturalPcOrder : sharpNaturalPcOrder;
  final index = order.indexOf(naturalPc);
  return index >= 0 && index < signatureCount ? index : -1;
}
