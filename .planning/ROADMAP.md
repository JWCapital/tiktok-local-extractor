# ROADMAP

## Active Milestone

**Milestone:** v2.1 Hive Compliance & Reprocessing
**Target Completion:** 2026-07-02

## Phases

- [x] **Phase 1: Contract Compliance Fixes** ✅ Completed 2026-06-24
  - Enforce routing_zone: work
  - Fix title extraction (meta.json first)
  - Strip @ from creator handles
  - Correct venv paths in scripts

- [ ] **Phase 2: Legacy Video Reprocessing** 📍 Active (73/381 complete)
  - Reprocess 381 local videos via reprocess_sources.sh
  - Validate routing_zone: work compliance
  - Update done_ids.txt ledger
  - Estimated completion: 2026-06-28

- [ ] **Phase 3: Documentation & Integration** ⏳ Parallel
  - Publish EXTRACTION_CONTRACT.md
  - Create TROUBLESHOOTING.md
  - Update README.md with correct paths
  - Publish Hive Brain skill docs

- [ ] **Phase 4: Hive Indexer Validation** ⏱️ Post-reprocessing
  - Validate 5 sample videos with Hive indexer
  - Test routing_zone: work routing
  - Address any contract issues

## Timeline

| Phase | Start      | Target      | Status      |
|-------|-----------|-----------|-----------|
| 1     | 2026-06-24 | 2026-06-24 | ✅ Complete |
| 2     | 2026-06-24 | 2026-06-28 | 📋 Active   |
| 3     | 2026-06-24 | 2026-06-25 | 📋 Active   |
| 4     | 2026-07-01 | 2026-07-02 | ⏱️ Pending  |

### Phase 2: Todo Triage & Promotion

**Goal**: User can review pending todo items and explicitly move selected work into active milestone scope
**Depends on**: Phase 1
**Requirements**: TRIAGE-01, TRIAGE-02
**Success Criteria** (what must be TRUE):

1. User can review each pending todo item and mark it as promote, defer, or keep pending.
2. User can promote selected pending todo items into active milestone planning scope.
3. User can verify triage outcomes remain visible and consistent after the review step is complete.

**Plans**: TBD

### Phase 3: Roadmap Linkage

**Goal**: User can explicitly link roadmap-approved todo items to phases without losing unmatched items
**Depends on**: Phase 2
**Requirements**: LINK-01, LINK-02
**Success Criteria** (what must be TRUE):

1. User can tag clearly matched pending todo items with `resolves_phase: N` after roadmap approval.
2. User can leave ambiguous or unmatched todo items unlinked while preserving their full content.
3. User can distinguish linked vs unlinked items during planning without losing any pending records.

**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Todo Capture Foundation | 1/1 | Complete | 2026-06-24 |
| 2. Todo Triage & Promotion | 0/0 | Not started | - |
| 3. Roadmap Linkage | 0/0 | Not started | - |

## Backlog

### Phase 999.1: Update extractor based on ingestion template contract (BACKLOG)

**Goal:** Captured for future planning
**Requirements:** EXTRACT-CT-01, EXTRACT-CT-02, EXTRACT-CT-03, EXTRACT-CT-04, EXTRACT-CT-05, EXTRACT-CT-06, EXTRACT-CT-07, EXTRACT-CT-08, EXTRACT-CT-09
**Plans:** 1 plan

Plans:

- [x] `999.1-01-PLAN.md` — Refactor extractor to ingestion contract

Backlog notes:

- Align asset IDs to `tiktok-video-[id]` naming.
- Add persistent extractor-owned ledger outside inbox path.
- Use atomic staging writes (`.staging` then move).
- Implement source-hash dedupe and idempotent resume behavior.
- Add structured extraction error ledger records.
- Expand frontmatter with extraction tracking and TikTok metadata completeness.
- Include supporting files inventory and quality check fields.
- Support default `zone: personal` with override to `work`.
- Verify outputs against the canonical ingestion folder/schema contract.
