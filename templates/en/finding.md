---
id: OPAQUE13CHARS
title: TITLE
type: finding
audience: internal
status: draft
class: empirical          # empirical | formal | review | analytical
created: 1970-01-01
updated: 1970-01-01
origin:
  project: PROJECT-NAME
  experiments: []
  commit: SHA
# corrects: <id>          # only when this supersedes an earlier finding
---

## Claim

One paragraph. A statement that could be wrong.

## Conditions and limits

Where it holds: the data slice, the classes, the tools with their versions,
what was excluded.

And separately: what it does **not** say. Name the inference a reader is most
likely to draw wrongly from it.

If this finding is destined for the shared knowledge base, spell definitions
out here in prose. A local decision identifier will not resolve outside this
project.

## What it rests on

`empirical` — the runs, with their numbers:

| Experiment | What was measured | On what (n) | Value | Spread |
|---|---|---|---|---|
| | | | | |

Carry the numbers themselves, not only the pointers. A reader who has this
file alone (exported, forwarded, pulled into another project) must be able to
judge whether a correction upstream changes the claim.

The other classes replace that table with what admits them:

- `formal` — the premises, and the proof or where it is written out.
- `review` — what was searched, where, and on which date. A claim that the
  field has not done something goes stale, and the date is what bounds it.
- `analytical` — the known properties argued from, and the range over which the
  conclusion holds.

## When to revisit

The observable event after which this has to be narrowed or withdrawn:
something that either happens or does not, rather than a date or an impression.
