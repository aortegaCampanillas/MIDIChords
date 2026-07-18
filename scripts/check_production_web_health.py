#!/usr/bin/env python3
"""
Comprueba que la web en producción sirve HTML, CSS y JS correctamente.

Uso:
  python3 scripts/check_production_web_health.py
  WEB_BASE_URL=https://ejemplo.com python3 scripts/check_production_web_health.py

Sale con código 0 si todo va bien; distinto de 0 y mensajes en stderr si falla.
Pensado para GitHub Actions (cron horario) y pruebas locales.

Variables de entorno:
  WEB_BASE_URL     Origen HTTPS (por defecto https://freemidichords.com)
  WEB_HEALTH_RETRIES  Reintentos por petición ante 404/5xx en edge (por defecto 2; Actions usa 4)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse


DEFAULT_BASE = "https://freemidichords.com"
TIMEOUT_SEC = 45
USER_AGENT = "MIDIChords-WebHealthCheck/1.0"
# Reintentos ante 404/5xx en edge (propagación CDN o deploy reciente). En CI: export WEB_HEALTH_RETRIES=4
_DEFAULT_RETRIES = 2


def _health_retry_count() -> int:
    try:
        return max(1, int(os.environ.get("WEB_HEALTH_RETRIES", str(_DEFAULT_RETRIES))))
    except ValueError:
        return max(1, _DEFAULT_RETRIES)


def strip_query_and_fragment(url: str) -> str:
    """Misma ruta sin ?query ni #fragment (p. ej. cache-bust en producción rota)."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, p.params, "", ""))


def pick_static_url(urls: list[str], needle: str) -> str | None:
    """Elige la primera URL cuyo path contenga `needle` (p. ej. 'style.css')."""
    for u in urls:
        path = urlparse(u).path
        if needle in path.replace("\\", "/"):
            return u
    return None


def pick_css_bundle_url(urls: list[str]) -> str | None:
    """CSS principal: /static/style.<hash>.css (deploy) o /static/style.css (legado)."""
    for u in urls:
        path = urlparse(u).path.replace("\\", "/")
        if "/static/style." in path and path.endswith(".css"):
            return u
    return pick_static_url(urls, "style.css")


def pick_js_bundle_url(urls: list[str]) -> str | None:
    """JS principal: /static/app.<hash>.js (deploy) o /static/app.js (legado)."""
    for u in urls:
        path = urlparse(u).path.replace("\\", "/")
        if "/static/app." in path and path.endswith(".js"):
            return u
    return pick_static_url(urls, "app.js")


def pick_chord_help_bundle_url(urls: list[str]) -> str | None:
    """Catálogo de acordes: versión con hash de deploy o nombre estable local."""
    for u in urls:
        path = urlparse(u).path.replace("\\", "/")
        if "/static/chord_help." in path and path.endswith(".js"):
            return u
    return pick_static_url(urls, "chord_help.js")


def pick_ui_texts_bundle_url(urls: list[str]) -> str | None:
    """Textos de interfaz: versión con hash de deploy o nombre estable local."""
    for u in urls:
        path = urlparse(u).path.replace("\\", "/")
        if "/static/ui_texts." in path and path.endswith(".js"):
            return u
    return pick_static_url(urls, "ui_texts.js")


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stylesheet_hrefs: list[str] = []
        self.script_srcs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "link" and a.get("rel", "").lower() == "stylesheet":
            href = a.get("href", "").strip()
            if href:
                self.stylesheet_hrefs.append(href)
        if tag == "script":
            src = a.get("src", "").strip()
            if src:
                self.script_srcs.append(src)


