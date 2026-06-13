# Ticktok Extractor

## What This Is

A local-first TikTok extraction toolkit that downloads source media and produces AI-ready export folders under `exports/` with transcripts, screenshots, and summaries.

## Core Value

Reliable, rights-aware TikTok extraction that preserves source context and produces reusable analysis artifacts.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Keep extraction runs repeatable and resilient.
- [ ] Preserve rich metadata and transcript artifacts for downstream analysis.
- [ ] Align extractor outputs with the ingestion contract used by downstream systems.

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

## Last updated

2026-06-13 after initialization.
