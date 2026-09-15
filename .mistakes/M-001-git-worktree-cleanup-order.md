---
id: M-001
title: Git worktree cleanup order
severity: soft
triggers:
  keywords:
  - git worktree remove
  - git branch -d fails
  - branch checked out in worktree
  commands:
  - git worktree remove <path>
  - git branch -d <branch>
guard:
  command: Always remove the worktree BEFORE deleting the branch — git worktree remove <path>, then git branch -d <branch>.
status: active
---

## Symptom
`git branch -d` fails because the branch is still checked out in a worktree

## Resolution
`git worktree list` shows no stale entries; `git branch -d <branch>` succeeds
