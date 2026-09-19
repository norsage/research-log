# Local conventions

**This project's own rules. Yours to edit; the skill never touches this file.**

The shipped rules are in [`conventions.md`](conventions.md). Local rules may
**add** and **tighten** them. They may not loosen anything there, and they may
not change the shape of a finding at all: a finding is the only document that
has to mean the same thing in another project.

Add to this file as the project goes along. A section may stay empty, but a
rule the project already follows has to be written down here.

Write it so someone on another machine can stand the project up without
asking you. Do not point at your environment, your agent's user-level
settings or a neighbouring repository: none of those travel with the project.
Copy such a rule in as text.

## Stack and environment

Language, package manager, how the environment is created and pinned, how
someone else reproduces it from scratch.

State the rule too: how a new dependency is added, and what happens to
something that cannot be installed that way.

With more than one environment, name each, say why they are separate, and say
which environment each entry point runs in.

## External tools

One row per tool that touches a number. Version, how it was installed, how it
is invoked, and whether it needs a licence.

| Tool | Version | Installed by | Notes |
|---|---|---|---|
| | | | |

A tool whose version is not written down here will be unknown within a month,
and every number it produced becomes unreproducible at that moment.

## Code layout

Where the pipelines live, where the library code lives, where notebooks live.
How scripts are named and which of them are entry points.

Written before the project's first script exists, and extended whenever a new
directory or module appears.

## Data

Where raw data lives and where derived data lives. The rule that derived
artifacts are regenerable and raw ones are never edited in place.

## Tests and linting

What runs, when, and what blocks a commit.

## How things are done

Step-by-step procedures are protocols, in [`protocols/`](protocols/), one file
each: installing a tool with its traps, rebuilding the metrics, assembling the
report. This file holds what is true; a protocol holds how to do it.

## Anything else this project decided

Additions to the shipped rules. If an addition turns out to be general rather
than local, say so: it belongs upstream in the skill instead.
