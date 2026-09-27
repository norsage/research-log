# Rationale

Why this design came out the way it did, and what was rejected on the way.
Development document: it is not installed with the skill, and a project using
the skill does not read it. `SKILL.md` states the rules; this file states the
arguments, so that a rejected option is not re-proposed as new.

Each section names the decision, the alternative, and what decided between
them. Reversals are marked, being the part most likely to be quietly undone.

---

## 1. The model: what the kinds are and how they relate

### 1.1 An experiment is not subordinate to a hypothesis

Decided: the relation is citation, M:M, optional from both sides. Rejected: the
chain `hypothesis → experiment`, with knowledge extracted from hypotheses and
the 1:M relation treated as the normal case.

Under the rejected design, M:M, 0:M and M:0 all look like bad bookkeeping.
Three arguments say they are the reality:

- Runs with no hypothesis are legitimate and common: baselines,
  characterisation, audits, controls, feasibility probes. None of them can be
  refuted, so none is a hypothesis.
- Mandatory subordination manufactures HARKing. If every run must hang off a
  hypothesis, an exploratory run gets one written after the result is visible,
  and that result then confirms it by construction. The discipline looks
  intact and every record becomes untrustworthy.
- An experiment is immutable and self-contained; a hypothesis is living. Making
  the record a child of the living document is the same bug as a living
  contract file absorbing its own history.

Once the relation is citation rather than subordination, M:M is the normal
case: one expensive pass over the data answers three questions.

Evidence from the project this design was drawn from: its knowledge model had
leaked into two extra homes, standing findings and decision records, because
knowledge attached to no hypothesis had nowhere else to go.

### 1.2 "Experiment" was three things, and one of them was a task

Decided: an experiment document is the document over a run, and nothing else.

In the source project, one identifier (`EXP-011`) was simultaneously a design
("test this variant across 5 folds × 2 seeds"), ten runs, and a report. That is
why its registry carried work-state fields, `status: completed` and
`expected_runs`, on a record declared immutable. A record that carries work
state is not immutable, whatever it says.

Split three ways: the design is a task, in whatever tracker; the runs belong to
the run tracker; the report is a finding. What remains for this skill is the
document over a run, and no kind called "experiment campaign" is needed.

Grouping fell out for free. Ten runs forming one comparison are one experiment
document with ten entries in `run.ids`. A set of experiments forming one line
of attack is a subheading inside the hypothesis.

### 1.3 Hypothesis and finding have the same shape and opposite times

Raised as an objection: *"what would refute it" is Popperian falsifiability,
which makes a finding look like a hypothesis.* Correct, and the boundary is
time relative to the evidence:

| | Hypothesis | Finding |
|---|---|---|
| written | before the evidence | after |
| the refutation section | a pre-commitment | a scope statement |
| status vocabulary | work state | reliability state |
| experiments | cites, resolvable | records as `origin` |
| when contradicted | refuted, a result | narrowed or withdrawn, a blast radius |

The sections are therefore named differently on purpose: *What would refute it*
in a hypothesis, *When to revisit* in a finding. The second is MADR's revisit
and kill criteria, which is what MADR was adopted with.

A hypothesis resolving in either direction produces a finding.

### 1.4 `idea` survived, with the danger fenced instead

Rejected by the user, against the first proposal: removing the `idea` status,
on the evidence that 42% of the source project's hypothesis files never left
it, and putting ideas in a one-line backlog instead. An idea's context can be
rich, and one line cannot hold it.

Better answer: keep `idea`, move the commitment from file creation to the `idea
→ active` transition, and forbid the one dangerous combination, an idea citing
experiments. Conversion is then a status change in the same file, so git
history keeps "why we thought this would work" attached to the hypothesis
instead of losing it in a copy-paste.

What cures the 42% is showing the count: `index.py` leads with `idea: 14,
active: 3, resolved: 5`. Nobody noticed the ratio for a year, not because the
schema allowed it, but because nothing displayed it.

Dropped at the same time: `validated` and `rejected`. The outcome lives in the
finding, and a second copy in the status would diverge. A hypothesis also
rarely resolves cleanly either way; it resolves as "yes for class A,
unmeasurable for class B", and both words would be lies. `recycled` was taken
from Stage-Gate-TD's vocabulary, for the question that turns out to be the
wrong question.

### 1.5 Decisions are one document each

Reversed a first lean toward a single append-only journal.

