# Setting a project up

Read this when someone asks to set a project up, start a research log, or
put a project on research-log — by `/research-log` or in their own
words. Skip it for every later operation; the rules for those are in `SKILL.md`
and in the project's own `conventions.md`.

Initialisation is a conversation that ends in a script run. `init.py` writes
five files and copies one section. The rest of what a project needs on day one
only exists in the head of the person starting it, and the only way to get it
out is to ask.

Ask in whatever language the person is writing in. This file is in English.

## The one rule

**They decide. You may draft anything.** If they ask you to write the question,
a refutation criterion, a threshold, or the whole brief, write it — that is
work, and refusing it is not integrity. What you may never do is put something
on the board that they have not seen and said yes to.

Draft out loud: say which words are yours, offer them as a draft, and take the
correction. A section nobody can answer yet, and nobody has asked you to draft,
is left out, and the gap is named at the end as a first step.

A pre-commitment binds by the **date** it carries. A threshold you proposed and
they accepted before any numbers existed is a real pre-commitment, and
`check.py` holds it to the same rule as one they wrote alone. What breaks the
mechanism is a threshold chosen once the results are visible, or a criterion
recorded today and dated last month. Authorship does not enter into either.

Never lecture about this. Refusing a request and explaining the methodology
behind the refusal is the failure mode, not the rule.

## How to ask

Ask what you would ask sitting next to them, with no notes and nothing open.
One sentence, ending in a question mark, in words they already use.

Everything you know that they do not need — which section an answer fills,
whether it is required, how long it should be, what a good one contains — is
yours to hold. That is how this file is organised and how the brief is filed
afterwards, and none of it belongs in what you say. Said aloud it turns the
question into a form, and someone filling in a form writes what fits the box
rather than what is true.

The test, applied to every question before you send it: could they answer in a
sentence of their own, without first asking what you mean?

When one does not land, do not add to it. Ask again, smaller, built out of
something they have already told you about their own project. Give at most one
example, and say it is the kind of thing you mean rather than a proposal: a
list of three tells them the shape of reply you are waiting for, and that is
what comes back.

## 0. Before anything

Four checks, all cheap:

1. **Is this the project's directory?** `init.py` runs where it is invoked and
   never asks. Confirm it with them if there is any doubt.
2. **Is it a git repository?** Every check this skill makes rests on the
   commit. If not, offer `git init` and say why.
3. **Is a board already here?** `docs/conventions.md`, `docs/hypotheses/`.
   If so this is not initialisation — say what is there and ask what they
   actually want. An `AGENTS.md` or `CLAUDE.md` alone is not a board.
4. **Does a brief already exist?** Look for `brief.md`, `BRIEF.md`,
   `docs/brief.md`, and then ask. Many projects have an assignment that is not
   called a brief: a task statement, a supervisor's document, a grant section,
   an email. Ask for it before offering to compose one.

## 1. The brief

### They brought one

Read it. Do not rewrite it, do not reorder it, do not translate it into
research prose. It is the assignment, and the person who set the project owns
its wording.

Ask only about what you cannot act on: a question you read two ways, a data
source named but not located, a deadline implied but not stated. One round of
questions, not an interrogation. Anything they cannot answer now stays absent.

### There is no brief

Compose one with them, from `templates/<lang>/brief.md`. You hold the pen; they
answer and approve.

**The one that has to be answered. Ask it first, and do not move on.**

> *"What does this project need to find out — the way you'd explain it to
> someone outside your field?"*

**That is the whole of it. Do not ask why the project matters, what the answer
is for, who needs it, or what it would change.** Take whatever purpose arrives
inside the answer, which it usually does, and write that down with the rest.
`vision.md` keeps a section for it, and the researcher fills it in when they
have something to put there.

**Then context.** Where the question came from, what is already known, what has
been tried and how it came out.

**Then four more topics, over three messages.**

What follows is what to cover, not what to say: **never read these tables
out**, and hold every question to *How to ask* above. When an earlier answer
already covered a topic, do not ask it again.

**First, the two that carry weight — one per message.** Ask the first, stop,
wait. Then the second. Batching these is what produces a wall of text nobody
can answer, and their answers are the ones the rest of the board is built from.

| Topic | Ask something like | What you are listening for |
|---|---|---|
| Hypothesis | *"Do you already expect a particular answer? If so, what result would make you say you were wrong?"* | "I do not know, that is why I am doing this" is a complete and correct answer: the project is exploratory, say so and move on. Do not talk them into one. If they ask you to draft one, draft it and mark it as your wording for them to accept or reject |
| Before the first computation | *"Some numbers in this work you will choose yourself rather than measure — what counts as a real effect, which cases to keep. Which of those can you name now?"* | The highest-value answer in the interview: each one becomes a dated decision in phase 3, and those are what the third check enforces. If it does not land, make it concrete from their own domain — one plausible threshold from what they have just told you, offered as an example of the kind of thing, not as a proposal |

**Then the remaining two together, in one short message.** These are cheap
to answer and cost more in round trips than in thought. Two questions, no
preamble, no restating the sections.

| Topic | Ask something like | What you are listening for |
|---|---|---|
| Data | *"What data do you have already, and where is it? If you do not have it yet, where will it come from?"* | Where it is, how it was produced, what has already been done to it. A dataset that is named but not reachable is worth writing down as exactly that |
| Constraints | *"How long is the project, and how many of you are there? Is anything in the way, like a paid tool or weak hardware?"* | "Two months, one person" changes the shape of everything downstream. Licences matter when a tool is on the critical path. Something the assignment rules out, such as a tool that may not be used, is a constraint too and goes here. Do not ask what else is ruled out and do not suggest exclusions: at the start the boundaries are unknown, and ones found later are recorded as decisions |

