#!/usr/bin/env python3
"""Comprueba contratos estructurales, SEO y recursos de las landings públicas."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "apps/web"


class LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1_count = 0
        self.images: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.meta: dict[tuple[str, str], str | None] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "link":
            self.links.append(attributes)
        elif tag == "meta":
            if "name" in attributes:
                self.meta[("name", attributes["name"] or "")] = attributes.get("content")
            if "property" in attributes:
                self.meta[("property", attributes["property"] or "")] = attributes.get("content")


def _structured_data(html: str) -> dict:
    match = re.search(
        r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise AssertionError("Faltan datos estructurados JSON-LD")
    return json.loads(match.group(1))


def check_page(filename: str, product_name: str) -> None:
    path = WEB_ROOT / filename
    html = path.read_text(encoding="utf-8")
    parser = LandingParser()
    parser.feed(html)

    assert parser.h1_count == 1, f"{filename}: se esperaba un único h1"
    assert any(link.get("rel") == "canonical" for link in parser.links)
    for meta_type, key in (
        ("name", "description"),
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:url"),
        ("property", "og:image"),
        ("name", "twitter:card"),
        ("name", "twitter:title"),
        ("name", "twitter:description"),
        ("name", "twitter:image"),
    ):
        assert parser.meta.get((meta_type, key)), f"{filename}: falta {key}"

    for image in parser.images:
        assert image.get("width") and image.get("height"), (
            f"{filename}: la imagen {image.get('src')} no reserva dimensiones"
        )

    for resource in set(re.findall(r'["\'](/static/[^"\']+)["\']', html)):
        local_path = WEB_ROOT / resource.removeprefix("/")
        assert local_path.is_file(), f"{filename}: no existe {resource}"

    schema = _structured_data(html)
    assert schema["@type"] == "SoftwareApplication"
    assert schema["name"] == product_name


def main() -> None:
    check_page("index.html", "FreeMIDIChords")
    check_page("fp30x.html", "PianoPilot")
    print("[landings] Estructura, metadatos y recursos validados.")


if __name__ == "__main__":
    main()
