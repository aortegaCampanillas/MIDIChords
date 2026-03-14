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


SPECS = [
    PackageSpec("setuptools", "82.0.1"),
    PackageSpec("flit-core", "3.12.0"),
    PackageSpec("packaging", "23.2"),
    PackageSpec("setuptools-scm", "9.2.2"),
    PackageSpec("altgraph", "0.17.5"),
    PackageSpec("pycparser", "3.0"),
    PackageSpec("mido", "1.3.2"),
    PackageSpec("sounddevice", "0.5.1"),
    PackageSpec("cffi", "2.0.0"),
    PackageSpec("numpy", "2.1.3"),
    PackageSpec("python-rtmidi", "1.5.8"),
    PackageSpec("pyinstaller-hooks-contrib", "2026.3"),
    PackageSpec("pyinstaller", "6.19.0"),
]


def fetch_release(spec: PackageSpec) -> dict:
    url = f"https://pypi.org/pypi/{spec.name}/{spec.version}/json"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def select_file(spec: PackageSpec, data: dict) -> dict:
    files = data["urls"]
    for item in files:
        if item["packagetype"] == "sdist" and item["filename"].endswith(".tar.gz"):
            return item
    raise RuntimeError(f"No suitable file found for {spec.name} {spec.version}")


def package_module(spec: PackageSpec, file_info: dict) -> dict:
    return {
        "name": f"python3-{spec.name}",
        "buildsystem": "simple",
        "build-commands": [
            f'pip3 install --verbose --ignore-installed --no-deps --exists-action=i --no-build-isolation --no-index --find-links="file://${{PWD}}" --prefix=${{FLATPAK_DEST}} "{spec.name}=={spec.version}"'
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
    payload = {
        "name": "python3-dependencies",
        "buildsystem": "simple",
        "build-commands": [],
        "modules": modules,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
