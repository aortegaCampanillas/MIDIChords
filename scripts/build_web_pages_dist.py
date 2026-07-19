#!/usr/bin/env python3
"""
Construye apps/web/pages-dist con fingerprint en los JS/CSS públicos enlazados.

Misma lógica que `python launch.py deploy-web` antes de wrangler; úsalo desde CI
(.github/workflows) para no duplicar pasos en shell.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from launch import prepare_web_pages_dist  # noqa: E402


def main() -> None:
    prepare_web_pages_dist(ROOT)


if __name__ == "__main__":
    main()
