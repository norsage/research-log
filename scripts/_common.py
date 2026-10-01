"""Shared helpers for research-log scripts.

Zero-dependency on purpose, like its sibling task-tracker: a small YAML-subset
parser and dumper for the schema we control, a project-root finder, and two
kinds of identifier minting.

Two identifier forms, deliberately:

  * Local kinds - hypothesis, experiment, technote, decision, protocol - use
    `<P>-NNNN.xxx`. The
    number is allocated locally as max+1 so documents created together stay
    adjacent; the random suffix is what keeps two branches that never saw each
    other from both minting 0042.

  * Findings use an opaque Crockford Base32 identifier with a check symbol.
    A finding is the only kind that graduates to a shared knowledge base, and
    minting it in the base's own form from the start makes graduation a `git
    mv` with no citation broken.

The frontmatter parser handles more than task-tracker's because our schema is
nested: `origin:` is a mapping, and `run.inputs` in older documents is a list
of mappings. It is
still a subset - no anchors, no multi-line scalars, no flow mappings.
"""
from __future__ import annotations

import fcntl
import os
import re
import secrets
import subprocess
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

CONFIG_NAME = ".research-log.md"

# kind -> (directory, id prefix or None for opaque ids)
KINDS = {
    "hypothesis": ("hypotheses", "H"),
    "experiment": ("experiments", "E"),
    "technote": ("technotes", "T"),
    "decision": ("decisions", "D"),
    "protocol": ("protocols", "P"),
    "finding": ("findings", None),
}

HYPOTHESIS_STATUSES = ("idea", "active", "hold", "resolved", "recycled")
FINDING_STATUSES = ("draft", "stable", "deprecated")
DECISION_STATUSES = ("accepted", "superseded")
PROTOCOL_STATUSES = ("draft", "stable", "deprecated")
AUDIENCES = ("public", "internal", "restricted")

# What admits a finding's claim. `empirical` is the run-backed case and the
# default; the others exist because a proof, a literature search and an
# argument over known properties are admitted by different evidence.
FINDING_CLASSES = ("empirical", "formal", "review", "analytical")

LANGS = ("en", "ru")

# base36 minus 0/1/l/o - the glyph pairs misread when an id is copied out of a
# filename by hand. Same alphabet as task-tracker, so the two boards' local
# ids look alike and neither is mistaken for the other's.
SUFFIX_ALPHABET = "23456789abcdefghijkmnpqrstuvwxyz"

# Crockford Base32: no I, L, O or U. Case-insensitive on read, upper on write.
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CROCKFORD_CHECK = CROCKFORD + "*~$=U"
_CROCKFORD_DECODE = {c: i for i, c in enumerate(CROCKFORD)}
for _a, _b in (("I", "1"), ("L", "1"), ("O", "0")):
    _CROCKFORD_DECODE[_a] = _CROCKFORD_DECODE[_b]

# 13 data symbols = 65 bits, which is ~8.6 million items before a one-in-a-
# million chance of any collision, and still half the length of a UUID.
FINDING_ID_LEN = 13

DEFAULTS = {
    "suffix_length": 3,
    "id_width": 4,
    "lang": "en",
    "project": "",
    "run_paths": [],
}
_INT_LIMITS = {"suffix_length": (0, 8), "id_width": (1, 8)}


# --- project layout -----------------------------------------------------

def board_root(root: Path, board: str | None = None) -> Path:
    """The directory holding hypotheses/, experiments/, findings/, decisions/."""
    if board is None:
        board = os.environ.get("RESEARCH_LOG_BOARD", "docs")
    board = board.strip().strip("/")
    return (root / board) if board else root


def kind_dir(root: Path, kind: str, board: str | None = None) -> Path:
    return board_root(root, board) / KINDS[kind][0]


def find_root(start: Path | None = None) -> Path:
    """Walk up from `start` looking for an existing board, then for a project
    marker. Falls back to cwd, so a fresh project still works.
    """
    start = (start or Path.cwd()).resolve()
    board = os.environ.get("RESEARCH_LOG_BOARD", "docs").strip().strip("/")
    for candidate in (start, *start.parents):
        base = (candidate / board) if board else candidate
        if any((base / d).is_dir() for d, _ in KINDS.values()):
            return candidate
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
            return candidate
    return start


