---
# --- written by a human ---
title: TITLE
# motivated_by: "0042.k3f"   # free-form; a task id in whatever tracker. Never parsed
# corrects: <id>             # correction record; not needed just for pre-acceptance text edits
# under: [P-0001.k3f]        # protocols this run is reproduced by

# --- written by the run wrapper ---
id: T-0000.xxx
type: technote
audience: internal
date: 1970-01-01             # the EARLIEST run's date, not the writing date
run:
  tracker: none              # or mlflow, or aim
  ids: []
  commit: SHA
  tools: {}
---

## What was checked

Which part of the tooling, against what, and why now.

Before this record's first acceptance into the main integration branch, refine
its text, results and conclusions directly during review, keeping its `id`.
After acceptance, correct errors with a new technote with `corrects`. Do not
substitute the tool/version, measurement conditions or result source. New
computations and run fields still follow the recording/rebase rules in
`conventions.md`; they are not free text edits.

## What it showed

Numbers, a table, or one sentence if it matched. The machine goes here when the
numbers depend on it: a timing with no hardware attached cannot be compared
with the next one.

If a choice was made on this result, write a decision and name this technote in
its `based_on`.
