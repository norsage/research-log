---
id: H-0000.xxx
title: TITLE
type: hypothesis
audience: internal
status: idea              # idea | active | hold | resolved | recycled
created: 1970-01-01
updated: 1970-01-01
criterion_set:            # empty in idea; required in active
experiments: []           # must stay empty in idea
# finding: <id>           # set when resolved
# successor: <id>         # set when recycled
---

## Question

What we are asking, why it might be true, what the expectation rests on.
Links, sketches and back-of-envelope estimates, with as much room as they need.
This section is what makes an idea worth keeping before anyone commits to it.

## What would refute it

Filled in when the status moves to `active`, and empty before that. Moving to
`active` is the commitment, and this section is that commitment.

An observable result, after which the hypothesis is held to be refuted. Editing
it once experiments exist means raising `criterion_set`, which is what makes
the edit visible.

## What the experiments showed

Accumulates as work proceeds, citing experiments by identifier. Dead ends with
numbers belong here too.

A dead end with no numbers is how the work went, and belongs in the task.
