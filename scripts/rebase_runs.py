#!/usr/bin/env python3
"""Follow records across a rebase, a squash or an amend of the commit they name.

    rebase_runs.py                                   # what a rewrite left behind
    rebase_runs.py E-0003.k3f --same --paths src/ configs/
    rebase_runs.py E-0003.k3f --same --basis "only README and tests changed"
    rebase_runs.py --all --same                      # with run_paths from the config
    rebase_runs.py E-0003.k3f --keep                 # tag the commit it ran on
    rebase_runs.py --check                           # exit 1 if anything is left
    rebase_runs.py --install-hooks                   # once per clone

Two fields name a commit: `run.commit` of an experiment or a technote, and
`origin.commit` of a finding minted here. Each is an ancestor of HEAD whenever
nothing rewrote the branch, because the record is committed after the code it
names. A rebase, a squash or an amend replaces that commit with a new one, and
the old one is collected once nothing holds it. check.py refuses a record in
that state, and this script settles it one of three ways:

  * **`--same`: the new commit is the code the record names.** The commit
    field moves to it, and `rebased` beside it keeps the old SHA, the date and
    the reason. The reason is the point: moving the SHA is a reproducibility
    claim, and `--paths` makes it a checked one - the paths the run used must
    not differ between the two commits. `--basis` is the same claim made by a
    person, for when no list of paths says it. Without either, `run_paths`
    from the board config is the list.
  * **`--keep`: it is not.** An annotated tag `research-log/<id>` holds the
    old commit, and the field stays on it.
    Push the tag, or the server never has the commit.
  * **Run it again.** If the numbers are the same, nothing new is written:
    `--same --basis "full rerun at <sha> reproduced the numbers: <which,
    old -> new>, <command>"`.
    If they differ, the new run is a new record that `corrects:` this one,
    and a corrected record is no longer followed or checked. Its tag, if it
    has one, stays until someone decides to delete it.

The new commit is found three ways, in order: the post-rewrite hook's record
of what replaced what, which is exact and covers squash and amend; a commit on
HEAD with the same patch, which covers a rebase done on the server, where no
local hook runs; `--to SHA`, when neither finds it.

With `run_paths` set, the post-rewrite hook settles by itself every record
whose paths did not change, and names the ones left. Nothing is committed: the
updated records are in the working tree for you to commit.

On the server, a rebase is a button in the merge request. Fetch, reset the
branch to what the server made, and run this: the old commits are still here.
"""
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    _dump_entry, commit_block, commit_state, find_root, git, iter_docs,
    keep_tag, load_config, local_project, parse_frontmatter, today,
)

KINDS = ("experiment", "technote", "finding")
HOOK_MARK = "# research-log hook"


# --- the records ----------------------------------------------------------

class Record:
    def __init__(self, kind, path, meta, state):
        self.kind, self.path, self.meta = kind, path, meta
        self.id = str(meta.get("id"))
        self.block = commit_block(kind)
        self.field = f"{self.block}.commit"
        self.commit = str((meta.get(self.block) or {}).get("commit") or "")
        self.tag = keep_tag(kind, self.id)
        self.state = state


def records(root: Path, board: str | None, only_broken: bool = True) -> list[Record]:
    project = local_project(root, load_config(root, board))
    docs = [(kind, path, meta) for kind in KINDS
            for path, meta, _ in iter_docs(root, kind, board)]
    # A record another one corrects is superseded, and its commit with it.
    corrected = {str(meta["corrects"]) for _, _, meta in docs if meta.get("corrects")}
    out = []
    for kind, path, meta in docs:
        block = meta.get(commit_block(kind))
        if not isinstance(block, dict) or not block.get("commit") or not meta.get("id"):
            continue
        if str(meta["id"]) in corrected:
            continue
        # A finding from another project names a commit of that project.
        if kind == "finding" and str(block.get("project") or "") != project:
            continue
        r = Record(kind, path, meta, None)
        r.state = commit_state(root, r.tag, r.commit)
        if only_broken and r.state not in ("rewritten", "missing"):
            continue
        out.append(r)
    return out


# --- where the commit went ------------------------------------------------

def rewrites_path(root: Path) -> Path:
    """Outside the tree, so recording a rewrite dirties nothing."""
    _, rel = git(root, "rev-parse", "--git-path", "research-log-rewritten")
    path = Path(rel)
    return path if path.is_absolute() else root / path


def load_rewrites(root: Path) -> dict[str, str]:
    path = rewrites_path(root)
    if not path.is_file():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def is_ancestor(root: Path, commit: str) -> bool:
    return git(root, "merge-base", "--is-ancestor", commit, "HEAD")[0] == 0


