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

python3 "$KT/check.py" | grep -q "0 errors, 0 warning" \
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
