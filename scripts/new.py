#!/usr/bin/env python3
"""Create a hypothesis, experiment, technote, finding, decision or protocol from its template.

    new.py hypothesis "Electrostatics predicts direction on charge deletion"
    new.py decision "Mutation classes and their definitions" --lang ru
    new.py finding "Which term wins depends on the mutation class" --rests-on E-0012.h7q
    new.py finding "A bound on the SASA discretisation error" --class formal
    new.py protocol "Running a PB calculation with APBS" --slug apbs-run

Never hand-assign an identifier: this allocates one under a board lock, so two
agents on the same checkout cannot mint the same number, and the random suffix
covers the two-branches case that no lock can see.

An experiment or technote created here has an empty `run:` block. Prefer
record_run.py (with `--kind technote` for a technote),
which fills it from the repository - a run block written by hand
is a reproducibility claim nobody checked.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    FINDING_CLASSES, KINDS, LANGS, HYPOTHESIS_STATUSES, allocate_id, board_lock,
    find_root, NeedSlug, kind_dir, load_config, parse_frontmatter, parse_local_id,
    set_field,
    skill_root, slugify, today, uncomment_field,
)


def template_path(lang: str, kind: str) -> Path:
    return skill_root() / "templates" / lang / f"{kind}.md"


def create(root: Path, kind: str, title: str, cfg: dict, *, lang: str,
           status: str | None = None, rests_on: list[str] | None = None,
           motivated_by: str | None = None, slug: str | None = None,
           klass: str | None = None, under: list[str] | None = None,
           board: str | None = None) -> Path:
    tpl = template_path(lang, kind)
    if not tpl.is_file():
        raise SystemExit(f"no template: {tpl}")
    text = tpl.read_text()
    name = slugify(title, slug)  # before the lock: a bad slug is not worth holding it

    with board_lock(root, board):
        doc_id = allocate_id(root, kind, cfg, board)
        text = set_field(text, "id", doc_id)
        text = set_field(text, "title", title)
        stamp = today()
        for field in ("created", "updated", "date"):
            try:
                text = set_field(text, field, stamp)
            except KeyError:
                pass  # not every kind carries every date field
        if status:
            text = set_field(text, "status", status)
        if kind == "finding":
            if klass:
                text = set_field(text, "class", klass)
            text = set_field(text, "origin.project", cfg.get("project") or root.name)
            tech_prefix = KINDS["technote"][1]
            runs = [str(r) for r in rests_on or []]
            technotes = [r for r in runs if (parse_local_id(r) or ("",))[0] == tech_prefix]
            text = set_field(text, "origin.experiments",
                             [r for r in runs if r not in technotes])
            text = set_field(text, "origin.technotes", technotes)
            text = set_field(text, "origin.commit", git_commit(root) or "")
        elif kind in ("experiment", "technote"):
            if rests_on and kind == "experiment":
                text = uncomment_field(text, "rests_on", list(rests_on))
            if under:
                text = uncomment_field(text, "under", list(under))
        elif kind == "decision" and rests_on:
            text = uncomment_field(text, "based_on", list(rests_on))
        if motivated_by:
            text = set_field(text, "motivated_by", motivated_by)

        folder = kind_dir(root, kind, board)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{doc_id}-{name}.md"
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
        path.write_text(text)
    return path


def git_commit(root: Path) -> str | None:
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=sorted(KINDS))
    ap.add_argument("title")
    ap.add_argument("--lang", choices=LANGS, help="overrides the board's setting")
    ap.add_argument("--status", help=f"hypothesis: one of {HYPOTHESIS_STATUSES}")
    ap.add_argument("--rests-on", nargs="*", metavar="ID",
                    help="what this document rests on: a finding's experiments and "
                         "technotes, "
                         "an experiment's decisions, a decision's technotes and "
                         "experiments")
    ap.add_argument("--under", nargs="*", metavar="ID",
                    help="experiment, technote: the protocols this run followed")
    ap.add_argument("--class", dest="klass", choices=FINDING_CLASSES,
                    help="finding: what admits the claim. Default: empirical")
    ap.add_argument("--motivated-by", metavar="REF",
                    help="experiment: a task reference in any tracker. Free-form")
    ap.add_argument("--slug", metavar="WORDS",
                    help="the filename's readable half, always English. Required "
                         "when the title is not")
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else find_root()
    cfg = load_config(root, args.board)
    lang = args.lang or cfg["lang"]

    if args.status and args.kind == "hypothesis" and args.status not in HYPOTHESIS_STATUSES:
        raise SystemExit(f"status must be one of {HYPOTHESIS_STATUSES}")
    if args.kind == "technote" and args.rests_on:
        raise SystemExit("a technote does not rest on decisions. If a decision "
                         "rests on it, name the technote in the decision's based_on")
    if args.kind == "hypothesis" and args.status == "active":
        print("note: status=active obliges you to fill 'what would refute it' "
              "and set criterion_set", file=sys.stderr)

    try:
        path = create(root, args.kind, args.title, cfg, lang=lang, status=args.status,
                      rests_on=args.rests_on, motivated_by=args.motivated_by,
                      slug=args.slug, klass=args.klass, under=args.under,
                      board=args.board)
    except NeedSlug as e:
        raise SystemExit(str(e))
    meta, _ = parse_frontmatter(path.read_text())
    print(meta["id"])
    print(path.relative_to(root) if path.is_relative_to(root) else path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
