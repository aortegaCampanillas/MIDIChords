#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANDROID_SDK = Path.home() / "Library" / "Android" / "sdk"
DEFAULT_FLUTTER_BIN = Path.home() / "dev" / "flutter" / "bin" / "flutter"
DEFAULT_IOS_SIMULATORS = {
    "F2AEE231-DF98-4373-9BA8-6725D7355ADF": "iPhone 17",
    "B3E6EBB0-F8E5-4221-A3F6-CAE536B665D8": "iPad Air 11-inch (M3)",
}


@dataclass
class EmulatorTarget:
    platform: str
    label: str
    launch_id: str
    detail: str


@dataclass
class DeviceTarget:
    platform: str
    label: str
    device_id: str
    detail: str


def _read_avd_image_sysdir(avd_name: str) -> str:
    config_path = Path.home() / ".android" / "avd" / f"{avd_name}.avd" / "config.ini"
    if not config_path.is_file():
        return ""
    for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("image.sysdir.1="):
            return line.split("=", 1)[1].strip()
    return ""


def _run_capture(
    cmd: list[str], *, cwd: str | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        cwd=cwd,
        env=env,
    )


def _android_env() -> dict[str, str]:
    env = os.environ.copy()
    sdk_root = env.get("ANDROID_SDK_ROOT") or env.get("ANDROID_HOME")
    if not sdk_root:
        sdk_root = str(DEFAULT_ANDROID_SDK)
    env["ANDROID_SDK_ROOT"] = sdk_root
    env["ANDROID_HOME"] = sdk_root
    path_parts = [
        str(Path(sdk_root) / "emulator"),
        str(Path(sdk_root) / "platform-tools"),
        str(Path(sdk_root) / "cmdline-tools" / "latest" / "bin"),
        env.get("PATH", ""),
    ]
    env["PATH"] = ":".join(part for part in path_parts if part)
    return env


