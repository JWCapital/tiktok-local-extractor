---
created: "2026-06-25T17:47:26.274Z"
title: "Full project review and reset to match Revised process overview"
area: planning
files:
  - Revised_process_overview.md
  - .planning/STATE.md
  - .planning/ROADMAP.md
  - .planning/phases/v2.1-01-contract-compliance/
  - .planning/phases/v2.1-02-reprocessing/
  - .planning/phases/v2.1-03-documentation/
  - .planning/phases/v2.1-04-hive-validation/
---

## Problem

The project's current GSD planning state (v2.1 milestone with 4 active phases) was designed around a storage layout and pipeline model that has since been superseded. A revised process overview (`Revised_process_overview.md`) defines a new canonical 3-step pipeline:

1. **Extract** → permanent assets land in `_assets/tiktok/tiktok-video-<id>/`
2. **Stage** → contract markdown built into `_staging/tiktok/tiktok-video-<id>/` for review
3. **Finalize** → move staged folder into `Inbox-Raw/tiktok/tiktok-video-<id>/` for Hive intake

Key differences from current planning:
- Storage model changed: `_assets/`, `_staging/`, and `Inbox-Raw/tiktok/` are now distinct top-level lanes (not the current `exports/` root)
- State tracking moves to `_assets/tiktok/state/` (`done_ids.txt`, `failed_ids.txt`, `*.log`) and `queues/` (`favs_raw.txt`)
- Extraction history ledger is `_assets/tiktok/extraction-history.json`
- All current v2.1 GSD phases were designed around the old layout and should be closed/archived

Current phases to close:
- v2.1-01-contract-compliance (already complete)
- v2.1-02-reprocessing (active, ~45% done under old paths)
- v2.1-03-documentation (active, parallel)
- v2.1-04-hive-validation (planned)

## Solution

1. **Close/archive all current v2.1 phases** — mark them done or cancelled as appropriate; archive to `.planning/archive/`
2. **Audit actual codebase** (`extract.py`, `batch_extract.sh`, `patch_metadata.py`, `reprocess_sources.sh`, `check_progress.sh`) against the Revised_process_overview.md to identify gaps
3. **Align STATE.md, ROADMAP.md, and PROJECT.md** to the new pipeline model and storage paths
4. **Create fresh phases** reflecting the revised pipeline (extract → stage → finalize) with updated storage contracts
5. **Verify actual disk state** of `_assets/tiktok/`, `_staging/tiktok/`, and `Inbox-Raw/tiktok/` to understand true reprocessing progress under the new layout

Start point: read `Revised_process_overview.md` as the authoritative spec, then diff against current code and planning docs to produce a gap list before creating new phases.
