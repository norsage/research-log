#!/usr/bin/env python3
"""Set up a research log in the current directory, from a brief.

    init.py                      # reads ./brief.md
    init.py --brief ../task.md   # or wherever the assignment lives
    init.py --lang ru --yes

Runs where it is invoked, like `git init`, and never asks where the project is.
It asks for one thing instead: a brief. No brief means it stops, which is also
what catches an agent started in the wrong directory.

Writes vision.md, conventions.md, conventions-local.md and .research-log.md
on the board, and nothing at the project root: pointing AGENTS.md or CLAUDE.md
at the board is left to the agent, from templates/<lang>/agents-section.md.
The brief's question is copied into vision.md. Nothing else is filled in:
vision.md's directions section starts empty, and a section the brief omits is
the work of whoever takes the project on, which this script only names on the
way out.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CONFIG_NAME, KINDS, LANGS, board_root, load_config, parse_frontmatter,
    set_field, skill_root,
)

BRIEF_NAMES = ("brief.md", "BRIEF.md", "docs/brief.md")

# Sections copied from the brief into vision.md, as (keywords that find it in
# the brief, keywords that find it in vision.md). Matched as lowercase
# substrings of the heading text. A brief that omits one leaves vision.md's own
# template text in place, which is the prompt to write it later.
COPIED_SECTIONS = {
    "en": [(("question",), ("question",))],
    "ru": [(("вопрос",), ("вопрос",))],
}

# Optional sections, by a keyword in their heading. A brief that omits one is
# not incomplete; the gap is reported as a first step, never filled in.
OPTIONAL_SECTIONS = {
    "en": [("data", ("data",)),
           ("constraints", ("constraint", "limit")),
           ("a hypothesis with a refutation criterion", ("hypothesis",)),
           ("what must be decided before the first computation",
            ("order of work", "before the first computation"))],
    "ru": [("данные", ("данн",)),
           ("ограничения", ("ограничен",)),
           ("гипотеза с критерием опровержения", ("гипотез",)),
           ("что должно быть решено до первых расчётов",
            ("порядок работ", "до первых расч"))],
}

# --- reading the brief --------------------------------------------------

def find_brief(root: Path, given: str | None) -> Path:
    if given:
        path = Path(given).expanduser()
        if not path.is_file():
            raise SystemExit(f"no brief at {path}")
        return path.resolve()
    for name in BRIEF_NAMES:
        path = root / name
        if path.is_file():
            return path
    raise SystemExit(
        f"no brief in {root}. A brief is the one thing initialisation needs: "
        f"write one from templates/<lang>/brief.md, or pass --brief PATH. "
        f"If this is not the project's directory, that is the other thing "
        f"this message catches."
    )


def sections(text: str) -> list[tuple[str, str]]:
    """(heading, body) for every level-2 heading, in order."""
    out, heading, body = [], None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if heading is not None:
                out.append((heading, "\n".join(body).strip()))
            heading, body = line[3:].strip(), []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        out.append((heading, "\n".join(body).strip()))
    return out


def section_body(text: str, keywords) -> str | None:
    for heading, body in sections(text):
        low = heading.lower()
        if any(k in low for k in keywords):
            return body
    return None


def detect_lang(text: str) -> str:
    cyrillic = len(re.findall(r"[а-яё]", text, re.IGNORECASE))
    return "ru" if cyrillic > len(re.findall(r"[a-z]", text, re.IGNORECASE)) else "en"


# --- writing the board --------------------------------------------------

def template(lang: str, name: str) -> str:
    path = skill_root() / "templates" / lang / f"{name}.md"
    if not path.is_file():
        raise SystemExit(f"no template: {path}")
    return path.read_text()


def replace_section(text: str, keywords, body: str) -> str:
    """Swap one section's body, keeping its heading and everything around it."""
    lines, out, inside, done = text.splitlines(), [], False, False
    for line in lines:
        if line.startswith("## "):
            if inside:
                inside = False
            elif not done and any(k in line[3:].strip().lower() for k in keywords):
                out.append(line)
                out.append("")
                out.append(body)
                out.append("")
                inside = done = True
                continue
        if not inside:
            out.append(line)
    return "\n".join(out) + "\n"


def targets(board: Path) -> dict[str, Path]:
    return {
        "vision": board / "vision.md",
        "conventions": board / "conventions.md",
        "conventions-local": board / "conventions-local.md",
        "config": board / CONFIG_NAME,
    }


