# push

**name:** push
**description:** Safe commit-and-push workflow with change classification and test gate.

## Goal

Ensure every push is clean: correct commit message, tests pass for code changes, rebased before push.

## When to use

- When work on a task or plan is complete and ready to share.
- Before closing a session if code or docs changed.

## When NOT to use

- Mid-task; finish the task first.
- Do not push if tests are failing.

## Inputs

None (reads repo state automatically).

## Procedure

1. Run `git log --oneline -15` to understand recent work.
2. Read active plans in `docs/plans/` and compare against recent commits.
   - Update task/step status to reflect completed work.
   - If the plan is fully complete, move it to `docs/plans/archive/` using `git mv`.
3. Stage changed files and commit with a conventional commit message.
4. Run `git diff origin/master..HEAD` to classify changes:
   - **Documentation only** (`.md`, `.txt`, `docs/`, comment-only changes): tests may be skipped.
   - **Any code or behavior change** (`.py`, `src/`, `tests/`): MUST run `unset VIRTUAL_ENV && uv run pytest` and all tests must pass.
5. If uncertain about classification → treat as code change.
6. Run `git fetch origin && git rebase origin/master`.
7. Run `git push`.

## Output format

- Confirmation of commit hash.
- Test run result (pass/skip with reason).
- Push confirmation.

## Guardrails

- Follow all rules in `CLAUDE.md`.
- NEVER push if tests fail.
- NEVER use `git pull` without `--rebase`.
- If classification is ambiguous → STOP and ask.