def _request_once(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            status = resp.getcode() or 200
            headers = {k.lower(): v for k, v in resp.headers.items()}
            body = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        return e.code, headers, body
    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo conectar a {url!r}: {e}") from e
    return status, headers, body


def _transient_status(status: int) -> bool:
    return status in (404, 408, 429, 502, 503, 520, 521, 522, 523, 524)


def _request(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
) -> tuple[int, dict[str, str], bytes]:
    """Petición HTTP con reintentos si WEB_HEALTH_RETRIES > 1 y el status es transitorio (404 en edge, 5xx)."""
    max_tries = _health_retry_count()
    last: tuple[int, dict[str, str], bytes] = (0, {}, b"")
    for attempt in range(max_tries):
        try:
            st, headers, body = _request_once(url, method=method, data=data)
        except RuntimeError:
            if attempt == max_tries - 1:
                raise
            time.sleep(min(30, 8 * (attempt + 1)))
            continue
        last = (st, headers, body)
        if not _transient_status(st) or attempt == max_tries - 1:
            return st, headers, body
        time.sleep(min(30, 8 * (attempt + 1)))
    return last


def _fail(msg: str) -> None:
    print(msg, file=sys.stderr)


def _static_body_looks_wrong_mime(
    raw: bytes, headers: dict[str, str], *, kind: str
) -> tuple[bool, list[str]]:
    """Devuelve (es_válido, lista_errores_si_no)."""
    errs: list[str] = []
    cth = (headers.get("content-type") or "").lower()
    if kind == "css":
        if "text/css" not in cth and "stylesheet" not in cth:
            errs.append(f"Content-Type inesperado: {cth!r}")
    else:
        if (
            "javascript" not in cth
            and "ecmascript" not in cth
            and "jscript" not in cth
        ):
            errs.append(f"Content-Type inesperado: {cth!r}")
    text = raw.decode("utf-8", errors="replace").lstrip()
    if text.startswith("<!") or text.lower().startswith("<html"):
        errs.append("el cuerpo parece HTML, no el recurso esperado")
    return (len(errs) == 0, errs)


def validate_static_asset(
    url: str,
    *,
    kind: str,
    min_len: int,
) -> list[str]:
    """
    Comprueba GET de un estático. Si la URL con ?v= da 404 pero la misma ruta sin query
    responde bien, devuelve un solo mensaje accionable (despliegue / worker).
    """
    try:
        st, hdrs, raw = _request(url)
    except RuntimeError as e:
        return [str(e)]

    clean = strip_query_and_fragment(url)
    has_qf = clean != url

    def ok_response(status: int, h: dict[str, str], body: bytes) -> bool:
        if status != 200:
            return False
        if len(body) < min_len:
            return False
        good, _ = _static_body_looks_wrong_mime(body, h, kind=kind)
        return good

    if ok_response(st, hdrs, raw):
        return []

    if st == 404 and has_qf:
        try:
            st2, hdrs2, raw2 = _request(clean)
        except RuntimeError:
            st2 = -1
            hdrs2 = {}
            raw2 = b""
        if ok_response(st2, hdrs2, raw2):
            label = "CSS" if kind == "css" else "JavaScript"
            return [
                f"{label}: el HTML enlaza {url!r} → HTTP 404; sin query {clean!r} → OK. "
                "Los navegadores cargan la URL del HTML (con ?v=), así que la página queda rota. "
                "Despliega producción con el workflow que ya no añade ?v= al index, o revisa "
                "el worker (_worker.js) y env.ASSETS.fetch en Cloudflare Pages."
            ]

    errs: list[str] = []
    if st != 200:
        line = f"GET {url} → HTTP {st}"
        if st == 404 and len(raw) == 0 and "/static/" in url:
            line += (
                " — si el HTML enlaza un `style.<hash>.css` / `app.<hash>.js` que no existe en el edge, "
                "vuelve a desplegar el bundle completo desde `main` (mismo `index.html` y carpeta `static/`)."
            )
        errs.append(line)
    _, mime_errs = _static_body_looks_wrong_mime(raw, hdrs, kind=kind)
    for m in mime_errs:
        errs.append(f"GET {url} → {m}")
    if len(raw) < min_len:
        errs.append(f"GET {url} → respuesta demasiado corta ({len(raw)} bytes)")
    return errs


def check_html_page(url: str, failures: list[str]) -> str:
    """GET url, verifica HTTP 200 + Content-Type HTML. Devuelve el cuerpo decodificado."""
    try:
        status, headers, html_bytes = _request(url)
    except RuntimeError as e:
        failures.append(str(e))
        return ""
    ct = (headers.get("content-type") or "").lower()
    if status != 200:
        failures.append(f"GET {url} → HTTP {status}")
    if "text/html" not in ct:
        failures.append(f"GET {url} → Content-Type inesperado: {ct!r}")
    try:
        html = html_bytes.decode("utf-8", errors="replace")
    except Exception:
        html = ""
    if "<html" not in html.lower() and "<!doctype" not in html.lower():
        failures.append(f"GET {url} → cuerpo no parece HTML")
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Comprueba HTML/CSS/JS de la web en producción.")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("WEB_BASE_URL", DEFAULT_BASE).rstrip("/"),
        help=f"Origen HTTPS (por defecto: {DEFAULT_BASE} o env WEB_BASE_URL)",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="No comprobar GET /api/meta (solo HTML/CSS/JS).",
    )
    args = parser.parse_args()
    base = args.base_url
    failures: list[str] = []

    # --- Landing principal (/) — HTML sin CSS/JS propios ---
    check_html_page(f"{base}/", failures)

    # --- Landing PianoPilot (/fp30x) — HTML sin CSS/JS propios ---
    check_html_page(f"{base}/fp30x", failures)

    # --- App SPA (/app) — HTML + CSS + JS ---
    app_url = f"{base}/app"
    app_html = check_html_page(app_url, failures)

    p = AssetParser()
    try:
        p.feed(app_html)
        p.close()
    except Exception as e:
        failures.append(f"Error parseando HTML de {app_url}: {e}")

    css_urls = [urljoin(app_url, h) for h in p.stylesheet_hrefs]
    js_urls = [urljoin(app_url, h) for h in p.script_srcs]

    css_url = pick_css_bundle_url(css_urls)
    chord_help_url = pick_chord_help_bundle_url(js_urls)
    ui_texts_url = pick_ui_texts_bundle_url(js_urls)
    js_url = pick_js_bundle_url(js_urls)

    if not css_url:
        failures.append(
            f"GET {app_url} → no se encontró <link rel=stylesheet> a /static/style…css"
        )
    if not js_url:
        failures.append(
            f"GET {app_url} → no se encontró <script src=…> a /static/app…js"
        )
    if not chord_help_url:
        failures.append(
            f"GET {app_url} → no se encontró <script src=…> a /static/chord_help…js"
        )
    if not ui_texts_url:
        failures.append(
            f"GET {app_url} → no se encontró <script src=…> a /static/ui_texts…js"
        )

    if css_url:
        failures.extend(validate_static_asset(css_url, kind="css", min_len=200))
    if js_url:
        failures.extend(validate_static_asset(js_url, kind="js", min_len=500))
    if chord_help_url:
        failures.extend(validate_static_asset(chord_help_url, kind="js", min_len=500))
    if ui_texts_url:
        failures.extend(validate_static_asset(ui_texts_url, kind="js", min_len=500))

    # --- API (worker) ---
    if not args.skip_api:
        meta_url = f"{base}/api/meta?language=es"
        try:
            st, hdrs, raw = _request(meta_url)
        except RuntimeError as e:
            failures.append(str(e))
        else:
            if st != 200:
                hint = ""
                if st == 404 and len(raw) == 0:
                    hint = (
                        " — cuerpo vacío: no es JSON del worker; suele ser **404 estático** (el worker no enruta `/api/*`). "
                        "Confirma que el último `pages deploy` incluye **`_routes.json`** y **`_worker.js`** y que "
                        "`freemidichords.com` está enlazado al proyecto Pages. **Redespliegue:** "
                        "`python launch.py deploy-web` desde `main` o push de etiqueta `v*`."
                    )
                failures.append(f"GET {meta_url} → HTTP {st}{hint}")
            else:
                try:
                    data: Any = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    failures.append(f"GET {meta_url} → respuesta no es JSON válido")
                else:
                    if not isinstance(data.get("chord_patterns"), list) or len(
                        data["chord_patterns"]
                    ) < 1:
                        failures.append(
                            f"GET {meta_url} → JSON sin chord_patterns usable (la app quedaría vacía)"
                        )

    if failures:
        _fail("Comprobación de salud web: FALLO")
        for line in failures:
            _fail(f"  - {line}")
        return 1

    print(
        f"OK: {base}/ (landing), {base}/app (SPA, CSS={css_url}, JS={js_url}), "
        f"{base}/fp30x (PianoPilot)"
        + ("" if args.skip_api else f", API {base}/api/meta")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
