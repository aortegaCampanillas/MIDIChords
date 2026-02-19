# MIDI Chords Analyzer

Desktop Python (Tkinter) app for macOS, Windows, and Linux that analyzes MIDI notes in real time, detects chords, and displays them on a piano keyboard and grand staff.

Author: Antonio Ortega González

## Features

- Real-time chord detection from currently active notes.
- Configurable MIDI input (external keyboard/controller).
- Built-in audio synthesis with an acoustic-piano-like timbre.
- Additional sampled presets:
  - `Grand piano (sample)`
  - `Nylon guitar (sample)`
- Interactive visual keyboard:
  - Active note highlighting.
  - Mouse input support.
  - Sustain pedal behavior using the `Shift` key.
- Grand staff display (treble and bass clef).
- Note names in Spanish or English.
- Option to show note names on white keys.
- Persistent configuration stored in `config.json`.

## Assets

- Application logo: `assets/app_logo.png`
- Staff brace image: `assets/brace_left.png`
- Instrument samples:
  - `assets/samples/grand_piano/*.mp3`
  - `assets/samples/guitar_nylon/*.mp3`
  - Attribution: `assets/samples/ATTRIBUTION.md`

## Requirements

- macOS, Windows 10/11, or Linux
- Python 3.10+
- MIDI input device (optional, mouse input is also supported)

Python dependencies:

- `mido`
- `python-rtmidi`
- `numpy`
- `sounddevice`

## Installation (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (macOS)

```bash
python app.py
```

## Installation (Linux)

Install Python and audio/MIDI runtime libraries first (Ubuntu/Debian example):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip libasound2-dev libjack-jackd2-dev
```

Then create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (Linux)

```bash
python app.py
```

## Installation (Windows)

If you have Python Launcher (`py`):

```powershell
py -3 -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

If `py` is not available, use `python`:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Or activate the environment from Command Prompt (`cmd`) without changing PowerShell policy:

```cmd
.venv\Scripts\activate.bat
```

If neither `py` nor `python` is recognized, install Python first:

```powershell
winget install Python.Python.3.12
```

## Run (Windows)

With Python Launcher:

```powershell
py app.py
```

Or with `python`:

```powershell
python app.py
```

## Windows Troubleshooting

### Error installing `python-rtmidi` (missing C/C++ compiler)

If you see an error like:

- `ERROR: Unknown compiler(s): [['icl'], ['cl'], ['c++'], ...]`
- `Could not find ... vswhere.exe`

`pip` is trying to build `python-rtmidi` from source, but no C/C++ build tools are installed.

Recommended fix (simplest):

1. Install Python 3.12.
2. Recreate the virtual environment with Python 3.12.
3. Reinstall requirements.

```powershell
deactivate
Remove-Item -Recurse -Force .venv
winget install Python.Python.3.12
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If `py` is not available, use the Python 3.12 executable directly:

```powershell
& "C:\Users\<YourUser>\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv
```

Alternative:

- Install Visual Studio Build Tools (C++) and then run `pip install -r requirements.txt` again.

## Quick Start

1. Open the app.
2. Click `Abrir configuración`.
3. Select language, MIDI input, and audio output.
4. (Optional) Enable `Mostrar notas en teclas blancas`.
5. Play notes on your MIDI keyboard or click keys on the on-screen piano.
6. Hold `Shift` for sustain; release `Shift` to release sustained notes.

## Project Structure

- `app.py`: main application (UI, MIDI, audio, staff/keyboard rendering).
- `requirements.txt`: project dependencies.
- `assets/`: graphic assets.

## Publish to GitHub

```bash
git init
git add .
git commit -m "Initial commit: MIDI Chords Analyzer"
# create the repository on GitHub, then:
git remote add origin <URL_DEL_REPO>
git branch -M main
git push -u origin main
```

## License

This project is distributed under the MIT license. See `LICENSE`.
