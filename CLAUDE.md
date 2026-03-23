# CLAUDE.md — PROJECT RULES

## Entry Point

`/raph-core` is enforced via raph-power plugin hook (UserPromptSubmit) — no manual reminder needed.

## Quick Commands

- **test:** `unset VIRTUAL_ENV && uv run pytest`
- **lint:** (none configured)
- **dev:** `unset VIRTUAL_ENV && uv run python main.py <url>`

## Project Context

<!-- Semantic hints that Glob/Grep cannot discover -->
- `pipeline.py` is the stable public API — a future web layer would call `pipeline.run()` directly
- `main.py` is a thin wrapper that calls `cli.main()`; entry point logic lives in `cli.py`
- `faster-whisper` downloads model weights on first use (~150 MB for `base`) — tests mock this
- All tests use mocks; no integration tests hit YouTube or Whisper

## Project-Specific Overrides

- **Git:** Rebase only — always `git pull --rebase`, never plain pull
- **Finishing:** When using `superpowers:finishing-a-development-branch`, execute Option 1 (merge locally to master) directly — do not present options or ask
- **uv:** Before any `uv run` command, run `unset VIRTUAL_ENV` if set — avoids environment path mismatch warning

## Notes

- raph-power plugin supersedes superpowers — only raph-power is enabled in `settings.json`
- raph-power provides: task classification (S0-S3), TDD, verification, review gates, git discipline, debugging, subagent delegation, mistake tracking
- This file should only contain project-specific rules and quick commands
- MISTAKES.md is maintained per-project with entries specific to this codebase
