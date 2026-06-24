# Phase 1: Todo Capture Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-24
**Phase:** 1-Todo Capture Foundation
**Areas discussed:** Todo file schema, Capture entrypoint, Validation behavior, Deduplication policy

---

## Todo file schema

| Option | Description | Selected |
| --- | --- | --- |
| YAML frontmatter + markdown body | Frontmatter: created,title,area,status,files; body: Problem/Solution/Notes. | ✓ |
| JSON only | Machine-friendly but less ergonomic for manual edits. | |
| Markdown body only | Flexible but weaker validation/automation. | |

**User's choice:** YAML frontmatter + markdown body
**Notes:** Preferred for human-editable files while keeping reliable structure.

---

## Capture entrypoint

| Option | Description | Selected |
| --- | --- | --- |
| Use `gsd-capture` and standardize its output | Leverage existing command with tightened schema. | ✓ |
| Add dedicated todo capture command/script | More explicit UX, higher implementation overhead. | |
| Manual template file creation only | No automation in this phase. | |

**User's choice:** Use `gsd-capture` and standardize its output
**Notes:** Favors reuse of existing workflow over adding command surface area in Phase 1.

---

## Validation behavior

| Option | Description | Selected |
| --- | --- | --- |
| Strict required fields (fail fast) | Reject write if title/area/problem/solution missing. | |
| Lenient with warnings + status draft | Persist incomplete entries, flag for triage. | ✓ |
| No validation | Fastest entry, low quality control. | |

**User's choice:** Lenient with warnings + status draft
**Notes:** Captures ideas quickly without dropping partially formed entries.

---

## Deduplication policy

| Option | Description | Selected |
| --- | --- | --- |
| Soft dedupe by title+area similarity | Warn and link probable duplicates; user decides merge. | ✓ |
| Hard block exact duplicate title+area | Prevent save when exact match exists. | |
| No dedupe in Phase 1 | Handle duplicates later during triage. | |

**User's choice:** Soft dedupe by title+area similarity
**Notes:** Keeps user control while surfacing probable duplicates early.

---

## the agent's Discretion

No areas were delegated as "you decide".

## Carry-forward from Phase 999.1

- Reuse the proven **human-editable frontmatter + markdown body** artifact style used in prior planning outputs.
- Apply the same **idempotent, warning-first ergonomics** principle from extractor dedupe/error handling to todo capture (warn, preserve user control, avoid destructive behavior).
- Preserve the **local-first file workflow** and explicit on-disk artifacts to keep reviewability and auditability consistent across phases.

## Deferred Ideas

None.
