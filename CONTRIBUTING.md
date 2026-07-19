# Contributing

Thanks for contributing.

## Recommended Workflow

1. Create a branch from `main`.
2. Keep changes small and self-contained.
3. Install development dependencies and run the relevant checks from the **project root**:

```bash
python -m pip install -r requirements-dev.txt
python scripts/check.py python
python scripts/check.py web
python scripts/check.py mobile
```

Use `python scripts/check.py all` when Python, web and Flutter tooling are all installed.

4. Open a Pull Request with a clear description:

- What problem it solves.
- Which files it changes.
- How to test it manually.

## Style

- Clear and readable Python.
- Avoid unnecessary dependencies.
- Keep macOS compatibility.

## For AI agents

- Prefer Spanish for user-facing strings and default UI language (`es` in `midichords.core.i18n`).
- Run the applicable check profiles above before considering a change complete. See **AGENTS.md** for project structure and **PROJECT_SPEC.md** for product spec.