def skill_root() -> Path:
    """This skill's own directory, so templates are found however it is invoked."""
    return Path(__file__).resolve().parent.parent


def version_tuple(value) -> tuple[int, ...]:
    """`0.2.0` as (0, 2, 0); anything unparsable as (), which sorts oldest."""
    try:
        return tuple(int(p) for p in str(value).split("."))
    except ValueError:
        return ()


def template_version(text: str) -> tuple[int, ...]:
    meta, _ = parse_frontmatter(text)
    return version_tuple(meta.get("template_version"))


def load_config(root: Path, board: str | None = None) -> dict:
    cfg = dict(DEFAULTS)
    path = board_root(root, board) / CONFIG_NAME
    if path.is_file():
        meta, _ = parse_frontmatter(path.read_text())
        for key in DEFAULTS:
            if key not in meta or meta[key] is None:
                continue
            value = meta[key]
            if key in _INT_LIMITS:
                lo, hi = _INT_LIMITS[key]
                # Loudly: a board that silently fell back to the default width
                # would hand out ids in a shape its neighbours do not expect.
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{path}: {key} must be an integer, got {value!r}")
                if not lo <= value <= hi:
                    raise ValueError(f"{path}: {key} must be in {lo}..{hi}, got {value}")
            if key == "run_paths" and not (isinstance(value, list) and all(
                    isinstance(v, str) and v.strip() for v in value)):
                raise ValueError(f"{path}: run_paths must be a list of paths, got {value!r}")
            if key == "lang" and value not in LANGS:
                raise ValueError(f"{path}: lang must be one of {LANGS}, got {value!r}")
            cfg[key] = value
    return cfg


# --- identifiers --------------------------------------------------------

_LOCAL_ID_RE = re.compile(r"^([A-Z])-0*(\d+)(?:\.([a-z0-9]+))?$")
_FILENAME_ID_RE = re.compile(r"^([A-Z]-\d+(?:\.[a-z0-9]+)?|[0-9A-Z*~$=]{14})-")
_FINDING_ID_RE = re.compile(r"^[0-9A-TV-Z]{13}[0-9A-Z*~$=]$")


def parse_local_id(value) -> tuple[str, int, str] | None:
    """(prefix, number, suffix) from a local id, or None."""
    if value is None or isinstance(value, bool):
        return None
    m = _LOCAL_ID_RE.match(str(value).strip())
    if not m:
        return None
    return m.group(1), int(m.group(2)), (m.group(3) or "")


def gen_suffix(length: int) -> str:
    """Random, not derived from author identity: two branches by the same
    author would draw the same derived value every time."""
    return "".join(secrets.choice(SUFFIX_ALPHABET) for _ in range(length))


def crockford_check(data: str) -> str:
    """Crockford's check symbol: the value modulo 37, in the extended alphabet.
    Catches every single-character error and most transpositions."""
    n = 0
    for ch in data.upper():
        n = n * 32 + _CROCKFORD_DECODE[ch]
    return CROCKFORD_CHECK[n % 37]


def mint_finding_id() -> str:
    """Redraws until the check symbol is a letter or a digit. Five of the 37 are
    `*~$=U`: valid Crockford, but `*` in a filename is a shell glob. Ids minted
    before this still validate."""
    while True:
        data = "".join(secrets.choice(CROCKFORD) for _ in range(FINDING_ID_LEN))
        check = crockford_check(data)
        if check in CROCKFORD:
            return data + check


def valid_finding_id(value) -> bool:
    s = str(value).strip().upper()
    if not _FINDING_ID_RE.match(s):
        return False
    return crockford_check(s[:FINDING_ID_LEN]) == s[FINDING_ID_LEN]


def all_ids(root: Path, kind: str, board: str | None = None) -> set[str]:
    return {str(meta["id"]) for _, meta, _ in iter_docs(root, kind, board)
            if meta.get("id")}