Say once, at the start of that message, that skipping is allowed and an empty
section is not a defect. Do not repeat it after every question.

Record their words. Tightening a sentence is fine; upgrading a hunch into a
falsifiable claim is not.

**Show the full draft before writing it to disk**, and write only after they
approve. Then `brief.md` at the project root.

## 2. Run init.py

```bash
python3 <skill>/scripts/init.py            # ./brief.md
python3 <skill>/scripts/init.py --brief PATH
```

It refuses over an existing board and asks once outside a git repository. It
writes `vision.md`, `conventions.md`, `conventions-local.md` and
`.research-log.md` on the board and nothing at the root, copies the brief's
question into `vision.md`, and ends by naming the sections the brief does not
carry.

Relay that closing list to them as it is. It is the agenda for what follows,
not an error.

## 3. What init.py leaves

The question is the only thing it copies. What remains is conversation
rather than editing.

**`AGENTS.md`.** Point the project's agent instructions at the board: add the
section in `templates/<lang>/agents-section.md` to the file the project's
agents read. That is `AGENTS.md`; if the project has a `CLAUDE.md` and no
`AGENTS.md`, it is `CLAUDE.md`; if it has neither, create `AGENTS.md` with the
project's name as its title. Where the file already says something the section
repeats, merge rather than duplicate. Show them the result. The skill never
touches this file again.

**`vision.md`.** It has two sections. `init.py` filled the question from the
brief; read it back, take any correction, and **ask nothing further**. The
second section, the project's directions, stays empty: directions appear once
several hypotheses turn out to be about the same thing, and asking for them on
day one would get invented ones.

**`conventions-local.md`.** Read the repository first: `pyproject.toml`, a
lockfile, `environment.yml`, `Makefile`, a test directory. Propose what you
found and have them confirm or correct it. Then, in order:

- **Nothing to read.** Keep it to one question, asked inside this step: what
  they write in, what installs packages, and whether an existing project's
  rules can be taken as they stand.
- **They name another project.** Read its `conventions-local.md`, say what you
  are taking, and copy the text across. Leave no reference to it, to a
  user-level `CLAUDE.md`, or to anything else outside this repository.
- **They have no answer.** Offer a preset from [`presets/`](../presets/) by
  what it does; read [`presets/README.md`](../presets/README.md) first. Write
  what they agree to into this file, with no reference back to `presets/`.
- **They decline that too.** Leave the section as it stands. The standing rule
  in `SKILL.md` picks it up at the first script.

The skill never touches this file again, so it is theirs from here on.

**A first protocol, if the brief already contains one.** An assignment often
carries installation detail — this tool needs its own environment, that one's
pip build breaks everything, use this lockfile. That is a procedure rather than
a rule:

```bash
python3 <skill>/scripts/new.py protocol "<what it does>" --slug <english-words>
```

Move it across and say you did. From then on the standing rule applies:
whenever you work out how something installs, runs or is assembled and it will
be needed again, write it as a protocol.

**A task tracker, only if one is already installed.** `init.py` says on the way
out if it found the task-tracker skill. If it did, offer it in the same
message as the `conventions-local.md` draft: tasks would live in `docs/tasks/`,
and an experiment's `motivated_by` would carry one of its ids. There is nothing
to create — task-tracker has no initialisation and builds its directories on
first use — so accepting costs nothing and declining costs nothing.

If it is not installed, ask nothing. Do not ask where they track work, do not
propose installing anything, and do not write a tracker into
`conventions-local.md`. This skill owns knowledge and owns no part of the work
side; the entire coupling is one free-form string that nothing parses, and a
project with no tracker on day one is the normal case, not a gap.

**Decisions, from what must be fixed before the first computation.** For each
one they named:

```bash
python3 <skill>/scripts/new.py decision "<what is being frozen>" --slug <english-words>
```

The title is in their language; `--slug` is always English, and the script
refuses a non-English title without one. Three or four words naming the thing
frozen, not a translation of the sentence: a Russian title naming the band
within which an effect is indistinguishable from noise becomes
`no-effect-band`.

Write the choice and its reasoning with them. The date is the point: an
experiment naming it in `rests_on` must run on or after it, and `check.py`
fails when it does not. A pre-commitment recorded a week into the analysis is
not one.

If they named none, say in one sentence what a decision is for and leave it —
unless they ask you to propose some, in which case propose them, say plainly
which parts are your wording, and record only what they accept.

**A hypothesis, only if the brief carries one.**

```bash
python3 <skill>/scripts/new.py hypothesis "<the claim>" --slug <english-words>
```

It opens at `status: idea`, which may not cite experiments. Moving it to
`active` needs *what would refute it* and `criterion_set`, and both are theirs
to write.

## 4. Close

```bash
python3 <skill>/scripts/index.py && python3 <skill>/scripts/check.py
```

Then commit. Tell them how it goes from here: they describe the work, you keep
the board as it goes under the standing rules in `SKILL.md`, and they approve
what you write. Ask them to say two things out loud, because you cannot see
either — a run they did themselves, and a choice taken in conversation rather
than in code. They never need a script name.

## What initialisation never does

- Put anything on the board they have not seen and agreed to. Drafting is
  yours; deciding is theirs.
- Fill a brief section from the repository, from inference, or from what
  similar projects do, without saying that is where it came from.
- Date a decision before the conversation that produced it. This is the one
  that is not negotiable at any request: the date is the whole mechanism.
- Refuse a request to write something, or explain why you would have.
- Rewrite a brief they brought.
- Create another skill's files. task-tracker builds its own directories on
  first use; `init.py` only reports whether it is installed.
