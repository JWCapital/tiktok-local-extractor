# ROADMAP

## Active Milestone

**Milestone:** v2.2 — Pipeline Alignment to Revised Process Overview
**Target Completion:** 2026-07-02

## Phases

- [ ] **Phase 1: Code Alignment**
  - Fix staging path: `Inbox-Raw/_staging/tiktok/` → `Sync_Data/_staging/tiktok/`
  - Fix image subfolder name: `assets/` → `images/`
  - Fix finalize destination: add `tiktok/` subfolder under `Inbox-Raw/`
  - Verify OCR → transcript timeline merge is implemented

- [ ] **Phase 2: Reprocess Remaining Videos**
  - Run 186 queued videos through corrected pipeline
  - Confirm outputs land in correct storage paths
  - Update done_ids.txt and extraction-history.json

- [ ] **Phase 3: Documentation**
  - Update README.md — reflect revised 3-step pipeline and new storage paths
  - Update AGENTS.md — correct all path references
  - Update EXTRACTION_CONTRACT.md — align to `_assets/`, `_staging/`, `Inbox-Raw/tiktok/` layout
  - Review and update TROUBLESHOOTING.md as needed

- [ ] **Phase 4: Validation**
  - End-to-end test: extract → stage → finalize on 2–3 sample videos
  - Verify Hive intake picks up from `Inbox-Raw/tiktok/`
  - Confirm routing_zone, title, creator handle fields are correct

## Timeline

| Phase | Target | Status |
|-------|--------|--------|
| 1. Code Alignment | 2026-06-26 | Not started |
| 2. Reprocess Remaining | 2026-06-28 | Not started |
| 3. Documentation | 2026-06-27 | Not started |
| 4. Validation | 2026-06-30 | Not started |

## Canonical Reference

All phases implement the architecture defined in:
- `Revised_process_overview.md` — authoritative pipeline spec

## Backlog

### Phase 999.1: Update extractor based on ingestion template contract (BACKLOG)

**Goal:** Captured for future planning
**Requirements:** EXTRACT-CT-01 through EXTRACT-CT-09
**Plans:** 1 plan

- [x] `999.1-01-PLAN.md` — Refactor extractor to ingestion contract
