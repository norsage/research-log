---
id: D-0000.xxx
title: TITLE
type: decision
audience: internal
date: 1970-01-01
status: accepted          # accepted | superseded
# superseded_by: <id>     # only when superseded
# based_on: [T-0002.p4r]   # technotes and experiments the choice was made on. Each must predate it
---

## Context

What had to be decided, and why it came up now.

## Decision

What was chosen. One sentence.

Before first acceptance into the main integration branch, refine wording and
rationale directly, including during review; agree the substance before use.
Once used in a run, do not retrospectively change thresholds, slices, budgets
or selection algorithms, even while still on review. Meaning-preserving text
edits remain allowed before acceptance; changed conditions need a new decision.
After acceptance, do not rewrite the text: replace it with a new decision and
mark the old `superseded` with `superseded_by`, not automatically with `corrects`.
The `accepted` status alone does not mean acceptance into the main branch.

## Rejected alternatives

What else was considered and why it lost. This is the part that gets read when
the results later surprise you.

## When to revisit

The observable event after which this stops being the right call.
