# Phase 4: Hive Validation & Sign-Off — PLAN

**Phase:** v2.1-04  
**Status:** 📍 PLANNED  
**Target Start:** 2026-06-29  
**Target Completion:** 2026-07-01  

---

## Goal

Validate that 381 reprocessed TikTok videos with Hive contract compliance fixes pass live Hive Brain indexer acceptance and deliver correct search/routing behavior end-to-end.

## Requirements

### VALIDATE-01: Sample acceptance
- [ ] Select 5 diverse videos (different creators, durations, genres)
- [ ] Verify each has routing_zone: work in content.md
- [ ] Submit to live Hive indexer via ingest.py

### VALIDATE-02: Indexing verification
- [ ] Each video appears in appropriate Hive collections (work, public, video)
- [ ] routing_zone: work routing confirmed (not personal/bridge)
- [ ] Metadata searchable (creator, title, tags)

### VALIDATE-03: Edge case identification
- [ ] Non-ASCII titles (Chinese, emoji, etc.)
- [ ] Long titles (>255 chars)
- [ ] Unusual creators (@handles with dots, numbers)
- [ ] Very short/long videos (< 5s, > 30min)

### VALIDATE-04: Remediation
- [ ] Document any issues found
- [ ] Categorize: blocker, warning, informational
- [ ] If blocker: implement fix, retest

## Tasks

### Wave 1: Sample Selection (2026-06-29)

1. Query staging directory:
   ```bash
   find /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging/tiktok \
     -type f -name content.md | head -5
   ```

2. Select diverse sample:
   - Video 1: Short (<10s) video
   - Video 2: Long (>10min) video
   - Video 3: Non-English title
   - Video 4: Unusual creator handle
   - Video 5: Random sample

### Wave 2: Live Validation (2026-06-30)

1. Run Hive ingest on 5 samples:
   ```bash
   python /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/ingest.py \
     --source tiktok \
     --sample-only
   ```

2. Verify in Hive Brain:
   - Check collections: work, public, video
   - Search by title, creator, tags
   - Confirm routing_zone: work

### Wave 3: Issues & Remediation (2026-07-01)

1. Document findings in VALIDATION.md
2. Categorize issues (blocker/warning/info)
3. If blocker: implement fix, retest
4. If warning/info: document workaround

## Validation Criteria

- [ ] All 5 samples successfully indexed
- [ ] routing_zone: work confirmed for all
- [ ] All metadata searchable
- [ ] No blocker-level issues

## Success Criteria

- ✅ 0 blocker issues (or all mitigated)
- ✅ All 5 samples discoverable in Hive collections
- ✅ End-to-end workflow verified
- ✅ Ready to archive v2.1 as complete

## What's Next

After sign-off:
- Archive `.planning/phases/v2.1-*`
- Tag git release: v2.1.0-validated
- Begin v2.2 planning (if applicable)

---

Prepared by: GSD Phase Orchestrator  
Created: 2026-06-24  
