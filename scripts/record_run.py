#!/usr/bin/env python3
"""Create an experiment document with its `run:` block filled from the world.

    record_run.py "Burial vs direction, charge deletion" \
        --input data/skempi-charge-deletion.parquet \
        --tool pyrosetta=2026.31 --tool freesasa=2.1.2 \
        --run-id a1b2c3d4 --motivated-by 0042.k3f --rests-on D-0003.m4k

Four things here are not conveniences:

  * **A dirty tree is refused.** `commit:` is a reproducibility claim, and on a
    tree with uncommitted edits it is a false one. `--allow-dirty` records
    `dirty: true` instead of lying, and should be rare.

  * **Inputs are hashed.** Git pins code and does not pin a data slice. Without
    a content hash, "same commit" reads as "same result" and is not.

  * **`date:` is the run's date, not today's.** The check that a hypothesis'
    refutation criterion predates its evidence compares against this field, so
    writing up a week-old run must not backdate the criterion into safety.
    Pass `--date` for a run that happened earlier.

  * **`--rests-on` names the decisions the run used**, and check.py holds each
    of them to a date on or before it. A threshold frozen after the numbers
    exist can always be moved until they look better. `--under` does the same
    for the protocols the run followed: a procedure written up after the result
    is not what the run followed.
"""
from __future__ import annotations

import argparse
import hashlib
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
    """Uncommitted paths that are not the research log itself.

    `commit:` is a claim about what produced the numbers. An uncommitted
    hypothesis or finding produced nothing, and counting it would make every
    session start with `--allow-dirty` - which is how a check stops being one.
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
        if rel_board and (path == rel_board or path.startswith(rel_board + "/")):
            continue
        out.append(path)
    return out


def sha256_of(path: Path) -> str:
    """Hash a file, or a directory's files in sorted order by path and content."""
    h = hashlib.sha256()
    if path.is_dir():
        for p in sorted(path.rglob("*")):
            if p.is_file():
                h.update(str(p.relative_to(path)).encode())
                h.update(p.read_bytes())
    else:
        h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title")
    ap.add_argument("--input", action="append", default=[], metavar="PATH",
                    help="a data input. Repeatable. Hashed into the record")
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
    ap.add_argument("--allow-dirty", action="store_true",
                    help="record dirty: true rather than refusing")
    ap.add_argument("--lang", choices=LANGS)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else find_root()
    cfg = load_config(root, args.board)
    lang = args.lang or cfg["lang"]

    try:  # before hashing anything: a bad slug is cheap to report early
        slug = slugify(args.title, args.slug)
    except NeedSlug as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    code, commit = git(root, "rev-parse", "HEAD")
    if code != 0:
        print("error: not a git repository - a run record without a commit is "
              "not a reproducibility record", file=sys.stderr)
        return 2
    _, porcelain = git(root, "status", "--porcelain")
    dirty = bool(dirty_paths(porcelain, board_root(root, args.board), root))
    if dirty and not args.allow_dirty:
        print("error: working tree is dirty. Commit first, or pass --allow-dirty\n"
              "       (commit: is a claim about what produced these numbers)",
              file=sys.stderr)
        return 2

    inputs = []
    for raw in args.input:
        p = Path(raw)
        if not p.exists():
            print(f"error: no such input: {raw}", file=sys.stderr)
            return 2
        inputs.append({"path": raw, "sha256": sha256_of(p)})

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
             f"  commit: {commit}",
             f"  dirty: {'true' if dirty else 'false'}"]
    block.append("  inputs:" if inputs else "  inputs: []")
    for item in inputs:
        block.append(f"    - path: {item['path']}")
        block.append(f"      sha256: {item['sha256']}")
    block.append("  tools:" if tools else "  tools: {}")
    for name, version in tools.items():
        block.append(f"    {name}: \"{version}\"")

    tpl = skill_root() / "templates" / lang / "experiment.md"
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
        doc_id = allocate_id(root, "experiment", cfg, args.board)
        text = set_field(text, "id", doc_id)
        folder = kind_dir(root, "experiment", args.board)
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
