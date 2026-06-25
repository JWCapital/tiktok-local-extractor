# Phase 2: Reprocess Remaining Videos - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-25
**Phase:** 2-Reprocess Remaining Videos
**Areas discussed:** Rights flag, Failed IDs — retry or skip, Legacy exports scope, batch_extract.sh staging glob fix

---

## Rights Flag for Batch Run

| Option | Description | Selected |
|--------|-------------|----------|
| --rights research (keep as-is) | Current default. Appropriate for bookmarked/study content. | ✓ |
| --rights own | For videos the user created or owns. Likely incorrect for TikTok favorites. | |
| --rights permitted | For videos with explicit creator permission. For curated partnerships. | |

**User's choice:** `--rights research` — keep the existing default in batch_extract.sh unchanged.
**Notes:** None.

---

## Failed IDs — Retry or Skip

| Option | Description | Selected |
|--------|-------------|----------|
| Skip them (keep as-is) | Leave failed_ids.txt untouched. batch_extract.sh skips them automatically. | ✓ |
| Clear and retry all 70 | Empty failed_ids.txt before running; re-adds any that fail again. | |
| Retry selectively | Manually review and remove specific IDs from failed_ids.txt. | |

**User's choice:** Skip — leave `failed_ids.txt` untouched.
**Notes:** 70 failed IDs stay skipped; they failed for a reason.

---

## Legacy Exports Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Only the 186 queued URLs | Scope strictly to favs_raw.txt. Legacy exports deferred. | ✓ |
| Include legacy exports | Reprocess all 390 legacy folders through corrected pipeline. | |

**User's choice:** Only the 186 queued URLs.
**Notes:** 390 folders in `_assets/tiktok/legacy_exports/` are out of scope for Phase 2.

---

## batch_extract.sh Staging Glob Fix

| Option | Description | Selected |
|--------|-------------|----------|
| Fix it in Phase 2 | One-line change on line 90: ${OUT_DIR%/*}/_staging/... instead of $OUT_DIR/_staging/... | ✓ |
| Leave it | Link logging fails silently; finalize still works. Fix later. | |

**User's choice:** Fix it in Phase 2 — consistent with Phase 1's intent.
**Notes:** The Phase 1 executor reported "glob not found at line 90" but the glob exists in the current committed file. Fix is one line.

---

## Claude's Discretion

- Whether to run all 186 URLs in one `batch_extract.sh` invocation or split into smaller batches
- Exact progress reporting format in the plan

## Deferred Ideas

- **Legacy exports reprocessing** — 390 folders in `_assets/tiktok/legacy_exports/` for future phase
- **Failed IDs retry** — 70 entries in `failed_ids.txt` may be retried in a future pass
