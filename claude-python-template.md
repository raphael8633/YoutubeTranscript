# Claude Python Project Bootstrap

新專案依照此文件從零重建 Claude + Python + uv 開發環境。

---

## 目錄結構

```
<project>/
├── CLAUDE.md
├── MISTAKES.md
├── pyproject.toml
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── docs/
│   └── plans/
│       └── archive/        ← 新增 .gitkeep
└── .claude/
    ├── settings.json
    └── skills/
        ├── start/
        │   └── SKILL.md
        ├── push/
        │   └── SKILL.md
        └── create-skill/
            └── SKILL.md
```

---

## 初始化步驟

```bash
# 1. 建立專案目錄並初始化 git
mkdir <project> && cd <project>
git init

# 2. 初始化 uv 專案
uv init --no-readme

# 3. 建立目錄骨架
mkdir -p src tests docs/plans/archive .claude/skills/start .claude/skills/push .claude/skills/create-skill
touch src/__init__.py tests/__init__.py docs/plans/archive/.gitkeep

# 4. 依照下方各節建立檔案內容

# 5. 安裝 pytest
uv add --dev pytest

# 6. 初次 commit
git add .
git commit -m "chore: bootstrap project with Claude config"
```

---

## `CLAUDE.md`

```markdown
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
```

---

## `MISTAKES.md`

```markdown
# Mistakes (Do Not Repeat)

- ❌ **Windows Bash tool is Git Bash (MSYS/MINGW64)**: Do NOT use `cd /d`, `dir`, or CMD backslash paths. Use Unix paths (`/d/dev/...`), `ls`, `mkdir -p`. For `mklink` use `cmd.exe /c "..."`. For `.ps1` scripts use `powershell.exe -ExecutionPolicy Bypass -File script.ps1`.
- ❌ **Git worktree cleanup order**: Remove the worktree BEFORE deleting the branch. `git branch -d` fails if the branch is still checked out in a worktree. Correct order: `git worktree remove <path>` then `git branch -d <branch>`.
```

---

## `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c \"cat MISTAKES.md 2>/dev/null || true\""
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git fetch:*)",
      "Bash(git rebase:*)",
      "Bash(git pull --rebase:*)",
      "Bash(git worktree:*)",
      "Bash(git log:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git checkout:*)",
      "Bash(git merge:*)",
      "Bash(git branch:*)",
      "Bash(git mv:*)",
      "Bash(git check-ignore:*)",
      "Bash(uv run pytest:*)",
      "Bash(uv run python -m pytest:*)",
      "Bash(uv sync:*)",
      "Bash(uv add:*)",
      "Bash(gh workflow:*)",
      "Bash(gh run:*)",
      "Bash(gh cache:*)",
      "Bash(ls:*)",
      "Bash(echo:*)",
      "Bash(grep:*)"
    ]
  },
  "enabledPlugins": {
    "superpowers@superpowers-marketplace": true
  }
}
```

---

## `.claude/skills/start/SKILL.md`

```markdown
# start

**name:** start
**description:** Orient the agent at the beginning of a session.

## Goal

Give the agent just enough context to begin work without asking redundant questions.

## When to use

- At the start of every new work session.
- When resuming after a break and context is unclear.

## When NOT to use

- Mid-task; do not re-run start if already oriented.

## Inputs

None.

## Procedure

1. Read `README.md` to understand the project.
2. Read `MISTAKES.md` to load known pitfalls into context.
3. List files under `docs/plans/` (sorted by filename, ascending) to check for active plans.
4. For each plan in order:
   a. Read the plan file; note target files and concrete expected outputs (named functions, removed duplication, structural changes, etc.).
   b. Read each target file and confirm every expected output is present in code. Git modification history is a hint only — code content is the truth.
   c. If all expected outputs confirmed: move to `docs/plans/archive/` using `git mv` and continue.
   d. Otherwise: report the plan as active and **immediately proceed to execute it** using `superpowers:executing-plans`. Do NOT ask for confirmation first. Stop iterating.
5. If no active plan remains, ask the user what they want to work on today.

## Output format

- One-sentence project summary.
- Active plan name (or "no active plan").
- Brief rationale: which plans were auto-archived vs. which is the current active plan.

## Guardrails

- Follow all rules in `CLAUDE.md`.
- Base completion judgement on whether the plan's concrete expected outputs are present in the code — not on git history or commit messages alone.
- When an active plan is found, proceed directly — **do not ask the user for confirmation** before invoking `superpowers:executing-plans`.
```

---

## `.claude/skills/push/SKILL.md`

```markdown
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
```

---

## `.claude/skills/create-skill/SKILL.md`

```markdown
# create-skill

**name:** create-skill
**description:** Scaffold a new shared skill in `.claude/skills/` with all required sections.

## Goal

Ensure every new skill has consistent structure so Claude can understand and invoke it.

## When to use

- When adding a new reusable workflow.

## When NOT to use

- For one-off tasks that will not be reused.
- For project-specific logic that should live in `CLAUDE.md` instead.

## Inputs

- `skill_name`: kebab-case name for the skill (e.g. `run-tests`).
- `description`: one-sentence description.

## Procedure

1. Create directory `.claude/skills/<skill_name>/`.
2. Create `.claude/skills/<skill_name>/SKILL.md` with the template below.
3. Fill in all sections — do NOT leave placeholders.
4. Commit: `git add .claude/skills/<skill_name>/SKILL.md && git commit -m "feat: add <skill_name> skill"`.

### Required SKILL.md template

\`\`\`markdown
# <skill_name>

**name:** <skill_name>
**description:** <one sentence>

## Goal
## When to use
## When NOT to use
## Inputs
## Procedure
## Output format
## Guardrails
\`\`\`

## Output format

- Confirmation of file path created.

## Guardrails

- Follow all rules in `CLAUDE.md`.
- `description` MUST include intent, not just name.
- `When NOT to use` section is REQUIRED.
- `Guardrails` section MUST reference `CLAUDE.md`.
- `Procedure` MUST be a numbered list.
```

---

## `pyproject.toml`

```toml
[project]
name = "project-name"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.pytest.ini_options]
testpaths = ["tests"]
```

> 記得將 `name` 改為實際專案名稱。

---

## 新增專案特定 MISTAKES

每次遇到新的可重複錯誤，依格式追加到 `MISTAKES.md`：

```markdown
- ❌ **錯誤標題**: 說明錯誤情境與正確做法。
```
