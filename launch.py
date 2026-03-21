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
    if reload:
        print("[web] Nota: --reload se ignora; wrangler ya sirve en modo desarrollo.")

    wrangler_cmd = _get_wrangler_cmd()
    project_root = Path(__file__).resolve().parent
    cmd = [
        *wrangler_cmd,
        "dev",
        "apps/web/worker/_worker.js",
        "--assets",
        "apps/web",
        "--ip",
        host,
        "--port",
        str(port),
    ]
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"wrangler dev falló con código {exc.returncode}") from exc


def _get_wrangler_cmd() -> list[str]:
    def _can_run(cmd: list[str], version_args: list[str]) -> bool:
        try:
            proc = subprocess.run(
                [*cmd, *version_args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return proc.returncode == 0
        except OSError:
            return False

    for candidate, v_args in (
        (["wrangler"], ["--version"]),
        (["npx", "--yes", "wrangler@4"], ["--version"]),
        (["npx", "wrangler"], ["--version"]),
    ):
        if _can_run(candidate, v_args):
            return candidate
    raise SystemExit(
        "No se encontró wrangler en PATH ni vía npx. Instala Node.js y luego: npm i -g wrangler"
    )


def _load_deploy_secrets(project_root: Path) -> None:
    """Carga CLOUDFLARE_* desde un fichero seguro si no están ya en el entorno."""
    candidates = [
        project_root / "apps" / "web" / ".env.deploy",
        project_root / ".env.deploy",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if value.startswith(("'", '"')) and value[0] == value[-1]:
                    value = value[1:-1]
                if key and key not in os.environ and value:
                    os.environ[key] = value
            return
        except OSError:
            continue


def run_deploy_web(project_name: str | None) -> None:
    """Prepara el bundle estático y despliega a Cloudflare Pages (producción) sin GitHub Actions."""
    import shutil

    project_root = Path(__file__).resolve().parent
    web_dir = project_root / "apps" / "web"
    pages_dist = web_dir / "pages-dist"

    # Cargar secretos desde fichero si existen (apps/web/.env.deploy o .env.deploy)
    _load_deploy_secrets(project_root)

    print("[deploy-web] Preparando bundle en apps/web/pages-dist ...")
    if pages_dist.exists():
        shutil.rmtree(pages_dist)
    (pages_dist / "static").mkdir(parents=True)

    shutil.copy(web_dir / "index.html", pages_dist / "index.html")
    shutil.copytree(web_dir / "static", pages_dist / "static", dirs_exist_ok=True)
    shutil.copy(web_dir / "worker" / "_worker.js", pages_dist / "_worker.js")
    if (web_dir / "_headers").exists():
        shutil.copy(web_dir / "_headers", pages_dist / "_headers")
    for extra in ("robots.txt", "sitemap.xml"):
        p = web_dir / extra
        if p.exists():
            shutil.copy(p, pages_dist / extra)

    for name in ("index.html", "static/app.js", "static/style.css", "_worker.js"):
        if not (pages_dist / name).exists():
            raise SystemExit(f"[deploy-web] Falta en el bundle: {name}")

    proj = project_name or os.environ.get("CLOUDFLARE_PAGES_PROJECT")
    if not proj:
        raise SystemExit(
            "[deploy-web] Nombre del proyecto no definido. "
            "Usa --project-name <nombre> o la variable de entorno CLOUDFLARE_PAGES_PROJECT."
        )
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        raise SystemExit(
            "[deploy-web] CLOUDFLARE_API_TOKEN no está definido. "
            "Exporta el token en tu entorno (o usa el secret del repo en GitHub Actions)."
        )
    if not os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
        raise SystemExit(
            "[deploy-web] CLOUDFLARE_ACCOUNT_ID no está definido. "
            "Exporta el account ID en tu entorno."
        )

    wrangler_cmd = _get_wrangler_cmd()
    cmd = [
        *wrangler_cmd,
        "pages",
        "deploy",
        str(pages_dist),
        "--project-name",
        proj,
        "--branch",
        "main",
    ]
    print("[deploy-web] Ejecutando:", " ".join(cmd))
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"[deploy-web] wrangler pages deploy falló con código {exc.returncode}") from exc
    print("[deploy-web] Despliegue completado. Comprueba la URL de producción.")


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
        proc = subprocess.run(cmd, cwd=str(project_dir), check=False)
    except FileNotFoundError:
        raise SystemExit("flutter no está instalado o no está en PATH")
    if proc.returncode != 0:
        cmd_str = " ".join(cmd)
        print(f"[mobile] flutter run falló con código {proc.returncode}.")
        print(f"[mobile] Comando: {cmd_str}")
        print("[mobile] Revisa el log anterior de Flutter/Xcode/Gradle para la causa real.")
        return


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


def _normalize_verbose_cli(argv: list[str]) -> list[str]:
    """Acepta --verbose, -v y /verbose (estilo Windows) como equivalentes."""
    out: list[str] = []
    for item in argv:
        low = item.lower().replace("\\", "/")
        if low in ("/verbose", "--verbose", "-v"):
            out.append("--verbose")
        else:
            out.append(item)
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    if argv is None:
        argv = sys.argv[1:]
    argv = _normalize_verbose_cli(list(argv))
    parser = argparse.ArgumentParser(description="MIDIChords launcher")
    parser.add_argument(
        "target",
        choices=["desktop", "web", "mobile", "mobile-ipad", "deploy-web"],
        nargs="?",
        default="desktop",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--project-name",
        default=None,
        help="Para deploy-web: nombre del proyecto en Cloudflare Pages (o usa CLOUDFLARE_PAGES_PROJECT).",
    )
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
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Trazas en stderr (audio, MIDI). Equivale a /verbose.",
    )
    args, extra = parser.parse_known_args(argv)
    # Unknown args are forwarded to flutter when target is mobile/mobile-ipad.
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.mobile_args = extra
    return args


def _strip_verbose_flags_from_sys_argv() -> None:
    """Evita que QApplication reciba --verbose o /verbose (ya interpretados aquí)."""
    if len(sys.argv) <= 1:
        return
    keep: list[str] = [sys.argv[0]]
    for a in sys.argv[1:]:
        low = a.lower().replace("\\", "/")
        if low in ("--verbose", "-v", "/verbose"):
            continue
        keep.append(a)
    sys.argv[:] = keep


def main() -> None:
    args = parse_args()
    if args.target == "deploy-web":
        run_deploy_web(project_name=args.project_name)
        return
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
    # Escritorio (target por defecto): verbose + argv limpio para QApplication.
    if args.verbose:
        os.environ["MIDICHORDS_VERBOSE"] = "1"
    _strip_verbose_flags_from_sys_argv()
    run_desktop()


if __name__ == "__main__":
    main()