def _flutter_cmd() -> list[str]:
    candidates = [
        DEFAULT_FLUTTER_BIN,
        Path.home() / "desarrollo" / "flutter" / "bin" / "flutter",
        Path.home() / "sdk" / "flutter" / "bin" / "flutter",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return [str(candidate)]
    path_entries = os.environ.get("PATH", "").split(":")
    for entry in path_entries:
        candidate = Path(entry) / "flutter"
        if candidate.is_file() and "homebrew" not in str(candidate):
            return [str(candidate)]
    resolved = shutil.which("flutter")
    if resolved:
        return [resolved]
    return ["flutter"]


def _load_ios_simulators(*, include_all: bool) -> list[EmulatorTarget]:
    proc = _run_capture(["xcrun", "simctl", "list", "devices", "available", "--json"])
    if proc.returncode != 0:
        return []
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []

    targets: list[EmulatorTarget] = []
    for runtime, devices in sorted(payload.get("devices", {}).items()):
        runtime_name = runtime.split(".")[-1].replace("-", " ")
        for device in devices:
            if not device.get("isAvailable", True):
                continue
            name = str(device.get("name", "")).strip()
            udid = str(device.get("udid", "")).strip()
            state = str(device.get("state", "")).strip() or "Unknown"
            if not name or not udid:
                continue
            if not include_all and udid not in DEFAULT_IOS_SIMULATORS:
                continue
            targets.append(
                EmulatorTarget(
                    platform="ios",
                    label=f"iOS | {name}",
                    launch_id=udid,
                    detail=f"{runtime_name} | {state}",
                )
            )
    if not include_all:
        targets.sort(
            key=lambda target: (
                0 if target.launch_id in DEFAULT_IOS_SIMULATORS else 1,
                target.label.lower(),
            )
        )
    return targets


def _load_android_emulators() -> list[EmulatorTarget]:
    env = _android_env()
    sdk_root = Path(env["ANDROID_SDK_ROOT"])
    emulator_bin = sdk_root / "emulator" / "emulator"
    if not emulator_bin.is_file():
        return []

    proc = _run_capture([str(emulator_bin), "-list-avds"])
    if proc.returncode != 0:
        return []

    targets: list[EmulatorTarget] = []
    for raw_line in proc.stdout.splitlines():
        avd_name = raw_line.strip()
        if not avd_name:
            continue
        image_path = _read_avd_image_sysdir(avd_name)
        detail = image_path or "AVD"
        targets.append(
            EmulatorTarget(
                platform="android",
                label=f"Android | {avd_name}",
                launch_id=avd_name,
                detail=detail,
            )
        )
    return targets


def _load_physical_devices() -> list[DeviceTarget]:
    proc = _run_capture([*_flutter_cmd(), "devices", "--machine"], cwd=str(PROJECT_ROOT))
    if proc.returncode != 0:
        return []
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []

    targets: list[DeviceTarget] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        if bool(item.get("emulator", False)):
            continue
        dev_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        platform = str(item.get("targetPlatform", "")).strip()
        sdk = str(item.get("sdk", "")).strip()
        if platform not in {"ios", "android-arm64", "android-x64", "android"}:
            continue
        if not dev_id or not name:
            continue
        targets.append(
            DeviceTarget(
                platform="ios" if platform == "ios" else "android",
                label=f"{'iOS' if platform == 'ios' else 'Android'} | {name}",
                device_id=dev_id,
                detail=sdk or platform,
            )
        )
    return targets


def _launch_ios(target: EmulatorTarget) -> int:
    open_proc = subprocess.run(["open", "-a", "Simulator"], check=False)
    if open_proc.returncode != 0:
        print("No se pudo abrir la app Simulator.", file=sys.stderr)
        return open_proc.returncode
    boot_proc = subprocess.run(
        ["xcrun", "simctl", "boot", target.launch_id],
        text=True,
        capture_output=True,
        check=False,
    )
    if boot_proc.returncode != 0:
        already_booted = "Unable to boot device in current state: Booted"
        if already_booted in (boot_proc.stderr or ""):
            return 0
        if boot_proc.stderr:
            print(boot_proc.stderr.strip(), file=sys.stderr)
    return boot_proc.returncode


def _launch_android(target: EmulatorTarget) -> int:
    env = _android_env()
    sdk_root = Path(env["ANDROID_SDK_ROOT"])
    emulator_bin = sdk_root / "emulator" / "emulator"
    if not emulator_bin.is_file():
        print(
            f"No se encontró el binario del emulador Android en {emulator_bin}.",
            file=sys.stderr,
        )
        return 1
    image_sysdir = _read_avd_image_sysdir(target.launch_id)
    if image_sysdir:
        image_dir = sdk_root / image_sysdir
        if not image_dir.is_dir():
            print(f"El AVD '{target.launch_id}' está roto.", file=sys.stderr)
            print(f"Falta la imagen de sistema: {image_dir}", file=sys.stderr)
            print(
                "No es un fallo del selector: ese AVD referencia una imagen no instalada.",
                file=sys.stderr,
            )
            print(
                "Instala esa imagen con:",
                file=sys.stderr,
            )
            print(
                '  "$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" '
                f'"system-images;android-35;google_apis_playstore_tablet;arm64-v8a"',
                file=sys.stderr,
            )
            return 1

    print(f"ANDROID_SDK_ROOT={env['ANDROID_SDK_ROOT']}")
    print(f"Lanzando AVD: {target.launch_id}")
    proc = subprocess.Popen([str(emulator_bin), "-avd", target.launch_id], env=env)
    print(f"PID: {proc.pid}")
    return 0


def _print_targets(targets: list[EmulatorTarget]) -> None:
    if not targets:
        print("No se encontraron simuladores/emuladores.")
        return
    for idx, target in enumerate(targets, start=1):
        print(f"{idx:>2}. {target.label} [{target.launch_id}]")
        print(f"    {target.detail}")


def _print_device_targets(targets: list[DeviceTarget]) -> None:
    if not targets:
        print("No se encontraron dispositivos físicos móviles.")
        return
    for idx, target in enumerate(targets, start=1):
        print(f"{idx:>2}. {target.label} [{target.device_id}]")
        print(f"    {target.detail}")


def _choose_target(
    targets: list[EmulatorTarget], *, can_show_more_ios: bool, can_show_devices: bool
) -> tuple[EmulatorTarget | None, bool, bool]:
    _print_targets(targets)
    if can_show_more_ios:
        print(" m. Mostrar más dispositivos iOS")
    if can_show_devices:
        print(" d. Mostrar dispositivos físicos")
    if not targets:
        return None, False, False
    while True:
        try:
            answer = input("Selecciona un número (Enter para cancelar): ").strip()
        except EOFError:
            return None, False, False
        if not answer:
            return None, False, False
        if can_show_more_ios and answer.lower() == "m":
            return None, True, False
        if can_show_devices and answer.lower() == "d":
            return None, False, True
        if not answer.isdigit():
            print("Introduce un número válido.")
            continue
        idx = int(answer)
        if 1 <= idx <= len(targets):
            return targets[idx - 1], False, False
        print("Número fuera de rango.")


def _choose_device_target(targets: list[DeviceTarget]) -> DeviceTarget | None:
    _print_device_targets(targets)
    if not targets:
        return None
    while True:
        try:
            answer = input("Selecciona un número (Enter para cancelar): ").strip()
        except EOFError:
            return None
        if not answer:
            return None
        if not answer.isdigit():
            print("Introduce un número válido.")
            continue
        idx = int(answer)
        if 1 <= idx <= len(targets):
            return targets[idx - 1]
        print("Número fuera de rango.")


def _launch_app_on_device(target: DeviceTarget) -> int:
    cmd = [sys.executable, str(PROJECT_ROOT / "launch.py"), "mobile", "-d", target.device_id]
    print(f"Lanzando app en {target.label} [{target.device_id}]")
    print("Comando:", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=False).returncode


def _build_targets(platform_filter: str, *, include_all_ios: bool) -> list[EmulatorTarget]:
    targets: list[EmulatorTarget] = []
    if platform_filter in {"all", "ios"}:
        targets.extend(_load_ios_simulators(include_all=include_all_ios))
    if platform_filter in {"all", "android"}:
        targets.extend(_load_android_emulators())
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lista y lanza simuladores iOS o emuladores Android en macOS."
    )
    parser.add_argument(
        "--platform",
        choices=("all", "ios", "android"),
        default="all",
        help="Filtra la lista por plataforma.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Solo lista simuladores/emuladores; no pregunta ni lanza nada.",
    )
    parser.add_argument(
        "--all-ios",
        action="store_true",
        help="Incluye todos los simuladores iOS disponibles; por defecto solo muestra los documentados.",
    )
    parser.add_argument(
        "--devices",
        action="store_true",
        help="Lista dispositivos físicos móviles y permite lanzar la app directamente en uno de ellos.",
    )
    args = parser.parse_args()

    if args.devices:
        devices = _load_physical_devices()
        if args.list:
            _print_device_targets(devices)
            return 0
        selected_device = _choose_device_target(devices)
        if selected_device is None:
            print("Cancelado.")
            return 0
        return _launch_app_on_device(selected_device)

    include_all_ios = args.all_ios
    targets = _build_targets(args.platform, include_all_ios=include_all_ios)
    if args.list:
        _print_targets(targets)
        return 0

    while True:
        can_show_more_ios = args.platform in {"all", "ios"} and not include_all_ios
        can_show_devices = args.platform == "all"
        target, requested_more_ios, requested_devices = _choose_target(
            targets,
            can_show_more_ios=can_show_more_ios,
            can_show_devices=can_show_devices,
        )
        if requested_more_ios:
            include_all_ios = True
            targets = _build_targets(args.platform, include_all_ios=include_all_ios)
            continue
        if requested_devices:
            devices = _load_physical_devices()
            selected_device = _choose_device_target(devices)
            if selected_device is None:
                print("Cancelado.")
                return 0
            return _launch_app_on_device(selected_device)
        if target is None:
            print("Cancelado.")
            return 0
        break

    print(f"Seleccionado: {target.label} [{target.launch_id}]")
    if target.platform == "ios":
        return _launch_ios(target)
    return _launch_android(target)


if __name__ == "__main__":
    raise SystemExit(main())
