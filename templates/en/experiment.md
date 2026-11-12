---
# --- written by a human ---
title: TITLE
# motivated_by: "0042.k3f"   # free-form; a task id in whatever tracker. Never parsed
# corrects: <id>             # correction record; not needed just for pre-acceptance text edits
# rests_on: [D-0003.m4k]     # decisions this run relied on. Each must predate it
# under: [P-0001.k3f]        # protocols this run is reproduced by

# --- written by the run wrapper ---
id: E-0000.xxx
type: experiment
audience: internal
date: 1970-01-01             # the EARLIEST run's date, not the writing date
run:
  tracker: mlflow            # or aim, or none
  ids: []
  commit: SHA
  tools: {}
---

## What was done

One paragraph in words, enough that the `run:` block above becomes meaningful.

Before this record's first acceptance into the main integration branch, refine
its text directly, including results and interpretation during review, keeping
its `id`. After acceptance, correct errors with a new experiment with `corrects`.
Never substitute runs, hide failed attempts or pass new computations off as
old ones. Run provenance and the recording/rebase rules in `conventions.md`
still apply; editing text does not permit arbitrary frontmatter changes.

## What came out

| What was measured | On what (n) | Value | Spread |
|---|---|---|---|
| | | | |

## Deviations

What failed, what was rerun and why, what differed from the plan. "The third
fold ran out of memory and was rerun at batch 16" is the line that decides
whether the number above can be reproduced.

An empty section is an answer, and rarely the true one.

## What follows from it

Conclusions bounded to this execution.

A claim that outlives the run goes in a finding. Left here, it is archived
along with this document and stops being visible.
