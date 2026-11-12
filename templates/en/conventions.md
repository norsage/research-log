---
template_version: 0.5.0
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

## Editing text: acceptance and use

Before a document's **first acceptance into the main integration branch**,
the text of all six kinds may be edited directly, including during review.
Keep its `id`. This concerns text, not arbitrary edits to service fields:
`id`, `run.commit`, run dates, run identifiers and data provenance remain
truthful and follow the existing recording and rebase mechanisms.

The main integration branch is the project's primary integration branch;
`main` is only an example name. First acceptance concerns the specific record,
identified by its stable `id`, not its first commit, push, MR/PR, removal of
Draft or reviewer approval. An open MR, a new branch, copying or renaming a
file or changing its slug does not reset a previously accepted record's
history or rules. Statuses (`draft`, `accepted`, `active`, etc.) do not mean
presence in that branch.

**Use of conditions in research is a separate boundary**, possibly before
acceptance. Do not retrospectively change definitions, criteria, budgets or
procedures already used, or distort actual runs. Changing only text can violate
this rule even with all service fields unchanged. Decision, protocol and
criterion dates must remain truthful: no retrospective pre-registration.

| Kind | Text before first acceptance | Boundary that text edits cannot bypass | After acceptance |
|---|---|---|---|
| experiment | refine the run description, correct transcription or interpretation, add limitations and conclusions; no separate `corrects` just for these review edits | do not substitute runs, hide failed attempts or pass new computations off as old ones; preserve numbers' provenance and code used | errors require a new experiment with `corrects: <id>`, not an edit to the accepted text |
| technote | refine the tool check's description, results and conclusions; no separate `corrects` just for these review edits | do not substitute the tool/version, measurement conditions or result source | errors require a new technote with `corrects: <id>` |
| finding | refine the claim, grounds, scope, limitations and recommendation | do not invent results in its sources or distort primary experiments; separate new interpretation from measured evidence | stays mutable under finding rules; no mandatory `corrects` for every refinement |
| hypothesis | refine question, motivation and wording; agree the criterion before evidence relevant to its test | once testing starts, do not replace the original claim or criterion to fit seen results and present it as pre-registered, even in prose alone | stays mutable, subject to pre-registration, `criterion_set`, statuses and experiment links |
| protocol | improve instructions, explain steps and limitations; distinguish future improvements from procedures already used | do not claim past runs used a changed procedure; correcting the account of steps actually performed needs reliable evidence | stays mutable; retain past procedures in git history and distinguish them in the text; a deprecated protocol's replacement is a new protocol |
| decision | refine wording and rationale; agree substance before use | once used in a run, do not retrospectively change thresholds, slices, budgets or selection algorithms; meaning-preserving wording is allowed before acceptance, changed conditions need a new decision | do not rewrite accepted text; replace with a new decision using `superseded` and `superseded_by`, not automatically `corrects` |

A substantive change to a hypothesis criterion requires raising `criterion_set`;
a wording clarification that preserves meaning does not. Preserve the original
conditions and evidence: neither changing that date nor leaving it untouched
makes the new criterion pre-registered for results already seen. A new question
uses `recycled`/`successor`. For hypotheses, protocols and decisions already
used, use these existing mechanisms for substantive revisions, preserving the
conditions of past runs. Permission to clarify is not permission to replace meaning.

## The moments that fire a rule

