#!/usr/bin/env python3
"""
Añade una entrada en CHANGELOG.md bajo ## Unreleased con ámbito explícito
(Todas / Escritorio / Web / Móvil / Core / Empaquetado) y opcionalmente
hace commit y push.

Uso:
  python3 scripts/document_release_changes.py --interactive
  python3 scripts/document_release_changes.py \\
    --scope desktop --section corregido --message "texto del cambio"
  python3 scripts/document_release_changes.py -i --commit-push --stage all

Ver también: .vscode/tasks.json → "Documentar cambios …"
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"

# Clave interna → prefijo en el bullet (alineado con el estilo del CHANGELOG)
SCOPE_PREFIX: dict[str, str] = {
    "all": "**Todas**",
    "desktop": "**Escritorio**",
    "web": "**Web**",
    "mobile": "**Móvil (Flutter)**",
    "core": "**Core / compartido**",
    "packaging": "**Empaquetado**",
}

# argparse choices → título exacto en CHANGELOG
SECTION_TITLE: dict[str, str] = {
    "anadido": "Añadido",
    "mejorado": "Mejorado",
    "corregido": "Corregido",
    "documentado": "Documentado",
}


def _split_unreleased(md: str) -> tuple[str, str, str]:
    """Devuelve (cabecera hasta y incl. '## Unreleased\\n\\n', cuerpo, resto desde '\\n## [')."""
    marker = "## Unreleased\n\n"
    if marker not in md:
        raise ValueError("No se encontró la sección ## Unreleased en CHANGELOG.md")
    before, _, after_marker = md.partition(marker)
    # Primer bloque de versión publicada
    m = re.search(r"\n## \[\d", after_marker)
    if not m:
        raise ValueError("No se encontró una versión publicada (## […) tras Unreleased")
    body = after_marker[: m.start()]
    tail = after_marker[m.start() :]
    return before + marker, body, tail


def _insert_bullet(unreleased_body: str, section_key: str, bullet_line: str) -> str:
    title = SECTION_TITLE[section_key]
    header = f"### {title}\n\n"

    if section_key == "mejorado" and f"### {title}\n\n" not in unreleased_body:
        anchor = "### Corregido\n\n"
        if anchor not in unreleased_body:
            raise ValueError("No se encontró ### Corregido en Unreleased (estructura inesperada)")
        block = f"### Mejorado\n\n{bullet_line}\n\n"
        return unreleased_body.replace(anchor, block + anchor, 1)

    if header not in unreleased_body:
        raise ValueError(f"No se encontró la subsección ### {title} en Unreleased")

    return unreleased_body.replace(header, header + bullet_line + "\n", 1)


def apply_changelog(scope: str, section_key: str, message: str) -> str:
    prefix = SCOPE_PREFIX[scope]
    bullet = f"- {prefix}: {message.strip()}"
    text = CHANGELOG.read_text(encoding="utf-8")
    head, body, tail = _split_unreleased(text)
    new_body = _insert_bullet(body, section_key, bullet)
    return head + new_body + tail


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def git_commit_push(*, stage: str, commit_subject: str) -> None:
    if stage not in {"changelog", "all"}:
        raise ValueError("stage debe ser 'changelog' o 'all'")

    st = _run_git(["status", "--porcelain"], ROOT)
    if st.returncode != 0:
        print(st.stderr, file=sys.stderr)
        sys.exit(1)
    if not st.stdout.strip():
        print("No hay cambios pendientes en git.")
        return

    if stage == "changelog":
        add_paths = ["CHANGELOG.md"]
    else:
        add_paths = ["-A"]

    add = _run_git(["add", *add_paths], ROOT)
    if add.returncode != 0:
        print(add.stderr, file=sys.stderr)
        sys.exit(1)

    diff = _run_git(["diff", "--cached", "--stat"], ROOT)
    print(diff.stdout)
    if not diff.stdout.strip():
        print("Nada en staging tras git add.", file=sys.stderr)
        sys.exit(1)

    cm = _run_git(["commit", "-m", commit_subject], ROOT)
    if cm.returncode != 0:
        print(cm.stderr, file=sys.stderr)
        sys.exit(1)

    pu = _run_git(["push"], ROOT)
    if pu.returncode != 0:
        print(pu.stdout + pu.stderr, file=sys.stderr)
        sys.exit(1)
    print("Push completado.")


def interactive() -> tuple[str, str, str, bool, str, str]:
    print("— Documentar cambios para la próxima release —\n")
    print("Ámbito:")
    keys = list(SCOPE_PREFIX.keys())
    for i, k in enumerate(keys, 1):
        print(f"  {i}) {SCOPE_PREFIX[k]} ({k})")
    choice = input("Elige número [1]: ").strip() or "1"
    try:
        scope = keys[int(choice) - 1]
    except (ValueError, IndexError):
        print("Selección no válida.", file=sys.stderr)
        sys.exit(1)

    print("\nSección del CHANGELOG:")
    secs = list(SECTION_TITLE.keys())
    labels = ["Añadido", "Mejorado", "Corregido", "Documentado"]
    for i, lab in enumerate(labels, 1):
        print(f"  {i}) {lab}")
    choice = input("Elige número [3]: ").strip() or "3"
    try:
        section_key = secs[int(choice) - 1]
    except (ValueError, IndexError):
        print("Selección no válida.", file=sys.stderr)
        sys.exit(1)

    message = input("\nDescripción (una línea, sin guion inicial):\n> ").strip()
    if not message:
        print("El mensaje no puede estar vacío.", file=sys.stderr)
        sys.exit(1)

    cp = (input("\n¿Hacer commit y push ahora? [s/N]: ").strip().lower() or "n") in (
        "s",
        "si",
        "sí",
        "y",
        "yes",
    )
    stage = "changelog"
    subj = "chore(changelog): actualizar notas de release"
    if cp:
        print("Archivos a incluir en el commit:")
        print("  1) Solo CHANGELOG.md")
        print("  2) Todos los cambios pendientes (git add -A)")
        s = input("Elige [1]: ").strip() or "1"
        stage = "all" if s == "2" else "changelog"
        subj = input("\nAsunto del commit [chore(changelog): actualizar notas de release]: ").strip()
        if not subj:
            subj = "chore(changelog): actualizar notas de release"

    return scope, section_key, message, cp, stage, subj


def main() -> None:
    p = argparse.ArgumentParser(description="Añade entrada en CHANGELOG (Unreleased) y opcionalmente commit/push.")
    p.add_argument("--scope", choices=list(SCOPE_PREFIX.keys()), help="Ámbito del cambio")
    p.add_argument(
        "--section",
        choices=list(SECTION_TITLE.keys()),
        help="Subsección: anadido|mejorado|corregido|documentado",
    )
    p.add_argument("--message", "-m", default="", help="Texto del bullet (sin prefijo de ámbito)")
    p.add_argument("--interactive", "-i", action="store_true", help="Menú interactivo en terminal")
    p.add_argument("--commit-push", action="store_true", help="Tras editar CHANGELOG: git commit y push")
    p.add_argument(
        "--stage",
        choices=["changelog", "all"],
        default="changelog",
        help="Qué incluir en el commit (con --commit-push)",
    )
    p.add_argument(
        "--commit-subject",
        default="chore(changelog): actualizar notas de release",
        help="Mensaje de commit (primer línea)",
    )
    args = p.parse_args()

    if args.interactive:
        scope, section_key, message, cp, stage, subj = interactive()
        args.scope = scope
        args.section = section_key
        args.message = message
        args.commit_push = bool(cp)
        args.stage = stage
        args.commit_subject = subj
    else:
        if not args.scope or not args.section or not args.message.strip():
            p.error("Fuera de --interactive hacen falta --scope, --section y --message (o usa -i).")

    new_md = apply_changelog(args.scope, args.section, args.message)
    CHANGELOG.write_text(new_md, encoding="utf-8", newline="\n")
    print(f"Actualizado: {CHANGELOG.relative_to(ROOT)}")
    bullet_preview = f"- {SCOPE_PREFIX[args.scope]}: {args.message.strip()}"
    print(f"Entrada: {bullet_preview[:120]}{'…' if len(bullet_preview) > 120 else ''}")

    if args.commit_push:
        git_commit_push(stage=args.stage, commit_subject=args.commit_subject)


if __name__ == "__main__":
    main()
