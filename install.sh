#!/usr/bin/env bash
# Install the research-log skill into ~/.claude/skills/ (global) or
# ./.claude/skills/ (project-local).
#
# Usage:
#   bash install.sh                  # global, copy (default)
#   bash install.sh --project        # project-local, into $(pwd)/.claude/skills/
#   bash install.sh --symlink        # symlink instead of copy (skill devs)
#   bash install.sh --global --symlink
#
# Re-running is idempotent: existing installs are replaced after a prompt.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="research-log"

if [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
    echo "error: $SCRIPT_DIR doesn't look like the skill source (no SKILL.md)" >&2
    exit 1
fi

MODE="copy"
SCOPE="global"

while [ $# -gt 0 ]; do
    case "$1" in
        --global)  SCOPE="global"; shift ;;
        --project) SCOPE="project"; shift ;;
        --symlink) MODE="symlink"; shift ;;
        --copy)    MODE="copy"; shift ;;
        -h|--help)
            sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "unknown option: $1" >&2
            exit 2
            ;;
    esac
done

if [ "$SCOPE" = "global" ]; then
    TARGET_PARENT="$HOME/.claude/skills"
else
    TARGET_PARENT="$(pwd)/.claude/skills"
fi
TARGET="$TARGET_PARENT/$SKILL_NAME"

mkdir -p "$TARGET_PARENT"

if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    echo "existing install at $TARGET will be replaced"
    if [ -t 0 ]; then
        printf "continue? [y/N] "
        read -r ans
        case "$ans" in
            y|Y|yes|YES) ;;
            *) echo "aborted."; exit 1 ;;
        esac
    fi
    rm -rf "$TARGET"
fi

if [ "$MODE" = "symlink" ]; then
    ln -s "$SCRIPT_DIR" "$TARGET"
    echo "symlinked $SCRIPT_DIR -> $TARGET"
else
    # Copy everything except VCS / OS cruft and this skill's own development
    # documents in guides/, which an installed project does not read.
    # --symlink installs the whole checkout, including them.
    if command -v rsync >/dev/null 2>&1; then
        rsync -a \
            --exclude='.git' --exclude='.gitignore' --exclude='.DS_Store' \
            --exclude='__pycache__' --exclude='*.pyc' \
            --exclude='guides' \
            "$SCRIPT_DIR/" "$TARGET/"
    else
        mkdir -p "$TARGET"
        (cd "$SCRIPT_DIR" && \
         find . -type f \
            -not -path './.git/*' -not -name '.DS_Store' \
            -not -path '*/__pycache__/*' -not -name '*.pyc' \
            -not -path './guides/*' \
            -print0 | \
         while IFS= read -r -d '' f; do
            mkdir -p "$TARGET/$(dirname "$f")"
            cp "$f" "$TARGET/$f"
         done)
    fi
    echo "installed $SKILL_NAME to $TARGET"
fi

if [ "$SCOPE" = "project" ]; then
    echo "(project-local; commit .claude/skills/$SKILL_NAME to share with the team)"
fi
