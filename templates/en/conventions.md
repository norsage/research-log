---
template_version: 0.1.0
---

# Conventions

**Shipped by research-log. Machine-owned; do not hand-edit.** The update
step overwrites this file whole. Your project's own rules go in
[`conventions-local.md`](conventions-local.md), which the skill never touches.

Local rules may add and tighten. They may not loosen anything here, and they
may not change the shape of a finding at all: a finding is the only document
that has to mean the same thing in another project.

## Where a new thing goes

Work down the list; the first match wins.

1. Is it a number someone will later compare? → an experiment. Never a task,
   never a chat message, never a notebook cell.
2. Is it a claim this project established, holding beyond one run? → a finding.
   The bar is that it changes a future decision. Set `class` to what admits it:
   `empirical` for runs, `formal` for a proof, `review` for a reading of the
   literature, `analytical` for an argument over known properties.
3. Is it a claim someone is about to test? → a hypothesis, moved to `active`,
   which obliges a refutation criterion.
4. Did it freeze a definition, a threshold or a data slice? → a decision.
5. Is it a sequence of steps someone will repeat? → a protocol. Installing a
   tool with its traps, rebuilding the metrics, assembling the report, the
   measurement a run follows.
6. Otherwise it is how the work went → the task tracker, or working state
   nothing may cite.

The title and the body are in the project's language. The filename is always
English: pass `--slug` with three or four English words. Without one, a
non-English title is refused rather than transliterated.

## The moments that fire a rule

| Moment | Rule |
|---|---|
| a run finishes | `record_run.py` writes the experiment. Not by hand: a `run:` block typed by a person is a reproducibility claim nobody checked |
| a hypothesis is taken up | status to `active`, write *What would refute it*, set `criterion_set`, in that order, before the first run |
| a hypothesis resolves | write the finding, set `status: resolved` and `finding:`. Refutation produces a finding too |
| the question turns out wrong | `status: recycled`, `successor:` |
| a number in a task appears | move it to an experiment, leave a reference behind |
| an experiment is found to be wrong | a **new** document with `corrects:`. Never an edit |
| a definition changes | a new decision superseding the old, never an edit in place |
| a run used a frozen threshold or slice | name the decision in the experiment's `rests_on` |
| a run followed a written procedure | name the protocol in the experiment's `under` |
| you work out how something installs, runs or is assembled | write a protocol if it will be needed again |
| the stack, the code layout or a tool version becomes real | one line in `conventions-local.md`, before the code that assumes it |

## Rules with a mechanism

Stated once, pointing at what enforces them. Restating a rule in prose beside
its mechanism gives it two sources of truth, and they diverge.

| Rule | Enforced by |
|---|---|
| A run on a dirty working tree is refused | `record_run.py` |
| Inputs are content-hashed; git pins code, not a data slice | `record_run.py` |
| `date:` is the earliest run's date, not the writing date | `record_run.py` |
| A hypothesis in `idea` cites no experiments | `check.py` |
| Every cited experiment postdates `criterion_set` | `check.py` |
| Every decision an experiment rests on predates the run | `check.py` |
| Every protocol an experiment ran `under` was created no later than the run | `check.py` |
| An `empirical` finding names at least one experiment in `origin` | `check.py` |
| Identifiers are unique, well-formed, and match their filename | `check.py` |
| Filenames are English: a non-English title without `--slug` is refused | `new.py`, `record_run.py` |
| Indexes are generated and current | `index.py --check` |

Run `check.py` before committing. The skill adds no other check; whatever else
blocks a commit here is recorded in `conventions-local.md`.

## Two habits that are not mechanised

A field with no reader goes stale in silence. If nothing and nobody reads a
column, a field or a section, either delete it or give it a check. Three files
once carried pre-audit labels for eight days with nothing to notice.

Do not restate a number. A number lives in exactly one experiment. A finding
carries the numbers it rests on; everything else cites.

## What this file does not cover

The stack, the environment, the code layout, the linter, the test policy, how
external tools are installed and invoked. All of that is project-specific and
belongs in `conventions-local.md`, which is filled in as the project learns
it.
