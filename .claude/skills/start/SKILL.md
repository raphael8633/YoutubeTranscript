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
