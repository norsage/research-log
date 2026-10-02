---
name: research-log
description: Markdown record kept beside a project's code: hypotheses, experiments, technotes, findings, protocols and decisions with stable identifiers. Use when a research or analysis project is being set up, started, or given a research log, in whatever words the user reaches for; whenever a project records what was measured, what it means, how a procedure is run, or why a choice was frozen; when the user asks where a result, a benchmark, a claim, a literature review or a runbook should go; or when the project contains docs/{hypotheses,experiments,technotes,findings,protocols,decisions}/ with frontmatter'd markdown. Independent of any task tracker.
---

# Research log

A project's work lives in a task tracker. What the work established lives here,
written so that it can later leave the project. This skill requires no
particular tracker and works the same with task-tracker, Jira, GitHub issues or
nothing at all.

```
AGENTS.md                     # the project's; points at docs/
docs/
├── .research-log.md     # board settings (committed)
├── conventions.md            # shipped by this skill. Machine-owned, never hand-edited
├── conventions-local.md      # this project's additions. Never touched by the skill
├── vision.md                 # why this project exists
├── hypotheses/
│   ├── H-NNNN.xxx-slug.md
│   └── _index.md             # generated
├── experiments/
│   └── E-NNNN.xxx-slug.md
├── technotes/
│   └── T-NNNN.xxx-slug.md
├── findings/
│   └── <OPAQUE-ID>-slug.md
├── protocols/
│   ├── P-NNNN.xxx-slug.md
│   └── _index.md             # generated
└── decisions/
    ├── D-NNNN.xxx-slug.md
    └── _index.md             # generated
```

`AGENTS.md` is the one index, at the project root, where Claude Code and other
agents look for it on startup. It belongs to the project. At initialisation
the agent adds the section in `templates/<lang>/agents-section.md` to it (or to
`CLAUDE.md`, if that is what the project uses), and the skill never touches it
again. The map of the board lives in `conventions.md`, which the skill owns.
Claude-specific instructions go in `AGENTS.md`, below everything else. Never
create a second copy under another name.

## Starting a project

Asked to set a project up, start a board, or put a project on
research-log: read [`references/initialisation.md`](references/initialisation.md)
and follow it. Do not go straight to `init.py`.

Initialisation is a conversation that ends in a script run. The script writes
five files and copies one section; the rest of what a project needs on day one
— the question, what the data is, what must be frozen before the first
computation — exists only in the head of the person starting it. It needs a
brief, and composing that brief with them is the first half of the job.

The rule that shapes all of it: they decide, you may draft. Write whatever they
ask you to write, say which words are yours, and put nothing on the board they
have not agreed to. A pre-commitment binds by the date it carries; authorship
does not enter into it.

## The six kinds

| Kind | Written | Mutable | Leaves the project |
|---|---|---|---|
| hypothesis | before the evidence | yes | no |
| experiment | after a run over the project's subject | never | no |
| technote | after a run over the project's tooling | never | no |
| finding | once the claim holds | yes | yes, the only one |
| protocol | when a procedure will be repeated | yes | no |
| decision | when a choice is frozen | no; superseded instead | no |

An experiment and a technote are the same record over a run. They differ in
what the run examined. An experiment's result says something about the subject
of the research: the model, the method, the data. A technote's result says
whether the project's tools can be trusted: parsing speed, agreement with
another library, whether features are read correctly. The test: would a
different number change an answer to the question in `vision.md`, or only an
opinion of a tool? The project's main computation, such as training and
evaluating a model, is always an experiment. When the test is unclear, write an
experiment. If the same doubt comes back, ask the user once and record the
answer in `conventions-local.md` as a class of runs.

A hypothesis states a claim before the evidence and pre-commits to what would
refute it; that pre-commitment is what makes the later test confirmatory. A
finding states a claim once it holds and describes where it holds. Same shape,
opposite times.

A finding carries `class`, which says what admits its claim:

| `class` | Admitted by | Required |
|---|---|---|
| `empirical` | runs in this project | at least one in `origin.experiments` or `origin.technotes` |
| `formal` | a proof | the premises, and where the proof is written out |
| `review` | a search of the literature | what was searched, where, on which date |
| `analytical` | an argument over known properties | the properties, and the range it holds over |

Only `empirical` is held to `origin` by `check.py`. The rest are held to the
prose their template asks for. A benchmark run in this project is `empirical`,
whether an experiment or a technote records it; a comparison argued from
complexity is `analytical`. The class follows what established the claim,
never its subject.

## Frontmatter

Shared by every kind: `id`, `title`, `type`, `audience`, `created`/`date`.