def exists(root: Path, commit: str) -> bool:
    return git(root, "cat-file", "-e", f"{commit}^{{commit}}")[0] == 0


def patch_ids(root: Path, *log_args: str) -> list[tuple[str, str]]:
    _, log = git(root, "log", "-p", "--no-merges", *log_args)
    if not log:
        return []
    _, ids = git(root, "patch-id", "--stable", stdin=log + "\n")
    return [tuple(line.split()[:2]) for line in ids.splitlines() if len(line.split()) >= 2]


def find_successor(root: Path, old: str) -> tuple[str | None, str]:
    """The commit on HEAD that replaced `old`, and how it was found."""
    rewrites = load_rewrites(root)
    new, seen = old, set()
    while new in rewrites and new not in seen:
        seen.add(new)
        new = rewrites[new]
    if new != old and exists(root, new) and is_ancestor(root, new):
        return new, "recorded by the post-rewrite hook"
    if not exists(root, old):
        return None, ""
    own = patch_ids(root, "-1", old)
    if not own:
        return None, ""
    _, base = git(root, "merge-base", old, "HEAD")
    span = f"{base}..HEAD" if base else "HEAD"
    for pid, sha in patch_ids(root, span):
        if pid == own[0][0]:
            return sha, "same patch on HEAD"
    return None, ""


def diff_stat(root: Path, old: str, new: str, paths=()) -> str:
    _, out = git(root, "diff", "--stat=100", old, new, "--", *paths)
    return out


# --- editing a record -----------------------------------------------------

def move_commit(text: str, block_key: str, new: str, entry: dict) -> str:
    """`text` with `<block>.commit` set to `new` and `entry` appended to
    `<block>.rebased`.

    Line-based like upgrade.py: only the commit line and the `rebased` list,
    which this script owns, are rewritten.
    """
    lines = text.splitlines(keepends=True)
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    top = next(i for i in range(1, end) if lines[i].startswith(f"{block_key}:"))

    def indent(line):
        return len(line) - len(line.lstrip(" "))

    def live(line):
        return bool(line.strip()) and not line.lstrip().startswith("#")

    child, last, commit_at, rebased = None, top, None, None
    i = top + 1
    while i < end:
        line = lines[i]
        if live(line) and indent(line) == 0:
            break
        if live(line):
            last = i
            if child is None:
                child = indent(line)
            key = line.strip().split(":", 1)[0]
            if indent(line) == child and key == "commit":
                commit_at = i
            elif indent(line) == child and key == "rebased":
                j = i + 1
                while j < end and (not lines[j].strip() or indent(lines[j]) > child):
                    j += 1
                while j > i + 1 and not lines[j - 1].strip():
                    j -= 1
                rebased = (i, j)
        i += 1
    child = child or 2

    meta, _ = parse_frontmatter(text)
    history = list((meta.get(block_key) or {}).get("rebased") or []) + [entry]
    block = [ln + "\n" for ln in _dump_entry("rebased", history, child)]

    lines[commit_at] = f"{' ' * child}commit: {new}\n"
    if rebased:
        lines[rebased[0]:rebased[1]] = block
    else:
        lines[last + 1:last + 1] = block
    return "".join(lines)


# --- commands -------------------------------------------------------------

def short(sha: str) -> str:
    return sha[:10]


def tag_name(r: Record) -> str:
    return r.tag.removeprefix("refs/tags/")


def show(root: Path, board: str | None) -> int:
    broken = records(root, board)
    if not broken:
        print("every record's commit is on HEAD or held by its tag")
        return 0
    run_paths = load_config(root, board)["run_paths"]
    for r in broken:
        print(f"{r.id}  {r.path.relative_to(root)}")
        print(f"  {r.field} {short(r.commit)} ({r.state})")
        new, how = find_successor(root, r.commit)
        if new:
            print(f"  now      {short(new)} ({how})")
            if r.state == "rewritten":
                stat = diff_stat(root, r.commit, new)
                if not stat:
                    print("  differs  nothing: the trees are identical")
                else:
                    shown = [ln.strip() for ln in stat.splitlines()]
                    print("  differs  " + "\n           ".join(shown[:15]
                          + (["..."] if len(shown) > 15 else [])))
        else:
            print("  now      not found; pass --to SHA")
        changed = bool(new and run_paths and r.state == "rewritten"
                       and diff_stat(root, r.commit, new, run_paths))
        if changed:
            print("  run_paths changed: the code it names is not on HEAD any more")
            print(f"  -> rebase_runs.py {r.id} --keep")
            print("     or run it again: same numbers -> --same --basis <the rerun>,")
            print("     different numbers -> a new record with corrects:")
            print(f"     or rebase_runs.py {r.id} --same --basis <why the change "
                  f"does not touch it>")
        elif r.state == "rewritten":
            hint = "" if run_paths else " --paths <what the run used>"
            print(f"  -> rebase_runs.py {r.id} --same{hint}")
            print(f"     rebase_runs.py {r.id} --keep")
        else:
            print("  the commit it named is gone from this clone: fetch it, or "
                  "--same --basis if you can say why the code is the same")
            print(f"  -> rebase_runs.py {r.id} --same --basis <why the code is the same>")
        print()
    return 1


