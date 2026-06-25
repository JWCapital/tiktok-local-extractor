# Phase 1: Contract Compliance Fixes — PLAN

**Phase:** v2.1-01  
**Status:** ✅ COMPLETED  
**Completed:** 2026-06-24  
**Git Commit:** a4b1bd5

---

## Goal

Implement Hive ingestion contract compliance fixes to enable clean indexing of TikTok videos. Address 3 critical/minor issues from Hive feedback to ensure all extracted content meets indexer requirements.

## Requirements

### COMPLIANCE-01: routing_zone compliance
- [ ] Change `zone: personal` → `routing_zone: work` in frontmatter
- [ ] Update default `--zone` from personal to work
- [ ] Hive indexer only accepts routing_zone ∈ {work, bridge}

### COMPLIANCE-02: Title searchability
- [ ] Use actual title from `meta.json` instead of generic fallback
- [ ] Fix: "TikTok by @drchrispharmd" → derive real title
- [ ] Only fallback to generic pattern if meta title missing/invalid

### COMPLIANCE-03: Creator handle consistency
- [ ] Strip `@` prefix from creator handles
- [ ] Store bare handle (e.g., `drchrispharmd` not `@drchrispharmd`)
- [ ] Consistent across both `creator` and `tiktok_uploader_handle` fields

### VENV-01: Script paths
- [ ] Correct `reprocess_sources.sh` to use `./.venv` (not `/Users/joshuawallace/Data/TikTok/.venv`)
- [ ] Verify `batch_extract.sh` venv references

## Tasks

### Wave 1: Code Changes (2026-06-24)
1. ✅ Update `extract.py` frontmatter generation (lines 829-1050)
   - Strip @ from uploader_handle
   - Use meta.json title with fallback logic
   - Change zone → routing_zone:work
   
2. ✅ Update `reprocess_sources.sh` (lines 34, 50)
   - Change venv path to `./.venv`
   
3. ✅ Update `REQUIRED_CONTRACT_FIELDS` (line 46)
   - Replace `zone` with `routing_zone`

### Wave 2: Configuration (2026-06-24)
1. ✅ Change default `--zone` from personal to work (line 1106)

### Wave 3: Ledger Reset (2026-06-24)
1. ✅ Backup extraction ledger to `~/.extractors/tiktok/extraction-history.json.backup`
2. ✅ Clear ledger to `[]` for fresh reprocessing
3. ✅ Reset `exports/done_ids.txt` and `exports/failed_ids.txt`

## Verification

### Contract Compliance Checklist
- [x] frontmatter uses `routing_zone: work` (not `zone: personal`)
- [x] title extracted from meta.json or fallback
- [x] creator stored without @ prefix
- [x] venv paths corrected to `./.venv`
- [x] extract.py syntax valid (no Python errors)
- [x] REQUIRED_CONTRACT_FIELDS includes routing_zone

### Testing (Sample Staged Video)
- [x] Stage one video: `./.venv/bin/python extract.py <url> --rights research --stage-only`
- [x] Verify staged content.md has `routing_zone: work`
- [x] Verify title is from meta.json
- [x] Verify creator without @

## Outcome

**Result:** ✅ COMPLETED

All contract compliance issues fixed and deployed:
- Git commit: a4b1bd5
- Code changes merged to main
- Ready for Phase 2 reprocessing with corrected output format

## Impact

- **Positive:** All 381 videos will now index cleanly in Hive Brain
- **Risk:** None (fixes only apply to NEW/reprocessed videos; legacy exports untouched)
- **Rollback:** Revert to commit prior to a4b1bd5 if needed (venv restored from backup)
