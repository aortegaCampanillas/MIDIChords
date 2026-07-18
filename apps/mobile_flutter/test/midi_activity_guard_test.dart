import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/midi_activity_guard.dart';

final class _FakeWakeLock implements WakeLockPort {
  int enableCount = 0;
  int disableCount = 0;

  @override
  Future<void> enable() async {
    enableCount += 1;
  }

  @override
  Future<void> disable() async {
    disableCount += 1;
  }
}

void main() {
  test('repeated MIDI activity renews one wake-lock window', () {
    fakeAsync((async) {
      final wakeLock = _FakeWakeLock();
      final guard = MidiActivityGuard(
        wakeLock: wakeLock,
        idleDuration: const Duration(seconds: 10),
      );

      guard.bump();
      async.elapse(const Duration(seconds: 8));
      guard.bump();
      async.elapse(const Duration(seconds: 8));

      expect(wakeLock.enableCount, 1);
      expect(wakeLock.disableCount, 0);
      async.elapse(const Duration(seconds: 2));
      expect(wakeLock.disableCount, 1);
    });
  });

  test('dispose cancels activity and ignores later bumps', () {
    fakeAsync((async) {
      final wakeLock = _FakeWakeLock();
      final guard = MidiActivityGuard(
        wakeLock: wakeLock,
        idleDuration: const Duration(seconds: 10),
      );

      guard.bump();
      guard.dispose();
      guard.dispose();
      guard.bump();
      async.elapse(const Duration(seconds: 20));

      expect(wakeLock.enableCount, 1);
      expect(wakeLock.disableCount, 1);
    });
  });
}