def settle(root: Path, board: str | None, args) -> int:
    broken = {r.id: r for r in records(root, board)}
    targets = list(broken) if args.all else args.ids
    if not targets:
        print("nothing to settle")
        return 0
    paths = args.paths or (None if args.basis else load_config(root, board)["run_paths"])
    status = 0
    for doc_id in targets:
        r = broken.get(doc_id)
        if r is None:
            print(f"{doc_id}: not a record left behind by a rewrite")
            status = 1
            continue
        if args.keep:
            status = max(status, keep(root, r))
        else:
            status = max(status, same(root, r, args.to, paths, args.basis))
    return status


def keep(root: Path, r: Record) -> int:
    if r.state == "missing":
        print(f"{r.id}: {short(r.commit)} is not in this clone, so nothing can hold it. "
              f"Fetch it, or --same, or run again")
        return 1
    tag = tag_name(r)
    code, _ = git(root, "tag", "-a", tag, r.commit, "-m",
                  f"research-log: the commit {r.id} names, kept past a rewrite")
    if code != 0:
        print(f"{r.id}: could not create tag {tag}")
        return 1
    print(f"{r.id}: tagged {tag} at {short(r.commit)}. Push it: git push origin {tag}")
    return 0


def same(root: Path, r: Record, to: str | None, paths, basis: str | None,
         quiet: bool = False) -> int:
    def say(msg):
        if not quiet:
            print(msg)

    how = "given"
    if to:
        code, new = git(root, "rev-parse", "--verify", "-q", f"{to}^{{commit}}")
        if code != 0:
            say(f"{r.id}: no such commit: {to}")
            return 1
    else:
        new, how = find_successor(root, r.commit)
        if not new:
            say(f"{r.id}: no successor of {short(r.commit)} found. Pass --to SHA")
            return 1
    if not is_ancestor(root, new):
        say(f"{r.id}: {short(new)} is not on HEAD")
        return 1

    reasons = []
    if paths:
        if r.state == "missing":
            say(f"{r.id}: {short(r.commit)} is not in this clone, so --paths cannot "
                f"compare it. Fetch it, or --basis")
            return 1
        paths = [p.rstrip("/") or "." for p in paths]
        for p in paths:
            # A mistyped path differs in nothing, which would pass.
            if git(root, "cat-file", "-e", f"{r.commit}:{p}")[0] != 0:
                say(f"{r.id}: {p} does not exist in {short(r.commit)}")
                return 1
        stat = diff_stat(root, r.commit, new, paths)
        if stat:
            say(f"{r.id}: the code the record names changed between {short(r.commit)} "
                f"and {short(new)}:\n{stat}\n"
                f"Keep the old commit (--keep), or run it again")
            return 1
        reasons.append("no changes under " + ", ".join(paths))
    if basis:
        reasons.append(basis.replace('"', "'"))
    if not reasons:
        if r.state == "rewritten" and not diff_stat(root, r.commit, new):
            reasons.append("identical tree")
        else:
            say(f"{r.id}: say why {short(new)} is the code the record names: "
                f"--paths for the checked claim, --basis for a stated one, or "
                f"run_paths in the board config")
            return 1

    entry = {"from": r.commit, "date": today(), "basis": "; ".join(reasons)}
    r.path.write_text(move_commit(r.path.read_text(), r.block, new, entry))
    say(f"{r.id}: {r.field} {short(r.commit)} -> {short(new)} ({how}). "
        f"Commit {r.path.relative_to(root)}")
    return 0


def check(root: Path, board: str | None) -> int:
    broken = records(root, board)
    for r in broken:
        print(f"research-log: {r.id} names {short(r.commit)} in {r.field}, which a "
              f"rewrite left behind ({r.state})", file=sys.stderr)
    if broken:
        print("research-log: run rebase_runs.py to settle them", file=sys.stderr)
        return 1
    return 0


