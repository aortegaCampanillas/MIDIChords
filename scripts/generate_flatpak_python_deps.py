#!/usr/bin/env python3
"""Generate Flatpak Python dependency modules from PyPI metadata."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "packaging" / "flatpak" / "python-deps.json"


@dataclass(frozen=True)
class PackageSpec:
    name: str
    version: str
    mode: str


SPECS = [
    PackageSpec("mido", "1.3.2", "py3-none-any"),
    PackageSpec("packaging", "23.2", "py3-none-any"),
    PackageSpec("altgraph", "0.17.5", "py3-none-any"),
    PackageSpec("pyinstaller-hooks-contrib", "2026.3", "py3-none-any"),
    PackageSpec("setuptools", "82.0.1", "py3-none-any"),
    PackageSpec("pycparser", "3.0", "py3-none-any"),
    PackageSpec("sounddevice", "0.5.1", "py3-none-any"),
    PackageSpec("pyinstaller", "6.19.0", "py3-none-any"),
    PackageSpec("cffi", "2.0.0", "cp312-manylinux-x86_64"),
    PackageSpec("numpy", "2.1.3", "cp312-manylinux-x86_64"),
    PackageSpec("python-rtmidi", "1.5.8", "cp312-manylinux-x86_64"),
]


def fetch_release(spec: PackageSpec) -> dict:
    url = f"https://pypi.org/pypi/{spec.name}/{spec.version}/json"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def select_file(spec: PackageSpec, data: dict) -> dict:
    files = data["urls"]
    if spec.mode == "py3-none-any":
        for item in files:
            if item["packagetype"] == "bdist_wheel" and item["filename"].endswith("py3-none-any.whl"):
                return item
    elif spec.mode == "cp312-manylinux-x86_64":
        for item in files:
            filename = item["filename"]
            if (
                item["packagetype"] == "bdist_wheel"
                and "cp312-cp312" in filename
                and "manylinux" in filename
                and "x86_64" in filename
            ):
                return item
    for item in files:
        if item["packagetype"] == "sdist" and item["filename"].endswith(".tar.gz"):
            return item
    raise RuntimeError(f"No suitable file found for {spec.name} {spec.version}")


def package_module(spec: PackageSpec, file_info: dict) -> dict:
    return {
        "name": f"python3-{spec.name}",
        "buildsystem": "simple",
        "build-commands": [
            f'pip3 install --verbose --exists-action=i --no-index --find-links="file://${{PWD}}" --prefix=${{FLATPAK_DEST}} "{spec.name}=={spec.version}"'
        ],
        "sources": [
            {
                "type": "file",
                "url": file_info["url"],
                "sha256": file_info["digests"]["sha256"],
            }
        ],
    }


def main() -> None:
    modules = []
    for spec in SPECS:
        data = fetch_release(spec)
        file_info = select_file(spec, data)
        modules.append(package_module(spec, file_info))
    OUTPUT.write_text(json.dumps(modules, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
