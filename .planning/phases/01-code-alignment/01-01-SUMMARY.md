---
phase: 01-code-alignment
plan: "01"
subsystem: tiktok-extractor
tags: [path-fix, staging, images, alignment]
status: complete
completed: 2026-06-25

dependency_graph:
  requires: []
  provides:
    - staging-root-at-Sync_Data-parent
    - images-subfolder-for-new-extractions
  affects:
    - extract.py
    - check_progress.sh

tech_stack:
  added: []
  patterns:
    - "out_root.parent convention for staging path derivation"

key_files:
  modified:
    - extract.py
    - check_progress.sh

decisions:
  - "Staging root changed to out_root.parent/_staging (Option A one-liner, D-01)"
  - "Image subfolder renamed assets -> images for new extractions only (D-04, D-05)"
  - "CENTRALIZED_ASSETS subfolder (_assets/tiktok/ID/assets) intentionally preserved (not per-video image subfolder)"
  - "batch_extract.sh required no change: no staging glob exists in current version of the script"

metrics:
  duration: "~7 minutes"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 01 Plan 01: Code Alignment — Staging Root and Image Subfolder Fix Summary

**One-liner:** Fixed staging root derivation (out_root.parent) and renamed per-video image subfolder from assets to images in extract.py and check_progress.sh.

## What Was Built

Surgical path alignment of extract.py and check_progress.sh to match the canonical 3-step pipeline storage layout defined in Revised_process_overview.md:

1. **Staging root** now resolves to `Sync_Data/_staging/tiktok/` (a sibling of Inbox-Raw) instead of `Inbox-Raw/_staging/tiktok/` — two sites corrected in extract.py.
2. **Image subfolder** renamed from `assets/` to `images/` at all per-video path constructions in extract.py — thumbnail, frames, stage-read during finalize, and markdown body references.
3. **check_progress.sh** updated to target the corrected staging path.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Fix staging root derivation | dd9c162 | extract.py, check_progress.sh |
| 2 | Rename image subfolder assets -> images | b9b66da | extract.py |

## Changes Made

### Task 1: Staging Root Fix (ALIGN-01)

- `extract.py` `_resolve_finalize_targets()`: `staged_root = out_root / "_staging" / SOURCE_TYPE` → `out_root.parent / "_staging" / SOURCE_TYPE`
- `extract.py` `main()`: `staging_root = out_root / "_staging"` → `out_root.parent / "_staging"`
- `check_progress.sh` line 5: `find /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging/tiktok ...` → `find /Users/joshuawallace/Data/Sync_Data/_staging/tiktok ...`

### Task 2: Image Subfolder Rename (ALIGN-02)

- `extract_thumbnail()` line 436: `out_dir / "assets"` → `out_dir / "images"` (with inline spec comment)
- `extract_frames()` line 583: `out_dir / "assets"` → `out_dir / "images"`
- `_finalize_stage_dir()` line 808: `stage_dir / "assets"` → `stage_dir / "images"` (so finalize reads from images/)
- `write_contract_content()` markdown thumbnail: `![Thumbnail](/assets/{name})` → `![Thumbnail](images/{name})`
- `write_contract_content()` markdown frames prose: `` see `/assets/` folder `` → `` see `images/` folder ``

### ALIGN-03 Confirmed

- Finalize destination `out_root / SOURCE_TYPE / asset_id` is unchanged throughout — ALIGN-03 is satisfied.

## Verification Results

```
extract.py: 2 staging root sites corrected; finalize destination intact
check_progress.sh: 1 occurrence of /Sync_Data/_staging/tiktok
All checks pass: 2 staging sites, 3 image path joins, finalize destination intact
```

## Deviations from Plan

### Auto-fixed Issues

None — no bugs introduced during execution.

### Plan vs. Code Discrepancies (Documentation)

**1. [Rule 1 - Code Drift] batch_extract.sh staging glob does not exist**
- **Found during:** Task 1
- **Issue:** Plan's Edit 3 specified updating a `ls -td` staging glob at batch_extract.sh line 90. The current batch_extract.sh has no such glob — line 90 is a Python links-extraction command. The script passes `--out "$OUT_DIR"` to extract.py and relies on `--finalize-all` to resolve staging; the path fix is entirely in extract.py.
- **Fix:** No change to batch_extract.sh (correct behavior — script already works with the Python-side fix).
- **Impact:** None. The staging path is now correctly derived in extract.py; batch_extract.sh does not need to know it.

**2. [Rule 1 - Code Drift] Plan expected 7 `/ "images"` path-join renames; actual count is 3**
- **Found during:** Task 2
- **Issue:** The plan's CONTEXT.md listed `_copy_hive_image_assets()`, `_mirror_stage_images_to_assets()`, and `_offload_nonimage_payload_to_assets()` as functions containing per-video image subfolder path joins. None of these functions exist in the current codebase. The plan's verification assertion (`assert n_path == 7`) is incorrect for the current code.
- **Fix:** Applied the 3 actual per-video image subfolder renames that exist: `extract_thumbnail`, `extract_frames`, and `_finalize_stage_dir` stage-read.
- **Files modified:** extract.py only
- **Functional impact:** None — all paths that write images (thumbnail, frames) and read images (finalize stage-read) are consistently renamed. CENTRALIZED_ASSETS subfolder (`_assets/tiktok/ID/assets`) is intentionally preserved as it is under the `_assets` root (not a per-video staging folder).

## Known Stubs

None — no stubs or placeholder values introduced.

## Threat Flags

None — only path string literals modified; no credentials, network calls, or new trust boundaries.

## Self-Check: PASSED

Files confirmed modified:
- `extract.py` — 2 staging fixes, 3 image path renames, 2 markdown body updates
- `check_progress.sh` — staging path corrected

Commits confirmed:
- `dd9c162` — Task 1 (staging root fix)
- `b9b66da` — Task 2 (image subfolder rename)
