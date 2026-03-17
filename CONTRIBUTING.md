# Contributing

Thanks for contributing.

## Recommended Workflow

1. Create a branch from `main`.
2. Keep changes small and self-contained.
3. Run tests from the **project root**:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Optionally verify that `app.py` compiles: `python3 -m py_compile app.py`.

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
- Run the test command above before considering a change complete. See **AGENTS.md** for project structure and **PROJECT_SPEC.md** for product spec.
