#!/usr/bin/env bash
# Stand a board up in a throwaway repository and exercise every script that
# writes. Run it after touching scripts/ or templates/; it takes a second and
# needs nothing but git and python3.
#
#   bash guides/smoke-test.sh
#
# A development document: install.sh does not copy guides/.

set -euo pipefail

KT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cd "$WORK"
git init -q .
git config user.email smoke@test
git config user.name "Smoke Test"
echo x > d.csv
git add -A
git commit -qm init

python3 "$KT/new.py" hypothesis "A claim worth testing" --lang ru
python3 "$KT/record_run.py" "First measurement" --tool foo=1.0
T=$(python3 "$KT/record_run.py" "Parser speed" --kind technote | head -1)
python3 "$KT/new.py" decision "Use the fast parser" --rests-on "$T"
python3 "$KT/index.py"
python3 "$KT/check.py"

# A clone without the hooks is warned, by name of the command, outside CI only.
env -u CI python3 "$KT/check.py" | grep -q "rebase_runs.py --install-hooks" \
    || { echo "check.py did not warn about missing hooks" >&2; exit 1; }
CI=1 python3 "$KT/check.py" | tee /dev/stderr | grep -q "0 errors, 0 warning" \
    || { echo "check.py warned on a fresh board" >&2; exit 1; }

# A document written by an older skill, with run.inputs, passes check.py;
# upgrade.py removes inputs and leaves every other byte alone.
OLD="$(mktemp -d)"
trap 'rm -rf "$WORK" "$OLD"' EXIT
git add -A && git commit -qm board
E=$(ls docs/experiments/E-*.md | head -1)
cp "$E" "$OLD/expected.md"
awk '{ print } /^  commit: / { print "  inputs:"; print "    - path: d.csv";
       print "      sha256: 0000" }' "$OLD/expected.md" > "$E"
O=$(ls docs/technotes/T-*.md | head -1)
cp "$O" "$OLD/expected-t.md"
awk '{ print } /^  commit: / { print "  inputs: []" }' "$OLD/expected-t.md" > "$O"
git commit -qam "old inputs"
python3 "$KT/check.py" --quiet >/dev/null \
    || { echo "check.py rejected a document with run.inputs" >&2; exit 1; }
OUT=$(python3 "$KT/upgrade.py" --check || true)
grep -q "$E: run.inputs to remove" <<<"$OUT" \
    || { echo "upgrade.py --check did not report run.inputs" >&2; exit 1; }
if cmp -s "$E" "$OLD/expected.md"; then echo "--check wrote a file" >&2; exit 1; fi
python3 "$KT/upgrade.py" >/dev/null || true
cmp -s "$E" "$OLD/expected.md" \
    || { echo "upgrade.py did not restore the experiment byte for byte" >&2; exit 1; }
cmp -s "$O" "$OLD/expected-t.md" \
    || { echo "upgrade.py did not restore the technote byte for byte" >&2; exit 1; }
git commit -qam "upgraded"

# A hypothesis citing a technote must fail the check.
H=$(ls docs/hypotheses/H-*.md)
sed -i.bak -e "s/^status: .*/status: active/" -e "s/^criterion_set:.*/criterion_set: 2000-01-01/" \
    -e "s/^experiments: .*/experiments: [$T]/" "$H" && rm "$H.bak"
if python3 "$KT/check.py" --quiet >/dev/null; then
    echo "check.py accepted a hypothesis citing a technote" >&2
    exit 1
fi

# A rebase that moves a run's commit: check.py refuses the record,
# rebase_runs.py follows it (through the hook, or by patch when no hook ran),
# --paths refuses when the code the run used changed, --keep tags it, and the
# pre-push hook refuses a push that leaves a record behind.
mkdir "$WORK/rb" && cd "$WORK/rb"
git init -q -b main .
git config user.email smoke@test
git config user.name "Smoke Test"
echo 'v=1' > model.py; echo readme > README.md
mkdir -p docs/experiments && touch docs/experiments/.keep
git add -A && git commit -qm init
git init -q --bare "$WORK/rb-remote.git"
git remote add origin "$WORK/rb-remote.git" && git push -q origin main
python3 "$KT/rebase_runs.py" --install-hooks >/dev/null
git checkout -qb feat
echo 'v=2' > model.py && git commit -qam "model v2"
E=$(python3 "$KT/record_run.py" "Run one" | head -1)
git add -A && git commit -qm "record $E"
git checkout -q main && echo more >> README.md && git commit -qam "main moves"
git checkout -q feat && git rebase -q main 2>/dev/null
if python3 "$KT/check.py" --quiet >/dev/null; then
    echo "check.py accepted a run.commit left behind by a rebase" >&2; exit 1
fi
if git push -q origin feat 2>/dev/null; then
    echo "pre-push let a record left behind through" >&2; exit 1
fi
OUT=$(python3 "$KT/rebase_runs.py" || true)
grep -q "recorded by the post-rewrite hook" <<<"$OUT" \
    || { echo "rebase_runs.py did not use the hook's record" >&2; exit 1; }
python3 "$KT/rebase_runs.py" "$E" --same --paths model.py >/dev/null
grep -q "basis: no changes under model.py" docs/experiments/$E-*.md \
    || { echo "rebase_runs.py wrote no run.rebased" >&2; exit 1; }
git commit -qam "follow the rebase"
python3 "$KT/check.py" --quiet >/dev/null \
    || { echo "check.py refused a record rebase_runs.py settled" >&2; exit 1; }
