<!-- generated-by: gsd-doc-writer -->
# TikTok Extraction Contract — Ingestion Specification

**Version:** 2.1.0 | **Updated:** 2026-06-24 | **Status:** Hive-Ready

## Overview

The TikTok extraction pipeline produces **Hive-compliant ingestion contracts** for every extracted video. This document specifies the contract format, field definitions, validation rules, and example output.

**Output Format:** YAML frontmatter + Markdown body in `content.md`

**Storage:** `/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/content.md`

---

## Contract Structure

### YAML Frontmatter (Required)

All fields must be present and validated before finalization. Missing fields trigger extraction failure and error logging.

#### Core Ingestion Fields

```yaml
source_type: tiktok
source_id: tiktok-video-{video_id}
source_system: tiktok
source_url: https://www.tiktok.com/@{creator}/video/{video_id}
extracted_from_url: https://www.tiktok.com/@{creator}/video/{video_id}
extracted_at: 2026-06-24T12:34:56Z
captured_at: 2026-06-20T08:15:00Z
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `source_type` | string | `tiktok` | Fixed value |
| `source_id` | string | `tiktok-video-1234567890123456` | Unique asset ID |
| `source_system` | string | `tiktok` | Fixed value |
| `source_url` | URL | `https://www.tiktok.com/@creator/video/...` | Canonical TikTok URL |
| `extracted_from_url` | URL | Same as `source_url` | For audit trail |
| `extracted_at` | ISO 8601 | `2026-06-24T12:34:56Z` | Extraction timestamp (UTC) |
| `captured_at` | ISO 8601 | `2026-06-20T08:15:00Z` | Video upload timestamp (UTC) |

#### Content Metadata

```yaml
title: "{title_from_meta_or_fallback}"
creator: {creator_handle_no_at}
content_form: reference
routing_zone: work
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `title` | string | `"Creating AI Agents with Claude"` | From `meta.json` title or fallback to `creator — caption` |
| `creator` | string | `pythonmaven` | TikTok handle, @ prefix stripped |
| `content_form` | string | `reference` | Source preserved on TikTok (not archived) |
| `routing_zone` | string | `work` | Classification: personal, work, bridge (v2.1: always work) |

#### Processing Metadata

```yaml
extraction_run_id: {uuid}
processor_id: tiktok-extractor-contract
processor_version: 2.1.0
source_hash: {sha256_first_16_chars}
extraction_status: complete
extracted_from_inbox_path: /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `extraction_run_id` | UUID | `550e8400-e29b-41d4-a716-446655440000` | Unique run identifier |
| `processor_id` | string | `tiktok-extractor-contract` | Fixed value |
| `processor_version` | string | `2.1.0` | Extractor version |
| `source_hash` | string | `3a4f2b8c9d1e5f7a` | SHA256 (first 16 chars) for dedup |
| `extraction_status` | string | `complete` | complete, failed, partial |
| `extracted_from_inbox_path` | path | `/Users/.../Inbox-Raw/_staging` | Staging directory |

#### TikTok-Specific Metadata

```yaml
tiktok_video_id: "1234567890123456"
tiktok_uploader_handle: pythonmaven
tiktok_uploader_name: "Python Maven"
tiktok_caption: "Creating AI agents with Claude..."
tiktok_video_url: https://www.tiktok.com/@pythonmaven/video/...
tiktok_save_timestamp: 2026-06-20T08:15:00Z
tiktok_video_duration: 45
tiktok_view_count: 125000
tiktok_like_count: 8500
tiktok_comment_count: 342
tiktok_hashtags: ["ai", "claude", "python"]
tiktok_detected_music: "Original audio"
tiktok_sound_url: ""
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `tiktok_video_id` | string | `1234567890123456` | TikTok video ID (17+ digits) |
| `tiktok_uploader_handle` | string | `pythonmaven` | Creator handle (no @) |
| `tiktok_uploader_name` | string | `Python Maven` | Humanized creator name |
| `tiktok_caption` | string | Video description text | May be truncated |
| `tiktok_video_url` | URL | Full TikTok URL | Same as `source_url` |
| `tiktok_save_timestamp` | ISO 8601 | Video upload time | Same as `captured_at` |
| `tiktok_video_duration` | integer | 45 | Seconds |
| `tiktok_view_count` | integer | 125000 | View count at extraction time |
| `tiktok_like_count` | integer | 8500 | Like count at extraction time |
| `tiktok_comment_count` | integer | 342 | Comment count at extraction time |
| `tiktok_hashtags` | array | `["ai", "claude"]` | Hashtags from caption |
| `tiktok_detected_music` | string | `Original audio` | Track name or "Original audio" |
| `tiktok_sound_url` | URL | Empty or URL | Sound/music track URL if available |

#### Extracted Content

```yaml
extracted_text_from_video: ["Line 1 of transcript", "Line 2 of transcript", ...]
media_extracted: true
image_analysis_performed: true
transcription_method: faster-whisper
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `extracted_text_from_video` | array | Array of transcript lines | From ASR transcription |
| `media_extracted` | boolean | `true` | Video downloaded/copied successfully |
| `image_analysis_performed` | boolean | `true` | Thumbnail extracted |
| `transcription_method` | string | `faster-whisper` | ASR engine used |

