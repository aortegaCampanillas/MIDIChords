from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from typing import Optional

import mido
import sounddevice as sd

from midichords.core.app_constants import DISABLE_RTMIDI_SCAN_ENV, FORCE_RTMIDI_SCAN_ENV
from midichords.core.verbose_log import vlog


class MidiIOMixin:
    def _is_frozen_app(self) -> bool:
        return bool(getattr(sys, "frozen", False))

    def _is_debug_session(self) -> bool:
        try:
            return bool(sys.gettrace())
        except Exception:
            return False

    def _use_inprocess_midi(self) -> bool:
        # In frozen bundles and debugger sessions, avoid spawning python subprocesses
        # for MIDI probing/bridge to prevent GUI recursion and debugpy SystemExit noise.
        return self._is_frozen_app() or self._is_debug_session()

    def _scan_midi_inputs_isolated(self) -> tuple[list[str], Optional[str]]:
        """Lista entradas MIDI con `mido` en el proceso actual.

        Antes, en builds no congelados se usaba un subprocess con `sys.executable -c`.
        Eso fallaba a menudo desde hilos de fondo (p. ej. refresco de Ajustes) porque
        bajo depurador `sys.gettrace()` solo está activo en el hilo principal: el worker
        creía que no era sesión de depuración, lanzaba el probe externo y podía vaciar
        `input_names` mientras el bridge MIDI seguía funcionando.
        Listar puertos en proceso es barato y evita ese desajuste.
        """
        try:
            return [str(x) for x in mido.get_input_names()], None
        except Exception as exc:
            return [], str(exc)
    def refresh_devices(self) -> None:
        force_scan = os.environ.get(FORCE_RTMIDI_SCAN_ENV, "").strip() == "1"
        disable_scan = os.environ.get(DISABLE_RTMIDI_SCAN_ENV, "").strip() == "1"
        self.midi_backend_available = force_scan or not disable_scan
        self.midi_backend_warning = ""
        if self.midi_backend_available:
            self.input_names, probe_error = self._scan_midi_inputs_isolated()
            if probe_error:
                self.midi_backend_available = False
                self.midi_backend_warning = (
                    "MIDI scan crashed in backend. "
                    "Reconnect device and relaunch app. "
                    f"Details: {probe_error}"
                )
                self.status_var.set(self.midi_backend_warning)
        else:
            self.input_names = []
            self.midi_backend_warning = (
                "MIDI scan disabled by environment. "
                "Unset MIDICHORDS_DISABLE_RTMIDI_SCAN or set MIDICHORDS_FORCE_RTMIDI_SCAN=1."
            )
            self.status_var.set(self.midi_backend_warning)

        # sd.query_devices() puede introducir un glitch/ruido audible en el
        # OutputStream activo (observado al abrir Ajustes mientras sonaba una
        # nota). Si hay actividad de audio muy reciente, se salta este escaneo
        # y se conservan las listas ya cargadas hasta el próximo refresco.
        if not self.audio_engine.has_recent_activity():
            self.audio_output_map = {}
            self.audio_output_names = []
            self.audio_input_map = {}
            self.audio_input_names = []
            try:
                devices = sd.query_devices()
                for idx, device in enumerate(devices):
                    if int(device.get("max_input_channels", 0)) > 0:
                        in_name = f"{idx}: {device.get('name', 'Input')}"
                        self.audio_input_map[in_name] = idx
                        self.audio_input_names.append(in_name)
                    if int(device.get("max_output_channels", 0)) <= 0:
                        continue
                    name = f"{idx}: {device.get('name', 'Output')}"
                    self.audio_output_map[name] = idx
                    self.audio_output_names.append(name)
            except Exception as exc:
                self.status_var.set(f"{self.tr('error_list_outputs')}: {exc}")
                self.audio_output_names = []
                self.audio_output_map = {}
                self.audio_input_names = []
                self.audio_input_map = {}
        if hasattr(self, "tuner_input_combo"):
            self.tuner_input_combo["values"] = [""] + self.audio_input_names
            if self.tuner_input_name in self.tuner_input_combo["values"]:
                self.tuner_input_var.set(self.tuner_input_name)
            elif self.tuner_input_var.get() not in self.tuner_input_combo["values"]:
                self.tuner_input_var.set("")
        vlog(
            "midi",
            "refresh_devices: midi_inputs=%s (backend_ok=%s) audio_outputs=%s probe=%s",
            len(self.input_names),
            self.midi_backend_available,
            len(self.audio_output_names),
            (self.midi_backend_warning or "")[:120],
        )
        if self.input_names:
            vlog("midi", "  MIDI in: %s", " | ".join(self.input_names[:12]) + (" …" if len(self.input_names) > 12 else ""))
    def connect_ports(self) -> None:
        self.disconnect_ports(stop_audio=False)
        self.audio_engine.set_preset(str(self.config_data.get("sound_preset", "acoustic")))
        self.audio_engine.set_guitar_preset(str(self.config_data.get("guitar_sound_preset", "steel_clean")))

        input_name = self.config_data.get("midi_input", "")
        audio_name = self.config_data.get("audio_output", "")
        audio_error: Optional[str] = None
        vlog(
            "midi",
            "connect_ports: midi_input=%r audio_output=%r",
            input_name,
            audio_name,
        )

        if input_name:
            if self.midi_backend_available:
                if not self.input_names or input_name not in self.input_names:
                    self.midi_bridge_connected = False
                    self.midi_backend_warning = (
                        f"{self.tr('error_open_input')}: "
                        f"{self.tr('status_unavailable')} ({input_name})"
                    )
                else:
                    try:
                        self.midi_bridge_connected = self._start_midi_bridge(input_name)
                        vlog("midi", "MIDI bridge start: name=%r ok=%s", input_name, self.midi_bridge_connected)
                    except Exception as exc:
                        vlog("midi", "MIDI bridge error: %s", exc)
                        self.status_var.set(f"{self.tr('error_open_input')}: {exc}")
                        self.input_port = None
            else:
                self.input_port = None
                self.midi_bridge_connected = False

        audio_device_index = self.audio_output_map.get(audio_name)
        vlog("midi", "audio device index=%s map_hit=%s", audio_device_index, audio_name in self.audio_output_map)
        self.audio_engine.set_output_device(audio_device_index)
        if audio_name and audio_device_index is None:
            audio_error = self.tr("status_unavailable")

        midi_out_name = self.config_data.get("midi_output", "")
        if self.sound_output == "midi" and midi_out_name:
            self.midi_output_port = self.open_midi_output(midi_out_name)
            if self.midi_output_port is None:
                audio_error = self.tr("status_unavailable")
        vlog("midi", "midi output name=%r opened=%s", midi_out_name, self.midi_output_port is not None)

        in_state = input_name if self.midi_bridge_connected else self.tr("status_no_input")
        if audio_error:
            out_state = self.tr("status_unavailable")
        elif audio_name and audio_name in self.audio_output_map:
            out_state = audio_name
        else:
            out_state = self.tr("status_default_output")

        status = f"{self.tr('status_input')}: {in_state}\n{self.tr('status_output')}: {out_state}"
        if audio_error:
            status += f"\n{self.tr('status_audio_error')}: {audio_error}"
        if self.midi_backend_warning:
            status += f"\n{self.midi_backend_warning}"
        self.status_var.set(status)
    def disconnect_ports(self, stop_audio: bool = True) -> None:
        if self.input_port is not None:
            try:
                self.input_port.close()
            except Exception:
                pass
            self.input_port = None
        self._stop_midi_bridge()
        self.midi_bridge_connected = False

        if self.midi_output_port is not None:
            try:
                self.midi_output_port.close()
            except Exception:
                pass
            self.midi_output_port = None
        # Un puerto/dispositivo nuevo no conoce el último Program Change
        # enviado al anterior; forzar reenviarlo en la próxima nota.
        self._midi_out_program = None

        # Guardar Ajustes llama a connect_ports() para cualquier cambio (idioma,
        # preset de sonido, etc.), no solo el dispositivo de audio. Parar y
        # reabrir el OutputStream aquí en cada guardado introducía un ruido/click
        # perceptible en la siguiente nota tocada, aunque el dispositivo de audio
        # no hubiera cambiado. Solo se detiene explícitamente al cerrar la app.
        if stop_audio:
            self.audio_engine.stop()
    def _on_midi_message(self, message: mido.Message) -> None:
        self.message_queue.put(message)
    def _start_midi_bridge(self, input_name: str) -> bool:
        self._stop_midi_bridge()

        # In packaged apps and debugger sessions, avoid subprocess bridge.
        if self._use_inprocess_midi():
            try:
                self.input_port = mido.open_input(input_name, callback=self._on_midi_message)
                self.midi_bridge_proc = None
                self.midi_bridge_thread = None
                vlog("midi", "open_input (in-process): %r", input_name)
                return True
            except Exception as exc:
                vlog("midi", "open_input (in-process) failed: %s", exc)
                self.input_port = None
                return False

        bridge_code = """
import json
import sys
import time
import mido

def emit(payload):
    print(json.dumps(payload, ensure_ascii=False), flush=True)

name = sys.argv[1]
try:
    port = mido.open_input(name)
except Exception as exc:
    emit({"event": "error", "error": str(exc)})
    sys.exit(2)

emit({"event": "ready", "name": name})
while True:
    for msg in port.iter_pending():
        if msg.type == "note_on":
            emit({"event": "midi", "type": "note_on", "note": int(msg.note), "velocity": int(msg.velocity)})
        elif msg.type == "note_off":
            emit({"event": "midi", "type": "note_off", "note": int(msg.note), "velocity": int(msg.velocity)})
    time.sleep(0.01)
"""
        try:
            proc = subprocess.Popen(
                [sys.executable, "-u", "-c", bridge_code, input_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception:
            return False
        self.midi_bridge_proc = proc
        vlog("midi", "MIDI bridge subprocess spawning: %r", input_name)
        self.midi_bridge_thread = threading.Thread(target=self._read_midi_bridge_output, daemon=True)
        self.midi_bridge_thread.start()
        time.sleep(0.1)
        if proc.poll() is not None:
            self._stop_midi_bridge()
            vlog("midi", "MIDI bridge subprocess exited early (poll=%s)", proc.poll())
            return False
        vlog("midi", "MIDI bridge subprocess running: %r", input_name)
        return True
    def _read_midi_bridge_output(self) -> None:
        proc = self.midi_bridge_proc
        if proc is None or proc.stdout is None:
            return
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if payload.get("event") != "midi":
                continue
            msg_type = str(payload.get("type", ""))
            note = int(payload.get("note", -1))
            velocity = int(payload.get("velocity", 0))
            if msg_type not in {"note_on", "note_off"} or not (0 <= note <= 127):
                continue
            try:
                message = mido.Message(msg_type, note=note, velocity=max(0, min(127, velocity)))
            except Exception:
                continue
            self.message_queue.put(message)
    def _stop_midi_bridge(self) -> None:
        proc = self.midi_bridge_proc
        self.midi_bridge_proc = None
        self.midi_bridge_thread = None
        if proc is None:
            return
        try:
            proc.terminate()
            proc.wait(timeout=0.5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # MIDI Output support
    def get_midi_output_names(self) -> list[str]:
        """Lista los puertos MIDI de salida disponibles."""
        try:
            return [str(x) for x in mido.get_output_names()]
        except Exception:
            return []

    def open_midi_output(self, output_name: str) -> Optional[mido.ports.BaseOutput]:
        """Abre un puerto MIDI de salida."""
        try:
            return mido.open_output(output_name)
        except Exception as exc:
            vlog("midi", "open_output failed: %s", exc)
            return None

    def send_midi_note_on(self, midi_output: Optional[mido.ports.BaseOutput], note: int, velocity: int = 80) -> None:
        """Envía un note_on al puerto MIDI de salida."""
        if midi_output is None:
            return
        try:
            msg = mido.Message("note_on", note=note, velocity=velocity)
            midi_output.send(msg)
        except Exception as exc:
            vlog("midi", "send note_on failed: %s", exc)

    def send_midi_note_off(self, midi_output: Optional[mido.ports.BaseOutput], note: int) -> None:
        """Envía un note_off al puerto MIDI de salida."""
        if midi_output is None:
            return
        try:
            msg = mido.Message("note_off", note=note)
            midi_output.send(msg)
        except Exception as exc:
            vlog("midi", "send note_off failed: %s", exc)

    def send_midi_program_change(self, midi_output: Optional[mido.ports.BaseOutput], program: int) -> None:
        """Envía un Program Change (General MIDI) al puerto MIDI de salida."""
        if midi_output is None:
            return
        try:
            msg = mido.Message("program_change", program=max(0, min(127, program)))
            midi_output.send(msg)
        except Exception as exc:
            vlog("midi", "send program_change failed: %s", exc)
