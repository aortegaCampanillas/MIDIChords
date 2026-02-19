from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def run_desktop() -> None:
    from apps.desktop.main import main

    main()


def run_web(host: str, port: int, reload: bool) -> None:
    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Faltan dependencias de la versión web. Ejecuta: "
            "pip install -r requirements-web.txt"
        ) from exc
    try:
        import apps.web.main  # noqa: F401
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Faltan dependencias de la API web (FastAPI/Jinja2). Ejecuta: "
            "pip install -r requirements-web.txt"
        ) from exc

    uvicorn.run("apps.web.main:app", host=host, port=port, reload=reload)


def run_mobile(mobile_args: list[str]) -> None:
    project_dir = Path(__file__).resolve().parent / "apps" / "mobile_flutter"
    cmd = ["flutter", "run", *mobile_args]
    try:
        subprocess.run(cmd, cwd=str(project_dir), check=True)
    except FileNotFoundError:
        raise SystemExit("flutter no está instalado o no está en PATH")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MIDIChords launcher")
    parser.add_argument("target", choices=["desktop", "web", "mobile"], nargs="?", default="desktop")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("mobile_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target == "web":
        run_web(host=args.host, port=args.port, reload=bool(args.reload))
        return
    if args.target == "mobile":
        mobile_args = args.mobile_args if args.mobile_args else []
        if mobile_args and mobile_args[0] == "--":
            mobile_args = mobile_args[1:]
        run_mobile(mobile_args=mobile_args)
        return
    run_desktop()


if __name__ == "__main__":
    main()
