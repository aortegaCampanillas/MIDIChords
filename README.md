# MIDI Chords Analyzer

Aplicación de escritorio en Python (Tkinter) para macOS que analiza notas MIDI en tiempo real, detecta acordes y los representa en teclado de piano y pentagrama.

Autor: Antonio Ortega González

## Características

- Detección de acordes en tiempo real a partir de notas activas.
- Entrada MIDI configurable (teclado/controlador externo).
- Síntesis de audio integrada con timbre tipo piano acústico.
- Teclado visual interactivo:
  - Resaltado de notas activas.
  - Soporte de entrada con ratón.
  - Pedal de sustain con tecla `Shift`.
- Pentagrama doble (clave de sol y clave de fa).
- Nombres de notas en español o inglés.
- Opción para mostrar nombres de nota sobre teclas blancas.
- Configuración persistente en `config.json`.

## Capturas / Recursos

- Logo de aplicación: `assets/app_logo.png`
- Llave del pentagrama: `assets/brace_left.png`

## Requisitos

- macOS
- Python 3.10+
- Dispositivo MIDI de entrada (opcional, también soporta ratón)

Dependencias Python:

- `mido`
- `python-rtmidi`
- `numpy`
- `sounddevice`

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

## Uso rápido

1. Abre la aplicación.
2. Pulsa `Abrir configuración`.
3. Selecciona idioma, entrada MIDI y salida de audio.
4. (Opcional) Activa `Mostrar notas en teclas blancas`.
5. Toca en el teclado MIDI o con el ratón sobre el piano en pantalla.
6. Mantén `Shift` para sustain; al soltar `Shift` se liberan notas sostenidas.

## Estructura del proyecto

- `app.py`: aplicación principal (UI, MIDI, audio, render de pentagrama/teclado).
- `requirements.txt`: dependencias del proyecto.
- `assets/`: recursos gráficos.

## Publicación en GitHub

```bash
git init
git add .
git commit -m "Initial commit: MIDI Chords Analyzer"
# crea el repositorio en GitHub y luego:
git remote add origin <URL_DEL_REPO>
git branch -M main
git push -u origin main
```

## Licencia

Este proyecto se distribuye bajo licencia MIT. Ver `LICENSE`.