#### Supporting Files (Required)

```yaml
supporting_files:
  - filename: source/video.mp4
    type: video
    description: Downloaded TikTok video
  - filename: thumbnail.jpg
    type: image
    description: Primary thumbnail
  - filename: transcript/transcript.txt
    type: transcript
    description: Plain transcript
  - filename: transcript/transcript.srt
    type: transcript
    description: SRT transcript
  - filename: transcript/transcript.json
    type: transcript
    description: Structured transcript
```

| Field | Type | Notes |
|-------|------|-------|
| `filename` | string | Relative path from asset directory |
| `type` | string | video, image, audio, transcript |
| `description` | string | Human-readable file purpose |

#### Quality Checks (Required)

```yaml
quality_checks:
  all_metadata_extracted: true
  dedup_checked: true
  all_references_valid: true
  extraction_errors: null
  metadata_gaps: []
```

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `all_metadata_extracted` | boolean | `true` | All required TikTok fields present |
| `dedup_checked` | boolean | `true` | Checked against `done_ids.txt` and ledger |
| `all_references_valid` | boolean | `true` | All URLs and paths valid |
| `extraction_errors` | string or null | `null` or error message | Null if no errors |
| `metadata_gaps` | array | `[]` or list of missing fields | Fields not extracted successfully |

#### Other Fields

```yaml
related_assets: []
```

---

## Field Validation Rules

### Required Fields (Extraction Fails Without)

- `source_type`, `source_id`, `source_system` — Must be present
- `source_url` — Must be valid TikTok URL or constructed from metadata
- `extracted_at`, `captured_at` — Must be valid ISO 8601 timestamps
- `title`, `creator` — Must not be empty
- `routing_zone` — Must be one of: personal, work, bridge
- `extraction_run_id` — Must be valid UUID
- `processor_id`, `processor_version` — Must match expected values
- `source_hash` — Must be 16-char hex string
- `extraction_status` — Must be one of: complete, failed, partial
- `quality_checks` — Must be present with all sub-fields
- `supporting_files` — Must include at least video or transcript

### Derived/Computed Fields

- `source_hash`: SHA256(source) — first 16 characters
- `title`: If not in `meta.json`, compute as `"{creator} — {caption[:80]}"`
- `creator`: Strip `@` from handles for consistency
- `extracted_text_from_video`: Array extracted from transcript.json

### Optional Fields

- `tiktok_sound_url` — May be empty if not available
- `related_assets` — Empty array unless cross-references needed
- `metadata_gaps` — Empty if all metadata extracted

---

## Example Contract