| Moment | Rule |
|---|---|
| a full run is about to start | first a trial run on a small slice: the tree may be dirty, and nothing is recorded. Once it passes, commit everything the run uses: code, config, the measuring script. Unrelated edits may stay uncommitted. Note the SHA. Committing after the run is too late: `commit:` would name code the run did not use, and rerunning is expensive. Just before the full run, rebase the branch onto main; open the merge request as soon as the record is written. Every rebase after a recorded run risks a record whose code changed under it, so rebase it only to merge. A run that needs no code of its own runs on a commit of main, with nothing committed on top: such a record names a commit no rebase can touch, whichever merge request goes in first |
| a run finishes | `record_run.py` writes the experiment, or the technote with `--kind technote`. If HEAD has moved since the run started, or unrelated edits remain in the tree, pass `--commit <SHA before the run>`. Not by hand: a `run:` block typed by a person is a reproducibility claim nobody checked |
| a branch is rebased, squashed or amended, here or by the server | with `run_paths` set, the post-rewrite hook has already moved every record whose paths did not change. `rebase_runs.py` lists the rest, experiments, technotes and findings, and shows what changed. `--same --paths <what the run used>` when that code did not change; `--keep` when it did, which tags the old commit: push the tag. Or run again, as a record with `corrects:`. Commit the updated records. Never edit `run.commit` or `origin.commit` by hand |
| several merge requests are ready at once | merge first those that change nothing under `run_paths`. A code change merged after other people's runs leaves their records intact; merged before, it leaves every record still on a branch naming code main no longer has. A code change several people need goes in first as its own small merge request, and they rebase onto it just before their runs |
| a rewrite changed code a record names, and an agent is settling it | `--keep` by default: it claims nothing. `--same --basis` only with evidence, written into the basis: the trial run on the small slice gave the same output at both commits (name the command), or the changed files are not among those the run loaded (say how that was established). A reading of the diff is not evidence: show the diff to the user and let them decide. Pushing a tag or a rewritten branch is the user's to approve |
| a record whose code changed is run again | same numbers: no new record; `rebase_runs.py <id> --same --basis "full rerun at <sha> reproduced the numbers: <which numbers, old → new>, <command>"`. Different numbers: a new record with `corrects:`, and review what cites the old one. A corrected record's commit is no longer checked; its tag stays until someone deletes it |
| a run or a finding has to be reproduced | check out the commit it names beside the working tree, not in it: `git worktree add ../repro-<id> $(grep -m1 '^  commit:' docs/*/<id>-*.md | awk '{print $2}')`. The commit is in the record's frontmatter, never in where the record sits in `git log`: a record merged after other code still names the code it ran on. `git worktree remove ../repro-<id>` when done |
| a commit has to be kept past a rewrite | the tag is `research-log/<id>`, made by `rebase_runs.py --keep` and by nothing else. The project's own tags stay out of `research-log/` |
| the paths a run's result depends on become clear | list them in `run_paths` in `.research-log.md` |
| a clone is made | `rebase_runs.py --install-hooks`, once. The post-rewrite hook records what replaced what; the pre-push hook refuses a push that leaves a record behind |
| a run reads data | the project pins its version, not the log. Under DVC or a similar tool the lock file is in git and `run.commit` pins the data with the code. Without one, the source and version of the data go in the protocol or in the document's text. `record_run.py` hashes no files |
| it is unclear whether a run is an experiment | write an experiment. If the same doubt comes back, ask the user once and record the class of runs in `conventions-local.md` |
| a hypothesis is taken up | status to `active`, write *What would refute it*, set `criterion_set`, in that order, before the first run |
| a hypothesis resolves | write the finding, set `status: resolved` and `finding:`. Refutation produces a finding too |
| the question turns out wrong | `status: recycled`, `successor:` |
| a number in a task appears | move it to an experiment or a technote, leave a reference behind |
| an experiment or a technote is found to be wrong | before its first acceptance, correct its text directly under the rules above, keeping its `id`; after acceptance, a **new** document of the same kind with `corrects: <id>`, never an edit to the accepted text |
| a definition changes | if the decision is already used or accepted into the main integration branch, a new decision superseding the old; before both boundaries, agree its content directly. A meaning-preserving clarification is not a changed definition, but an applied definition cannot be rewritten under cover of a draft edit |
| a run used a frozen threshold or slice | name the decision in the experiment's `rests_on` |
| a run can be reproduced by a written protocol | name the protocol in the experiment's `under` |
| a choice was made on a technote or an experiment | name them in the decision's `based_on` |
| you work out how something installs, runs or is assembled | write a protocol if it will be needed again |
| the stack, the code layout or a tool version becomes real | one line in `conventions-local.md`, before the code that assumes it |

Text-editing permission does not change the rerun and history-rewrite rules
above, even before first acceptance. New computations are not editorial fixes;
record them under those rules rather than substitute their numbers for old ones.

## Rules with a mechanism

| Rule | Enforced by |
|---|---|
| A run on a dirty working tree is refused; in the log directory only `.md` files are exempt | `record_run.py` |
| `--commit` accepts only a commit that exists | `record_run.py` |
| `date:` is the earliest run's date, not the writing date | `record_run.py` |
| Every `run.commit`, and `origin.commit` of a finding minted here, is on HEAD or held by the record's tag | `check.py`, the pre-push hook |
| `--same --paths` moves `run.commit` only when those paths are unchanged | `rebase_runs.py` |
| A hypothesis in `idea` cites no experiments | `check.py` |
| Every cited experiment postdates `criterion_set` | `check.py` |
| Every decision an experiment rests on predates the run | `check.py` |
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

A protocol's status. `draft`: nobody has yet gone through it end to end, or it
has steps never executed and not marked as such. `stable`: someone has gone
through it end to end at least once, the steps match the project as it is now,
and any step not yet executed is marked in the text. `deprecated`: no longer
used; write the replacement as a new protocol. A run naming the protocol in
`under`, or a note in a task, is what shows it was gone through. Whoever
checked that, person or agent, changes the status and names the evidence in
the commit message. Steps change with the project; bump `updated` on each edit.
