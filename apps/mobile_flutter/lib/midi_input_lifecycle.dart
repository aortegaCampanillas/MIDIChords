import 'dart:async';

import 'package:flutter_midi_command/flutter_midi_command.dart';

/// Posee las suscripciones del plugin MIDI y expone solo datos independientes
/// del plugin al estado de la aplicación.
final class MidiInputLifecycle {
  MidiInputLifecycle({
    required Stream<List<int>>? midiBytes,
    required Stream<Object?>? setupEvents,
    required void Function(List<int> bytes) onMidiBytes,
    required void Function() onSetupChanged,
  }) : _midiBytes = midiBytes,
       _setupEvents = setupEvents,
       _onMidiBytes = onMidiBytes,
       _onSetupChanged = onSetupChanged;

  factory MidiInputLifecycle.fromCommand({
    required MidiCommand command,
    required void Function(List<int> bytes) onMidiBytes,
    required void Function() onSetupChanged,
  }) => MidiInputLifecycle(
    midiBytes: command.onMidiDataReceived?.map(
      (packet) => List<int>.unmodifiable(packet.data),
    ),
    setupEvents: command.onMidiSetupChanged,
    onMidiBytes: onMidiBytes,
    onSetupChanged: onSetupChanged,
  );

  final Stream<List<int>>? _midiBytes;
  final Stream<Object?>? _setupEvents;
  final void Function(List<int> bytes) _onMidiBytes;
  final void Function() _onSetupChanged;
  StreamSubscription<List<int>>? _dataSubscription;
  StreamSubscription<Object?>? _setupSubscription;
  bool _started = false;

  void start() {
    if (_started) return;
    _started = true;
    _dataSubscription = _midiBytes?.listen(_onMidiBytes);
    _setupSubscription = _setupEvents?.listen((_) => _onSetupChanged());
  }

  Future<void> dispose() async {
    if (!_started) return;
    _started = false;
    await _dataSubscription?.cancel();
    await _setupSubscription?.cancel();
    _dataSubscription = null;
    _setupSubscription = null;
  }
}
