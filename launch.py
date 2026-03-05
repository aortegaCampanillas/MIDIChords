from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from typing import Iterable


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

    try:
        uvicorn.run("apps.web.main:app", host=host, port=port, reload=reload)
    except OSError as exc:
        if "Address already in use" in str(exc) or "error while attempting to bind" in str(exc):
            raise SystemExit(
                f"El puerto {port} ya está en uso. "
                f"Prueba con: python launch.py web --host {host} --port {port + 1}"
            ) from exc
        raise


def run_mobile(mobile_args: list[str]) -> None:
    project_dir = Path(__file__).resolve().parent / "apps" / "mobile_flutter"
    cmd = ["flutter", "run"]
    has_sdkroot_define = any(
        arg.startswith("--dart-define=SdkRoot=") or arg.startswith("SdkRoot=")
        for arg in mobile_args
    ) or any(
        mobile_args[i] == "--dart-define"
        and i + 1 < len(mobile_args)
        and mobile_args[i + 1].startswith("SdkRoot=")
        for i in range(len(mobile_args))
    )
    if not has_sdkroot_define:
        requested_device: str | None = None
        for i, arg in enumerate(mobile_args):
            if arg == "-d" and i + 1 < len(mobile_args):
                requested_device = mobile_args[i + 1]
                break
            if arg.startswith("-d="):
                requested_device = arg.split("=", 1)[1]
                break
        if requested_device:
            devices = _flutter_list_devices(project_dir)
            resolved = _resolve_flutter_device(requested_device, devices)
            selected = next(
                (
                    d
                    for d in devices
                    if str(d.get("id", "")) == (resolved or requested_device)
                    or str(d.get("name", "")) == (resolved or requested_device)
                ),
                None,
            )
            if selected is not None:
                platform = str(selected.get("targetPlatform", "")).lower()
                if platform == "ios":
                    is_emulator = bool(selected.get("emulator", False))
                    sdk = "iphonesimulator" if is_emulator else "iphoneos"
                    try:
                        sdk_root = subprocess.check_output(
                            ["xcrun", "--sdk", sdk, "--show-sdk-path"],
                            text=True,
                        ).strip()
                    except Exception:
                        sdk_root = ""
                    if sdk_root:
                        cmd.extend(["--dart-define", f"SdkRoot={sdk_root}"])
    cmd.extend(mobile_args)
    try:
        subprocess.run(cmd, cwd=str(project_dir), check=True)
    except FileNotFoundError:
        raise SystemExit("flutter no está instalado o no está en PATH")
    except subprocess.CalledProcessError as exc:
        cmd_str = " ".join(cmd)
        raise SystemExit(
            f"flutter run falló con código {exc.returncode}.\n"
            f"Comando: {cmd_str}"
        ) from exc


def _local_lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No external traffic is sent; this only resolves the preferred local route.
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        sock.close()
    return ip


def _port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.25)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def _next_free_port(start_port: int, host: str = "127.0.0.1", max_tries: int = 30) -> int:
    port = int(start_port)
    for _ in range(max_tries):
        if not _port_in_use(port, host=host):
            return port
        port += 1
    raise SystemExit(
        f"No se encontró un puerto libre desde {start_port} tras {max_tries} intentos"
    )


def _flutter_list_devices(project_dir: Path) -> list[dict]:
    try:
        out = subprocess.check_output(
            ["flutter", "devices", "--machine"],
            cwd=str(project_dir),
            text=True,
        )
    except Exception:
        return []
    try:
        data = json.loads(out)
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict)]
    except Exception:
        return []
    return []


