# CLAUDE.md — HARD CONSTRAINTS

## Priority (conflict → higher wins; tie → ask user)

1. User explicit instructions
2. Superpowers skills & this file
3. Other documents

## Rules

**0. Session Start** — Before ANY action (including skill invocation), read `MISTAKES.md` and load all listed mistakes into active context. Rule violation → STOP + ask. New uncovered error → STOP, summarize 1–2 bullets, ask if new rule. No auto-logging.

**1. Superpowers** — Always use matching skill; never reimplement it yourself.

**2. Git** — Rebase only: always `git pull --rebase`, never plain pull.

**3. TDD** — All code changes need tests that actually run (not comments).

**4. Verification** — Never mark complete or claim features exist without code verification (`superpowers:verification-before-completion`).

**5. Shell (Windows)** — Bash tool = Git Bash (MSYS/MINGW64), not CMD/PS. Always use Unix-style paths: Windows drives map as `/c/`, `/d/`, etc. (e.g. `/d/dev/project`). Bash tool CWD does not persist between calls — chain commands with `&&` instead of `cd` + separate call. Windows-only ops: `cmd.exe /c "..."`. PS1 scripts: `powershell.exe -ExecutionPolicy Bypass -File x.ps1`. Forbidden: CMD's `cd /d` drive-switch flag, `dir` command, backslash paths (`D:\foo`). **uv**: before any `uv run` command, run `unset VIRTUAL_ENV` if `VIRTUAL_ENV` is set — avoids the "does not match project environment path" warning.

**6. Plans** — Active only in `docs/plans/`. Completed → move to `docs/plans/archive/` using `git mv` (never native `mv`). Never read archive during planning.

**7. Finishing** — When using `superpowers:finishing-a-development-branch`, do NOT present options or ask — execute Option 1 (merge locally to master) directly and immediately, unless the user has explicitly said otherwise beforehand.