def task_tracker_installed(root: Path) -> bool:
    for base in (root / ".claude" / "skills", Path.home() / ".claude" / "skills"):
        if (base / "task-tracker" / "SKILL.md").is_file():
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", metavar="PATH", help=f"default: one of {BRIEF_NAMES}")
    ap.add_argument("--lang", choices=LANGS, help="overrides the brief's frontmatter")
    ap.add_argument("--project", help="overrides the brief's frontmatter")
    ap.add_argument("--board")
    ap.add_argument("--yes", action="store_true",
                    help="answer the one question this asks, for non-interactive use")
    args = ap.parse_args()

    root = Path.cwd().resolve()
    board = board_root(root, args.board)
    brief_path = find_brief(root, args.brief)
    brief = brief_path.read_text()
    meta, _ = parse_frontmatter(brief)

    # Only a config file on disk outranks the brief's own language. load_config
    # returns DEFAULTS when there is none, and `lang: en` out of that default
    # gave a Russian brief an English board — the ordinary case, because a brief
    # composed in the interview carries no frontmatter at all.
    existing_lang = None
    if (board / CONFIG_NAME).is_file():
        existing_lang = load_config(root, args.board).get("lang")
    lang = args.lang or meta.get("lang") or existing_lang
    if lang not in LANGS:
        lang = detect_lang(brief)
    project = args.project or meta.get("project") or root.name

    # Guard one: a board already here. conventions-local.md is the project's
    # own file and the skill never touches it, so re-initialising would be the
    # one way to lose it.
    existing = [p for p in targets(board).values() if p.exists()]
    existing += [board / d for d, _ in KINDS.values() if (board / d).is_dir()]
    if existing:
        print("a board is already set up here:", file=sys.stderr)
        for p in existing:
            print(f"  {p.relative_to(root)}", file=sys.stderr)
        raise SystemExit("refusing to re-initialise over it")

    # Guard two: no git. Every check this skill makes rests on the commit.
    if not (root / ".git").exists() and any(root.iterdir()) and not args.yes:
        if not sys.stdin.isatty():
            raise SystemExit(f"{root} is not a git repository. Run `git init` first, "
                             f"or pass --yes to set up the board anyway.")
        answer = input(f"{root} is not a git repository, and record_run.py needs "
                       f"one. Set up the board anyway? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            raise SystemExit("aborted")

    board.mkdir(parents=True, exist_ok=True)
    written = []


    vision = template(lang, "vision")
    copied = []
    for from_brief, into_vision in COPIED_SECTIONS[lang]:
        body = section_body(brief, from_brief)
        copied.append(body)
        if body:
            vision = replace_section(vision, into_vision, body)
    question = copied[0]  # the first pair is the question, the one required section
    (board / "vision.md").write_text(vision)
    written.append(board / "vision.md")

    for name in ("conventions", "conventions-local"):
        (board / f"{name}.md").write_text(template(lang, name))
        written.append(board / f"{name}.md")

    config = set_field(template(lang, "config"), "lang", lang)
    config = set_field(config, "project", project)
    (board / CONFIG_NAME).write_text(config)
    written.append(board / CONFIG_NAME)

    if not brief_path.is_relative_to(root):
        (board / "brief.md").write_text(brief)
        written.append(board / "brief.md")

    for path in written:
        print(path.relative_to(root))

    print(f"\nproject: {project}   lang: {lang}   brief: {brief_path}", file=sys.stderr)
    if not question:
        print("the brief has no question section, so vision.md keeps its template "
              "text. That section is the one a brief has to carry.", file=sys.stderr)
    print(f"add templates/{lang}/agents-section.md to the project's AGENTS.md "
          f"or CLAUDE.md", file=sys.stderr)
    print("run rebase_runs.py --install-hooks once in every clone", file=sys.stderr)
    if task_tracker_installed(root):
        print("the task-tracker skill is installed", file=sys.stderr)

    headings = " | ".join(h.lower() for h, _ in sections(brief))
    missing = [label for label, keys in OPTIONAL_SECTIONS[lang]
               if not any(k in headings for k in keys)]
    if missing:
        print("\nthe brief does not say, and these are first steps rather than "
              "gaps to fill in:", file=sys.stderr)
        for label in missing:
            print(f"  - {label}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
