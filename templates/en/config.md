---
# Board settings. Copy to <board root>/.research-log.md, next to
# hypotheses/ and experiments/, not inside them. Every key is optional; the
# values below are the defaults.

# Language of the documents this board creates: en or ru.
#
# It selects which templates/<lang>/ a new document is cut from, and nothing
# else. Keys and enum values (status, criterion_set, origin, audience) are
# identical in both languages, because they are read by check.py, by the
# export, and eventually by the shared base. Override per document with
# --lang; the two can coexist on one board.
lang: en

# Name this project is known by outside itself. It is stamped into every
# finding as origin.project, and that stamp is what says where a claim came
# from once it has left. Defaults to the directory name, which is usually
# right and occasionally embarrassing.
project: ""

# Characters of random discriminator appended to each local id: H-0042.k3f.
# Applies to every kind except findings, whose identifier is opaque and
# globally unique by construction.
#
# This is a wire format rather than a preference. Commit it, and keep it the
# same for every writer on this board. The number is allocated as max+1, so
# two branches forked from one commit both mint 0042; the suffix is what keeps
# them apart. Sizing, as P(collision) for k branches contesting one number,
# and board-wide for k branches creating n documents each:
#
#   width   k=2      k=3      k=10     k=10, n=10
#   2       0.098%   0.29%    4.3%     36%
#   3       0.003%   0.009%   0.14%    1.4%
#   4       0.0001%  0.0003%  0.004%   0.04%
#
# 0 disables suffixes entirely. Only safe on a genuinely single-writer board,
# and solo is not single-writer: worktrees, a second machine, or a swarm of
# agents under one git identity are all concurrent writers. Mixing 0 with a
# nonzero width across writers is the one unsafe combination: a bare `H-0042`
# is then both a valid id and a prefix of `H-0042.k3f`.
#
# Raising it later is free: numbers never overlap across time, so old bare ids
# coexist with new suffixed ones.
suffix_length: 3

# Zero-padding of the number part.
id_width: 4
---

# Board settings

The frontmatter above configures this board. The body is yours, and is a good
place for what belongs to this board rather than to the tool: which run tracker
the experiments point at, where the raw data lives, who reads the findings.
