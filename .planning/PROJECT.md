# TikTok Extraction Pipeline — Project Overview

**Status:** Active | **Version:** 2.2.0 | **Updated:** 2026-06-25

## Project Goal

Transform TikTok videos (URLs or local files) into ingestion-contract-ready assets for the Hive Brain knowledge pipeline. Each extraction produces a self-contained `tiktok-video-<id>` directory with normalized metadata, transcripts, frames, and structured YAML frontmatter compliant with Hive indexer requirements.

## Current Milestone: v2.2 — Pipeline Alignment to Revised Process Overview

**Goal:** Align the codebase to the canonical 3-step pipeline defined in `Revised_process_overview.md` (Extract → Stage → Finalize), fix storage path discrepancies, reprocess 186 remaining queued videos, and update all documentation.

**Status:** Planning — Phase 1 starting

### Milestone Progress

| Phase | Goal | Status |
|-------|------|--------|
| Phase 1: Code Alignment | Fix staging/finalize paths and image folder naming | 📋 Not started |
| Phase 2: Reprocess Remaining | Run 186 queued videos through corrected pipeline | 📋 Not started |
| Phase 3: Documentation | Update README, AGENTS.md, EXTRACTION_CONTRACT.md | 📋 Not started |
| Phase 4: Validation | End-to-end test + Hive intake verification | 📋 Not started |

**Estimated Completion:** 2026-07-02

## Canonical Pipeline (Revised_process_overview.md)

```
TikTok URL / local file
        │
        ▼
  1. EXTRACT → _assets/tiktok/tiktok-video-<id>/
        │        source/, images/, transcript/, audio/, meta.json
        ▼
  2. STAGE   → _staging/tiktok/tiktok-video-<id>/
        │        <slug>.md (contract), images/
        ▼
  3. FINALIZE → Inbox-Raw/tiktok/tiktok-video-<id>/
                 Hive intake polls this lane
```

## Core Value

Reliable, rights-aware TikTok extraction that preserves source context, enforces Hive contract compliance, and produces indexer-ready ingestion artifacts.

## Key Constraints

- **Python 3.12 only** — faster-whisper ctranslate2 wheels not available for 3.14+
- **Venv:** `/Users/joshuawallace/Data/Sync_Data/tools/tittok-local-extactor/.venv`
- **--rights mandatory:** own | permitted | research
- **routing_zone: work** enforced (changed from personal)
- **Two-step process:** stage → finalize (atomic promotion)
- [ ] Keep roadmap and todo artifacts traceable via explicit phase linkage.

### Out of Scope

- Full cloud ingestion orchestration — this repo focuses on local extraction.
- Non-TikTok source connectors — deferred unless explicitly scoped.

## Context

- Python-based extractor workflow already operating against `exports/`.
- Existing output corpus contains many historical extracted videos.
- Upcoming work needs contract alignment with the ingestion template.

## Constraints

- **Local-first**: Outputs must remain on local disk — avoids external dependencies.
- **Rights-aware operation**: Extraction must respect rights mode requirements.
- **Backwards compatibility**: Existing export corpus should remain readable during migration.

## Key Decisions

| Decision                             | Rationale                                                   | Outcome   |
| ------------------------------------ | ----------------------------------------------------------- | --------- |
| Use GSD planning artifacts in-repo   | Enables phase/backlog tracking for structured changes       | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

## Last updated

2026-06-24 after milestone v1.1 start.