def allocate_id(root: Path, kind: str, cfg: dict, board: str | None = None) -> str:
    """The next identifier for `kind`. Call under `board_lock`."""
    prefix = KINDS[kind][1]
    taken = all_ids(root, kind, board)
    if prefix is None:
        for _ in range(100):
            candidate = mint_finding_id()
            if candidate not in taken:
                return candidate
        raise RuntimeError("could not mint a free finding id")

    number = 0
    for value in taken:
        parsed = parse_local_id(value)
        if parsed and parsed[1] > number:
            number = parsed[1]
    folder = kind_dir(root, kind, board)
    if folder.is_dir():
        # Filename prefixes too, so a half-written document still burns its id.
        for p in folder.rglob("*.md"):
            m = _FILENAME_ID_RE.match(p.name)
            parsed = parse_local_id(m.group(1)) if m else None
            if parsed and parsed[1] > number:
                number = parsed[1]
    number += 1

    width = cfg.get("id_width", DEFAULTS["id_width"])
    length = cfg.get("suffix_length", DEFAULTS["suffix_length"])
    if length <= 0:
        return f"{prefix}-{number:0{width}d}"
    for _ in range(100):
        candidate = f"{prefix}-{number:0{width}d}.{gen_suffix(length)}"
        if candidate not in taken:
            return candidate
    raise RuntimeError(
        f"could not draw a free {length}-char suffix; raise suffix_length in {CONFIG_NAME}")


# ASCII only. Anything else is dropped rather than transliterated: `\w` with
# re.UNICODE used to keep every Unicode word character, and a transliterated
# slug is greppable in neither the source language nor English. See
# guides/rationale.md §16.
_SLUG_RE = re.compile(r"[^a-z0-9\s-]")


class NeedSlug(Exception):
    """A non-English title, with no English slug given for it."""


_NON_ASCII = re.compile(r"[^\x00-\x7f]")


def slugify(title: str, given: str | None = None, max_words: int = 5) -> str:
    """The filename's readable half, always English.

    An English title slugifies itself. Anything else needs `given`: whoever
    wrote the title can say it in English, and no mechanical rule can. A title
    with one Cyrillic word is caught too, because stripping it silently is how
    a filename ends up meaning something else than the document.
    """
    if given is None and _NON_ASCII.search(title):
        raise NeedSlug(
            f"{title!r} is not English, so it cannot name its own file. "
            f"Filenames stay English whatever the document's language: "
            f"transliteration is neither, and greppable in neither. "
            f"Pass --slug with three or four English words, "
            f"e.g. --slug no-effect-band"
        )
    s = _SLUG_RE.sub("", (given if given is not None else title).lower())
    words = [w for w in s.split() if w][:max_words]
    slug = "-".join(words)
    if not slug:
        raise NeedSlug(f"--slug {given!r} leaves nothing usable: "
                       f"three or four English words, letters and digits")
    return slug


# --- frontmatter --------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta, _ = _parse_block(lines[1:end], 0, 0)
    body = "\n".join(lines[end + 1:])
    if body and not body.endswith("\n"):
        body += "\n"
    return meta, body.lstrip("\n")


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _significant(lines, i):
    """Index of the next line that is neither blank nor a comment."""
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith("#"):
            return i
        i += 1
    return len(lines)


def _parse_block(lines, i, indent):
    """Parse a mapping or a sequence starting at `indent`. Returns (value, i)."""
    i = _significant(lines, i)
    if i >= len(lines) or _indent_of(lines[i]) < indent:
        return None, i
    if lines[i].strip().startswith("- "):
        return _parse_sequence(lines, i, indent)
    return _parse_mapping(lines, i, indent)


