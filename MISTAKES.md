# Mistakes (Active)

This file keeps only active high-risk mistakes (target <= 20).
Historical records are archived under `docs/mistakes/archive/`.

## Entry Template

### M-XXX <short title>
- Trigger:
- Symptom:
- Guard:
- Verification:

## Active Entries

### M-001 Git worktree cleanup order
- Trigger: Removing a git worktree and its branch
- Symptom: `git branch -d` fails because the branch is still checked out in a worktree
- Guard: Always remove the worktree BEFORE deleting the branch: `git worktree remove <path>` then `git branch -d <branch>`
- Verification: `git worktree list` shows no stale entries; `git branch -d <branch>` succeeds

## Archived References
<!-- Trigger keywords from archived entries. Maintained by raph-mistakes — do not edit manually. -->
<!-- Format: - M-XXX: keyword1, keyword2, keyword3 → archived YYYY-MM-DD -->
