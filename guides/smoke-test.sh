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
python3 "$KT/record_run.py" "First measurement" --input d.csv --tool foo=1.0
python3 "$KT/index.py"
python3 "$KT/check.py"

echo "smoke test passed in $WORK"
