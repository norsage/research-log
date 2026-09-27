#!/usr/bin/env python3
"""Bring a board up to the installed skill.

    upgrade.py            # rewrite what is out of date
    upgrade.py --check    # report only; exit 1 if anything is out of date

Two things are upgraded:

  * conventions.md, the one file on a board the skill owns: it is copied from
    the template verbatim, so replacing it loses nothing.
  * the `run:` block of experiments and technotes, from which `inputs` is
    removed. Older skills wrote file hashes there; they repeated the commit for
    files in git and restored nothing for files outside it. Every other line of
    the document is left byte for byte.

AGENTS.md, vision.md, conventions-local.md and the board config belong to the
project and are never touched.

No file is written while it has uncommitted changes, so after an upgrade
`git diff` shows exactly what changed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    board_root, find_root, iter_docs, load_config, template_version,
)
from init import template  # noqa: E402


def uncommitted(root: Path, path: Path) -> bool:
    """True if git reports changes to `path`. Outside a repository, False."""
    out = subprocess.run(["git", "status", "--porcelain", "--", str(path)],
                         cwd=root, capture_output=True, text=True)
    return out.returncode == 0 and bool(out.stdout.strip())


def fmt(version: tuple[int, ...]) -> str:
    return ".".join(map(str, version)) or "none"


def strip_run_inputs(text: str) -> str:
    """`text` without `inputs` and the lines under it in the frontmatter's `run:`.

    Line-based, so nothing else is re-serialised: comments, quoting and order
    stay as they were.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return text

    def indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def significant(line: str) -> bool:
        return bool(line.strip()) and not line.lstrip().startswith("#")

    run = next((i for i in range(1, end)
                if lines[i].startswith("run:") and significant(lines[i])), None)
    if run is None:
        return text
    child = None  # the indentation of run's own keys
    i = run + 1
    while i < end:
        line = lines[i]
        if not significant(line):
            i += 1
            continue
        if indent(line) == 0:
            break
        if child is None:
            child = indent(line)
        if indent(line) == child and line.strip().split(":", 1)[0] == "inputs":
            j = i + 1
            while j < end and (not lines[j].strip() or indent(lines[j]) > child
                               or (lines[j].lstrip().startswith("-") and indent(lines[j]) == child)):
                j += 1
            # A trailing blank line belongs to what follows, not to inputs.
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            return "".join(lines[:i] + lines[j:])
        i += 1
    return text


def upgrade_conventions(root: Path, board: str | None, check: bool) -> int:
    """Replace conventions.md when it is older than the template. 1 if not done."""
    lang = load_config(root, board)["lang"]
    path = board_root(root, board) / "conventions.md"
    rel = path.relative_to(root)
    if not path.is_file():
        print(f"{rel}: missing. Is this a board set up by init.py?")
        return 1

    current, new = path.read_text(), template(lang, "conventions")
    have, ship = template_version(current), template_version(new)
    if have > ship:
        print(f"{rel}: version {fmt(have)} is newer than the installed skill's "
              f"{fmt(ship)}. Update the skill instead")
        return 1
    if have == ship and current == new:
        print(f"{rel}: up to date ({fmt(have)})")
        return 0
    if have == ship:
        print(f"{rel}: version {fmt(have)}, but the text differs from the shipped "
              f"one. Compare it with templates/{lang}/conventions.md: move any hand "
              f"edits to conventions-local.md, then copy the template over")
        return 1
    if check:
        print(f"{rel}: {fmt(have)} -> {fmt(ship)}")
        return 1
    if uncommitted(root, path):
        print(f"{rel}: has uncommitted changes. Commit or revert them first")
        return 1
    path.write_text(new)
    print(f"{rel}: upgraded {fmt(have)} -> {fmt(ship)}")
    return 0


def upgrade_runs(root: Path, board: str | None, check: bool) -> int:
    """Remove `run.inputs` from experiments and technotes. 1 if any is left."""
    status = 0
    for kind in ("experiment", "technote"):
        for path, meta, _ in iter_docs(root, kind, board):
            run = meta.get("run")
            if not isinstance(run, dict) or "inputs" not in run:
                continue
            rel = path.relative_to(root)
            text = path.read_text()
            new = strip_run_inputs(text)
            if new == text:
                print(f"{rel}: run.inputs could not be located. Remove it by hand")
                status = 1
            elif check:
                print(f"{rel}: run.inputs to remove")
                status = 1
            elif uncommitted(root, path):
                print(f"{rel}: has uncommitted changes. Commit or revert them first")
                status = 1
            else:
                path.write_text(new)
                print(f"{rel}: removed run.inputs")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    ap.add_argument("--check", action="store_true",
                    help="report only, and exit 1 if anything is out of date")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else find_root()
    status = upgrade_conventions(root, args.board, args.check)
    return max(status, upgrade_runs(root, args.board, args.check))


if __name__ == "__main__":
    raise SystemExit(main())