| Kind | Adds |
|---|---|
| hypothesis | `status` (`idea` \| `active` \| `hold` \| `resolved` \| `recycled`), `criterion_set`, `experiments`, optional `finding`, `successor` |
| experiment | `date` (the earliest run's date), `run:` with `tracker`, `ids`, `commit`, `dirty` (only when `true`), `tools`, `rebased` (only after a rewrite); optional `rests_on`, `under`, `motivated_by`, `corrects` |
| technote | as experiment, without `rests_on` |
| finding | `status`, `class`, `origin:` with `project`, `experiments`, `technotes`, `commit`, `rebased` (only after a rewrite); optional `corrects` |
| protocol | `status` (`draft` \| `stable` \| `deprecated`) |
| decision | `status` (`accepted` \| `superseded`), optional `superseded_by`, `based_on` |

The templates are the source of truth for the rest. Generate from them; never
write a document's frontmatter from this table alone.

## Relations

```
vision
  │
  ├──► hypothesis ◄──resolves into── finding ═══► shared knowledge base
  │        │                            │
  │        │ cites (resolvable)         │ origin (data, not a link)
  │        └────► experiment ◄──────────┘
  │                │       │ rests_on
  │        under   │       ▼
  │                │   decision, dated on or before the run
  │                ▼
  │            protocol, created on or before the run
  │
  ╎ motivated_by: free-form string, never parsed
  ▼
task tracker (any) · run tracker (mlflow / aim / none)
```

| Relation | Cardinality | Required |
|---|---|---|
| hypothesis → experiment | M:M | no, from either side |
| finding → experiment, technote | 1:M via `origin` | at least one run when `class: empirical` |
| finding → hypothesis | 0:1 | no |
| experiment → decision | M:M via `rests_on` | no |
| experiment → protocol | M:M via `under` | no |
| experiment → run | 1:1 or 1:M | yes |
| experiment → task | free-form string | no |
| decision → technote, experiment | M:M via `based_on` | no |

Three of those optionalities are deliberate:

- An experiment with no hypothesis: a baseline, an audit of the data, a
  characterisation, a control, a feasibility probe of a method.
- A hypothesis with no experiment: one not yet tested.
- An experiment with no task: requiring a task would drop from the log every
  experiment that had none.

## When to do what

### A result came out of a run

Write an experiment. One document per comparison, however many runs it took.
The wrapper fills the `run:` block; you write the title and the four sections.
Its conclusions are bounded to that execution.

### A run checked the tooling

Write a technote with `record_run.py --kind technote`: a benchmark of the
project's code, a comparison against another library, a check that files or
features are read correctly. It carries the same `run:` block as an experiment.

If a choice was made on it, also write a decision naming it in `based_on`.
Experiments computed with the chosen tool then rest on that decision, so a
technote later found wrong leads through the decision to every run it touched.

A smoke test or a debugging session, whose numbers nobody will compare, stays
in the task.

### A claim the project established holds beyond one run

Write a finding, and set `class` to what admits it. The bar: it changes a future
decision, and it is no longer about one execution. Carry what it rests on inside
it, because a finding that only points outward cannot be read once it travels.

A theorem proved here, a reading of what the field has and has not done, a
comparison argued from the methods' properties — all findings, of the classes
above. Reach for the class by asking what would have to be wrong for the claim
to fall: a run, a proof, a search, or an argument.

### Someone commits to testing a claim

Create a hypothesis at `status: idea` with the context, then move it to
`active`. Moving it requires *What would refute it* and `criterion_set`.

A hypothesis in `idea` may not list experiments: an idea with runs attached is
hypothesising after the results are known.

### You work out how something installs, runs or is assembled

Write a protocol if it will be needed again: a tool's installation with its
traps, rebuilding the metrics, assembling the report, the measurement a run
follows.

An experiment names in `under` every protocol its run followed, and `check.py`
holds each to a creation date on or before the run. `conventions-local.md` holds
what is true about the project; a protocol holds how to do it.

### The stack, the layout or a tool becomes real

Write it to `conventions-local.md` before the code that assumes it. The first
script settles the layout, installing a tool settles a version, a linter
settles what blocks a commit. Each is a line or two in the section that
already holds it.

Read [`presets/`](presets/) before proposing any of it, here as much as at
initialisation: a layout, a package manager, a library for the field.
Offer what you find there, take their correction, and write the result here.

Add to the file as the project learns it. Most of it cannot be written on day
one: a tool's one working installation route is learned the day it is
installed, and a layout needs code before it can be described.

Write it so someone on another machine can reproduce the project without
asking. Copy in anything taken from a user-level `CLAUDE.md`, a personal skill
or another repository; those stay behind when the project moves.

`check.py` ignores this file, which has no schema. `AGENTS.md` puts it in
front of every task, and that is all that keeps it current.

### A definition or a threshold is frozen

Write a decision. Mutation classes, the data slice, the cutoff, which tool
computes what. Left undecided, these get re-decided silently and numbers stop
being comparable.

An experiment computed under one names it in `rests_on`, which is what holds
the decision to a date on or before the run.

### A hypothesis resolves

Write a finding from it and set `status: resolved`, `finding: <id>`. The
hypothesis stays as the record of the question and the dead ends; the finding
carries the claim. Refutation resolves the same way, with a negative claim.

### The question turns out to be the wrong question

`status: recycled`, `successor: <id>`.

## Behavioural rules

- Every experiment a hypothesis cites must be dated after its `criterion_set`.
  Editing the refutation criterion later means raising that date.
- Every decision an experiment rests on must be dated on or before it. A
  threshold frozen after the numbers exist can be moved until they look better.
- Every protocol an experiment ran `under` must have been created on or before
  it. A procedure written up after the result is not what the run followed.
- `date` on an experiment is the earliest run's date, not the writing date. The
  wrapper writes it.
- An experiment or a technote is never edited. A mistake found later is a new
  document of the same kind carrying `corrects: <id>`, which also drives the
  blast-radius walk.
- A number someone will compare belongs in an experiment or a technote, not in
  a task. The task keeps a reference.
- No hypothesis or experiment cites a technote: what tests a hypothesis is an
  experiment. A finding may, in `origin.technotes`, when a technical detail
  matters in its own right.
- Citations are identifiers, never titles or paths. A slug is advisory: rewrite
  it freely. It is always English, even when the document is not.
- Citation flows one way, project to shared base. A finding that graduates
  spells out its conditions in prose, because a local identifier does not
  resolve outside the project. The export check catches this at the boundary.
- A convention with a mechanism gets one line pointing at the mechanism, never
  a restatement of it.
- Local conventions may add and tighten, never loosen, and may not touch the
  shape of a finding.

## Identifiers

Hypothesis, experiment, technote, decision and protocol use `<P>-NNNN.xxx`: a
type prefix, a sequential number, and a random three-character suffix so two
branches minting `0042` at once do not collide. `H-0003.k3f`, `E-0012.h7q`,
`T-0002.p4r`, `D-0003.m4k`, `P-0001.k3f`.

Findings use the shared base's own form: 13 characters of Crockford Base32 with
a check symbol, which omits I, L, O and U and is case-insensitive, so it
transcribes by hand without error. Minting it in that form from the start makes
graduation a `git mv` with no citation broken.

Filenames are `<ID>-<slug>.md`. Citations carry the identifier alone.

**The slug is always English, whatever language the document is written in.**
An English title slugifies itself; anything else needs `--slug` with three or
four English words, and `new.py` and `record_run.py` refuse without it rather
than guess. A slug names the thing in three or four words; it is not a
translation of the title and never a transliteration of one.

Never hand-assign an identifier and never reuse one.

## Language

Templates ship in `templates/en/` and `templates/ru/`. The project picks one at
initialisation.

Prose is translated; keys and enum values are not. `status: active`,
`class: review`, `criterion_set`, `origin`, `under` are a wire format read by the checks
and by the export. Section headings and guidance differ between the two
directories; everything a machine reads is identical.

This skill's own instructions stay in English, because a translated second copy
would drift from this one.

## Operations

Seven scripts in `scripts/`, covering the operations a person must not do by
hand: setting a board up, upgrading it, allocating an identifier, writing a
`run:` block, following it across a rewrite of history, and the four checks
that are methodological rather than clerical.

```
init.py [--brief PATH] [--lang ru] [--project NAME] [--yes]
new.py <kind> "<title>" [--slug WORDS] [--status S] [--class C] [--rests-on ID ...] [--under ID ...] [--motivated-by REF] [--lang ru]
record_run.py "<title>" [--kind technote] --tool NAME=VERSION --run-id ID [--slug WORDS] [--rests-on ID ...] [--under ID ...] [--date D] [--commit SHA]
index.py [--check]
check.py
rebase_runs.py [ID ... | --all] [--same --paths PATH ... | --same --basis TEXT | --keep] [--to SHA]
rebase_runs.py --check | --install-hooks
upgrade.py [--check]
```

`init.py` sets up a board in the current directory, like `git init`, and never
asks where the project is. It needs a brief (`templates/{en,ru}/brief.md`),
read as prose: no brief means it stops, which is also what catches an agent
started in the wrong directory. It writes the five files, refuses to run over
an existing board, and asks once before setting up outside a git repository.
It writes nothing at the project root. It copies the brief's question into
`vision.md`, whose other section, the project's directions, starts empty, and
names on the way out the sections the brief does not carry. It is the middle of the
procedure in [`references/initialisation.md`](references/initialisation.md),
not the whole of it.

`new.py` allocates under a board lock, so two agents on one checkout cannot
mint the same number. The lock is `fcntl.flock` in the temp directory, held for
milliseconds, which makes it a local-checkout mechanism: over NFS or sshfs it
is unreliable, and two writers on a network mount can collide. For an
experiment or a technote use `record_run.py`: it reads the commit and refuses a
dirty tree. It hashes no files: the version of the data is the project's to
pin. Under DVC or a similar tool the lock file is in git, so `run.commit` pins
the data too; without one, the source and version of the data go in the
protocol or in the document's text. It runs after the run, so a long run needs
the order kept by hand. First a trial run on a small slice, on any tree, with
nothing recorded. Then commit everything the run uses: code, config, the
measuring script. Unrelated edits may stay uncommitted. Note the SHA. Then the
full run, then `record_run.py`, with `--commit <SHA>` if HEAD has moved since
or unrelated edits remain. A commit made after the full run is one the run never
saw. `check.py` is the gate before a commit.

`run.commit`, and `origin.commit` of a finding minted here, must stay on HEAD
or be held by the record's tag (`research-log/<id>`), and `check.py`
refuses a record where it is neither. A rebase, a squash or an amend replaces
the commit, which is ordinary when several people work against one main, and
`rebase_runs.py` follows it. It finds the replacement through the post-rewrite
hook, or by patch when the server did the rebase, and shows what differs.
`--same --paths <what the run used>` moves the commit when those paths did not
change, and records the old SHA and the reason in `rebased` beside it;
`--basis` states the reason in words where no list of paths says it. With
`run_paths` in the board config, that list is the default, and the hook moves
every record it clears without being asked. `--keep` tags the old commit
instead, for when the code did change. The third way out is a new run with
`corrects:`. `rebase_runs.py --install-hooks` once per clone adds the
post-rewrite hook and a pre-push hook that refuses a push leaving a record
behind. Git does not copy hooks, so `check.py` warns in a clone that lacks
either one, naming the command, except where `CI` is set. What the hosting has to be set to, so that it does not rewrite a
branch unseen, is [`references/git-hosting.md`](references/git-hosting.md).

`upgrade.py` replaces `conventions.md` with the installed skill's when its
`template_version` is older, and removes `inputs` from the `run:` block of
experiments and technotes written by older skills, leaving every other line as
it was. `check.py` warns when `conventions.md` is behind. It refuses a file with
uncommitted changes, so `git diff` shows the upgrade. Nothing else in the
project is the skill's to rewrite.

Which rule each script enforces is stated once, in the project's
`conventions.md`, next to the moment that fires it.

Board settings live in `<board>/.research-log.md`, at the board root
beside the kind directories rather than inside one: `lang`, `project`,
`id_width`, `suffix_length`, `run_paths`. The board is `docs/` unless `--board` or
`RESEARCH_LOG_BOARD` says otherwise. `id_width` is per board, sized from
the table in `templates/<lang>/config.md`; it is committed and must be the same
for every writer, because a width changed under one writer renumbers nothing
and collides with everything.

## Reference

- `references/initialisation.md`: the procedure for setting a project up — the
  checks before anything, the brief interview, what `init.py` leaves, and what
  initialisation must never do. Read when a project is being started, and not
  otherwise
- `references/git-hosting.md`: hosting settings that keep the server from
  rewriting a record's commit unseen, what to do after a rebase in the merge
  request, and a CI job running `check.py`. Read when the project merges
  through merge requests or pull requests
- `templates/{en,ru}/{hypothesis,experiment,technote,finding,protocol,decision}.md`:
  the six kinds, in the two shipped languages
- `templates/{en,ru}/{conventions,vision,agents-section,config}.md`: what a
  project gets at initialisation, being the shipped rules, its own purpose,
  the section its `AGENTS.md` gets, and its board settings
- `templates/{en,ru}/brief.md`: the assignment a project starts from, and the
  input initialisation reads. One required section, read as prose and never
  parsed. What a brief omits is the work of whoever takes the project on, and
  initialisation does not fill it in
