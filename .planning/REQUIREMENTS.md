# TikTok Extraction Pipeline — Requirements

**Version:** 2.1.0 | **Updated:** 2026-06-24

## Functional Requirements (Active)

### FR-1: Single-Video Extraction

- ✅ Accept TikTok URL or local file path
- ✅ Download video using yt-dlp (with TikTok fallback)
- ✅ Copy local file to staging area

### FR-2: Metadata Extraction

- ✅ Extract video metadata (id, uploader, description, duration)
- ✅ Strip @ prefix from creator handles (dedup consistency)
- ✅ Use meta.json title (or fallback to creator—caption)
- ✅ Construct canonical TikTok URL

### FR-3: ASR Transcription

- ✅ Extract audio, convert to 16kHz mono WAV
- ✅ Transcribe using faster-whisper (small model default)
- ✅ Generate transcript.txt, .json, .srt, .vtt

### FR-4: Frame Extraction

- ✅ Scene-based keyframe extraction (threshold 0.35)
- ✅ Thumbnail extraction (1sec into video)
- ✅ Support interval-based frames

### FR-5: Contract Generation

- ✅ Generate YAML frontmatter (content.md)
- ✅ Enforce routing_zone: work for public TikTok
- ✅ Validate all required contract fields
- ✅ Track quality checks (metadata, dedup, validation)

### FR-6: Batch Processing

- ✅ Read URLs from favs_raw.txt
- ✅ Skip done_ids.txt and failed_ids.txt
- ✅ Write only after successful finalize

### FR-7: Legacy Reprocessing

- ✅ Crawl exports/*/source/ directories
- ✅ Re-extract into contract format
- ✅ Use --force flag to bypass dedup

### FR-8: Rights Policy

- ✅ --rights mandatory (own | permitted | research)
- ✅ Extraction refused without valid rights
- ✅ Rights recorded in ledger

## Non-Functional Requirements

- **Performance:** <5 min/video, <2 min ASR (faster-whisper:small)
- **Storage:** ~50-150 MB/video + 500 MB ASR cache (one-time)
- **Reliability:** Transactional finalize, error logging, ledger persistence
- **Compliance:** Hive contract v2.1.0, routing_zone: work enforced

## Out of Scope

| Feature | Reason |
| --- | --- |
| Full external task manager sync | Not required for this milestone’s planning loop. |
| Automatic todo-to-phase linking without review | Risks incorrect phase mapping; explicit user control required. |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| TODO-01 | Phase 1 | Pending |
| TODO-02 | Phase 1 | Pending |
| TRIAGE-01 | Phase 2 | Pending |
| TRIAGE-02 | Phase 2 | Pending |
| LINK-01 | Phase 3 | Pending |
| LINK-02 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0 ✅

---
*Requirements defined: 2026-06-24*
*Last updated: 2026-06-24 after milestone v1.1 definition*
