import 'package:flutter_test/flutter_test.dart';
import 'package:midichords/midi_output_controller.dart';

void main() {
  test('sends the program before the first note and caches it', () {
    final port = _FakeMidiOutputPort();
    final controller = MidiOutputController(port);

    controller.noteOn(note: 60, velocity: 80, program: 0);
    controller.noteOn(note: 64, velocity: 90, program: 0);

    expect(port.messages, <List<int>>[
      <int>[0xC0, 0],
      <int>[0x90, 60, 80],
      <int>[0x90, 64, 90],
    ]);
  });

  test('changes program when the visible instrument changes', () {
    final port = _FakeMidiOutputPort();
    final controller = MidiOutputController(port);

    controller.noteOn(note: 60, velocity: 80, program: 0);
    controller.noteOn(note: 55, velocity: 70, program: 25);

    expect(port.messages[2], <int>[0xC0, 25]);
    expect(port.messages[3], <int>[0x90, 55, 70]);
  });

  test('normalizes data bytes and sends note off', () {
    final port = _FakeMidiOutputPort();
    final controller = MidiOutputController(port);

    controller.noteOn(note: 188, velocity: 208, program: 153);
    controller.noteOff(188);

    expect(port.messages, <List<int>>[
      <int>[0xC0, 25],
      <int>[0x90, 60, 80],
      <int>[0x80, 60, 0],
    ]);
  });

  test('retries a program change that failed', () {
    final port = _FakeMidiOutputPort(failuresRemaining: 1);
    final controller = MidiOutputController(port);

    controller.noteOn(note: 60, velocity: 80, program: 25);
    controller.noteOn(note: 64, velocity: 80, program: 25);

    expect(port.messages, <List<int>>[
      <int>[0x90, 60, 80],
      <int>[0xC0, 25],
      <int>[0x90, 64, 80],
    ]);
  });

  test('reset forces the current program to be sent again', () {
    final port = _FakeMidiOutputPort();
    final controller = MidiOutputController(port);

    controller.noteOn(note: 60, velocity: 80, program: 0);
    controller.resetProgram();
    controller.noteOn(note: 62, velocity: 80, program: 0);

    expect(port.messages.where((message) => message.first == 0xC0), <List<int>>[
      <int>[0xC0, 0],
      <int>[0xC0, 0],
    ]);
  });
}

final class _FakeMidiOutputPort implements MidiOutputPort {
  _FakeMidiOutputPort({this.failuresRemaining = 0});

  final List<List<int>> messages = <List<int>>[];
  int failuresRemaining;

  @override
  void send(List<int> bytes) {
    if (failuresRemaining > 0) {
      failuresRemaining -= 1;
      throw StateError('MIDI unavailable');
    }
    messages.add(List<int>.of(bytes));
  }
}
