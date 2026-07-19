import 'dart:math' as math;

const Map<int, String> grandPianoSamples = <int, String>{
  48: 'samples/grand_piano/C3.mp3',
  52: 'samples/grand_piano/E3.mp3',
  55: 'samples/grand_piano/G3.mp3',
  60: 'samples/grand_piano/C4.mp3',
  64: 'samples/grand_piano/E4.mp3',
  67: 'samples/grand_piano/G4.mp3',
  72: 'samples/grand_piano/C5.mp3',
};

const Map<int, String> guitarNylonSamples = <int, String>{
  40: 'samples/guitar_nylon/E2.mp3',
  45: 'samples/guitar_nylon/A2.mp3',
  50: 'samples/guitar_nylon/D3.mp3',
  52: 'samples/guitar_nylon/E3.mp3',
  55: 'samples/guitar_nylon/G3.mp3',
  59: 'samples/guitar_nylon/B3.mp3',
  64: 'samples/guitar_nylon/E4.mp3',
};

final class SampleTonePlan {
  const SampleTonePlan({
    required this.assetPath,
    required this.sampleMidi,
    required this.playbackRate,
  });

  final String assetPath;
  final int sampleMidi;
  final double playbackRate;
}

SampleTonePlan? planSampleTone({
  required int midi,
  required String instrument,
}) {
  final safeMidi = midi.clamp(0, 127);
  final isGuitar = instrument == 'guitar';
  final bank = isGuitar ? guitarNylonSamples : grandPianoSamples;
  final low = isGuitar ? 40 : 48;
  final high = isGuitar ? 76 : 84;
  if (safeMidi < low || safeMidi > high || bank.isEmpty) return null;

  final sampleMidi = bank.keys.reduce(
    (left, right) =>
        (left - safeMidi).abs() <= (right - safeMidi).abs() ? left : right,
  );
  final assetPath = bank[sampleMidi];
  if (assetPath == null) return null;
  final semitones = safeMidi - sampleMidi;
  final playbackRate = math
      .pow(2.0, semitones / 12.0)
      .toDouble()
      .clamp(0.5, 2.0);
  return SampleTonePlan(
    assetPath: assetPath,
    sampleMidi: sampleMidi,
    playbackRate: playbackRate,
  );
}
