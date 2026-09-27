---
template_version: 0.2.0
---

# Conventions

**Shipped by research-log. Machine-owned; do not hand-edit.** `upgrade.py`
overwrites this file whole. Your project's own rules go in
[`conventions-local.md`](conventions-local.md), which the skill never touches.

## The map

| Looking for | Read |
|---|---|
| what this project is for, and its directions, including those set aside | [`vision.md`](vision.md) |
| stack, environment, code layout, external tools, tests | [`conventions-local.md`](conventions-local.md) |
| what is under test right now | [`hypotheses/_index.md`](hypotheses/_index.md) |
| what has been established | [`findings/_index.md`](findings/_index.md) |
| what is frozen and why | [`decisions/_index.md`](decisions/_index.md) |
| what was run, and on what | `experiments/` |
| how the tooling was checked | `technotes/` |
| how to install, rebuild or run something | [`protocols/_index.md`](protocols/_index.md) |
| what is being worked on | the task tracker; `tasks/` if the project has the task-tracker skill |

## Where a new thing goes

Work down the list; the first match wins.

1. Is it a run whose result says something about the project's subject: the
   model, the method, the data? → an experiment. So is the project's main
   computation, such as training and evaluating a model, and any run you are
   unsure about. Its numbers never go in a task, a chat message or a notebook
   cell.
2. Is it a run that checked the project's tooling: the speed of its code,
   agreement with another library, how files or features are read? → a
   technote, even when its numbers are compared later. If a choice was made on
   it, write a decision as well.
3. Is it a claim this project established, holding beyond one run? → a finding.
   The bar is that it changes a future decision. Set `class` to what admits it:
   `empirical` for runs, `formal` for a proof, `review` for a reading of the
   literature, `analytical` for an argument over known properties.
4. Is it a claim someone is about to test? → a hypothesis, moved to `active`,
   which obliges a refutation criterion.
5. Did it freeze a definition, a threshold or a data slice? → a decision.
6. Is it a sequence of steps someone will repeat? → a protocol. Installing a
   tool with its traps, rebuilding the metrics, assembling the report, the
   measurement a run follows.
7. Otherwise it is how the work went → the task tracker. Smoke tests and
   debugging sessions belong here too.

The title and the body are in the project's language. The filename is always
English: pass `--slug` with three or four English words. Without one, a
non-English title is refused rather than transliterated.

## The moments that fire a rule

| Moment | Rule |
|---|---|
| a full run is about to start | first a trial run on a small slice: the tree may be dirty, and nothing is recorded. Once it passes, commit everything the run uses: code, config, the measuring script. Unrelated edits may stay uncommitted. Note the SHA. Committing after the run is too late: `commit:` would name code the run did not use, and rerunning is expensive |
| a run finishes | `record_run.py` writes the experiment, or the technote with `--kind technote`. If HEAD has moved since the run started, or unrelated edits remain in the tree, pass `--commit <SHA before the run>`. Not by hand: a `run:` block typed by a person is a reproducibility claim nobody checked. The commit in `run.commit` is never rewritten: no rebase, squash or amend |
| a run reads data | the project pins its version, not the log. Under DVC or a similar tool the lock file is in git and `run.commit` pins the data with the code. Without one, the source and version of the data go in the protocol or in the document's text. `record_run.py` hashes no files |
| it is unclear whether a run is an experiment | write an experiment. If the same doubt comes back, ask the user once and record the class of runs in `conventions-local.md` |
| a hypothesis is taken up | status to `active`, write *What would refute it*, set `criterion_set`, in that order, before the first run |
| a hypothesis resolves | write the finding, set `status: resolved` and `finding:`. Refutation produces a finding too |
| the question turns out wrong | `status: recycled`, `successor:` |
| a number in a task appears | move it to an experiment or a technote, leave a reference behind |
| an experiment or a technote is found to be wrong | a **new** document of the same kind with `corrects:`. Never an edit |
| a definition changes | a new decision superseding the old, never an edit in place |
| a run used a frozen threshold or slice | name the decision in the experiment's `rests_on` |
| a run followed a written procedure | name the protocol in the experiment's `under` |
| a choice was made on a technote or an experiment | name them in the decision's `based_on` |
| you work out how something installs, runs or is assembled | write a protocol if it will be needed again |
| the stack, the code layout or a tool version becomes real | one line in `conventions-local.md`, before the code that assumes it |

## Rules with a mechanism

| Rule | Enforced by |
|---|---|
| A run on a dirty working tree is refused; in the log directory only `.md` files are exempt | `record_run.py` |
| `--commit` accepts only a commit that exists | `record_run.py` |
| `date:` is the earliest run's date, not the writing date | `record_run.py` |
| A hypothesis in `idea` cites no experiments | `check.py` |
| Every cited experiment postdates `criterion_set` | `check.py` |
| Every decision an experiment rests on predates the run | `check.py` |
| Every protocol an experiment ran `under` was created no later than the run | `check.py` |
| An `empirical` finding names at least one experiment or technote in `origin` | `check.py` |
| No hypothesis or experiment cites a technote | `check.py` |
| Every technote or experiment a decision is `based_on` ran no later than the decision | `check.py` |
| Identifiers are unique, well-formed, and match their filename | `check.py` |
| Filenames are English: a non-English title without `--slug` is refused | `new.py`, `record_run.py` |
| Indexes are generated and current | `index.py --check` |

Run `check.py` before committing. The skill adds no other check; whatever else
blocks a commit here is recorded in `conventions-local.md`.

## Two habits that are not mechanised

A field with no reader goes stale in silence. If nothing and nobody reads a
column, a field or a section, either delete it or give it a check. Three files
once carried pre-audit labels for eight days with nothing to notice.

Do not restate a number. A number lives in exactly one experiment or technote.
A finding carries the numbers it rests on; everything else cites.
