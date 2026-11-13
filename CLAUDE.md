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
- yt-dlp、youtube-transcript-api、faster-whisper are the optional extra `local`; this VPS installs without it (YouTube blocks cloud IPs) and runs Gemini only. Modules import them guarded; `pipeline.local_available()` gates the local path, and the module tests for it skip when the extra is absent
- All tests use mocks; no integration tests hit YouTube or Whisper

## Project-Specific Overrides

- **Git:** Rebase only — always `git pull --rebase`, never plain pull
- **uv:** Before any `uv run` command, run `unset VIRTUAL_ENV` if set — avoids environment path mismatch warning

## Notes

- raph-power provides: task classification (S0-S3), TDD, verification, review gates, git discipline, debugging, subagent delegation, mistake tracking
- This file should only contain project-specific rules and quick commands
- `.mistakes/` registry (raph-mistakes CLI; `raph-mistakes capture` to add, `check` to scan) is maintained per-project with entries specific to this codebase