```yaml
---
source_type: tiktok
source_id: tiktok-video-1715824537482240
source_system: tiktok
source_url: https://www.tiktok.com/@pythonmaven/video/1715824537482240
extracted_from_url: https://www.tiktok.com/@pythonmaven/video/1715824537482240
extracted_at: 2026-06-24T14:32:15Z
captured_at: 2026-06-20T08:15:00Z

title: "Python Maven — Creating AI agents with Claude in 2026"
creator: pythonmaven
content_form: reference
routing_zone: work

extraction_run_id: 550e8400-e29b-41d4-a716-446655440000
processor_id: tiktok-extractor-contract
processor_version: 2.1.0
source_hash: 3a4f2b8c9d1e5f7a
extraction_status: complete
extracted_from_inbox_path: /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging

tiktok_video_id: "1715824537482240"
tiktok_uploader_handle: pythonmaven
tiktok_uploader_name: "Python Maven"
tiktok_caption: "Creating AI agents with Claude in 2026..."
tiktok_video_url: https://www.tiktok.com/@pythonmaven/video/1715824537482240
tiktok_save_timestamp: 2026-06-20T08:15:00Z
tiktok_video_duration: 45
tiktok_view_count: 125000
tiktok_like_count: 8500
tiktok_comment_count: 342
tiktok_hashtags: ["ai", "claude", "python", "coding"]
tiktok_detected_music: "Original audio"
tiktok_sound_url: ""
extracted_text_from_video:
  - "Creating AI agents with Claude is the future of coding"
  - "Here's how I build autonomous agents"
  - "Step 1: Define your agent's purpose"

media_extracted: true
image_analysis_performed: true
transcription_method: faster-whisper

related_assets: []

supporting_files:
  - filename: source/1715824537482240.mp4
    type: video
    description: Downloaded TikTok video
  - filename: thumbnail.jpg
    type: image
    description: Primary thumbnail
  - filename: transcript/transcript.txt
    type: transcript
    description: Plain transcript
  - filename: transcript/transcript.srt
    type: transcript
    description: SRT transcript
  - filename: transcript/transcript.json
    type: transcript
    description: Structured transcript with timestamps
  - filename: audio/audio.wav
    type: audio
    description: Extracted audio (16kHz mono)

quality_checks:
  all_metadata_extracted: true
  dedup_checked: true
  all_references_valid: true
  extraction_errors: null
  metadata_gaps: []
---

# TikTok Video: Python Maven — Creating AI agents with Claude in 2026

**Creator:** Python Maven (@pythonmaven)
**Duration:** 45 seconds
**Extracted:** 2026-06-24T14:32:15Z

## Transcript

Creating AI agents with Claude is the future of coding. Here's how I build autonomous agents...

[Full transcript content follows]

## Assets

- Video: [source/1715824537482240.mp4](source/1715824537482240.mp4)
- Thumbnail: [thumbnail.jpg](thumbnail.jpg)
- Transcript: [transcript/transcript.txt](transcript/transcript.txt)
- Audio: [audio/audio.wav](audio/audio.wav)
```

---

## Changes in v2.1.0 (2026-06-24)

| Field | v2.0.0 | v2.1.0 | Reason |
|-------|--------|--------|--------|
| `routing_zone` | personal | work | Hive indexer compliance; public TikTok content |
| `title` | Generic fallback | `meta.json` first | Better searchability and accuracy |
| `tiktok_uploader_handle` | With @ prefix | @ stripped | Dedup consistency with downstream systems |
| Default `--zone` | personal | work | Aligns with new default for public content |

---

## Validation Checklist

Before each extraction is finalized:

- [ ] All required fields present
- [ ] `routing_zone` is `work` (not personal)
- [ ] `source_hash` is 16-char hex
- [ ] `extracted_at` and `captured_at` are valid ISO 8601
- [ ] `creator` has no @ prefix
- [ ] `title` from `meta.json` or properly formatted fallback
- [ ] `supporting_files` array non-empty
- [ ] `quality_checks.all_metadata_extracted` is true (or gaps listed)
- [ ] No extraction errors (or errors documented)
- [ ] `extraction_status` is `complete`

---

## Hive Indexer Integration

**Accepted Fields for Indexing:**
- `source_url` — For link tracking
- `title` — For search
- `creator` — For faceting
- `extracted_text_from_video` — For semantic search
- `tiktok_hashtags` — For topic faceting
- `routing_zone` — For lane routing

**Rejection Criteria:**
- Missing required fields
- `routing_zone` != `work` (public TikTok)
- Extraction errors documented in `quality_checks`
- `metadata_gaps` with critical fields

---

## Related Documentation

- [README.md](./README.md) — Quick start guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — Common issues
- [AGENTS.md](./AGENTS.md) — Agent instructions
- [.planning/STATE.md](./.planning/STATE.md) — Current extraction progress
