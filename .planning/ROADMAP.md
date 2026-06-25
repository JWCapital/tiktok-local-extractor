# ROADMAP

## Active Milestone: v2.2 — Pipeline Alignment to Revised Process Overview

**Target Completion:** 2026-07-02

### Phase 1: Code Alignment

**Goal:** Fix storage path discrepancies so extract.py and scripts match the canonical layout in Revised_process_overview.md
**Depends on:** —
**Requirements:** ALIGN-01, ALIGN-02, ALIGN-03
**Success Criteria** (what must be TRUE):

1. Staging path is `Sync_Data/_staging/tiktok/` (not inside `Inbox-Raw/`)
2. Image subfolder is named `images/` (not `assets/`)
3. Finalize destination is `Inbox-Raw/tiktok/tiktok-video-<id>/` (with `tiktok/` subfolder)
4. OCR → transcript timeline merge is verified present or implemented

**Plans:** TBD

### Phase 2: Reprocess Remaining Videos

**Goal:** Run the 186 queued videos through the corrected pipeline so all pending content lands in the right storage locations
**Depends on:** Phase 1
**Requirements:** REPROCESS-01, REPROCESS-02
**Success Criteria** (what must be TRUE):

1. All 186 URLs in `favs_raw.txt` are processed through the corrected pipeline
2. Each video's permanent assets land in `_assets/tiktok/tiktok-video-<id>/`
3. Finalized content lands in `Inbox-Raw/tiktok/tiktok-video-<id>/`
4. `done_ids.txt` and `extraction-history.json` are updated correctly

**Plans:** TBD

### Phase 3: Documentation

**Goal:** Update all documentation to reflect the revised 3-step pipeline and corrected storage paths
**Depends on:** Phase 1
**Requirements:** DOC-01, DOC-02, DOC-03
**Success Criteria** (what must be TRUE):

1. README.md accurately describes the Extract → Stage → Finalize pipeline with correct paths
2. AGENTS.md references correct storage locations (`_assets/`, `_staging/`, `Inbox-Raw/tiktok/`)
3. EXTRACTION_CONTRACT.md reflects the revised architecture
4. TROUBLESHOOTING.md is reviewed and updated as needed
5. No doc references old paths (`exports/`, `Inbox-Raw/_staging/`, flat `Inbox-Raw/tiktok-video-*`)

**Plans:** TBD

### Phase 4: Validation

**Goal:** End-to-end verification that the full pipeline works and Hive intake picks up finalized content correctly
**Depends on:** Phase 2, Phase 3
**Requirements:** VALIDATE-01, VALIDATE-02
**Success Criteria** (what must be TRUE):

1. 2–3 sample videos pass full extract → stage → finalize cycle without errors
2. Finalized content appears in `Inbox-Raw/tiktok/` and is picked up by Hive intake
3. Frontmatter fields (routing_zone, title, creator) are correct on all samples

**Plans:** TBD

## Timeline

| Phase | Target | Status |
|-------|--------|--------|
| 1. Code Alignment | 2026-06-26 | Not started |
| 2. Reprocess Remaining | 2026-06-28 | Not started |
| 3. Documentation | 2026-06-27 | Not started (parallel with Phase 2) |
| 4. Validation | 2026-06-30 | Not started |

## Canonical Reference

All phases implement the architecture defined in:
- `Revised_process_overview.md` — authoritative pipeline spec

## Backlog

### Phase 999.1: Update extractor based on ingestion template contract (BACKLOG)

**Goal:** Captured for future planning
**Requirements:** EXTRACT-CT-01, EXTRACT-CT-02, EXTRACT-CT-03, EXTRACT-CT-04, EXTRACT-CT-05, EXTRACT-CT-06, EXTRACT-CT-07, EXTRACT-CT-08, EXTRACT-CT-09
**Plans:** 1 plan

- [x] `999.1-01-PLAN.md` — Refactor extractor to ingestion contract
