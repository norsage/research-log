## Research log

Before any task, read:

1. [`docs/conventions.md`](docs/conventions.md): where things are, where a new
   document goes, and what fires at which moment. Shipped by the research-log
   skill, not ours to edit.
2. [`docs/conventions-local.md`](docs/conventions-local.md): this project's own
   rules, being stack, environment, code layout, tools and tests.
3. [`docs/vision.md`](docs/vision.md): what this project is for and its
   directions.

Once per clone, install the git hooks, which git does not copy:
`python3 .agents/skills/research-log/scripts/rebase_runs.py --install-hooks`
(with the skill installed globally, `~/.agents/skills/` instead of
`.agents/skills/`). Without them an amend or a rebase moves no record's
`run.commit`, and nothing refuses a push that leaves a record behind;
`check.py` warns until they are in. What to do after the server rebases a
branch is in
[`.agents/skills/research-log/references/git-hosting.md`](.agents/skills/research-log/references/git-hosting.md#when-someone-presses-the-rebase-button).
