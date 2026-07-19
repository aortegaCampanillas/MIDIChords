import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/sample_tone_plan.dart';

void main() {
  test('exact piano sample needs no transposition', () {
    final plan = planSampleTone(midi: 60, instrument: 'piano');

    expect(plan?.assetPath, 'samples/grand_piano/C4.mp3');
    expect(plan?.sampleMidi, 60);
    expect(plan?.playbackRate, 1.0);
  });

  test('nearest sample is transposed by equal temperament', () {
    final plan = planSampleTone(midi: 62, instrument: 'piano');

    // Equal distance keeps the lower/earlier sample, matching the old reduce.
    expect(plan?.sampleMidi, 60);
    expect(plan?.playbackRate, closeTo(math.pow(2, 2 / 12), 0.000001));
  });

  test('guitar uses its own bank and playable range', () {
    final plan = planSampleTone(midi: 41, instrument: 'guitar');

    expect(plan?.assetPath, 'samples/guitar_nylon/E2.mp3');
    expect(plan?.sampleMidi, 40);
    expect(planSampleTone(midi: 39, instrument: 'guitar'), isNull);
    expect(planSampleTone(midi: 77, instrument: 'guitar'), isNull);
  });

  test('piano rejects notes reserved for synthesis fallback', () {
    expect(planSampleTone(midi: 47, instrument: 'piano'), isNull);
    expect(planSampleTone(midi: 85, instrument: 'piano'), isNull);
  });

  test('MIDI values are normalized before range selection', () {
    expect(planSampleTone(midi: -20, instrument: 'piano'), isNull);
    expect(planSampleTone(midi: 200, instrument: 'guitar'), isNull);
  });
}