def _resolve_flutter_device(requested: str | None, devices: list[dict]) -> str | None:
    if not requested:
        return None
    req = requested.strip()
    if not req:
        return None

    # 1) Exact id/name match
    for d in devices:
        dev_id = str(d.get("id", ""))
        dev_name = str(d.get("name", ""))
        if req == dev_id or req == dev_name:
            return dev_id or dev_name

    req_l = req.lower()

    # 2) Common aliases for iOS simulators/emulators
    if req_l in {"apple_ios_simulator", "ios_simulator", "simulator", "emulator"}:
        # Prefer true iOS emulators/simulators first.
        for d in devices:
            platform = str(d.get("targetPlatform", "")).lower()
            emulator = bool(d.get("emulator", False))
            if platform == "ios" and emulator:
                dev_id = str(d.get("id", ""))
                if dev_id:
                    return dev_id
        # Fallback for tools that don't set `emulator=true` reliably.
        for d in devices:
            platform = str(d.get("targetPlatform", "")).lower()
            name = str(d.get("name", "")).lower()
            if platform == "ios" and ("simulator" in name or "iphone" in name):
                dev_id = str(d.get("id", ""))
                if dev_id:
                    return dev_id

    # 3) Partial/contains match in id or name
    for d in devices:
        dev_id = str(d.get("id", ""))
        dev_name = str(d.get("name", ""))
        hay = f"{dev_id} {dev_name}".lower()
        if req_l in hay:
            return dev_id or dev_name

    return None


def run_mobile_ipad(
    port: int,
    flutter_device: str | None,
    mobile_args: list[str],
    *,
    start_backend: bool = True,
    api_base_override: str | None = None,
) -> None:
    project_root = Path(__file__).resolve().parent
    project_dir = project_root / "apps" / "mobile_flutter"
    ios_dir = project_dir / "ios"
    selected_port = int(port)
    if start_backend:
        selected_port = _next_free_port(port, host="127.0.0.1")
        if selected_port != port:
            print(f"[iPad] Puerto {port} en uso. Se usará {selected_port} para el backend web.")
    if api_base_override:
        api_base = api_base_override.strip()
    else:
        lan_ip = _local_lan_ip()
        api_base = f"http://{lan_ip}:{selected_port}"

    env = os.environ.copy()

    print("[iPad] Preparando dependencias Flutter/iOS...")
    pub = subprocess.run(["flutter", "pub", "get"], cwd=str(project_dir), check=False, env=env)
    if pub.returncode != 0:
        raise SystemExit("[iPad] `flutter pub get` falló")
    pod = subprocess.run(["pod", "install"], cwd=str(ios_dir), check=False, env=env)
    if pod.returncode != 0:
        raise SystemExit("[iPad] `pod install` falló")

    web_proc: subprocess.Popen[str] | None = None
    if start_backend:
        web_cmd = [
            sys.executable,
            str(project_root / "launch.py"),
            "web",
            "--host",
            "0.0.0.0",
            "--port",
            str(selected_port),
        ]
        web_proc = subprocess.Popen(web_cmd, cwd=str(project_root), env=env)
        time.sleep(0.8)
        if web_proc.poll() is not None:
            raise SystemExit("No se pudo iniciar el backend web para iPad")

    flutter_cmd = ["flutter", "run"]
    devices = _flutter_list_devices(project_dir)
    if flutter_device:
        resolved = _resolve_flutter_device(flutter_device, devices)
        if not resolved:
            print(f"[iPad] Dispositivo no encontrado: {flutter_device}")
            print("[iPad] Disponibles:")
            for d in devices:
                print(f"  - {d.get('name')} ({d.get('id')})")
            print("[iPad] Ajusta --device en launch de VS Code.")
            return
        if resolved != flutter_device:
            print(f"[iPad] Device '{flutter_device}' resuelto a '{resolved}'.")
        flutter_cmd.extend(["-d", resolved])
    flutter_cmd.extend(["--dart-define", f"MIDICHORDS_API_BASE={api_base}"])
    flutter_cmd.extend(mobile_args)

    if start_backend:
        print(f"[iPad] Backend web: {api_base}")
        print("[iPad] Asegúrate de que iPad y Mac estén en la misma red Wi-Fi.")
    else:
        print(f"[iPad] Usando backend existente: {api_base}")
    print(f"[iPad] Ejecutando: {' '.join(flutter_cmd)}")

    try:
        try:
            proc = subprocess.run(flutter_cmd, cwd=str(project_dir), check=False, env=env)
        except FileNotFoundError:
            raise SystemExit("flutter no está instalado o no está en PATH")
        if proc.returncode != 0:
            print(f"[iPad] flutter run terminó con código {proc.returncode}.")
            print("[iPad] Revisa el log anterior (firmado iOS, device offline o target incorrecto).")
            print("[iPad] Puedes probar manualmente:")
            print(f"  cd {project_dir}")
            print(f"  {' '.join(flutter_cmd)}")
            return
    finally:
        if web_proc is not None and web_proc.poll() is None:
            web_proc.send_signal(signal.SIGINT)
            try:
                web_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                web_proc.kill()


