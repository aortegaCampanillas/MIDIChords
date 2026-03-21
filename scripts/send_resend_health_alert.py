#!/usr/bin/env python3
"""
Envía el correo de alerta del workflow web-production-health vía Resend.

Requisitos de Resend: cabecera User-Agent; el remitente debe ser un dominio
verificado en la cuenta para enviar a direcciones arbitrarias (p. ej. Gmail).

Orden de remitentes (el primero que funcione):
  1. NOTIFY_FROM (variable de repo / env)
  2. MIDIChords <notifications@freemidichords.com>  (dominio del proyecto)
  3. onboarding@resend.dev
  4. MIDIChords <onboarding@resend.dev>

Variables de entorno: RESEND_API_KEY (obligatoria), NOTIFY_FROM, ALERT_TO,
GITHUB_SERVER_URL, GITHUB_REPOSITORY, GITHUB_RUN_ID.
Argumento: ruta al fichero web-health.log (por defecto ./web-health.log).
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _build_request(payload: dict, api_key: str) -> urllib.request.Request:
    return urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "MIDIChords-GitHub-Actions/1.0 (web-production-health)",
        },
        method="POST",
    )


def main() -> int:
    log_path = Path(sys.argv[1] if len(sys.argv) > 1 else "web-health.log")
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    if not api_key:
        print("RESEND_API_KEY vacío; no se envía correo.", file=sys.stderr)
        return 0

    log = log_path.read_text(encoding="utf-8", errors="replace")
    run_url = (
        os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        + "/"
        + os.environ.get("GITHUB_REPOSITORY", "")
        + "/actions/runs/"
        + os.environ.get("GITHUB_RUN_ID", "")
    )
    alert_to = (os.environ.get("ALERT_TO") or "").strip() or "aortega98@gmail.com"

    notify = (os.environ.get("NOTIFY_FROM") or "").strip()
    from_candidates: list[str] = []
    if notify:
        from_candidates.append(notify)
    from_candidates.extend(
        [
            "MIDIChords <notifications@freemidichords.com>",
            "onboarding@resend.dev",
            "MIDIChords <onboarding@resend.dev>",
        ]
    )
    # Sin duplicados
    seen: set[str] = set()
    ordered_from: list[str] = []
    for f in from_candidates:
        if f not in seen:
            seen.add(f)
            ordered_from.append(f)

    subject = "MIDIChords: la web en producción no pasa el chequeo de salud"
    html_body = (
        "<p>El chequeo horario de <strong>freemidichords.com</strong> "
        "(HTML, CSS, JS y <code>/api/meta</code>) ha fallado.</p>"
        f"<p><a href='{html.escape(run_url)}'>Ver ejecución en GitHub Actions</a></p>"
        "<p>Detalle (stderr / salida del script):</p>"
        f"<pre style='white-space:pre-wrap;font-size:12px'>{html.escape(log)}</pre>"
    )
    text_body = (
        f"Chequeo web freemidichords.com fallido.\n\n"
        f"Run: {run_url}\n\n"
        f"---\n{log}\n"
    )

    last_http: urllib.error.HTTPError | None = None
    last_body = ""

    for from_addr in ordered_from:
        payload = {
            "from": from_addr,
            "to": [alert_to],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }
        req = _build_request(payload, api_key)
        try:
            urllib.request.urlopen(req)
            print(f"Correo de aviso enviado (remitente: {from_addr!r}).")
            return 0
        except urllib.error.HTTPError as e:
            last_http = e
            last_body = e.read().decode("utf-8", errors="replace")
            if e.code == 422 and "domain" in last_body.lower():
                print(
                    f"::notice::Resend 422 con remitente {from_addr!r}: {last_body.strip()}"
                )
                continue
            print(f"::warning::Resend rechazó el envío: HTTP {e.code} {e.reason}")
            print("--- Cuerpo de respuesta (Resend) ---")
            print(last_body or "(vacío)")
            print("--- fin ---")
            return 1
        except OSError as e:
            print(f"::warning::Error de red al llamar a Resend: {e}", file=sys.stderr)
            return 1

    if last_http is not None:
        print(
            f"::warning::Ningún remitente válido para Resend. Último error HTTP {last_http.code}"
        )
        print("--- Cuerpo de respuesta (Resend) ---")
        print(last_body or "(vacío)")
        print("--- fin ---")
        print(
            "::notice::Configura NOTIFY_FROM_EMAIL en el repo con un remitente de un dominio "
            "verificado en resend.com/domains.",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