git push -q origin feat

echo 'v=3' > model.py && git commit -qam "model v3"
E2=$(python3 "$KT/record_run.py" "Run two" | head -1)
git add -A && git commit -qm "record $E2"
git checkout -q main && echo again >> README.md && git commit -qam "main again"
git checkout -q feat && git -c core.hooksPath=/dev/null rebase -q main 2>/dev/null
OUT=$(python3 "$KT/rebase_runs.py" || true)
grep -q "same patch on HEAD" <<<"$OUT" \
    || { echo "rebase_runs.py did not find a hookless rebase by patch" >&2; exit 1; }
python3 "$KT/rebase_runs.py" "$E" --same --paths model.py >/dev/null
echo 'v=4' > model.py && git commit -qam "model v4"
if python3 "$KT/rebase_runs.py" "$E2" --same --to HEAD --paths model.py >/dev/null; then
    echo "rebase_runs.py --paths accepted changed code" >&2; exit 1
fi
python3 "$KT/rebase_runs.py" "$E2" --keep >/dev/null
git rev-parse -q --verify "refs/tags/research-log/$E2" >/dev/null \
    || { echo "--keep did not make the research-log/<id> tag" >&2; exit 1; }
python3 "$KT/check.py" --quiet >/dev/null \
    || { echo "check.py refused a record held by its tag" >&2; exit 1; }

# With run_paths, the hook moves a run and a finding by itself when the rebase
# leaves those paths alone.
printf -- '---\nproject: rb\nrun_paths: [model.py]\n---\n' > docs/.research-log.md
git add -A && git commit -qm "run_paths"
E3=$(python3 "$KT/record_run.py" "Run three" | head -1)
python3 "$KT/new.py" finding "Model five holds" --rests-on "$E3" >/dev/null
git add -A && git commit -qm "record $E3 and a finding"
git checkout -q main && echo third >> README.md && git commit -qam "main third"
git checkout -q feat && git rebase -q main 2>/dev/null
grep -q "basis: no changes under model.py" docs/experiments/$E3-*.md \
    || { echo "the hook did not move a run under run_paths" >&2; exit 1; }
grep -q "basis: no changes under model.py" docs/findings/*.md \
    || { echo "the hook did not move a finding's origin.commit" >&2; exit 1; }
git commit -qam "follow"
python3 "$KT/check.py" --quiet >/dev/null \
    || { echo "check.py refused records the hook moved" >&2; exit 1; }

# A record whose code changed and that was run again with different numbers:
# the new record corrects it, and the old one is no longer checked or warned on.
E4=$(python3 "$KT/record_run.py" "Run four" | head -1)
git add -A && git commit -qm "record $E4"
git checkout -q main && echo 'v=9' > model.py && git commit -qam "main changes the model"
git checkout -q feat && git rebase -q -X ours main 2>/dev/null
if python3 "$KT/check.py" --quiet >/dev/null; then
    echo "check.py accepted a record whose code changed under it" >&2; exit 1
fi
E5=$(python3 "$KT/record_run.py" "Run four again" | head -1)
sed -i.bak -e "s/^# corrects: .*/corrects: $E4/" docs/experiments/$E5-*.md
rm docs/experiments/$E5-*.md.bak
python3 "$KT/rebase_runs.py" --all --keep >/dev/null  # the earlier ones, not the corrected
if git rev-parse -q --verify "refs/tags/research-log/$E4" >/dev/null; then
    echo "rebase_runs.py --all tagged a corrected record" >&2; exit 1
fi
python3 "$KT/check.py" | grep -q "0 errors, 0 warning" \
    || { echo "check.py still reports a corrected record" >&2; exit 1; }
cd "$WORK"

# Neither init.py nor upgrade.py touches the project's AGENTS.md, and
# upgrade.py brings an older conventions.md up to date.
SKILL="$(dirname "$KT")"
mkdir "$WORK/up" && cd "$WORK/up"
git init -q .
git config user.email smoke@test
git config user.name "Smoke Test"
printf '# Проект\n\n## Вопрос\n\nЧто выяснить.\n' > brief.md
printf '# Existing\n\nprojects own line\n' > AGENTS.md
cp AGENTS.md AGENTS.before
python3 "$KT/init.py" --lang ru --yes >/dev/null 2>&1
cmp -s AGENTS.md AGENTS.before \
    || { echo "init.py touched AGENTS.md" >&2; exit 1; }
git add -A && git commit -qm init
python3 "$KT/upgrade.py" --check >/dev/null

sed -i.bak -e 's/^template_version: .*/template_version: 0.1.0/' docs/conventions.md
rm docs/conventions.md.bak
git commit -qam "pretend 0.1.0"
python3 "$KT/check.py" | grep -q "Run upgrade.py" \
    || { echo "check.py did not warn about old conventions" >&2; exit 1; }
if python3 "$KT/upgrade.py" --check >/dev/null; then
    echo "upgrade.py --check passed an out-of-date board" >&2; exit 1
fi
python3 "$KT/upgrade.py" >/dev/null
cmp -s docs/conventions.md "$SKILL/templates/ru/conventions.md" \
    || { echo "upgrade.py did not replace conventions.md" >&2; exit 1; }
cmp -s AGENTS.md AGENTS.before \
    || { echo "upgrade.py touched AGENTS.md" >&2; exit 1; }

echo "smoke test passed in $WORK"