Citability decided it: experiments and findings cite decisions, and an anchor
inside a shared file needs a second resolution mechanism beside "identifier
equals filename prefix". The ceremony objection is answered by `new.py
decision` plus a generated index. MADR is per-document by definition.

Cut from MADR: `deciders` (one student), `decision drivers` (dissolves into
context), `consequences` (overlaps *when to revisit*, and two similar sections
guarantee one empty one).

### 1.6 Procedures belong to this skill

Decided: a procedure is knowledge, and this skill keeps it.

**Half of this section is superseded by §1.7, 2026-09-19.** The home was
`docs/howto/`, plain files with no identifier, no index and no check; it is now
`docs/protocols/`, a kind with all three. What stands is the argument that
procedures belong here at all, and the rejected alternatives below.

The gap was real and `conventions-local.md` could not close it. That file holds
what is *true* of a project — the stack, a table of tool versions, where raw
and derived data live. A procedure is a different thing: the mutation-effect
brief carries thirty lines on installing structural tools, including that their
pip builds break the whole environment, and no cell of a versions table holds
that. After initialisation it had nowhere to go, and the answers are all bad:
into the task tracker, where §3.1 says receipts for work live and knowledge
does not; into a table cell, truncated; or nowhere.

By §3.1's own test it belongs to this skill: a runbook has value after its work
closes, which is what separates knowledge from a task.

Rejected at the time, and this is the half §1.7 reversed: a fifth kind, with a
template, `new.py runbook`, an identifier and an index. Identifiers here exist
for citation — a finding cites experiments, an experiment rests on decisions —
and nothing cites a procedure. Minting `R-0001.k3f` would be machinery bought
for nothing, and §2.6 had just settled that this skill refuses rather than
adds. The filename carries the topic, which is all a directory listing needs.

The premise is false, and the survey in `agentic-design/docs/methodology.md`
had already recorded why: an experiment cites a procedure constantly, which is
what a standard operating procedure is for. `docs/howto/` became
`docs/protocols/`.

Rejected: leaving it to each project. It is one line in `conventions.md` and
one row in the map, against a section of a real brief that would otherwise be
lost at initialisation.

Who writes them: the agent, when it has worked something out and it will be
needed again — the same shape as the rules that already fire on a finished run
or a resolved hypothesis. A directory nobody is prompted to fill stays empty.

### 1.7 Five kinds, and a finding says what admits it

Decided 2026-09-19, reversing §1.6's second half. Protocols become a kind with
an identifier, an index and a date check. A finding gains `class`, and
`origin.experiments` is required of the empirical class alone.

**What §1.6 got wrong.** It reasoned that identifiers exist for citation and
nothing cites a procedure. An experiment cites a procedure constantly — *this
was measured under protocol P* is the sentence a standard operating procedure
exists to make possible. The survey in `agentic-design/docs/methodology.md` had
already found the gap from the other side, as its third keeper finding:
*"Nothing says measured under protocol P on date D by instrument I, aggregated
by script at version V"*, with Session 6's proxy-validity ledger resting on
that field. `record_run.py` was writing the machine half of provenance —
`commit`, `tools`, `inputs[].sha256` — and had no field for the human half.

The check follows the shape of the two that existed: a protocol named in
`under` must have been created on or before the run. A procedure written up
after the result is not what the run followed, for the same reason a threshold
frozen after the numbers is not a pre-commitment.

**Why classes rather than more kinds.** A theorem proved here, a reading of
what the field has and has not done, a comparison argued from the methods'
properties — each is a claim this project established and each travels, so each
wants the finding's identifier form and its export check. What differs is only
what admits it. That is a field, and ResearchLoop's claim-ledger fields, the
form `methodology.md` already proposes taking, make it one. The operational
test in the same document decides what earns a class: *does it change what
evidence admits a statement of this kind?* Four do. A benchmark does not — it
is admitted by runs, so it is `empirical`, and the class follows what
established a claim rather than its subject.

Rejected: sibling kinds for theorem, review and analysis. They would need four
templates, four directories and four index files to express one difference that
one field expresses, and every one of them would have to re-derive that a
finding travels.

Rejected: renaming `finding` to `claim`, which reads better for a theorem.
`agentic-design/docs/structure.md` already uses `finding` in the one place the
cross-home type vocabulary is half-written, and forking a vocabulary to improve
a word is the more expensive half of the trade.

Not taken here, and left to Session 3: whether `protocol` and the four classes
enter the shared base's type list under these names. The list does not exist,
and this skill is the only thing that can exercise them. What it produces is
the input.

**Literature is two things, and that is what kept the question tangled.** The
papers are external, cited, and the base's material once one exists. The claim
*"as of this date the field has not done C"* is this project's own, dated, and
it is what a hypothesis' novelty rests on — a finding of the review class.
Splitting those apart is what made the edge decidable.

### 1.8 Technotes: runs over the tooling

Decided 2026-09-27. A sixth kind, `technote`, records a run that checked the
project's tooling rather than its subject. It carries the same `run:` block as
an experiment and is written by `record_run.py --kind technote`.

**What went wrong.** The conventions sent every number someone would later
compare to an experiment. In a project about training models, a benchmark of
the parsing code was filed as an experiment because its numbers were compared,
although nothing in it bore on the project's question. The project patched
this locally: speed measurements and comparisons of reading and features
against other libraries went to task notes, with the script, the commit, the
inputs with sha256, the machine and the versions written beside them.

**Why the local patch was not enough.** Task notes pile up in the tracker, and
a result someone needs a month later is hard to find there. The conditions the
project listed are the `run:` block almost field by field, so the record
already existed. Only its name and its citers had to change.

**Where the boundary runs.** The boundary is what the run examined. An
experiment's result says something about the subject of the research; a
technote's says whether a tool can be trusted. The test: would a different
number change an answer to the question in `vision.md`, or only an opinion of a
tool? Data analysis is an experiment, because it changes what is known about
the data the conclusions are drawn from. So is the project's main computation. A run in
doubt is an experiment: a technote filed as an experiment clutters the log,
while an experiment filed as a technote can no longer test a hypothesis. A
doubt that recurs is settled once by the user and written to
`conventions-local.md` as a class of runs.

**What `check.py` holds.** No hypothesis cites a technote, and no experiment
rests on one. A finding may name technotes in `origin.technotes`, kept apart
from `origin.experiments`, because a technical detail sometimes matters in its
own right and is worth carrying to another project. A decision names the
technotes and experiments its choice was made on in the new `based_on`, each
dated on or before it. Through that chain, from technote to decision to
experiment, a technote later found wrong reaches every run computed with the
tool it vouched for.

Rejected: a field on the experiment, such as `subject: tooling`, which the
reasoning of §1.7 would favour. Finding classes share their relations and
differ only in what admits the claim. A technote differs in who may cite it,
which is what `check.py` enforces, and a field would leave tooling runs in
`docs/experiments/` under the name that caused the error.

Rejected: routing every tooling check into a decision or a protocol. A protocol
is an instruction and holds no results. A decision needs a choice, and many
checks end without one.

Rejected: requiring a task tracker at initialisation. It would add to the
tracker's load, which was the complaint, and §3.1 keeps this skill independent
of any tracker.

Rejected: the names `measurement` and `note`. Data analysis is a measurement
too, which blurred the boundary the kind was meant to draw, and `note` invites
drafts, reviews and plans.

Rejected: a `machine` field in `run:`. When a technote's numbers depend on the
hardware, its text says what the hardware was.

## 2. What enforces it: checks, fields, identifiers, language

### 2.1 The pre-commitment is checked by comparing two dates

Decided: `criterion_set` is a date, and every experiment a hypothesis cites
must be dated after it.

Confirmatory work is worth keeping, and what makes it confirmatory is that the
refutation criterion was written before the evidence. Reduced to a mechanism,
that is a date comparison. Editing the criterion later means raising that date,
which turns an invisible edit into a visible one.

Two consequences that look like details and are not:

- `date:` on an experiment is the earliest run's date, not the writing date.
  Otherwise: run Monday, see the result, write the criterion Wednesday, write
  up the experiment Thursday, and the check passes on a document that violates
  everything it is checking for.
- A hypothesis in `idea` may cite no experiments. An idea with runs attached is
  HARKing in progress.

### 2.2 `origin` from the start, not a translation

Decided: a finding carries `origin` inside the project, in the same form it
will have in the shared base. Rejected by the user, against the first design:
`rests_on` inside the project, converted to `origin` by the exporter.

The reason was better than the design: a finding may be pulled into another
project as context, so it must always say where it came from, and a field with
two forms can break on the conversion.

This sharpened the model. A finding does not cite experiments, it records
provenance. Citation is what must resolve in the same plane; provenance is
data. A hypothesis cites; a finding does not.

### 2.3 Blast radius has to be cheap

Asked directly: if provenance crossing into the shared base becomes prose, can
you still find which findings an erroneous experiment poisoned? It could not,
and two things fixed it:

- `origin` stays structured in the base, as data the export check never tries
  to resolve, so it violates nothing and cannot dangle.
- A finding carries the numbers it rests on, not only pointers. `origin`
  answers "which findings are affected"; only the numbers answer "does the
  error change the claim". This also makes a finding readable when it travels
  alone as a single file.

`corrects:` on a new document drives the walk, because an experiment is never
edited and so never raises a review flag by being edited.

### 2.4 Language: prose yes, keys never

Templates ship in `en` and `ru`, and the board picks one. Keys and enum values
are identical in both, `status: active`, `criterion_set`, `origin`, because
they are a wire format read by the checks and eventually by a shared base. A
project whose frontmatter is in Russian stops being readable by any of them.

`SKILL.md` and `guides/` stay English-only: a translated second copy of the
rules would drift from the first.

Decided: `templates/ru/` is written as technical documentation in its own
register. Rejected: translating the English templates clause by clause.

The first Russian set was a literal translation, and it was grammatical and
unreadable: *a claim that outlived its run*, *a number is not restated*, *first
match wins*, all carried across word for word. The English here is aphoristic
and personifies its subjects, and Russian built on that structure reads as
machine output. One calque was not a word in either language.

What the rewrite settled on:

- Recast the rule and let the sentence go. *A claim that outlived its run*
  becomes *a claim that stays true after the run*.
- The familiar second-person imperative, *delete* and *write down*, over the
  polite form and over the infinitive.
- Standard terms only. No coinages: rewrite the sentence around the gap.
- Cut anecdotes, wordplay, and figures that personify documents or numbers.
- One clause per rule.

The two sets therefore say the same things and do not read alike, which is the
point. Each is documentation in the register its language uses for it.

### 2.5 Identifiers: two forms, and a slug

Local kinds use `<P>-NNNN.xxx`. The suffix keeps two branches from both minting
`0042`; it is borrowed from task-tracker, along with its sizing table.

Findings use 13 Crockford Base32 characters plus a check symbol, which is the
shared base's own form, so graduation is a `git mv` with no citation broken.

Filenames are `<ID>-<slug>.md` and citations carry the identifier alone. The
slug was argued in: without it the directory is unbrowsable, an exported single
file does not say what it is, and an agent choosing what to open must otherwise
consult an index first. That last reason is the strongest. The cost is that
OKF's "path equals identifier" equality breaks, which is a paper cost with no
external consumers.

For patent-value and third-party-agreement classes the slug is omitted, because
there the title is itself the leak.

### 2.6 The slug is English, and the script refuses rather than guesses

Decided: filenames are English whatever language the document is written in.
`--slug` supplies one, and `new.py` and `record_run.py` refuse a non-English
title that does not carry it.

Rejected: transliteration, which is what was there. The first real interview
produced `D-0001.dnr-polosa-bez-effekta-po-δδg.md`, and seeing it settled the
question — `polosa-bez-effekta` is not Russian, not English, and greppable in
neither. It is the shape of a Russian phrase with none of its letters, so a
Russian speaker has to sound it out and an English speaker gets nothing. §2.4
already drew this line for frontmatter keys and enum values; the filename is
the same kind of surface and had been missed.

Rejected: dropping the slug for non-Latin titles, leaving `D-0001.dnr.md`. That
keeps `ls` honest and makes it useless, and the slug exists precisely so a
directory listing can be read.

Rejected: machine translation of the title, by any means. It fails silently and
at the worst moment — on the domain terms that carry the meaning.

The refusal is the interesting half. Every other guard in this skill refuses
rather than guesses — a dirty tree, an existing board, a missing brief — and
this is the same move: whoever wrote the title can render it in English, and no
mechanical rule can. The check is deliberately crude, any non-ASCII character
in the title, because a rule about which titles are "English enough" would need
maintaining and the cost of a false positive is typing four words.

A slug is three or four words naming the thing, not a translation of the
sentence: a Russian title naming the band within which a ΔΔG difference is
indistinguishable from noise is `no-effect-band`. That it reads better than a
translation would is a side effect of the same constraint that makes every
filename in every project greppable from any machine.

### 2.7 `run:` hashes no files

Decided 2026-09-27. `record_run.py` no longer takes `--input`, and `run:`
records the commit, `dirty` when it is true, the tools and the tracker's run ids. The version
of the data is the project's to pin.

The hashes were justified by one sentence, that git pins code and not a data
slice. In practice they did not pin anything. For files in git a hash repeats
the commit: in one real technote all eight entries were committed fixtures,
sixteen lines that added nothing. For data outside git a hash says the file
changed, not where it came from or how to get the old one back. And the
`check.py` warning on an empty list pushed people to fill it with whatever was
at hand, which is how the fixtures got there.

Versioning data is a separate tool's job. Under DVC the lock file is in git,
so `run.commit` pins the data along with the code and a hash in the log is
redundant. Without such a tool the hash restores nothing either. What remains
is a sentence in the protocol or the document saying where the data came from
and which version it was.

Not taken: reading `dvc.lock` into `run:`. It is worth doing once a project
actually uses DVC, and not before.

## 3. The files a project gets

### 3.1 The watershed: who owns a document's shape

Decided: value after closing. Rejected: "does it graduate to the shared base?"

The rejected criterion fails because only findings graduate, which would leave
hypotheses to the task tracker. The right question is whether a document has
value once its work is finished. A task is a receipt for work and has none;
everything else has.

Two concrete breakages if the tracker owned hypotheses:

- task-tracker's `archive.py` sweeps terminal items after 14 days. Correct for
  a task. A rejected hypothesis is a thesis chapter.
- Changing tracker takes the hypotheses with it. Tasks are cheap to lose.

This is also why there is no dependency in either direction between this skill
and any task tracker: another project may use Jira, GitHub issues, or nothing.

### 3.2 Conventions split by file owner, not by topic

Methodology comes from above and is extended locally. The mechanism that makes
updates possible at all: `conventions.md` is machine-owned and overwritten
whole; `conventions-local.md` is human-owned and never touched. Same pattern as
a generated index.

Local rules may add and tighten, never loosen, and may not touch the shape of a
finding, the only kind that must mean the same thing elsewhere.

Two rules came out of this and saved real text:

- A convention with a mechanism is not restated in prose. One line pointing at
  the script. Two sources of truth for one rule diverge.
- Half of "commit before running" is not a convention but a check in the
  wrapper. The other half, pinning the data, is the project's; §2.7 says why
  the log stopped trying.

### 3.3 What was cut from the source document

The source material was `binding-affinity/docs/project-organization.md`, 122
lines, cut down to what a fresh project needs on day one.

| Section | Verdict |
|---|---|
| lifecycle classification, 4 kinds | kept, reduced to three; "ephemeral" became one line |
| where a new thing goes, 8 items | cut to 5 |
| conversion rules, 9 moments | kept 7, reworded around the new kinds |
| six invariants and `check_layout.py` | dropped entirely: CI over accumulated content. On an empty project there is nothing to catch, and a check that is red on day one trains everyone to ignore CI |
| "a field with no reader goes stale in silence" | kept, one line |

### 3.4 vision.md is the question and the directions, and its history is git

Decided: `vision.md` carries the question, copied from the brief at
initialisation, and the project's directions, which start empty. Nothing else.

Removed: *Why it matters* and *What would end it*. Both failed the test that
decided §4.3: nothing reads them. No script parses either, no check touches
either, and once the entrance stopped asking for them (§4.3) they were template
text that would sit unwritten forever. The applied purpose now lives inside the
question, where the one real brief had put it unprompted. A project's end is
what a deadline and a supervisor are for, and this skill was pretending to hold
it without any mechanism that could.

Removed later: *Out of scope*, from the brief template, the interview and
`vision.md`. At the start of a research project nobody knows where its
boundaries are, and asking "is anything already ruled out?" got either nothing
or exclusions made up to answer the question. What the section could honestly
hold goes to two places that already existed. An exclusion set by the
assignment, such as a ban on licensed software, is a constraint and sits with
the brief's constraints. An exclusion found during the work is a decision,
which is dated, can be named in `rests_on`, and is checked. `init.py` is back
to copying one section.

Added: *Directions*. In the source project nine directions appeared during the
work, each in a file of its own, linked to hypotheses many to many, with states
such as "exhausted" and "premise answered negatively" kept in prose and in no
field. One of them, on relative binding free energy, was created a month after
the vision had listed it as a priority, and in that month its hypotheses had
spread over four other directions. The level is real, and it appears late, so
the template gives it a place and asks nothing about it on day one. A
direction is a subheading with its state in words; one that is set aside stays,
with the reason, which is the job the old out-of-scope section of `vision.md`
was actually doing. The named source for the level is Goal-Question-Metric +
Strategies (Basili et al., *Computer* 43(4), 2010).

Rejected for now: a `direction` kind with an identifier, a status and a
`directions` field on hypotheses. A field that nothing reads goes stale
unnoticed, and a project on its first day has no hypotheses to group. The
trigger for revisiting is the first direction that needs a state something
could query, or a summary of its own when it closes.

Rejected: any structure for tracking how the vision changes — a changelog
section, a `scope_set` date in the frontmatter mirroring `criterion_set`. Most
changes to it are ordinary and git already records them with dates and commits;
restating that inside the file is precisely what "a convention with a mechanism
gets one line pointing at the mechanism" forbids. The `scope_set` date fails
for a harder reason: nothing cites `vision.md`, so there is no second date to
compare it against and no check could be written.

The one dangerous change, narrowing the question after the first numbers
exist, is the disease decisions already cure. It is
recorded as a decision, which is dated, can be named in `rests_on`, and is
therefore checkable. One line in the template points at that, and no new
machinery was added for it.

### 3.5 Development conventions accrete; they do not arrive

`conventions-local.md` accrues over a project's life. Its table of tool
versions is empty on day one by construction — a version cannot be recorded
before the tool is installed — and §1.6 already noted that the traps around an
installation are learned the day it happens. A code layout is the same: it
needs code before it can be described.

The cut is *when the fact becomes knowable*. Some of it is external and arrives
at the entrance: the language, the package manager, a lab standard, a licence.
The rest cannot arrive there at any price. So the file gets two entry points —
one step in initialisation, one standing rule in `SKILL.md` — and the same fact
uses whichever applies. *We use uv* may be settled on day one or at the first
script, and a design that picks one moment loses the other.

None of it becomes a sixth interview topic. The entrance test from §4.5's
neighbours is whether a script reads the answer, and nothing parses this file.
What the greenfield case earns instead is one question inside the existing
`conventions-local.md` step, justified differently: the next thing that happens
after initialisation is usually code, and with no answer the agent writes it to
its own habits and the project inherits them.

Rejected: a section in `brief.md`. The brief is the assignment, owned by
whoever set the project — a supervisor, a grant, an email — and §4.4 forbids
rewriting one they brought. Stack preferences belong to the researcher, and
would have to be retyped for every project.

Rejected: a user-level `CLAUDE.md` as the channel. It is invisible from the
project. The whole point of the file is that someone on another machine stands
the project up without asking, and a rule reachable only through the author's
dotfiles fails exactly at handover. A global file remains useful as somewhere
to draft from, so the rule is that its text is **copied in**, never referenced.

### 3.6 Presets: read-only drafts the agent proposes from

Accepted, after one wrong answer: `presets/`, drafts of those sections shipped
with the skill. The first answer was to reject them wholesale, on the grounds
that recommending a package manager puts ecosystem advice in a domain-neutral
skill and that `install.sh` would overwrite whatever the user edited. Both
objections are about a *mutable* preset that the project keeps depending on. A
read-only draft is a different object: it is proposed at initialisation,
corrected, copied into `conventions-local.md`, and never consulted again.
`references/initialisation.md` is already exactly this — skill-owned content,
read by the agent and not the user, rightly overwritten on reinstall.

It closes the weak spot in the greenfield path above. An open question put to
someone with no view on packaging gets *not decided yet*, and the standing rule
then waits for a script written to the agent's habits. A draft they can react
to gets an answer.

Presets carry the date they were last checked, since they are claims about an
ecosystem rather than about this method. A file about libraries dates faster
than one about a package manager.

Domain material was ruled out of `presets/` at first, on the same argument that
keeps it out of `conventions.md`: a skill that serves every project cannot
recommend libraries for one field. The user's correction was that `presets/`
*is* the customisation layer, and the argument only applies to what every
project reads. `structural-bio.md` followed.

A second attempt to split the directory into convention drafts and domain
guides was also wrong, and the user caught it: no preset holds a convention.
Conventions live in the project's `conventions-local.md`, shaped by
`templates/`. Every preset is read-only reference the agent consults before
proposing, and they differ only in subject — an environment and a layout, or a
field's libraries. What reaches the project is whatever the user agreed to,
written into the project's own files, with no reference pointing back here.

Conventions still travel between one researcher's projects with no machinery
beyond the previous project's `conventions-local.md`, which is committed and
can be pointed at.

Reversed: `presets/` was reachable only from `references/initialisation.md`, on
the *stated once* principle. The second project to need it was already
initialised, so nothing led the agent to that file, and it proposed a layout
with neither the presets nor a question. The standing rule in `SKILL.md` fires
exactly at that moment and now points at the directory itself. Stating a
pointer once is right; stating it in a file the reader has no reason to open is
not stating it.

The first project to use one showed where a preset goes thin. Its conda branch
was a single sentence with no commands, against three commands on the uv side,
and the agent filled the gap by inventing `conda env update` without `--prune`,
which adds packages but never removes them. It also recorded `conda-lock.yml`
in `conventions-local.md` before generating the file. Both are now in
`conda.md`, with the order stated: build, verify, lock, then record. A branch
that says *keep the rest* and stops is an instruction to improvise.

That project also raised the case no file covered: several environments in one
project, because a package will not co-solve or is large and separately
licensed. The rule is that an environment boundary follows a process boundary —
imported code shares an environment, a tool called through a subprocess does
not have to — and that each environment gets its own manifest and lockfile,
with every entry point naming the one it runs in. A run crossing two
environments passes `--tool` for both, which `record_run.py` already accepts.

Rejected: a `check.py` warning when code exists while those sections are still
template text. It was built and reverted the same hour. The prototype flagged
all eight sections, which is what a heuristic over a schemaless file does;
narrowing it to two made it quieter but not principled, and §2.6's rule is that
this skill refuses rather than adds. Nothing checks this file, and the honest
statement of that is in `SKILL.md` rather than a check that approximates one.

### 3.7 One index file, once Claude Code stopped needing two

Decided: nothing at the project root is written but `AGENTS.md`. Since §3.8 the
agent writes it, not `init.py`.

Until 2026-09-18 it also wrote a `CLAUDE.md` holding the single line
`@AGENTS.md`, because Claude Code read `CLAUDE.md` and ignored `AGENTS.md`
while every other agent did the reverse. Claude Code 2.1.277 reads `AGENTS.md`
when no `CLAUDE.md` is present, and the shim stopped paying for itself the day
that shipped.

Rejected: keeping it for Bedrock, Vertex and Foundry, which the changelog names
as not yet carrying the feature, and for Claude Code below 2.1.277. The board's
owner does not deploy on any of them, and a file kept against a platform nobody
here uses is the kind of thing that outlives its reason by years. Anyone who
needs it writes two lines.

The general form: two files holding one instruction is a workaround for a
reader, not a design. When the reader is fixed the workaround goes, and the
check that it is really gone is that nothing has to explain which of the two is
authoritative.

### 3.8 An upgrade rewrites the skill's files, and AGENTS.md is the project's

Decided 2026-09-27. `upgrade.py` replaces `conventions.md` whole when its
`template_version` is older than the skill's, and `check.py` warns when it is
behind. The one other thing it rewrites is `run.inputs` (§2.7), which it
removes line by line. Nothing else in the project is rewritten.

The split follows §3.1. `conventions.md` is copied from the template verbatim,
so overwriting it loses nothing. `AGENTS.md` used to hold the map of the board
as well, which made it half the skill's and half the project's, and every way
of upgrading such a file was a merge. The map moved into `conventions.md`.
What stays is three links that change only when a new file has to be read
before every task. `init.py` does not write them: the agent adds them at
initialisation, because it can see what a script cannot, whether the project's
agents read `AGENTS.md` or `CLAUDE.md` and whether the file already says some
of it. After that the file is the project's.

A file with uncommitted changes is refused, so `git diff` is the whole record
of an upgrade.

Rejected: markers around the skill's part of `AGENTS.md`, replaced on upgrade.
Agents add rows to that table, and the next upgrade would erase them.

Rejected: a three-way merge against a copy of the template stored in the
project. It works, and it is a second file kept only to repair the mixed
ownership that moving the map removed.

Migrating documents is the exception. New fields stay optional, so an old
document remains valid and nothing has to be rewritten. A removed field is also
valid and nothing checks for it, but it is noise in every block that still
carries it, so `upgrade.py` removes it. The `run:` block is the wrapper's, not the author's,
which is why rewriting it is the skill's business.

---

## 4. Setting a project up

### 4.1 The brief, and why it formalises almost nothing

Decided: a project starts from a brief with one required section, read as prose
and never parsed.

The name is PRINCE2's Project Brief, a management product created by *Starting
up a Project* and consumed by *Initiating a Project*. The mapping holds all the
way through: brief → initialisation → project documentation, and PRINCE2's own
brief carries the project definition, its constraints and its
*project approach*, which is where "these libraries, this tool, this licence"
belongs.

Rejected: Terms of Reference, established but with no defined consuming
process, so it names a document that flows nowhere; Project Charter (PMBOK), an
authorisation instrument whose sections are empty for a student project;
Statement of Work, contractual and deliverables-shaped; answers file (copier)
and context (cookiecutter), honest names for a generator's input but names of
machine files, whereas a brief is read by a person first; and *kickstart*, an
invented word where the field has its own.

Reversed: a first design gave the brief eight sections and a table mapping each
one to the file initialisation would generate from it. That presumed the brief
knows enough about the task to derive anything. It does not: often the only
thing that exists at the start is the research question. So the brief has one
required section, the frontmatter is two optional keys, and a brief with no
frontmatter at all still works.

A section the brief omits is not a gap to be filled at initialisation. The
order of work, the limits of applicability, the traps of the method are the
research itself, and for a student project they are most of the point.
Rejected: having initialisation interview its way to the missing sections,
which does the researcher's work for them, without data, and worse. §4.2 draws
the line this leaves: you may ask the person who set the project for an answer
only they have, and you may not supply one for them.

The same section therefore means two different things by its presence: written,
it is given; absent, it is assigned.

The hypothesis section is optional, and must visibly be so. A required field
gets filled: a search project would acquire a hypothesis written to occupy the
slot, and everything later found would confirm it, which is the HARKing
mechanism of §1.1 moved earlier and made harder to see. The test for whether a
project has one: can you name, now, an observable result after which you would
call the claim wrong? "I would narrow it rather than drop it" means a
direction. Of the two projects this was drawn from, one has a hypothesis and
one does not.

Refutation and invalidation were split. "What would refute the hypothesis" is a
result; "what makes any result worthless", a metric that a constant answer
wins, a descriptor that does not beat the size of what was deleted, a threshold
chosen after the fact, is a trap of the method. They were one section and
produced confusion; the first now lives inside the hypothesis section, the
second stands alone and exists in every project.

The seam with `vision.md` runs along ownership. Every answer in the brief
belongs to whoever set the project, whoever typed it; `vision.md` belongs to
the project and is living. They overlap on purpose, and a month in they
diverge, which is what a supervisor needs to be able to see. PRINCE2 keeps the
same pair for the same reason.

When a fuller statement exists elsewhere, the project receives a cut-down
derivative of it. What gets cut has a criterion: whatever the project is
supposed to produce. What survives the cut regardless is any pre-commitment
whose absence is unrecoverable. A threshold that must be fixed before the first
computation cannot be rediscovered later, because by then it can only be
fitted.

### 4.2 Initialisation is a conversation, and the script is its middle

Decided: `references/initialisation.md` carries the procedure, `SKILL.md` gets
a paragraph pointing at it, and `init.py` stays exactly as it is.

The gap this closes: everything written before it described what `init.py`
does, so the whole user-facing scenario read as *write a brief, then run a
script*. That is the wrong shape twice over. Nobody starting a project has a
brief, and telling them to write one from a template first is the highest
threshold the skill could have put at its own entrance. And the script's six
files are not the valuable part of day one — the question and what turns on its
answer, the condition under which the work stops, and what has to be frozen
before the first computation are, and none of them can be read off a
repository.

The line against §4.1: interviewing the person who sets the project is not
filling in what the brief leaves to whoever takes it on. Their answers are the
input either way; the only question was whether they arrive by the person
editing a template alone or by being asked. Asked is strictly better, because a
question that has the same consequence whichever way it resolves is visible in
conversation and invisible in a form. Pushing back there, once, is the one
place initialisation is allowed to have an opinion.

The forbidden list is therefore explicit, and it is the load-bearing half of
the file: no hypothesis nobody committed to, no refutation criterion written on
their behalf, no section filled from the repository or from what similar
projects do, no decision dated before the conversation that produced it, no
rewriting a brief they brought.

A separate file rather than a `SKILL.md` section: initialisation happens once
per project, and `SKILL.md` is in context for every session of every project
where it never happens again.

Rejected: a `/kt-init` slash command. A skill directory is already invokable as
`/<name>`, so the command would have bought nothing and cost the packaging —
slash commands of one's own need a plugin, with a manifest and a marketplace,
where an install script and `~/.claude/skills/` do. `/init` specifically is a
Claude Code built-in and would have collided. The trigger is therefore the
skill's own description plus `/research-log`, and a person asking in their
own words is the path the design expects.

`init.py` gained nothing from this. Its brief requirement was the guard that
catches an agent started in the wrong directory, and under the conversation it
still is: the brief now exists because the interview produced it, and a script
run with no brief in sight still means something went wrong upstream.

**Which agents this works in.** `~/.claude/skills/` turned out not to be a
Claude Code detail: opencode, Cursor and Claude Code all scan it, and Codex and
Gemini scan `~/.agents/skills/`, which one symlink covers. Run end to end on
opencode 1.18.31 on 2026-09-18, on a local 27B model, with nothing installed
but `install.sh`: the skill triggered on a plain Russian sentence, read
`references/initialisation.md` unprompted, did the phase-0 checks, interviewed,
held the draft brief for approval, ran `init.py`, minted the decision, and
closed with `check.py` and a commit. It also volunteered which sentences were
its own rather than the researcher's, twice, unprompted — which is the
forbidden list doing its work.

That a small local model follows the file is the evidence that matters. The
protocol is procedure, and it does not need a large model to hold.

The portability is not really the skill's doing. After initialisation the board
is self-describing: `AGENTS.md` and `conventions.md` are committed to the
project, so an agent reads the rules from the repository and the skill is
needed only to set a project up and to run the scripts. The design decision
that bought this was moving the index to the project root, taken on other
grounds entirely.

### 4.3 The entrance asks one question, and the purpose is not one of them

Reversed, on the first real interview: the *Question* section asked for the
question and then, separately, what changes if the answer is yes and what
changes if it is no, with "if nothing changes either way, the question is the
wrong one". §4.2 had made that the one place the interview was told to push
back. Both are gone, and so is the replacement — see the second reversal below.
The entrance now asks one thing: *"What does this project need to find out —
the way you'd explain it to someone outside your field?"*

What the reversal is answering: the split was defending against a null
question, one whose answer changes nothing. That is rare, and it is not a
danger anyone walks into at the entrance — a person setting up a project has a
reason, usually a supervisor with one. Against that rarity the cost is paid
every time: an interrogation where a question belongs, and a shape that reads
as a form to complete rather than a thing to say.

The one part that was load-bearing survives elsewhere and always did. A
negative result being worth having is the substance of *What would end it*,
which already says the work stops when the answer arrives or when it is shown
to be unreachable, and which is asked in phase 3 while nobody has a stake in
the outcome. Asking it twice bought nothing.

The evidence was the brief a person had already written. Its question section
gives the applied purpose in a sentence and lets the two outcomes fall out of
it — "if a descriptor is found, selection stops being brute force; if none
exists, the direction closes". That is the same information, arrived at by
saying what the project is for, and nobody had to be asked twice to produce it.

The general lesson is about where a rule is enforced. A methodological point
does not need a checkpoint at every door it is relevant to. Put it at the one
door where acting on it is cheap and the answer is not yet motivated.

**Reversed again, one round later: the purpose is not asked at all.** The
replacement for the dichotomy was *who needs the answer and what they will do
with it*, and it was worse in a new way. It invents a stakeholder where there
is none: a student answers "my supervisor" and the answer is empty. Worse, it
was written as a second obligatory half, so the agent chased it — *"The second
half of the required section is still missing: one or two sentences in your own
words"* — and chased it for something the person had already supplied inside
their first answer.

The test that settled it is what consumes the field. What must be frozen before
the first computation becomes dated decisions and `check.py` enforces them. A
hypothesis becomes `criterion_set` and `check.py` enforces that. The purpose is
read by nothing — no script parses it, no check touches it. It earns a section
in `vision.md` for the researcher to fill when they have something to put
there, and it does not earn a turn of a student's attention at the entrance,
where attention is scarcest and the whole board is still ahead of them.

It arrives anyway. People say what a thing is for while saying what it is, and
the brief a person had already written proves it: its question paragraph
carries "selection stops being brute force" without anyone asking. Taking what
comes beats demanding it.

### 4.4 The agent may draft; only the date is untouchable

Reversed, on the user's instruction, and the reversal is a correction rather
than a relaxation. §4.2 stated the rule as *never answer for them*, and every
document here repeated it: no hypothesis nobody committed to, no refutation
criterion written on their behalf. What came out of that was an agent
delivering a sermon — refusing to draft a criterion and a threshold, and
explaining the methodology behind the refusal at length — when the researcher
had asked it to write them.

The rule conflated two things that are not the same. A pre-commitment is
binding because of **when** it was recorded; authorship never entered the
mechanism. A threshold an agent proposed and the researcher accepted before any
numbers existed is a real pre-commitment, and `check.py` holds it to exactly
the rule it holds a hand-written one to. What actually breaks the mechanism is
a threshold chosen once the results are visible, or a criterion recorded today
and dated last month.

So the rule is now *they decide, you may draft*: write anything asked for, say
which words are yours, and put nothing on the board they have not agreed to.
The one line that survives untouched at any request is the dating of a
decision, because that is the whole mechanism rather than a preference about
who holds the pen.

The failure mode is named explicitly in the file, because it is what the old
rule produced: refusing a request and explaining why is the defect, not the
discipline.

### 4.5 A question, not a description of a question

Found three times before it was named. Every round produced the same shape: the
agent read out the *specification* of a question instead of asking one.
"REQUIRED. What has to be found out (one paragraph, no internal vocabulary) AND
who needs the answer... That is the question plus the why, both at once." "What
the project does not answer — where is its boundary? (for example: one protein
family only, point mutations only, no kinetics)." A label, the question
restated once or twice, a note on the form of the answer, and a menu of three
example answers.

The cause was that the topics were written as descriptions — *what has to be
found out, one paragraph, no project-internal vocabulary* — and a description
of a question is what a model says when asked to ask one. Fixing them one at a
time worked and did not generalise, so the rule is now stated once, up front,
as *How to ask*: a question is one sentence a person could be asked out loud,
and the section names, the requiredness and the form of the answer are how this
file is organised, not what is said. Each topic then carries an example in the
register rather than a description of itself.

The menu of examples got its own clause, because it is the tell that looks
helpful. Three supplied before the person has tried tell them the shape of
reply expected, and that is what comes back. One example, built from what they
have already said, offered only after a question failed to land.

## Implementation lessons

Eight bugs found while building, kept because each is a trap the next change
can walk back into.

- The slug regex was `[^\w\s-]` with `re.UNICODE`, which keeps every Unicode
  word character. Only Cyrillic was transliterated, so a Greek or CJK title
  survived into the filename: a Russian decision title ending in ΔΔG had its
  Cyrillic transliterated and kept the Greek, becoming `...-po-δδg.md`, which
  git escapes and a shell has to quote. Found by
  the first real interview, not by any test, because every test title was
  Latin or Cyrillic. `\w` never means ASCII.

  Fixing the regex exposed the larger mistake underneath, which is §2.6.

- `init.py` resolved the board language as `--lang`, then the brief's
  frontmatter, then `load_config().get("lang")`, then detection from the
  brief's text. The third of those never fails: `load_config` returns
  `DEFAULTS` when no config file exists, so `lang: en` came back for a project
  that had no board yet and detection was unreachable. A Russian brief got an
  English board, and only in the ordinary case — a brief composed in the
  interview carries no frontmatter at all, which is why the rehearsals on
  `brief-mutation-effect.md` never showed it. A default returned by value is
  not the same as a setting, and a fallback chain has to distinguish them.

- `init.py` matches template prose literally: the brief's optional-section
  headings it reports as missing.
  Rewording a template silently turns those substitutions into no-ops, and no
  check catches it. Rewording `templates/<lang>/` means grepping `init.py` for
  the strings it carries in that language.

- Round-tripping a template through parse-then-dump destroys its comments. The
  templates teach through comments: allowed `status` values, the rule that
  `experiments` stays empty in `idea`, optional fields shown commented out. A
  generated document is therefore the template with a few values substituted by
  line, byte-identical otherwise.
- The parser did not strip trailing comments, so `experiments: []  # ...`
  parsed as a string and the checker iterated it character by character,
  reporting 47 unresolved citations for one bad line. Fixed at the parser, plus
  a type guard in the checker so the next such bug reports one error rather
  than forty.
- The board lock file dirtied the working tree, and `record_run.py` refuses to
  run on a dirty tree, so taking the lock blocked the tool that takes it. The
  lock lives in the temp directory, outside the repository.
- Dirty means dirty code, not dirty notes. Creating a hypothesis dirties the
  tree; if that blocked a run recording, `--allow-dirty` would be habitual
  within a week and the check would be over. The board directory is excluded
  from the dirty scan.
- Crockford's check symbol is the value modulo 37, and five of the 37 values
  map to `*~$=U`. The first finding minted in a real project was
  `DHMWSN0CD09VJ*`, and a `*` in a filename is expanded by the shell as a
  glob. `mint_finding_id` now redraws until the check symbol is a letter or a
  digit, which loses about 0.2 bits of the 65 and keeps every existing id
  valid. The validator still accepts all 37: an id already minted is never
  renamed.

## Designed but untested

Three mechanisms have no shared knowledge base to run against yet, so they are
arguments rather than verified behaviour: graduation of a finding, the export
check at the project→base boundary, and the blast-radius query over `origin`.
Treat their details as provisional until a base exists.
