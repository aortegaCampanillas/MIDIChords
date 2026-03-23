#!/usr/bin/env python3
"""
Envía el correo de alerta del workflow web-production-health vía Resend.

Uso típico (workflow, tras fallar el 1er chequeo):
  python3 scripts/send_resend_health_alert.py web-health-1.log --mail-kind resolved|action_required
  python3 scripts/send_resend_health_alert.py web-health-1.log --second-log web-health-2.log --mail-kind resolved

Asuntos (español, visibles de un vistazo):
  --mail-kind resolved         → [RESUELTO] … recuperada tras redeploy automático
  --mail-kind action_required  → [ACCIÓN REQUERIDA] … sigue fallando o redeploy falló

Sin --mail-kind (modo legado): mismo cuerpo que antes con asunto genérico de fallo.

Variables: RESEND_API_KEY, NOTIFY_FROM, ALERT_TO, GITHUB_SERVER_URL, GITHUB_REPOSITORY, GITHUB_RUN_ID.
"""

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Correo Resend para chequeo web en producción.")
    parser.add_argument("log1", type=Path, help="Salida del 1er check_production_web_health.py")
    parser.add_argument(
        "--second-log",
        type=Path,
        default=None,
        help="Salida del 2º chequeo (tras redeploy automático), si existe.",
    )
    parser.add_argument(
        "--mail-kind",
        choices=("resolved", "action_required"),
        default=None,
        help="Tipo de aviso: producción recuperada vs intervención manual necesaria.",
    )
    args = parser.parse_args()

    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    if not api_key:
        print("RESEND_API_KEY vacío; no se envía correo.", file=sys.stderr)
        return 0

    log1 = args.log1.read_text(encoding="utf-8", errors="replace")
    log2 = ""
    if args.second_log is not None and args.second_log.is_file():
        log2 = args.second_log.read_text(encoding="utf-8", errors="replace")

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
    seen: set[str] = set()
    ordered_from: list[str] = []
    for f in from_candidates:
        if f not in seen:
            seen.add(f)
            ordered_from.append(f)

    kind = args.mail_kind
    if kind == "resolved":
        subject = "[RESUELTO] MIDIChords: freemidichords.com OK tras redeploy automático en Actions"
        lead_html = (
            "<p><strong>El primer chequeo falló</strong>, se ejecutó un <strong>redeploy automático</strong> "
            "de Cloudflare Pages desde la rama <code>main</code> y el <strong>segundo chequeo pasó</strong>. "
            "No hace falta acción urgente salvo que el problema vuelva a repetirse.</p>"
        )
        lead_text = (
            "El 1er chequeo falló; tras redeploy automático desde main el 2º chequeo pasó. "
            "No se requiere acción urgente.\n\n"
        )
    elif kind == "action_required":
        subject = (
            "[ACCIÓN REQUERIDA] MIDIChords: freemidichords.com sigue mal o falló el redeploy automático"
        )
        lead_html = (
            "<p>El <strong>primer chequeo de salud</strong> falló. Se intentó <strong>redeploy automático</strong> "
            "desde <code>main</code>; revisa los logs: el bundle, <code>wrangler pages deploy</code> o el "
            "<strong>segundo chequeo</strong> pueden haber fallado. <strong>Revisa credenciales Cloudflare, "
            "dominio custom y proyecto Pages.</strong></p>"
        )
        lead_text = (
            "El 1er chequeo falló y la autocuración no dejó la web sana (o falló el deploy). "
            "Revisa el run en GitHub y Cloudflare.\n\n"
        )
    else:
        subject = "MIDIChords: la web en producción no pasa el chequeo de salud"
        lead_html = (
            "<p>El chequeo de <strong>freemidichords.com</strong> "
            "(HTML, CSS, JS y <code>/api/meta</code>) ha fallado.</p>"
        )
        lead_text = "Chequeo web freemidichords.com fallido.\n\n"

    blocks_html = [
        lead_html,
        f"<p><a href='{html.escape(run_url)}'>Ver ejecución en GitHub Actions</a></p>",
        "<p><strong>Primer chequeo (stderr / salida):</strong></p>",
        f"<pre style='white-space:pre-wrap;font-size:12px'>{html.escape(log1)}</pre>",
    ]
    blocks_text = [lead_text, f"Run: {run_url}\n\n", "--- Primer chequeo ---\n", log1]
    if log2:
        blocks_html.append("<p><strong>Segundo chequeo (tras redeploy automático):</strong></p>")
        blocks_html.append(
            f"<pre style='white-space:pre-wrap;font-size:12px'>{html.escape(log2)}</pre>"
        )
        blocks_text.extend(["\n--- Segundo chequeo ---\n", log2])

    html_body = "".join(blocks_html)
    text_body = "".join(blocks_text)

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
            print(f"Correo enviado (remitente: {from_addr!r}, asunto: {subject!r}).")
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