def _parse_mapping(lines, i, indent):
    out: dict = {}
    while True:
        i = _significant(lines, i)
        if i >= len(lines):
            break
        line = lines[i]
        if _indent_of(line) < indent:
            break
        stripped = line.strip()
        if ":" not in stripped:
            raise ValueError(f"frontmatter: cannot parse line {stripped!r}")
        key, _, rest = stripped.partition(":")
        key, rest = key.strip(), _strip_comment(rest)
        if rest == "":
            nxt = _significant(lines, i + 1)
            if nxt < len(lines) and _indent_of(lines[nxt]) > indent:
                value, i = _parse_block(lines, i + 1, _indent_of(lines[nxt]))
                out[key] = value
                continue
            out[key] = None
            i += 1
            continue
        out[key] = _parse_value(rest)
        i += 1
    return out, i


def _parse_sequence(lines, i, indent):
    out: list = []
    while True:
        i = _significant(lines, i)
        if i >= len(lines):
            break
        line = lines[i]
        if _indent_of(line) != indent or not line.strip().startswith("- "):
            break
        item = _strip_comment(line.strip()[2:])
        # `- key: value` opens a mapping whose remaining keys are indented to
        # where that first key starts.
        if ":" in item and not item.startswith(("'", '"', "[")):
            inner_indent = _indent_of(line) + 2
            sub_lines = [" " * inner_indent + item] + lines[i + 1:]
            value, consumed = _parse_mapping(sub_lines, 0, inner_indent)
            out.append(value)
            i += consumed
            continue
        out.append(_parse_value(item))
        i += 1
    return out, i


def _strip_comment(v: str) -> str:
    """Drop a trailing ` # ...` comment, respecting quotes.

    The shipped templates document each vocabulary inline - `status: idea
    # idea | active | hold | ...` - which is the whole point of them: a student
    editing the file sees the allowed values without opening anything else. So
    the parser has to tolerate what the templates teach.
    """
    out: list[str] = []
    quote = None
    for i, ch in enumerate(v):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or v[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).strip()


def _parse_value(v: str):
    if v == "" or v.lower() in {"null", "~"}:
        return None
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    if v == "{}":
        return {}
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [] if not inner else [_parse_scalar(x.strip()) for x in inner.split(",")]
    return _parse_scalar(v)


def _parse_scalar(v: str):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


_FIELD_ORDER = (
    "id", "title", "type", "audience", "status", "class", "date",
    "created", "updated", "criterion_set",
    "experiments", "origin", "run",
    "finding", "successor", "corrects", "superseded_by", "based_on",
    "motivated_by",
)


def dump_frontmatter(meta: dict, body: str) -> str:
    keys = [k for k in _FIELD_ORDER if k in meta]
    keys += [k for k in meta if k not in _FIELD_ORDER]
    lines = ["---"]
    for k in keys:
        lines.extend(_dump_entry(k, meta[k], 0))
    lines.append("---")
    body = body.lstrip("\n")
    out = "\n".join(lines) + "\n\n" + body
    return out if out.endswith("\n") else out + "\n"


def _dump_entry(key, value, indent):
    pad = " " * indent
    if isinstance(value, dict) and value:
        out = [f"{pad}{key}:"]
        for k, v in value.items():
            out.extend(_dump_entry(k, v, indent + 2))
        return out
    if isinstance(value, list) and value and any(isinstance(x, dict) for x in value):
        out = [f"{pad}{key}:"]
        for item in value:
            first = True
            for k, v in item.items():
                sub = _dump_entry(k, v, indent + 4)
                sub[0] = (pad + "  - " + sub[0].lstrip()) if first else sub[0]
                first = False
                out.extend(sub)
        return out
    return [f"{pad}{key}: {_dump_value(value)}"]


def _dump_value(v) -> str:
    if v is None:
        return ""
    if isinstance(v, dict):
        return "{}"
    if isinstance(v, list):
        return "[" + ", ".join(_dump_scalar(x) for x in v) + "]"
    return _dump_scalar(v)


_NUMERIC_RE = re.compile(r"-?\d+")


def _dump_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()[:10]
    s = str(v)
    # Quote anything that would read back as something else. `id: "0042"` loses
    # its padding the first time a rewrite touches the frontmatter otherwise.
    if s == "" or any(c in s for c in ":#[]{}\"'") or _NUMERIC_RE.fullmatch(s):
        return '"' + s.replace('"', '\\"') + '"'
    return s


