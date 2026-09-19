# Presets

Where this skill is customised. Read-only reference you consult before
proposing something to the user. Conventions live in the project's
`conventions-local.md`, whose shape comes from `templates/`.

In English. Propose in whatever language the user is writing in. A preset's
`##` heading names the section of `conventions-local.md` its content belongs
in. Match it to the project's own heading, whichever language that file is in.

## What is here

- `python-uv.md` — the computation is Python and the external tools are few.
- `conda.md` — conda is already here, or a tool they need has no wheel.
  Carries the conda commands, the lockfile order, and the rules for a project
  with more than one environment.
- `python-qa.md` — Python formatting, linting, type checking and tests. Any
  package manager.
- `structural-bio.md` — proteins and structures: parsing, surfaces,
  preparation, simulation, trajectories.

## How to use one

1. Offer it by what it does: *"I can start you on uv with a committed
   lockfile and a `src/` layout. Want to see it?"*
2. Show what it says. Say it is a starting point they can change or drop.
3. Write what they agreed into the project: `conventions-local.md` for the
   stack and the layout, the tools table for a package and its version,
   a protocol for an installation with traps.
4. Leave no reference to this directory in the project.
5. Stop consulting the preset. The project's own files are the authority from
   then on.

## Keeping them current

Each file carries the date it was last checked; say so when you offer one
whose date is old.

Domain material belongs here. Keep it out of `conventions.md` and the
templates.
