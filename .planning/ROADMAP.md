# ROADMAP

## Active Milestone

(No active milestone phases yet.)

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
