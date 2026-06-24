# Pending Todos (Phase 1 Capture Contract)

This folder defines how pending todo items are captured and persisted for milestone planning.

## Scope

Phase 1 covers **capture and persistence only**:

- Write pending todo files to `.planning/todos/pending/`
- Enforce a consistent schema and section structure
- Preserve local-first, human-editable markdown records

Out of scope for this phase:

- Triage/promotion workflow (Phase 2)
- Roadmap linkage via `resolves_phase` tagging (Phase 3)

## Capture Entry Point

Use `gsd-capture` as the primary entrypoint for creating pending todo items.

Expected output location:

- `.planning/todos/pending/*.md`

## File Naming

Recommended filename format:

- `YYYYMMDD_<short-slug>.todo.md`

Example:

- `20260624_capture-todo-contract.todo.md`

## Required Frontmatter

Each pending todo file must include:

- `created` (ISO date)
- `title`
- `area`
- `status` (default: `pending`)
- `files` (array)

## Required Body Sections

Each pending todo file must include:

- `## Problem`
- `## Solution`
- `## Notes`

## Validation Behavior (Lenient)

Capture uses **lenient validation**:

- Missing fields are warned, not blocked
- Incomplete entries may still be persisted for later refinement
- `status: pending` should remain the default unless explicitly changed

## Deduplication Behavior (Soft)

Capture uses **soft dedupe** based on `title+area` similarity:

- System warns when probable duplicates are detected
- User retains control to keep, merge, or defer items
- No hard blocking of capture in Phase 1

## Example Pending Todo

```markdown
---
created: 2026-06-24
title: "Standardize todo capture contract"
area: "planning"
status: pending
files:
  - .planning/todos/pending/_TEMPLATE.todo.md
  - .planning/todos/README.md
---

## Problem

Pending todo ideas are captured inconsistently, making later triage harder.

## Solution

Introduce a canonical markdown template with required frontmatter and body sections.

## Notes

Keep this phase limited to capture/persistence; defer triage and linkage behavior.
```

## Verification Checklist

- [ ] Create one pending todo from `_TEMPLATE.todo.md`
- [ ] Confirm required frontmatter keys are present
- [ ] Save under `.planning/todos/pending/`
- [ ] Reopen the file and confirm `Problem`, `Solution`, and `Notes` content is unchanged