def _normalize_mobile_ipad_args(
    raw_args: Iterable[str],
    *,
    default_port: int,
    default_device: str | None,
) -> tuple[list[str], int, str | None]:
    args = list(raw_args)
    cleaned: list[str] = []
    port = default_port
    device = default_device
    i = 0
    while i < len(args):
        item = args[i]
        if item == "--":
            i += 1
            continue
        if item == "--port":
            if i + 1 < len(args):
                try:
                    port = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
                continue
            i += 1
            continue
        if item.startswith("--port="):
            try:
                port = int(item.split("=", 1)[1])
            except ValueError:
                pass
            i += 1
            continue
        if item == "--device":
            if i + 1 < len(args):
                device = args[i + 1]
                i += 2
                continue
            i += 1
            continue
        if item.startswith("--device="):
            device = item.split("=", 1)[1]
            i += 1
            continue
        cleaned.append(item)
        i += 1
    return cleaned, port, device


def _extract_mobile_ipad_launcher_flags(
    raw_args: Iterable[str],
    *,
    default_no_backend: bool,
    default_api_base: str | None,
) -> tuple[list[str], bool, str | None]:
    args = list(raw_args)
    cleaned: list[str] = []
    no_backend = bool(default_no_backend)
    api_base = default_api_base
    i = 0
    while i < len(args):
        item = args[i]
        if item == "--no-backend":
            no_backend = True
            i += 1
            continue
        if item == "--api-base":
            if i + 1 < len(args):
                api_base = args[i + 1]
                i += 2
                continue
            i += 1
            continue
        if item.startswith("--api-base="):
            api_base = item.split("=", 1)[1]
            i += 1
            continue
        cleaned.append(item)
        i += 1
    return cleaned, no_backend, api_base


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MIDIChords launcher")
    parser.add_argument("target", choices=["desktop", "web", "mobile", "mobile-ipad"], nargs="?", default="desktop")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--device", default=None, help="Device id/name para flutter run (iPad)")
    parser.add_argument(
        "--no-backend",
        action="store_true",
        help="Para mobile-ipad: no arranca API web automáticamente.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Para mobile-ipad: URL base API existente (ej: http://192.168.1.100:8000).",
    )
    args, extra = parser.parse_known_args()
    # Unknown args are forwarded to flutter when target is mobile/mobile-ipad.
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.mobile_args = extra
    return args


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
    if args.target == "mobile-ipad":
        mobile_args = args.mobile_args if args.mobile_args else []
        mobile_args, final_no_backend, final_api_base = _extract_mobile_ipad_launcher_flags(
            mobile_args,
            default_no_backend=bool(args.no_backend),
            default_api_base=args.api_base,
        )
        mobile_args, final_port, final_device = _normalize_mobile_ipad_args(
            mobile_args,
            default_port=args.port,
            default_device=args.device,
        )
        run_mobile_ipad(
            port=final_port,
            flutter_device=final_device,
            mobile_args=mobile_args,
            start_backend=not bool(final_no_backend),
            api_base_override=final_api_base,
        )
        return
    run_desktop()


if __name__ == "__main__":
    main()
