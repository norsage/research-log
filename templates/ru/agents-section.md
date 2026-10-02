## Журнал исследования

Перед любой задачей прочитай:

1. [`docs/conventions.md`](docs/conventions.md): где что лежит, куда класть
   новый документ и что делать в каждой ситуации. Файл поставляется скиллом
   research-log, править его не нужно.
2. [`docs/conventions-local.md`](docs/conventions-local.md): правила этого
   проекта — стек, окружение, структура кода, инструменты, тесты.
3. [`docs/vision.md`](docs/vision.md): цель проекта и её направления.

Один раз в каждом клоне установи git-хуки — git их не копирует:
`python3 .agents/skills/research-log/scripts/rebase_runs.py --install-hooks`
(если скилл установлен глобально — `~/.agents/skills/` вместо
`.agents/skills/`). Без них amend или rebase не переносит `run.commit` записей,
и ничто не остановит push, после которого запись останется без своего коммита;
`check.py` предупреждает, пока хуки не установлены. Что делать после rebase
на сервере — в
[`.agents/skills/research-log/references/git-hosting.md`](.agents/skills/research-log/references/git-hosting.md#when-someone-presses-the-rebase-button).