# --- editing a template in place ----------------------------------------
#
# Generating a document by parse-then-dump would be shorter and is wrong: it
# drops every comment, and the templates teach through comments. The allowed
# values of `status`, the rule that `experiments` stays empty in `idea`, the
# optional fields shown commented out - all of it lives there, where a student
# editing the file sees it without opening anything else. So a generated
# document is the template with a few values substituted, byte-identical
# otherwise.

_VALUE_LINE = re.compile(r"^(?P<pad>\s*)(?P<key>[A-Za-z_][\w-]*):"
                         r"(?P<gap>[ \t]*)(?P<val>.*?)"
                         r"(?P<comment>(?<=[ \t])#.*)?$")


def set_field(text: str, dotted_key: str, value) -> str:
    """Set `key` or `parent.key` in the frontmatter, keeping its comment.

    Raises KeyError when the template has no such line, which is the loud
    failure we want: a silently missing field becomes a missing field in every
    document made from that template.
    """
    parts = dotted_key.split(".")
    lines = text.splitlines()
    idx = _find_field_line(lines, parts)
    if idx is None:
        raise KeyError(f"template has no field {dotted_key!r}")
    m = _VALUE_LINE.match(lines[idx])
    pad, key = m.group("pad"), m.group("key")
    comment = m.group("comment") or ""
    rendered = _dump_value(value)
    line = f"{pad}{key}: {rendered}".rstrip()
    if comment:
        line = f"{line}  {comment.strip()}" if rendered else f"{line}  {comment.strip()}"
    lines[idx] = line
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def uncomment_field(text: str, key: str, value) -> str:
    """Fill a field the template ships commented out, keeping its comment.

    Optional fields ship commented because an empty field invites filling it
    with something invented. Falls back to set_field when the line is already
    live, and raises KeyError when the template has neither.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped.startswith(f"# {key}:") and not stripped.startswith(f"#{key}:"):
            continue
        pad = line[:len(line) - len(stripped)]
        body = stripped.lstrip("#").lstrip()
        m = _VALUE_LINE.match(body)
        comment = (m.group("comment") or "").strip() if m else ""
        rendered = _dump_value(value)
        lines[i] = f"{pad}{key}: {rendered}" + (f"  {comment}" if comment else "")
        return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    return set_field(text, key, value)


def replace_block(text: str, key: str, block_lines: list[str]) -> str:
    """Replace a top-level mapping key and everything indented under it."""
    lines = text.splitlines()
    idx = _find_field_line(lines, [key])
    if idx is None:
        raise KeyError(f"template has no field {key!r}")
    base = _indent_of(lines[idx])
    end = idx + 1
    while end < len(lines):
        s = lines[end]
        if s.strip() and _indent_of(s) <= base:
            break
        end += 1
    return "\n".join(lines[:idx] + block_lines + lines[end:]) + \
        ("\n" if text.endswith("\n") else "")


def _find_field_line(lines: list[str], parts: list[str]) -> int | None:
    """Index of the line defining `parts`, walking into nested mappings.

    Only scans the frontmatter: a `## Status` heading in the body must never be
    mistaken for a field.
    """
    end = len(lines)
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break

    depth_indent = 0
    start = 1 if lines and lines[0].strip() == "---" else 0
    for level, part in enumerate(parts):
        found = None
        for i in range(start, end):
            line = lines[i]
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = _indent_of(line)
            if level > 0 and indent <= depth_indent:
                if found is None and i > start:
                    break
            m = _VALUE_LINE.match(line)
            if not m or m.group("key") != part:
                continue
            if level == 0 and indent != 0:
                continue
            if level > 0 and indent <= depth_indent:
                continue
            found = i
            break
        if found is None:
            return None
        if level == len(parts) - 1:
            return found
        depth_indent = _indent_of(lines[found])
        start = found + 1
    return None


# --- documents ----------------------------------------------------------

def iter_docs(root: Path, kind: str, board: str | None = None):
    """Yield (path, meta, body) for every document of `kind`."""
    folder = kind_dir(root, kind, board)
    if not folder.is_dir():
        return
    for p in sorted(folder.glob("*.md")):
        if p.name.startswith((".", "_")):
            continue
        try:
            meta, body = parse_frontmatter(p.read_text())
        except Exception as exc:
            # Never swallow this: a skipped document is an invisible document,
            # and invisible is how a malformed field passes every gate.
            import sys
            print(f"warning: skipping {p}: {exc}", file=sys.stderr)
            continue
        yield p, meta, body


def iter_all(root: Path, board: str | None = None):
    for kind in KINDS:
        for item in iter_docs(root, kind, board):
            yield (kind, *item)


def as_date(v):
    if not v:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return datetime.fromisoformat(str(v)).date()
    except Exception:
        return None


def today() -> str:
    return date.today().isoformat()


# --- git ----------------------------------------------------------------

def git(root: Path, *args: str, stdin: str | None = None) -> tuple[int, str]:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], input=stdin,
                             capture_output=True, text=True, timeout=60)
        return out.returncode, out.stdout.strip()
    except Exception:
        return 1, ""


TAG_PREFIX = "research-log/"


def keep_tag(kind: str, doc_id: str) -> str:
    """The tag that keeps a record's commit alive past a rewrite of its branch.

    One namespace for every kind, so one pattern protects and lists them all
    and none collides with the project's own tags; the id says the kind. A
    finding's tag drops the check symbol: it may be `*` or `~`, which no ref
    name may carry, and the thirteen data symbols are unique without it.
    """
    if kind == "finding":
        doc_id = str(doc_id)[:FINDING_ID_LEN]
    return f"refs/tags/{TAG_PREFIX}{doc_id}"


def commit_state(root: Path, tag: str, commit: str) -> str:
    """Where a record's commit stands against HEAD.

    `ok`: an ancestor of HEAD, which is where it is when nothing rewrote the
    branch - the record is committed after the code it names. `tagged`: not an
    ancestor, but `tag` holds it. `rewritten`: in the object store and held by
    nothing; rebase_runs.py's to follow. `missing`: not in this repository at
    all - collected after a rewrite, or never fetched. `unknown`: no git, no
    HEAD, or a shallow clone, where the question cannot be answered.
    """
    code, head = git(root, "rev-parse", "--verify", "-q", "HEAD")
    if code != 0 or not head:
        return "unknown"
    if git(root, "rev-parse", "--is-shallow-repository")[1] == "true":
        return "unknown"
    code, full = git(root, "rev-parse", "--verify", "-q", f"{commit}^{{commit}}")
    if code != 0:
        return "missing"
    if git(root, "merge-base", "--is-ancestor", full, head)[0] == 0:
        return "ok"
    code, tagged = git(root, "rev-parse", "--verify", "-q", f"{tag}^{{commit}}")
    if code == 0 and tagged == full:
        return "tagged"
    return "rewritten"


def commit_block(kind: str) -> str:
    """The frontmatter mapping that carries a record's commit."""
    return "origin" if kind == "finding" else "run"


def local_project(root: Path, cfg: dict) -> str:
    """The name findings minted here carry in `origin.project`, as new.py stamps it."""
    return cfg.get("project") or root.name


# --- locking ------------------------------------------------------------

@contextmanager
def board_lock(root: Path, board: str | None = None):
    """Exclusive lock while allocating an id and writing one file.

    Scoped to one checkout, which is what makes concurrent agents on a shared
    working tree safe - and what cannot help two separate clones. That is what
    the random suffix is for.
    """
    base = board_root(root, board)
    base.mkdir(parents=True, exist_ok=True)
    # Outside the repository on purpose. A lock file inside it would show up in
    # `git status`, and record_run.py refuses to run on a dirty tree - so the
    # act of taking the lock would block the tool that takes it.
    import hashlib
    import tempfile
    digest = hashlib.sha256(str(base.resolve()).encode()).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"research-log-{digest}.lock"
    with open(lock_path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
