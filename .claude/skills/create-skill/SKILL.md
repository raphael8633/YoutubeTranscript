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

```markdown
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
```

## Output format

- Confirmation of file path created.

## Guardrails

- Follow all rules in `CLAUDE.md`.
- `description` MUST include intent, not just name.
- `When NOT to use` section is REQUIRED.
- `Guardrails` section MUST reference `CLAUDE.md`.
- `Procedure` MUST be a numbered list.
