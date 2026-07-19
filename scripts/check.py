#!/usr/bin/env python3
"""Punto de entrada estable para las verificaciones locales y de CI."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MOBILE_ROOT = PROJECT_ROOT / "apps" / "mobile_flutter"
PROFILE_ORDER = ("python", "web", "mobile")


def _display_command(command: Sequence[str]) -> str:
    return " ".join(command)


def _run(label: str, command: Sequence[str], *, cwd: Path = PROJECT_ROOT) -> None:
    print(f"\n==> {label}", flush=True)
    print(f"    $ {_display_command(command)}", flush=True)
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except FileNotFoundError as exc:
        executable = command[0]
        raise SystemExit(
            f"ERROR: no se encontró '{executable}'. Instala la herramienta necesaria "
            f"para ejecutar este perfil."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc


def check_python() -> None:
    _run(
        "Tests Python (incluye unittest y tests pytest)",
        (sys.executable, "-m", "pytest", "tests"),
    )


def check_web() -> None:
    node = shutil.which("node")
    if node is None:
        raise SystemExit("ERROR: el perfil web requiere Node.js en PATH.")

    web_root = PROJECT_ROOT / "apps/web"
    source_html = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (web_root / "app.html", web_root / "index.html", web_root / "fp30x.html")
    )
    script_paths = tuple(
        dict.fromkeys(re.findall(r'src="(/static/[^"?#]+\.js)"', source_html))
    )
    if not script_paths:
        raise SystemExit("ERROR: el HTML web no enlaza scripts bajo /static/.")
    for script_path in script_paths:
        local_path = f"apps/web{script_path}"
        _run(f"Sintaxis web: {Path(script_path).name}", (node, "--check", local_path))
    _run(
        "Sintaxis del Cloudflare Worker",
        (node, "--check", "apps/web/worker/_worker.js"),
    )
    _run(
        "Fuente de verdad pública de PianoPilot",
        (sys.executable, "scripts/check_pianopilot_landing.py"),
    )
    _run(
        "Estructura y metadatos de las landings",
        (sys.executable, "scripts/check_landing_pages.py"),
    )
    web_tests = tuple(
        str(path.relative_to(PROJECT_ROOT))
        for path in sorted((PROJECT_ROOT / "apps/web/test").glob("*.test.js"))
    )
    if not web_tests:
        raise SystemExit("ERROR: no se encontraron pruebas en apps/web/test/.")
    _run("Tests JavaScript de la web", (node, "--test", *web_tests))
    _run(
        "Bundle estático de Cloudflare Pages",
        (sys.executable, "scripts/build_web_pages_dist.py"),
    )


def check_mobile() -> None:
    flutter = shutil.which("flutter")
    if flutter is None:
        raise SystemExit("ERROR: el perfil mobile requiere Flutter en PATH.")

    _run("Análisis estático Flutter", (flutter, "analyze"), cwd=MOBILE_ROOT)
    _run("Tests Flutter", (flutter, "test"), cwd=MOBILE_ROOT)


CHECKS: dict[str, Callable[[], None]] = {
    "python": check_python,
    "web": check_web,
    "mobile": check_mobile,
}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta verificaciones reproducibles por plataforma.",
    )
    parser.add_argument(
        "profiles",
        nargs="*",
        choices=(*PROFILE_ORDER, "all"),
        default=["all"],
        help="Perfiles a ejecutar (por defecto: all).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    requested = PROFILE_ORDER if "all" in args.profiles else tuple(args.profiles)

    profiles = tuple(dict.fromkeys(requested))
    for profile in profiles:
        CHECKS[profile]()

    print(f"\nOK: verificaciones completadas ({', '.join(profiles)}).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
