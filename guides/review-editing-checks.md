# Text-editing acceptance checks

Manual policy regression checklist. Compare `SKILL.md`, both convention
templates and the six document templates in each language. These are editorial
rules, not a new Git-based check in `check.py` or CI.

| Scenario | Expected rule |
|---|---|
| A new document of each of the six kinds is in an open MR/PR | Direct text refinement is allowed with the same `id`, subject to truthful evidence and conditions already used. No separate E/T `corrects` just for review edits. |
| A new record is committed, pushed, taken out of Draft or approved by a reviewer | None is first acceptance into the project's main integration branch. `main` is an example name; document statuses are not branch membership. |
| An E/T error is addressed in a new branch after that record once entered the main integration branch | A new record of the same kind with `corrects: <id>`, not an edit to the accepted text. |
| A previously accepted record is renamed, copied or given a new slug | Stable `id` carries its history; it does not become new. |
| A finding, hypothesis or protocol needs an update after acceptance; a decision needs replacement | The first three remain mutable under their own rules. Replace the decision through `superseded`/`superseded_by`, not automatically `corrects`. |
| A hypothesis is not merged, but testing has started or results have been seen | No replacement of the original claim/criterion under cover of a prose edit; preserve pre-registration, `criterion_set`, statuses and experiment links. Raising the date does not pre-register old evidence. |
| A budget decision is still on review, but the search has started | Clarifying wording without changing meaning is allowed before acceptance. A different budget or selection algorithm needs a new decision; keep the original conditions. |
| A protocol is still on a branch, but a run has followed it | Clarifications and evidence-based corrections of the account are allowed; a new procedure is not presented as the one past runs used. Preserve historical procedures and distinguish future steps. |
| Review prompts new computations rather than a correction of a report | Existing run-recording and rerun/rebase rules still apply, even before acceptance; do not pass new numbers off as the old run. |
| Someone wants to change service fields or only the text of an applied definition | No arbitrary edits to ids, commit links, dates, run identifiers or provenance. Semantic constraints apply to text too; no retrospective pre-registration. |

For the executable regression checks run `bash guides/smoke-test.sh`. Its
temporary EN/RU boards exercise the convention version upgrade, check-only
behaviour and idempotence, and verify byte-for-byte preservation of local
conventions, all six kinds, board settings, vision and indexes. It also checks
that the project's `AGENTS.md` is unchanged.
