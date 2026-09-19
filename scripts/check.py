#!/usr/bin/env python3
"""Check the research log. Exit 1 if anything is broken.

Four of these checks are methodological rather than clerical, and they are the
reason this script exists at all:

  * **A hypothesis in `idea` may not cite experiments.** An idea with runs
    already attached to it is hypothesising after the results are known: the
    claim was written once the answer was visible, and the test that "confirms"
    it confirms nothing.

  * **Every experiment a hypothesis cites is dated after its `criterion_set`.**
    That is the whole pre-commitment, reduced to comparing two dates. Editing
    the refutation criterion later means raising that date, which turns an
    invisible edit into a visible one.

  * **Every decision an experiment rests on is dated on or before it.** A
    threshold, a data slice or a definition frozen after the numbers exist can
    be moved until they look better. The two checks cover different documents:
    a refutation criterion is a hypothesis' pre-commitment, and a decision is
    the definition a run was computed under.

  * **Every protocol an experiment ran under existed on or before it.** An
    experiment naming a protocol claims it followed what that file says; a
    protocol written after the run is a procedure reconstructed from the
    result.

Everything else is well-formedness: fields present, identifiers unique and
resolvable, vocabularies respected. A finding's `class` decides which of those
applies: `origin.experiments` is required of the empirical class and of no
other, because a proof and a literature search are admitted by different
evidence.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    AUDIENCES, DECISION_STATUSES, FINDING_CLASSES, FINDING_STATUSES,
    HYPOTHESIS_STATUSES, KINDS, PROTOCOL_STATUSES,
    as_date, find_root, iter_docs, parse_local_id, valid_finding_id,
)

STATUS_VOCAB = {
    "hypothesis": HYPOTHESIS_STATUSES,
    "finding": FINDING_STATUSES,
    "decision": DECISION_STATUSES,
    "protocol": PROTOCOL_STATUSES,
}
REQUIRED = {
    "hypothesis": ("id", "title", "type", "audience", "status"),
    "experiment": ("id", "title", "type", "audience", "date"),
    "finding": ("id", "title", "type", "audience", "status", "class"),
    "decision": ("id", "title", "type", "audience", "status", "date"),
    "protocol": ("id", "title", "type", "audience", "status", "created"),
}


def as_list(rep, path, field, value):
    """A list field, or an error and an empty list.

    Without this a stray string iterates character by character, and one bad
    line reports forty-seven unresolved citations instead of one bad line.
    """
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    rep.error(path, f"{field}: expected a list, got {value!r}")
    return []


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: Path, msg: str) -> None:
        self.errors.append(f"{path}: {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warnings.append(f"{path}: {msg}")


def collect(root: Path, board: str | None):
    docs: dict[str, list] = {k: [] for k in KINDS}
    for kind in KINDS:
        for path, meta, body in iter_docs(root, kind, board):
            docs[kind].append((path, meta, body))
    return docs


def run_checks(root: Path, board: str | None) -> Report:
    rep = Report()
    docs = collect(root, board)
    ids: dict[str, list[Path]] = {}
    by_id: dict[str, tuple[str, Path, dict]] = {}

    for kind, items in docs.items():
        for path, meta, _ in items:
            doc_id = meta.get("id")
            if doc_id:
                ids.setdefault(str(doc_id), []).append(path)
                by_id[str(doc_id)] = (kind, path, meta)

    for doc_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            # This is what a bad merge looks like: two branches minting the same
            # number, files that merge cleanly because the slugs differ, and a
            # citation that then resolves to whichever was read last.
            rep.errors.append(
                f"duplicate id {doc_id}: " + ", ".join(str(p) for p in paths))

    def resolves(ref) -> bool:
        return str(ref) in by_id

    for kind, items in docs.items():
        for path, meta, _ in items:
            for field in REQUIRED[kind]:
                if meta.get(field) in (None, "", []):
                    rep.error(path, f"missing required field {field!r}")

            if meta.get("type") != kind:
                rep.error(path, f"type is {meta.get('type')!r}, expected {kind!r}")

            doc_id = str(meta.get("id") or "")
            if doc_id and not path.name.startswith(doc_id + "-"):
                rep.error(path, f"filename does not start with its id {doc_id}")

            if kind == "finding":
                if doc_id and not valid_finding_id(doc_id):
                    rep.error(path, f"{doc_id} is not a valid Crockford id "
                                    "(wrong length, bad symbol, or failed check digit)")
            elif doc_id and parse_local_id(doc_id) is None:
                rep.error(path, f"{doc_id} is not a valid local id")

            audience = meta.get("audience")
            if audience and audience not in AUDIENCES:
                rep.error(path, f"audience {audience!r} not in {AUDIENCES}")

            vocab = STATUS_VOCAB.get(kind)
            status = meta.get("status")
            if vocab and status and status not in vocab:
                rep.error(path, f"status {status!r} not in {vocab}")

            for field in ("corrects", "superseded_by", "finding", "successor"):
                ref = meta.get(field)
                if ref and not resolves(ref):
                    rep.error(path, f"{field}: {ref} does not resolve")

            if kind == "hypothesis":
                _check_hypothesis(rep, path, meta, by_id, resolves)
            elif kind == "experiment":
                _check_experiment(rep, path, meta, by_id, resolves)
            elif kind == "finding":
                _check_finding(rep, path, meta, resolves)
            elif kind == "decision":
                if status == "superseded" and not meta.get("superseded_by"):
                    rep.error(path, "status is superseded but superseded_by is empty")

    return rep


def _check_hypothesis(rep, path, meta, by_id, resolves) -> None:
    status = meta.get("status")
    experiments = as_list(rep, path, "experiments", meta.get("experiments"))
    criterion = as_date(meta.get("criterion_set"))

    if status == "idea":
        if experiments:
            rep.error(path, "status is idea but experiments are already cited - "
                            "a claim written after its evidence is not a hypothesis")
        if criterion:
            rep.warn(path, "criterion_set is set while status is idea; move to "
                           "active, which is what taking the commitment means")
        return

    if status in ("active", "hold", "resolved") and not criterion:
        rep.error(path, f"status is {status} but criterion_set is empty - "
                        "the refutation criterion has no date to be checked against")

    for ref in experiments:
        if not resolves(ref):
            rep.error(path, f"cites experiment {ref}, which does not resolve")
            continue
        _, _, exp_meta = by_id[str(ref)]
        exp_date = as_date(exp_meta.get("date"))
        if criterion and exp_date and exp_date < criterion:
            rep.error(path, f"experiment {ref} ran {exp_date}, before "
                            f"criterion_set {criterion} - either the criterion was "
                            "written after the result, or its date was not raised")

    if status == "resolved" and not meta.get("finding"):
        rep.error(path, "status is resolved but no finding is named - "
                        "a resolved question that produced no claim left nothing behind")
    if status == "recycled" and not meta.get("successor"):
        rep.error(path, "status is recycled but successor is empty")


def _check_experiment(rep, path, meta, by_id, resolves) -> None:
    run = meta.get("run") or {}
    if not isinstance(run, dict):
        rep.error(path, "run: must be a mapping")
        return
    if not run.get("commit"):
        rep.error(path, "run.commit is empty - nothing pins the code that ran")
    if run.get("dirty"):
        rep.warn(path, "run.dirty is true: the commit does not describe what ran")
    if not run.get("inputs"):
        rep.warn(path, "run.inputs is empty - git pins code, not a data slice")

    ran = as_date(meta.get("date"))
    for ref in as_list(rep, path, "rests_on", meta.get("rests_on")):
        if not resolves(ref):
            rep.error(path, f"rests_on names {ref}, which does not resolve")
            continue
        kind, _, dec_meta = by_id[str(ref)]
        if kind != "decision":
            rep.error(path, f"rests_on names {ref}, which is a {kind}. It names "
                            "the decisions a run was computed under")
            continue
        decided = as_date(dec_meta.get("date"))
        if ran and decided and decided > ran:
            rep.error(path, f"rests on {ref}, decided {decided}, after this ran "
                            f"{ran} - a threshold frozen after the numbers exist "
                            "can be moved until they look better")

    for ref in as_list(rep, path, "under", meta.get("under")):
        if not resolves(ref):
            rep.error(path, f"under names {ref}, which does not resolve")
            continue
        kind, _, proto_meta = by_id[str(ref)]
        if kind != "protocol":
            rep.error(path, f"under names {ref}, which is a {kind}. It names the "
                            "protocols a run followed")
            continue
        written = as_date(proto_meta.get("created"))
        if ran and written and written > ran:
            rep.error(path, f"ran under {ref}, created {written}, after this ran "
                            f"{ran} - a procedure written after the result is not "
                            "what the run followed")


def _check_finding(rep, path, meta, resolves) -> None:
    klass = meta.get("class")
    if klass and klass not in FINDING_CLASSES:
        rep.error(path, f"class {klass!r} not in {FINDING_CLASSES}")

    origin = meta.get("origin") or {}
    if not isinstance(origin, dict):
        rep.error(path, "origin: must be a mapping")
        return
    if not origin.get("project"):
        rep.error(path, "origin.project is empty - a finding that travels must "
                        "say where it came from")
    experiments = as_list(rep, path, "origin.experiments", origin.get("experiments"))
    if not experiments and klass == "empirical":
        rep.error(path, "origin.experiments is empty on an empirical finding - "
                        "a claim resting on runs must name them, and a claim "
                        "resting on something else belongs to another class")
    for ref in experiments:
        if not resolves(ref):
            rep.warn(path, f"origin names {ref}, which does not resolve here. "
                           "Expected if this finding came from another project")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--board")
    ap.add_argument("--quiet", action="store_true", help="errors only")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else find_root()
    rep = run_checks(root, args.board)

    for line in rep.errors:
        print(f"error: {line}")
    if not args.quiet:
        for line in rep.warnings:
            print(f"warning: {line}")

    if rep.errors:
        print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
        return 1
    print(f"ok - 0 errors, {len(rep.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
