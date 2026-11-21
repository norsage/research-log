# research-log

Keeps the record of a research project: where each number came from, and what
was decided along the way. Written as the work happens, in markdown beside the
code. Use when a project is given a research log, or when the work produces
one of those.

## Install

```sh
git clone https://github.com/norsage/research-log.git && RL=$PWD/research-log

bash $RL/install.sh            # every project on this machine
bash $RL/install.sh --symlink  # link the clone: the agent reads your checkout

cd my-project
bash $RL/install.sh --project  # into the current directory, committed with this project
```

Re-running replaces the install, after a prompt.

## Using it

Start your agent in the project's directory and say what you want, or type
`/research-log`.

> *"Set this project up with a research log."*

Setup is a conversation, fifteen to thirty minutes, mostly on what the project
has to find out. Skip what you cannot answer yet. Ask the agent to draft
anything and correct it; nothing lands until you say yes. Bring an existing
brief (assignment, supervisor's statement, grant section) and only the
ambiguities get asked. It ends with `AGENTS.md`, `docs/` and a commit.

Then describe the work. The agent picks the kind, writes it, shows you.

| Kind | You say | Holds | Written |
|---|---|---|---|
| hypothesis | *"I expect the cheap features to match the full set. Let's test that."* | a claim you are about to test, and what would refute it | before the evidence |
| experiment | *"Train both feature sets and compare them on the held-out split."* | what one comparison produced | after the run |
| technote | *"Check our parser against pandas and time both."* | a run that checked the tooling, with its conditions | after the run |
| finding | *"Summarise what the experiments under that hypothesis add up to."* | a claim that outlives the run behind it | once it holds |
| protocol | *"Install the tool and write down the manual."* | a procedure that will be repeated | when you work it out |
| decision | *"We settled on the evaluation process. Let's save the motivation behind it."* | a threshold or a definition, fixed | when it is taken |

Anything that is not one of those six is how the work went, and belongs in
your tracker, whichever one you use. Dates are checked: an experiment cannot
cite a criterion or a decision younger than itself.

## Customising

Templates ship in English and Russian; keys and enum values are identical in
both, and only prose is translated. They are starting points — edit them in
`templates/` to match how you actually write, and the scripts read them at
runtime, so changes take effect immediately.

Project-level additions go in `conventions-local.md`, which this skill never
touches. That file also holds the development conventions — stack, package
manager, code layout, tool versions — and fills up as the project learns them,
since most of it cannot be written on day one. Write it so someone on another
machine can stand the project up without asking.

`presets/` is read-only reference the agent consults before proposing a stack,
a layout, a quality setup or a set of libraries. Currently uv, conda, Python QA,
and structural bioinformatics. Whatever you agree to is written into the
project's own files. See [`presets/README.md`](presets/README.md).

## Reading further

- [`SKILL.md`](SKILL.md) — the rules the agent follows: the six kinds, the
  relations between them, what to write when, the frontmatter, and the scripts
- [`references/initialisation.md`](references/initialisation.md) — the
  interview, in full
- [`guides/rationale.md`](guides/rationale.md) — why it is shaped this way, and
  what was tried and rejected. A development document; `install.sh` leaves it
  out
