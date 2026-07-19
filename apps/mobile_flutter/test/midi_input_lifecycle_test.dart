import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/midi_input_lifecycle.dart';

void main() {
  test('start forwards MIDI bytes and setup changes once', () async {
    final data = StreamController<List<int>>.broadcast(sync: true);
    final setup = StreamController<Object?>.broadcast(sync: true);
    final packets = <List<int>>[];
    var setupChanges = 0;
    final lifecycle = MidiInputLifecycle(
      midiBytes: data.stream,
      setupEvents: setup.stream,
      onMidiBytes: packets.add,
      onSetupChanged: () => setupChanges += 1,
    );

    lifecycle.start();
    lifecycle.start();
    data.add(<int>[0x90, 60, 100]);
    setup.add(null);

    expect(packets, <List<int>>[
      <int>[0x90, 60, 100],
    ]);
    expect(setupChanges, 1);
    await lifecycle.dispose();
    await data.close();
    await setup.close();
  });

  test('dispose cancels both subscriptions and is idempotent', () async {
    final data = StreamController<List<int>>.broadcast(sync: true);
    final setup = StreamController<Object?>.broadcast(sync: true);
    var dataEvents = 0;
    var setupEvents = 0;
    final lifecycle = MidiInputLifecycle(
      midiBytes: data.stream,
      setupEvents: setup.stream,
      onMidiBytes: (_) => dataEvents += 1,
      onSetupChanged: () => setupEvents += 1,
    )..start();

    await lifecycle.dispose();
    await lifecycle.dispose();
    data.add(<int>[0x80, 60, 0]);
    setup.add(Object());

    expect(dataEvents, 0);
    expect(setupEvents, 0);
    await data.close();
    await setup.close();
  });
}
