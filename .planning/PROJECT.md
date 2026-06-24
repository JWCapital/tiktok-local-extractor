# TikTok Extraction Pipeline — Project Overview

**Status:** Active | **Version:** 2.1.0 | **Updated:** 2026-06-24

## Project Goal

Transform TikTok videos (URLs or local files) into ingestion-contract-ready assets for the Hive Brain knowledge pipeline. Each extraction produces a self-contained `tiktok-video-<id>` directory with normalized metadata, transcripts, frames, and structured YAML frontmatter compliant with Hive indexer requirements.

## Current Milestone: v2.1 Compliance & Reprocessing

**Goal:** Reprocess 381 legacy local TikTok videos with corrected Hive contract compliance (routing_zone: work, proper title extraction, creator handle normalization).

**Status:** In Progress (Phase 2 Active)

### Milestone Progress

| Phase | Goal | Status | Progress |
|-------|------|--------|----------|
| Phase 1: Contract Compliance | Implement Hive ingestion fixes | ✅ Complete | 3/3 fixes deployed (git a4b1bd5) |
| Phase 2: Reprocessing | Stage & finalize 381 videos | 📍 Active | 172/381 staged (45%) — ETA 2026-06-28 |
| Phase 3: Documentation | Complete docs suite | 📍 Active (parallel) | 9/9 docs complete, GSD phases created |
| Phase 4: Hive Validation | Verify indexing end-to-end | 📋 Planned | 0/5 samples (starts 2026-06-29) |

**Estimated Completion:** 2026-07-01

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
