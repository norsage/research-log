# Python: linting, types and tests

Last checked: 2026-09. Python only; none of it transfers to R or Julia.

For any package manager. The environment itself is in `python-uv.md` or
`conda.md`.

## Tests and linting

| Tool | Covers | Mode |
|---|---|---|
| `ruff format` | layout | let it fix |
| `ruff check` | undefined names, unused imports, mutable defaults | check only |
| `pyright` | types, on the library layer | check only |
| `pytest` | anything with a right answer | check only |

`ruff check --fix` stays off: it deletes an import kept for a registration
side effect. Prefer pyright to mypy, unless the project uses a framework whose
mypy plugin is worth having.

Point pyright at `src/` and leave `notebooks/` and one-off scripts alone; they
change shape weekly. For arrays, jaxtyping annotates shape and dtype and
pyright enforces them.

Test what has a known right answer: parsers, geometry, unit conversions, index
arithmetic. Compare floats with an explicit tolerance. Use a committed fixture,
not the real dataset.

A test pinning a computed result detects change. Whether the value is correct
belongs in an experiment or a finding.

`check.py` is the gate before a commit, and `conventions.md` already requires
it. Run the tools above at that same point, not inside `check.py`: that script
ships with the skill and an update overwrites it. Record in
`conventions-local.md` which of them block a commit. Keep the gate read-only,
except a formatter that re-stages what it changed. Or format on save and leave
the gate nothing to do.
