# Conda

Last checked: 2026-09. Say so when you offer it if that date is old.

Reach for it when conda is already the project's environment manager, or when
a tool they need ships only as a conda package or a system binary: simulation
engines, structural biology tools.

It replaces `python-uv.md` when conda owns the whole project. It also works
beside it: a uv project can hold one isolated conda environment for a package
that will not co-solve, using *More than one environment* below.

Offer it as *conda with a committed lockfile, and a separate environment for
anything that will not co-solve*. Everything below is a draft they can change
or drop.

---

## Stack and environment

The environment is conda, named in this file. Its manifest is
`environment.yml`; the exact build is `conda-lock.yml`, and both are
committed.

```bash
conda env create -n <name> -f environment.yml          # first build
conda env update -n <name> -f environment.yml --prune  # after editing the manifest
conda-lock -f environment.yml -p <platform>            # regenerate the lock
conda-lock install -n <name> conda-lock.yml            # exact rebuild from the lock
```

`--prune` is required: without it a package deleted from the manifest stays in
the environment.

A new dependency goes into `environment.yml` and then through `conda env
update`. Installing into the environment by hand leaves the manifest wrong.

Generate the lockfile and rebuild from it once before recording any of this in
`conventions-local.md`. For an environment that was built by hand, start with
`conda env export --from-history > environment.yml`, check that the manifest
recreates it, and lock after that.

## More than one environment

One environment is the default: binaries that co-solve stay together, external
or not.

Split only when forced: packages that will not co-solve, one that ships only
for a Python version the project has moved past, or one large or separately
licensed enough to isolate (PyRosetta, a vendor simulator).

A split has to fall on a process boundary. A package the project's own code
imports lives in one environment, the project's. A tool reached through a
subprocess can have its own.

Two environments holding different builds of the same package are safe, since
each interpreter loads its own. What breaks is mixing inside one environment:
pip installing over a conda-installed package, or another environment's
`site-packages` reaching `sys.path` through `PYTHONPATH`. A compiled extension
then loads against a numpy it was not built for.

Once split:

- each environment gets its own manifest and lockfile, named after it:
  `environment-pyrosetta.yml`, `conda-lock-pyrosetta.yml`;
- the code that runs in the isolated environment lives in its own directory,
  separate from `scripts/`, with one driver in the main environment that calls
  it and names the environment it needs;
- each entry point states the environment it runs in, at the top of the file
  and in `conventions-local.md`;
- a run that crossed two environments passes `--tool` for both when
  `record_run.py` writes the experiment;
- nothing is installed into one environment from another's manifest.

## Code layout

```
src/<package>/     library code: importable, no side effects on import
scripts/           entry points, one file per thing you run from a shell
notebooks/         exploration. Nothing here is a source of numbers
tests/
pyproject.toml     the project's own package
environment.yml    manifest
conda-lock.yml     committed lockfile
```

conda owns the environment; the project's own code is still a package. Install
it once into the environment so that imports stop depending on the working
directory:

```bash
pip install -e . --no-deps   # --no-deps: conda owns the dependencies
```

A number that will be compared comes from `scripts/` or `src/` through
`record_run.py`. A notebook that turns out to produce a real result gets its
logic moved into `src/` first.

Name a script for what it produces: `extract_interface.py` over
`run_step2.py`.

Installation traps for each binary go in a protocol.

---

## If they push back

- **conda-lock is another tool, or `conda env export` looks like a manifest.**
  Either export is a lock: the full transitive set, pinned, platform-specific.
  Keep it under a name that says lock, and write the manifest with
  `--from-history` beside it.
- **They want uv for the Python packages and conda for the binaries.** Works
  when the binaries are called through a subprocess and uv owns the
  interpreter. Two resolvers over one environment do not work: if the
  binaries ship Python bindings they import, keep everything in conda. On a
  project whose conda environment already carries the libraries its code
  imports, the split buys nothing and costs a second manifest and lockfile.
- **The environment was built by hand and works.** Do not rebuild it today.
  Export the manifest, commit it, and check the rebuild before the next run
  that produces numbers.
- **They want to move an existing project to another package manager.** Once
  numbers are on the board, say what it costs: another solver resolves other
  versions, the old lock is unusable, and runs before and after the move are
  comparable only through the tool versions each experiment recorded. Update
  the tools table as part of the move.
- **"It is a pipeline, not a package, so it needs no `pyproject.toml`."**
  Without one, imports resolve through the working directory and a run
  launched from anywhere else picks up something different or fails. The file
  is eight lines and also holds the pytest and linter configuration.
