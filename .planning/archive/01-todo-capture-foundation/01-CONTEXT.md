# Phase 1: Todo Capture Foundation - Context

**Gathered:** 2026-06-24
**Status:** Ready for planning

## Phase Boundary

This phase delivers a reliable todo-capture foundation: users can create and persist pending todo items with consistent structure in `.planning/todos/pending/`.

## Implementation Decisions

### Todo file schema

- **D-01:** Use YAML frontmatter plus markdown body for each pending todo file.
- **D-02:** Standard frontmatter fields include `created`, `title`, `area`, `status`, and `files`.
- **D-03:** Body sections should include `Problem`, `Solution`, and `Notes` for downstream triage clarity.

### Capture entrypoint

- **D-04:** Use `gsd-capture` as the primary capture path and standardize its todo output format.

### Validation behavior

- **D-05:** Use lenient validation during capture: persist entry with warnings and set draft-ready status when required content is incomplete.

### Deduplication policy

- **D-06:** Use soft dedupe based on title+area similarity and warn users; keep final merge/defer decision user-controlled.

### the agent's Discretion

No additional discretionary areas were requested.

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone and scope

- `.planning/ROADMAP.md` — Active milestone v1.1 phase definitions and Phase 1 goal/success criteria.
- `.planning/REQUIREMENTS.md` — Phase 1 requirement mapping for TODO-01 and TODO-02.
- `.planning/PROJECT.md` — Milestone goal and target features for v1.1 `bring`.

### Prior implementation context

- `.planning/phases/999.1-update-extractor-based-on-this-information-ingestion-templat/999.1-01-PLAN.md` — Prior backlog implementation plan that established extractor contract alignment patterns.
- `.planning/phases/999.1-update-extractor-based-on-this-information-ingestion-templat/999.1-01-SUMMARY.md` — Completed summary with validated decisions and implementation outcomes from Phase 999.1.

### External specifications

- No external specs — requirements fully captured in decisions above.

## Existing Code Insights

### Reusable Assets

- `gsd-capture` workflow/command path can be reused as the capture entrypoint instead of introducing a new dedicated command in this phase.

### Established Patterns

- Planning artifacts are markdown + YAML frontmatter driven; this pattern should be preserved for pending todo files.
- Local-first, file-based workflow conventions in this repo favor explicit on-disk records over hidden state.

### Integration Points

- New todo capture output writes to `.planning/todos/pending/`.
- Follow-on phases consume these files for triage and roadmap linkage (`resolves_phase`).

## Specific Ideas

- Keep capture ergonomic by leveraging the existing `gsd-capture` entrypoint.
- Preserve human-editable files while maintaining enough structure for future automation.

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 1-Todo Capture Foundation*  
*Context gathered: 2026-06-24*
