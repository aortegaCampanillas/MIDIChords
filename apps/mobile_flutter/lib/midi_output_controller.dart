import 'dart:typed_data';

import 'package:flutter_midi_command/flutter_midi_command.dart';

abstract interface class MidiOutputPort {
  void send(List<int> bytes);
}

final class MidiCommandOutputPort implements MidiOutputPort {
  MidiCommandOutputPort(this._command);

  final MidiCommand _command;

  @override
  void send(List<int> bytes) {
    _command.sendData(Uint8List.fromList(bytes));
  }
}

/// Encapsula los mensajes MIDI de salida y el timbre activo del receptor.
final class MidiOutputController {
  MidiOutputController(this._port);

  final MidiOutputPort _port;
  int? _program;

  void noteOn({
    required int note,
    required int velocity,
    required int program,
  }) {
    final normalizedProgram = program & 0x7F;
    if (_program != normalizedProgram &&
        _safeSend(<int>[0xC0, normalizedProgram])) {
      _program = normalizedProgram;
    }
    _safeSend(<int>[0x90, note & 0x7F, velocity & 0x7F]);
  }

  void noteOff(int note) {
    _safeSend(<int>[0x80, note & 0x7F, 0]);
  }

  void resetProgram() {
    _program = null;
  }

  bool _safeSend(List<int> bytes) {
    try {
      _port.send(bytes);
      return true;
    } catch (_) {
      return false;
    }
  }
}
