# Python with uv

Last checked: 2026-09. Say so when you offer it if that date is old.

For a project whose computation is Python and whose external tools are few.
Use `conda.md` instead when conda is already the environment manager or the
work is built around binary tools.

One uncooperative package does not move the project to conda. Something that
will not co-solve, or is large and separately licensed like PyRosetta, gets
its own conda environment beside this one, under the rules in `conda.md`.

Offer it as *uv, a committed lockfile and a `src/` layout*. Everything below
is a draft they can change or drop.

---

## Stack and environment

Python, version pinned by `requires-python` in `pyproject.toml`. uv installs
the interpreter, so a machine with no Python reproduces the project.

Dependencies are added with `uv add <package>`, never by hand-editing
`pyproject.toml`. `uv.lock` is committed; `uv sync` reconstructs the
environment from it exactly.

```bash
uv sync                 # environment from the lockfile
uv run python -m ...    # anything that touches the project
uv add <package>        # a new dependency, lockfile updated
```

Install separately anything uv cannot: a binary tool, or something distributed
only through conda or a system package manager. Give it a row with its version
in the tools table in `conventions-local.md`, and put its installation traps in
a protocol.

## Code layout

```
src/<package>/     library code: importable, no side effects on import
scripts/           entry points, one file per thing you run from a shell
notebooks/         exploration. Nothing here is a source of numbers
tests/
pyproject.toml     dependencies and the project's own packaging
uv.lock            committed
```

A number that will be compared comes from `scripts/` or `src/` through
`record_run.py`. A notebook that turns out to produce a real result gets its
logic moved into `src/` first.

Name a script for what it produces: `build_features.py` over `run_step2.py`.

---

## If they push back

- **`src/` feels like ceremony.** At two files it is. The reason to keep it:
  `import mypackage` then cannot pick up the working directory in place of the
  installed package. Say that once and take their answer.
- **They already use conda.** Switch to `conda.md`, which carries the conda
  commands and the lockfile order. Do not convert a project mid-flight.
- **They have no opinion.** Take this as the answer. They can change it later;
  the research log does not depend on any of it.
