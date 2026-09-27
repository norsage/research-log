#!/usr/bin/env python3
"""Create an experiment or a technote with its `run:` block filled from the world.

    record_run.py "Burial vs direction, charge deletion" \
        --tool pyrosetta=2026.31 --tool freesasa=2.1.2 \
        --run-id a1b2c3d4 --motivated-by 0042.k3f --rests-on D-0003.m4k

Three things here are not conveniences:

  * **A dirty tree is refused.** `commit:` is a reproducibility claim, and on a
    tree with uncommitted edits it is a false one. Only `.md` files in the log
    directory are exempt; a script kept beside a task is code. `--allow-dirty`
    records `dirty: true` instead of lying, and should be rare. A clean tree
    writes no `dirty` field.

    This script runs after the run, too late to catch uncommitted code, so a
    long run needs the order kept by hand: a trial run on a small slice, on any
    tree and unrecorded; a commit of everything the run uses (code, config,
    the measuring script) and a note of its SHA; the full run; this script. A
    commit made after the full run is one the run never saw. Unrelated edits
    may stay uncommitted. If they remain, or HEAD has moved since, `--commit
    SHA` names the commit the run used, and the tree is not checked.
    The commit in `run.commit` is never rebased, squashed or amended.

  * **`date:` is the run's date, not today's.** The check that a hypothesis'
    refutation criterion predates its evidence compares against this field, so
    writing up a week-old run must not backdate the criterion into safety.
    Pass `--date` for a run that happened earlier.

  * **`--rests-on` names the decisions the run used**, and check.py holds each
    of them to a date on or before it. A threshold frozen after the numbers
    exist can always be moved until they look better. `--under` does the same
    for the protocols the run followed: a procedure written up after the result
    is not what the run followed.

Input files are not hashed. Data outside git is versioned by the project's own
tool: under DVC or the like, the lock file is in git and `commit:` pins the
data with the code. Without such a tool, the protocol or the document's text
says where the data came from and which version it was.

`--kind technote` writes the same record for a run that checked the project's
tooling rather than its subject: a speed benchmark, a comparison against
another library. No hypothesis or experiment may cite a technote, and check.py
enforces that; a decision may name one in `based_on`, a finding in
`origin.technotes`. When unsure which kind a
run is, it is an experiment.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    LANGS, allocate_id, board_lock, board_root, find_root, kind_dir,
    NeedSlug, load_config, replace_block, set_field, skill_root, slugify, today,
    uncomment_field,
)


def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        out = subprocess.run(["git", "-C", str(root), *args],
                             capture_output=True, text=True, timeout=30)
        return out.returncode, out.stdout.strip()
    except Exception:
        return 1, ""


def dirty_paths(porcelain: str, board: Path, root: Path) -> list[str]:
    """Uncommitted paths other than the research log's markdown.

    `commit:` is a claim about what produced the numbers. An uncommitted
    hypothesis or finding produced nothing, and counting it would make every
    session start with `--allow-dirty` - which is how a check stops being one.
    Any other file under the log directory, such as a script beside a task,
    can have produced the numbers, so it counts. `porcelain` must list untracked
    files one by one (`-uall`): a collapsed `docs/tasks/x/` hides what is in it.
    """
    try:
        rel_board = board.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rel_board = None
    out = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip().strip('"')
        # Renames read as "old -> new"; the destination is what matters.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        in_board = rel_board is not None and (rel_board == "." or path.startswith(rel_board + "/"))
        if in_board and path.endswith(".md"):
            continue
        out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title")
    ap.add_argument("--kind", choices=("experiment", "technote"), default="experiment",
                    help="technote for a run that checked the tooling rather than "
                         "the project's subject. Default: experiment")
    ap.add_argument("--tool", action="append", default=[], metavar="NAME=VERSION",
                    help="an external tool and its version. Repeatable")
    ap.add_argument("--run-id", action="append", default=[], metavar="ID",
                    help="a run id in the run tracker. Repeatable")
    ap.add_argument("--tracker", default="none",
                    help="mlflow, aim, none. Default: none")
    ap.add_argument("--motivated-by", metavar="REF")
    ap.add_argument("--slug", metavar="WORDS",
                    help="the filename's readable half, always English. Required "
                         "when the title is not")
    ap.add_argument("--rests-on", nargs="*", default=[], metavar="ID",
                    help="the decisions this run relied on: a threshold, a data "
                         "slice, a definition. Each must predate the run")
    ap.add_argument("--under", nargs="*", default=[], metavar="ID",
                    help="the protocols this run followed. Each must predate it")
    ap.add_argument("--date", metavar="YYYY-MM-DD",
                    help="the earliest run's date. Default: today")
    ap.add_argument("--commit", metavar="SHA",
                    help="the commit the run used, when HEAD has moved since. "
                         "Default: HEAD, which must then be clean")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="record dirty: true rather than refusing")
    ap.add_argument("--lang", choices=LANGS)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    args = ap.parse_args()

    if args.kind == "technote" and args.rests_on:
        print("error: a technote does not rest on decisions. If a decision rests "
              "on it, name the technote in the decision's based_on",
              file=sys.stderr)
        return 2

    root = args.root.resolve() if args.root else find_root()
    cfg = load_config(root, args.board)
    lang = args.lang or cfg["lang"]

    try:  # before touching git: a bad slug is cheap to report early
        slug = slugify(args.title, args.slug)
    except NeedSlug as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    code, commit = git(root, "rev-parse", "HEAD")
    if code != 0:
        print("error: not a git repository - a run record without a commit is "
              "not a reproducibility record", file=sys.stderr)
        return 2
    if args.commit:
        # The tree now is whatever came after the run; only the commit counts.
        code, _ = git(root, "cat-file", "-e", f"{args.commit}^{{commit}}")
        if code != 0:
            print(f"error: no such commit: {args.commit}", file=sys.stderr)
            return 2
        _, commit = git(root, "rev-parse", f"{args.commit}^{{commit}}")
        dirty = False
    else:
        _, porcelain = git(root, "status", "--porcelain", "--untracked-files=all")
        uncommitted = dirty_paths(porcelain, board_root(root, args.board), root)
        dirty = bool(uncommitted)
    if dirty and not args.allow_dirty:
        listed = "\n".join(f"         {p}" for p in uncommitted)
        print("error: working tree is dirty:\n" + listed + "\n"
              "       If these are unrelated to the run, pass --commit SHA for "
              "the commit it used;\n       if the run used them, pass "
              "--allow-dirty\n"
              "       (commit: is a claim about what produced these numbers)",
              file=sys.stderr)
        return 2

    tools = {}
    for raw in args.tool:
        name, sep, version = raw.partition("=")
        if not sep:
            print(f"error: --tool wants NAME=VERSION, got {raw!r}", file=sys.stderr)
            return 2
        tools[name.strip()] = version.strip()

    block = ["run:",
             f"  tracker: {args.tracker}",
             f"  ids: [{', '.join(args.run_id)}]",
             f"  commit: {commit}"]
    if dirty:  # only the exception is written; a missing field is a clean tree
        block.append("  dirty: true")
    block.append("  tools:" if tools else "  tools: {}")
    for name, version in tools.items():
        block.append(f"    {name}: \"{version}\"")

    tpl = skill_root() / "templates" / lang / f"{args.kind}.md"
    text = tpl.read_text()
    text = set_field(text, "title", args.title)
    text = set_field(text, "date", args.date or today())
    text = replace_block(text, "run", block)
    if args.motivated_by:
        text = uncomment_field(text, "motivated_by", str(args.motivated_by))
    if args.rests_on:
        text = uncomment_field(text, "rests_on", list(args.rests_on))
    if args.under:
        text = uncomment_field(text, "under", list(args.under))

    with board_lock(root, args.board):
        doc_id = allocate_id(root, args.kind, cfg, args.board)
        text = set_field(text, "id", doc_id)
        folder = kind_dir(root, args.kind, args.board)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{doc_id}-{slug}.md"
        if path.exists():
            print(f"refusing to overwrite {path}", file=sys.stderr)
            return 2
        path.write_text(text)

    print(doc_id)
    print(path.relative_to(root) if path.is_relative_to(root) else path)
    if dirty:
        print("warning: recorded with dirty: true - the commit does not describe "
              "what ran", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
