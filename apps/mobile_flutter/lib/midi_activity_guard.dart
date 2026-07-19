import 'dart:async';

import 'package:wakelock_plus/wakelock_plus.dart';

abstract interface class WakeLockPort {
  Future<void> enable();
  Future<void> disable();
}

final class PluginWakeLockPort implements WakeLockPort {
  const PluginWakeLockPort();

  @override
  Future<void> enable() => WakelockPlus.enable();

  @override
  Future<void> disable() => WakelockPlus.disable();
}

typedef ActivityTimerFactory = Timer Function(
  Duration duration,
  void Function() callback,
);

Timer _defaultTimerFactory(Duration duration, void Function() callback) =>
    Timer(duration, callback);

/// Ventana renovable de actividad MIDI, aislada de la UI y del plugin nativo.
final class MidiActivityGuard {
  MidiActivityGuard({
    required WakeLockPort wakeLock,
    required Duration idleDuration,
    ActivityTimerFactory timerFactory = _defaultTimerFactory,
  }) : _wakeLock = wakeLock,
       _idleDuration = idleDuration,
       _timerFactory = timerFactory;

  final WakeLockPort _wakeLock;
  final Duration _idleDuration;
  final ActivityTimerFactory _timerFactory;
  Timer? _timer;
  bool _disposed = false;
  bool _enabled = false;

  void bump() {
    if (_disposed) return;
    _timer?.cancel();
    if (!_enabled) {
      _enabled = true;
      unawaited(_ignorePluginFailure(_wakeLock.enable));
    }
    _timer = _timerFactory(_idleDuration, () {
      _timer = null;
      if (_disposed) return;
      _disable();
    });
  }

  void cancel() {
    _timer?.cancel();
    _timer = null;
    _disable();
  }

  void dispose() {
    if (_disposed) return;
    _disposed = true;
    cancel();
  }

  Future<void> _ignorePluginFailure(Future<void> Function() operation) async {
    try {
      await operation();
    } catch (_) {}
  }

  void _disable() {
    if (!_enabled) return;
    _enabled = false;
    unawaited(_ignorePluginFailure(_wakeLock.disable));
  }
}