def record_rewrite(root: Path, board: str | None, command: str) -> int:
    """The post-rewrite hook: `old new` pairs on stdin. Never fails the rewrite."""
    pairs = [line.split()[:2] for line in sys.stdin if len(line.split()) >= 2]
    if not pairs:
        return 0
    with open(rewrites_path(root), "a") as f:
        for old, new in pairs:
            f.write(f"{old} {new} {command} {today()}\n")
    try:
        broken = records(root, board)
        run_paths = load_config(root, board)["run_paths"]
    except Exception as exc:
        print(f"research-log: {exc}", file=sys.stderr)
        return 0
    if not broken:
        return 0
    settled, left = [], []
    for r in broken:
        if run_paths and r.state == "rewritten" \
                and same(root, r, None, run_paths, None, quiet=True) == 0:
            settled.append(r.id)
        else:
            left.append(r.id)
    if settled:
        print(f"research-log: moved to the rewritten commits, run_paths unchanged: "
              f"{', '.join(settled)}. Commit the records", file=sys.stderr)
    if left:
        print(f"research-log: left behind by this {command}: {', '.join(left)}. "
              f"Run rebase_runs.py", file=sys.stderr)
    return 0


def pre_push(root: Path, board: str | None) -> int:
    """The pre-push hook: `<local ref> <local sha> <remote ref> <remote sha>`."""
    _, head = git(root, "rev-parse", "HEAD")
    pushed = [line.split()[1] for line in sys.stdin if len(line.split()) >= 4]
    if head not in pushed:
        return 0  # a tag, or another branch: its records are not the working tree's
    return check(root, board)


def install_hooks(root: Path, board: str | None) -> int:
    _, rel = git(root, "rev-parse", "--git-path", "hooks")
    if not rel:
        print("not a git repository")
        return 1
    hooks = Path(rel) if Path(rel).is_absolute() else root / rel
    hooks.mkdir(parents=True, exist_ok=True)
    me = shlex.quote(str(Path(__file__).resolve()))
    extra = f" --board {shlex.quote(board)}" if board is not None else ""
    wanted = {
        "post-rewrite": ("follows records across rewritten commits",
                         f'exec python3 {me}{extra} --record-rewrite "$1"'),
        "pre-push": ("refuses a push whose records a rewrite left behind",
                     f"exec python3 {me}{extra} --pre-push"),
    }
    status = 0
    for name, (what, line) in wanted.items():
        path = hooks / name
        if path.exists() and HOOK_MARK not in path.read_text():
            print(f"{path}: another hook is here. Add this line to it:\n  {line}")
            status = 1
            continue
        path.write_text(f"#!/bin/sh\n{HOOK_MARK}: {what}\n{line}\n")
        path.chmod(0o755)
        print(f"installed {path}")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", metavar="ID", help="records to settle")
    ap.add_argument("--all", action="store_true", help="every record left behind")
    what = ap.add_mutually_exclusive_group()
    what.add_argument("--same", action="store_true",
                      help="the new commit is the code the record names")
    what.add_argument("--keep", action="store_true",
                      help="it is not: tag the commit the record names")
    ap.add_argument("--paths", nargs="+", metavar="PATH",
                    help="with --same: what the run used, which must not differ. "
                         "Default: run_paths from the board config")
    ap.add_argument("--basis", metavar="TEXT",
                    help="with --same: why the code is the same, in words")
    ap.add_argument("--to", metavar="SHA", help="with --same: the new commit")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if a record is left behind; print nothing otherwise")
    ap.add_argument("--install-hooks", action="store_true",
                    help="post-rewrite and pre-push hooks for this clone")
    ap.add_argument("--record-rewrite", metavar="COMMAND", help=argparse.SUPPRESS)
    ap.add_argument("--pre-push", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else find_root()
    if args.record_rewrite:
        return record_rewrite(root, args.board, args.record_rewrite)
    if args.pre_push:
        return pre_push(root, args.board)
    if args.install_hooks:
        return install_hooks(root, args.board)
    if args.check:
        return check(root, args.board)
    if args.ids or args.all:
        if not (args.same or args.keep):
            ap.error("settling a record needs --same or --keep")
        if args.keep and (args.paths or args.basis or args.to):
            ap.error("--paths, --basis and --to go with --same")
        return settle(root, args.board, args)
    if args.same or args.keep:
        ap.error("name the records to settle, or --all")
    return show(root, args.board)


if __name__ == "__main__":
    raise SystemExit(main())
