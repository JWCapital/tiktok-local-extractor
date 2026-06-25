# Phase 2: Legacy Video Reprocessing — PLAN

**Phase:** v2.1-02  
**Status:** 📍 ACTIVE  
**Started:** 2026-06-24  
**Target Completion:** 2026-06-28  

---

## Goal

Reprocess all 381 legacy local TikTok videos through the corrected extraction pipeline with Hive contract compliance fixes. Populate `Inbox-Raw/` with finalized ingestion contracts ready for Hive Brain indexing.

## Requirements

### REPROCESS-01: Complete extraction
- [ ] All 381 videos staged via `reprocess_sources.sh --force`
- [ ] Each video: source → acquire → transcribe → extract frames → finalize

### REPROCESS-02: Ledger tracking
- [ ] Update `exports/done_ids.txt` after successful finalize
- [ ] Track failures in `exports/failed_ids.txt`
- [ ] Persistent ledger at `~/.extractors/tiktok/extraction-history.json`

### REPROCESS-03: Compliance validation
- [ ] All staged videos have `routing_zone: work`
- [ ] All videos have real titles (from meta.json or fallback)
- [ ] All creator handles without @ prefix
- [ ] Supporting files (transcript, frames, thumbnail) present

### REPROCESS-04: Performance
- [ ] Transcription speed: ~1-2 min/video (faster-whisper:small)
- [ ] Estimated total runtime: 6-13 hours
- [ ] No dependencies on external services (local-first)

## Tasks

### Wave 1: Staging (2026-06-24 — 2026-06-28)

**Status:** IN PROGRESS (160/381 staged, 42%)

1. Run: `./reprocess_sources.sh`
   - Loops through all 381 local mp4 files in `exports/*/source/`
   - Each video: `.venv/bin/python extract.py <file> --rights research --stage-only --force`
   - Stages to `_staging/tiktok/tiktok-video-<id>/`
   - Monitor: `tail -f exports/reprocess_sources.log`

2. Monitor progress:
   - Background: `./check_progress.sh` (30 sec updates)
   - Current: 160/381 (42%)
   - Est. completion: ~2026-06-28 18:00

### Wave 2: Finalization (2026-06-28)

1. Finalize all staged videos:
   ```bash
   ./.venv/bin/python extract.py --finalize-all \
     --out /Users/joshuawallace/Data/Sync_Data/Inbox-Raw
   ```
   - Moves `content.md` → `Inbox-Raw/tiktok/tiktok-video-<id>/`
   - Moves assets → `Inbox-Raw/_assets/tiktok/tiktok-video-<id>/`
   - Updates ledger on success

2. Verify finalization:
   - Count: `find Inbox-Raw/tiktok -type d -name "tiktok-video-*" | wc -l` (expect 381)
   - Sample check: `.planning/phases/v2.1-04-hive-validation/` (Phase 4)

### Wave 3: Cleanup (2026-06-28)

1. Clear staging directory:
   ```bash
   rm -rf /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging/tiktok
   ```

2. Snapshot ledger:
   ```bash
   cp ~/.extractors/tiktok/extraction-history.json \
      ~/.extractors/tiktok/extraction-history.json.phase2-complete
   ```

3. Document final state: see `STATE.md` update

## Progress Tracking

### Metrics

| Metric | Current | Target | ETA |
|--------|---------|--------|-----|
| Videos Staged | 160/381 | 381/381 | 2026-06-28 18:00 |
| Videos Finalized | 0/381 | 381/381 | 2026-06-29 08:00 |
| Inbox-Raw Size | 0 GB | ~50-80 GB | 2026-06-29 |
| Errors | 0 | <5 | 2026-06-29 |

### Monitoring

**Live Monitor:**
```bash
cd /Users/joshuawallace/Data/Sync_Data/tools/tittok-local-extactor
./check_progress.sh  # runs in background
tail -f exports/reprocess_sources.log
```

**Status Files:**
- `exports/done_ids.txt` — finalized video IDs
- `exports/failed_ids.txt` — failed video IDs
- `exports/reprocess_sources.log` — detailed execution log

## Validation Criteria

- [ ] 381 videos successfully staged (0 failures)
- [ ] All staged videos have routing_zone: work
- [ ] All staged videos have real titles
- [ ] All staged videos have creator without @
- [ ] Finalization runs without errors
- [ ] 381 content.md files in Inbox-Raw/tiktok/
- [ ] All assets in Inbox-Raw/_assets/tiktok/

## Risks & Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Transcription timeout (Whisper) | Low | Restart reprocess from last failed ID |
| Disk space exhaustion | Medium | Verify 100+ GB free before finalizing |
| Network interruption | Very Low | Local-only, not applicable |
| Duplicate extraction | Very Low | --force flag bypasses dedup checks |

## What Happens Next

**Phase 3: Documentation** (Parallel, mostly done)
- Final docs merged to main branch
- TROUBLESHOOTING.md published

**Phase 4: Hive Validation** (2026-07-01)
- Sample 5 finalized videos
- Verify routing_zone: work routing
- Test indexer acceptance
- Address any remaining issues

---

Prepared by: GSD Phase Orchestrator  
Created: 2026-06-24  
Updated: 2026-06-24  
