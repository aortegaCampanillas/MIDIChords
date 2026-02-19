# MIDIChords Monorepo

Repositorio reorganizado para albergar varias versiones de la app con librerías compartidas:

- `apps/desktop`: aplicación de escritorio (Tkinter, Python)
- `apps/web`: aplicación web (FastAPI + frontend JS)
- `apps/mobile_flutter`: aplicación tablet (Flutter para iOS/Android)
- `midichords`: librería Python común (teoría musical, audio y lógica compartida)
- `assets`: recursos gráficos y muestras de audio compartidas

## Estructura

```text
.
├── apps/
│   ├── desktop/
│   │   └── main.py
│   ├── web/
│   │   ├── main.py
│   │   ├── templates/
│   │   └── static/
│   └── mobile_flutter/
├── midichords/
├── assets/
├── launch.py
├── app.py
├── requirements.txt
└── requirements-web.txt
```

## Requisitos

- Python 3.10+
- Dependencias desktop: `requirements.txt`
- Dependencias web: `requirements-web.txt`
- Flutter (solo para móvil): 3.38+

## Instalación (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-web.txt
```

## Ejecución unificada

### Desktop

```bash
python launch.py desktop
```

También sigue funcionando:

```bash
python app.py
```

### Web

```bash
python launch.py web --host 127.0.0.1 --port 8000 --reload
```

Abrir: `http://127.0.0.1:8000`

## Flutter (tablets iOS/Android)

Proyecto base creado en `apps/mobile_flutter`.

```bash
python launch.py mobile
```

Opcional, para pasar argumentos a Flutter:

```bash
python launch.py mobile -- -d <device_id>
```

Nota: la app Flutter ya incluye detección, generación de acordes, generación de escalas, metrónomo y afinador.

## VS Code launch

Se añadieron dos configuraciones:

- `Desktop: MIDIChords`
- `Web: MIDIChords`

Archivo: `.vscode/launch.json`

## Librerías compartidas

- La lógica musical reutilizable para web/desktop está en `midichords/core/music_service.py`.
- Esta capa expone:
  - detección armónica de acordes
  - generación de acordes
  - generación de escalas
  - listados de patrones
