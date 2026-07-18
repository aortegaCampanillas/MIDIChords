import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/scale_guitar_marker.dart';

void main() {
  test('matches desktop scale marker priority', () {
    expect(
      scaleGuitarMarkerStyle(
        note: 60,
        tonicPitchClass: 0,
        currentNotes: const <int>{60},
        selectedStartNote: 60,
      ),
      ScaleGuitarMarkerStyle.current,
    );
    expect(
      scaleGuitarMarkerStyle(
        note: 72,
        tonicPitchClass: 0,
        currentNotes: const <int>{},
        selectedStartNote: 72,
      ),
      ScaleGuitarMarkerStyle.selectedStart,
    );
    expect(
      scaleGuitarMarkerStyle(
        note: 48,
        tonicPitchClass: 0,
        currentNotes: const <int>{},
        selectedStartNote: 72,
      ),
      ScaleGuitarMarkerStyle.tonic,
    );
    expect(
      scaleGuitarMarkerStyle(
        note: 64,
        tonicPitchClass: 0,
        currentNotes: const <int>{},
        selectedStartNote: 72,
      ),
      ScaleGuitarMarkerStyle.degree,
    );
  });
}
