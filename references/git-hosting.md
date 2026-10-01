# Git hosting: merges that keep records whole

Last checked: 2026-10. GitLab and GitHub. On another host, find the same five
settings under its own names.

A record names the commit it ran on, and `check.py` refuses one whose commit
is neither on HEAD nor held by its tag `research-log/<id>`. Locally,
`rebase_runs.py` follows a rewrite, and its hooks catch one before a push.
The server is out of their reach, and it can rewrite a branch three ways
without anyone's clone seeing it: when it merges, when someone presses a
rebase button in the review, and when it rebases by itself before merging.
The settings below shut the first and the third. The second cannot be shut
on either host, so it is followed, and CI checks what a clone without the
hooks let through.

## Settings

| What to prevent | GitLab: Settings → Merge requests | GitHub: Settings → General → Pull Requests, and branch rules |
|---|---|---|
| The merge rewrites the branch's commits | Squash commits when merging: **Do not allow**. Any merge method: fast-forward moves main to the branch's commits and changes no SHA | Allow squash merging: **off**. Allow rebase merging: **off**: GitHub's rebase merge makes new SHAs even when a fast-forward was possible. Allow merge commits: **on**, the only method that keeps them |
| The server rebases before merging | Enable automatic rebase prior to merge: **off**. Merge trains: **off** | Merge queue, if used, with the merge method **Merge commit**. Require linear history: **off**: it allows only squash and rebase merges |
| A merge with records left behind | Pipelines must succeed: **on** | Require status checks to pass, with the CI job below required |

A linear main on GitHub has no button. Rebase the branch locally, let the hook
follow the records, then fast-forward main from the command line:
`git push origin <branch>:main`. GitHub marks the pull request merged once its
commits are on main. The branch rules must let the people who merge push to
main.

## When someone presses the rebase button

GitLab: Rebase in the merge request, or `/rebase`. GitHub: Update branch →
Update with rebase. Neither host lets a project turn it off. Afterwards:

1. `git fetch`
2. `git reset --hard origin/<branch>`
3. `rebase_runs.py`. No local hook ran, so it finds the new commits by patch.
   With `run_paths` set, `rebase_runs.py --all --same` settles what they
   clear
4. Commit the updated records and push. The CI job fails until this is done

The old commits are still in the clone of whoever ran the work. GitLab keeps
the commits of every pushed version of a merge request; GitHub keeps only the
pull request's latest head, so on GitHub that clone and the tags are the only
copy.

Not checked here: whether GitLab still refuses the merge after "Rebase without
pipeline", when the newest commit has no pipeline. Try it once on a throwaway
merge request and record the answer in `conventions-local.md`.

## The CI job

The scripts must be in the repository for CI to run them: install the skill
project-local with `bash install.sh --project` and commit
`.agents/skills/research-log` with its link `.claude/skills/research-log`.
CI needs the whole history and the tags: a shallow clone cannot say what is
on HEAD, and without the tags every record held by one fails.

GitLab, `.gitlab-ci.yml`:

```yaml
research-log:
  image: python:3.12          # the full image: it has git, -slim does not
  variables:
    GIT_DEPTH: 0
  script:
    - python3 .agents/skills/research-log/scripts/check.py
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

The runner fetches tags by default. If the project narrowed its refspecs, keep
`+refs/tags/*:refs/tags/*`.

GitHub, `.github/workflows/research-log.yml`:

```yaml
name: research-log
on:
  pull_request:
  push:
    branches: [main]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0      # all history and all tags
      - run: python3 .agents/skills/research-log/scripts/check.py
```

## Optional: protect the tags

A `research-log/` tag can hold the only copy of the commit a record
names. Keep anyone from moving or deleting one.

- GitLab: Settings → Repository → Protected tags, `research-log/*`,
  allowed to create: Developers and Maintainers.
- GitHub: Settings → Rules → Rulesets → New tag ruleset, targeting
  `research-log/*`, restricting updates and deletions.
