# PROJECT-NAME

This file is an index. Rules live in the documents it links to, not here. Keep
it short enough to read in full before every task.

## Before any task

1. Read [`docs/conventions.md`](docs/conventions.md): where a new thing goes,
   and what fires at which moment. Shipped, not ours to edit.
2. Read [`docs/conventions-local.md`](docs/conventions-local.md): this
   project's own rules, being stack, environment, code layout, tools and
   tests.
3. Read [`docs/vision.md`](docs/vision.md): what this project is for and what
   it deliberately does not do.

## The map

| Looking for | Read |
|---|---|
| what this project is for | [`docs/vision.md`](docs/vision.md) |
| where a document goes, and when it converts | [`docs/conventions.md`](docs/conventions.md) |
| stack, environment, code layout, external tools, tests | [`docs/conventions-local.md`](docs/conventions-local.md) |
| what is under test right now | [`docs/hypotheses/_index.md`](docs/hypotheses/_index.md) |
| what has been established | [`docs/findings/_index.md`](docs/findings/_index.md) |
| what is frozen and why | [`docs/decisions/_index.md`](docs/decisions/_index.md) |
| what was run, and on what | `docs/experiments/` |
| how to install, rebuild or run something | [`docs/protocols/_index.md`](docs/protocols/_index.md) |
| what is being worked on | the task tracker, not this repository's concern |

## Where a number goes

A number someone will compare lives in an experiment, written by
`record_run.py`. A claim that outlives its run is a finding. Everything else is
how the work went, and belongs in the task tracker.

Run `check.py` before committing.
