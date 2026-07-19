import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/piano_layout.dart';

void main() {
  test('fits a short keyboard exactly without scrolling', () {
    final metrics = computePianoKeyMetrics(
      viewportW: 360,
      viewportH: 200,
      whiteKeyCount: 10,
    );

    expect(metrics.whiteW, 36);
    expect(metrics.whiteH, 124);
    expect(metrics.scrollable, isFalse);
  });

  test('uses the available height when a wide viewport can fit all keys', () {
    final metrics = computePianoKeyMetrics(
      viewportW: 1000,
      viewportH: 100,
      whiteKeyCount: 20,
    );

    expect(metrics.whiteW, 50);
    expect(metrics.whiteH, 94);
    expect(metrics.scrollable, isFalse);
  });

  test('keeps web key proportions and enables scroll for a full piano', () {
    final metrics = computePianoKeyMetrics(
      viewportW: 1000,
      viewportH: 130,
      whiteKeyCount: 52,
    );

    expect(metrics.whiteW, pianoMaxWhiteKeyWidth);
    expect(metrics.whiteH, pianoWhiteKeyHeight);
    expect(metrics.scrollable, isTrue);
  });
}
