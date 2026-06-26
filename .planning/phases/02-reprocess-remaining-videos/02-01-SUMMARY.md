---
phase: 02-reprocess-remaining-videos
plan: "01"
subsystem: batch-runner
tags: [batch, staging, glob-fix, shell]
status: complete

dependency_graph:
  requires: [01-code-alignment/01-VERIFICATION.md]
  provides: [corrected-staging-glob-in-batch_extract.sh]
  affects: [batch_extract.sh]

tech_stack:
  added: []
  patterns: [bash-parameter-expansion, out_root-parent-glob]

key_files:
  modified:
    - batch_extract.sh (line 90: staging glob prefix corrected from $OUT_DIR to ${OUT_DIR%/*})

decisions:
  - D-04: Change batch_extract.sh line-90 glob prefix from "$OUT_DIR" to "${OUT_DIR%/*}" so link-extraction finds staged folders written by extract.py --stage-only under Sync_Data/_staging/tiktok/

metrics:
  duration: "~82 seconds"
  completed: "2026-06-25T19:52:14Z"
  tasks_completed: 1
  tasks_total: 1
  files_changed: 1
---

# Phase 02 Plan 01: Fix batch_extract.sh Link-Extraction Staging Glob (D-04) Summary

**One-liner:** Changed `batch_extract.sh` line 90 glob prefix from `"$OUT_DIR"` to `"${OUT_DIR%/*}"` so post-stage link logging resolves to `Sync_Data/_staging/tiktok/` (parent of Inbox-Raw), consistent with Phase 1's corrected `extract.py` staging root.

## Tasks Completed

| # | Name | Commit | Files |
|---|------|--------|-------|
| 1 | Fix link-extraction staging glob prefix (D-04) | 534eeab | batch_extract.sh (1 line) |

## What Was Built

Single-line edit to `batch_extract.sh` line 90: the `ls -td` staging glob now uses `"${OUT_DIR%/*}"/_staging/tiktok/tiktok-video-*/` instead of `"$OUT_DIR"/_staging/tiktok/tiktok-video-*/`.

**Before:** `latest_stage=$(ls -td "$OUT_DIR"/_staging/tiktok/tiktok-video-*/ 2>/dev/null | head -1)`
**After:** `latest_stage=$(ls -td "${OUT_DIR%/*}"/_staging/tiktok/tiktok-video-*/ 2>/dev/null | head -1)`

`OUT_DIR` = `/Users/joshuawallace/Data/Sync_Data/Inbox-Raw`
`${OUT_DIR%/*}` = `/Users/joshuawallace/Data/Sync_Data` (parent, the correct staging prefix)

## Verification Results

All 5 acceptance criteria passed:
1. Corrected glob present: `grep -cF '${OUT_DIR%/*}/_staging/...'` returns 1
2. Old Inbox-Raw-rooted glob absent: zero matches in non-comment lines
3. `bash -n batch_extract.sh` exits 0 — no syntax regression
4. `git diff --numstat` shows exactly 1 insertion + 1 deletion
5. Lines 85 and 121 retain `--out "$OUT_DIR"` unchanged (2 occurrences, confirmed via Python)

Note: the system's `grep` is aliased to `ugrep` which treats `--out` as a flag when passed as a pattern. Python verification was used for acceptance criterion 5 as a workaround; the file content is correct.

## Deviations from Plan

None — plan executed exactly as written. The single-line change was applied without any additional modifications.

## Known Stubs

None.

## Threat Flags

None. This plan introduced no network endpoints, auth paths, file access patterns, or schema changes at trust boundaries. The single-line glob-prefix change is a purely local path correction.

## Self-Check: PASSED

- `batch_extract.sh` modified: confirmed (line 90 uses `${OUT_DIR%/*}` prefix)
- Commit 534eeab exists: confirmed
- `bash -n batch_extract.sh` passes: confirmed
- `git diff --numstat` = 1+1: confirmed
