---
gsd_state_version: 1.0
milestone: v2.1
milestone_name: Hive Compliance & Reprocessing
status: active
last_updated: "2026-06-24T18:30:00.000Z"
last_activity: "2026-06-24 18:30 — Phase 1 complete; Phase 2 active (160/381 staged, 42%); GSD phases archived & restructured"
progress:
  total_phases: 4
  completed_phases: 1
  active_phase: 2
  total_planned_videos: 381
  staged_videos: 172
  finalized_videos: 0
  percent_staged: 45
---

# TikTok Extraction Pipeline — Current State

**Last Updated:** 2026-06-24 18:30 UTC | **Phase:** Legacy Video Reprocessing (Phase 2 Active)

See: [PROJECT.md](./PROJECT.md) — Project overview and constraints

## Extraction Progress

### Overall Status

- **Total Videos to Reprocess:** 381
- **Staged (ready for finalize):** 172 (45%)
- **Finalized (in Inbox-Raw):** 0
- **Estimated Completion:** 2026-06-28
- **Background Process:** Active (check_progress.sh monitoring)

### Phase Completion Summary

| Phase | Status | Completed | Last Update |
|-------|--------|-----------|-------------|
| Phase 1: Contract Compliance | ✅ COMPLETE | 2026-06-24 | a4b1bd5 |
| Phase 2: Reprocessing | 📍 ACTIVE | 160/381 | 2026-06-24 18:30 |
| Phase 3: Documentation | 📍 ACTIVE (parallel) | All docs done | 2026-06-24 18:00 |
| Phase 4: Hive Validation | 📋 PLANNED | Starts 2026-06-29 | — |

## Phase 1 Outcome ✅ (2026-06-24)

**Git Commit:** a4b1bd5

- ✅ Enforce `routing_zone: work` (was zone: personal)
- ✅ Title extraction: prefer `meta.json` title
- ✅ Creator handles: strip @ prefix for dedup consistency
- ✅ Venv paths corrected to `./.venv`
- ✅ Extraction ledger reset for fresh reprocessing
- ✅ All 9 docs created/updated
- ✅ Old GSD phases archived to `.planning/archive/`

**Ready for Phase 2:** Yes

## Deduplication & Ledger

### File Locations

- **Persistent Ledger:** `~/.extractors/tiktok/extraction-history.json` (reset 2026-06-24)
- **Backup:** `~/.extractors/tiktok/extraction-history.json.backup` (pre-reset state)
- **Done IDs:** `exports/done_ids.txt` (updated after successful finalize)
- **Failed IDs:** `exports/failed_ids.txt` (manual retry by removing ID)

### Ledger Reset (2026-06-24)

Cleared extraction history to enable reprocessing of all 381 legacy videos without dedup bypass logic triggering. Backup preserved for recovery if needed.

## Current Configuration

- **Python:** 3.12 (venv at `./.venv`)
- **Output Root:** `/Users/joshuawallace/Data/Sync_Data/Inbox-Raw`
- **Default Zone:** `work` (public TikTok content)
- **Whisper Model:** `small` (~1-2 min/video + 500 MB cache first run)
- **Scene Threshold:** 0.35
- **Frame Mode:** scene-based

## Next Steps (Phase 2 Active)

1. Continue batch extraction via `./reprocess_sources.sh`
2. Monitor `exports/reprocess_sources.log` for progress
3. Validate `routing_zone: work` on sample videos (Phase 4)
4. Publish documentation (Phase 3, parallel)
5. Validate with Hive indexer after reprocessing completes
