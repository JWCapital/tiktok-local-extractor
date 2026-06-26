# TikTok Extraction — Pipeline Overview

The pipeline extracts videos from TikTok and produces Hive-ready assets. Work happens in three phases: **extract** (permanent asset storage), **stage** (contract markdown for review), and **finalize** (promote into the polled inbox for Hive intake).

## What extraction captures

Each run starts from a TikTok URL (or a local video file) and pulls as much signal as possible from the video itself.

**Video and audio**

- Download and preserve the **full video** under `_assets/tiktok/tiktok-video-<id>/source/`.
- **Extract audio** from the video into `audio/audio.wav`.

**Transcript**

- Prefer the **platform transcript** from TikTok when available.
- If no usable TikTok transcript exists, run **speech-to-text on the extracted audio**.
- All transcript output is **timestamped** (`transcript.txt`, `.srt`, `.vtt`, `.json`).

**Screenshots and on-screen text**

- Sample the video and keep **screenshots that carry useful information** — scene changes, slides, diagrams, captions burned into the frame, etc.
- When a screenshot contains **URLs, usernames, handles, or other readable text**, extract that text via OCR (or equivalent) and record it in **metadata** (`meta.json` and related sidecar files under the video folder).
- Each screenshot entry in metadata should include its **capture timestamp** (position in the video when the frame was taken).
- On-screen text is also **merged into the transcript timeline** at the time it appeared on screen, so spoken words and visible text share one chronological record.

**Metadata → ingestion document**

Metadata files (`meta.json`, transcript JSON, screenshot/OCR sidecars) are the intermediate layer. During **stage**, they are assembled into the Hive ingestion contract markdown file. Full field definitions live in [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md); the sections below are the checklist this pipeline must satisfy.

---

## Hive ingestion contract — `{video-name}.md`

Each staged video produces one markdown file named from the **video title in `meta.json`**. The title is **slugified** for a safe, readable filename:

- Lowercase; spaces and punctuation → hyphens
- Strip characters unsafe on disk (`/`, `\`, `:`, etc.)
- Collapse repeated hyphens; trim leading/trailing hyphens
- **Maximum 150 characters** for the slug (excluding `.md`) — truncate long titles at a word boundary when possible

Example: `"Creating AI Agents with Claude"` → `creating-ai-agents-with-claude.md`

If title is missing, fall back to `{creator}-{video_id}.md` (also slugified, still under 150 characters).

The file contains YAML frontmatter (machine-readable contract) plus a markdown body (human-readable timeline for indexing). Hive intake polls finalized copies from `Inbox-Raw/tiktok/`.

### Required YAML frontmatter

All fields must be present and validated before finalize. Missing required fields block promotion to the inbox lane.

#### 1. Core ingestion

```yaml
source_type: tiktok
source_id: tiktok-video-{video_id}
source_system: tiktok
source_url: https://www.tiktok.com/@{creator}/video/{video_id}
extracted_from_url: https://www.tiktok.com/@{creator}/video/{video_id}
extracted_at: 2026-06-24T12:34:56Z
captured_at: 2026-06-20T08:15:00Z
```

| Field | Source | Notes |
| --- | --- | --- |
| `source_type` | fixed | Always `tiktok` |
| `source_id` | video ID | `tiktok-video-{video_id}` — unique asset ID |
| `source_system` | fixed | Always `tiktok` |
| `source_url` | `meta.json` | Canonical TikTok URL |
| `extracted_from_url` | `meta.json` | Same as `source_url`; audit trail |
| `extracted_at` | run timestamp | When extraction ran (UTC, ISO 8601) |
| `captured_at` | `meta.json` | Video upload/save time on TikTok (UTC) |

#### 2. Content metadata

```yaml
title: "{title_from_meta_or_fallback}"
creator: {creator_handle_no_at}
content_form: reference
routing_zone: work
```

| Field | Source | Notes |
| --- | --- | --- |
| `title` | `meta.json` | From title, or fallback `{creator} — {caption[:80]}` |
| `creator` | `meta.json` | TikTok handle — **no `@` prefix** |
| `content_form` | fixed | Always `reference` (source stays on TikTok) |
| `routing_zone` | fixed | Always `work` for public TikTok content |

#### 3. Processing metadata

```yaml
extraction_run_id: {uuid}
processor_id: tiktok-extractor-contract
processor_version: 2.1.0
source_hash: {sha256_first_16_chars}
extraction_status: complete
extracted_from_inbox_path: /Users/joshuawallace/Data/Sync_Data/_staging
```

| Field | Source | Notes |
| --- | --- | --- |
| `extraction_run_id` | run | Unique UUID per extraction run |
| `processor_id` | fixed | `tiktok-extractor-contract` |
| `processor_version` | fixed | Current extractor version |
| `source_hash` | computed | SHA256 of source — first 16 hex chars (dedup) |
| `extraction_status` | run | `complete`, `failed`, or `partial` |
| `extracted_from_inbox_path` | fixed | Staging root (`…/Sync_Data/_staging`) |

#### 4. TikTok-specific metadata

```yaml
tiktok_video_id: "{video_id}"
tiktok_uploader_handle: {creator_handle_no_at}
tiktok_uploader_name: "{display_name}"
tiktok_caption: "{caption_text}"
tiktok_video_url: https://www.tiktok.com/@{creator}/video/{video_id}
tiktok_save_timestamp: 2026-06-20T08:15:00Z
tiktok_video_duration: 45
tiktok_view_count: 125000
tiktok_like_count: 8500
tiktok_comment_count: 342
tiktok_hashtags: ["ai", "claude", "python"]
tiktok_detected_music: "Original audio"
tiktok_sound_url: ""
```

All values from `meta.json` / yt-dlp metadata at extract time. `tiktok_save_timestamp` matches `captured_at`. Counts reflect values at extraction time.

#### 5. Extracted content flags

```yaml
extracted_text_from_video:
  - "Spoken or OCR line 1"
  - "Spoken or OCR line 2"
media_extracted: true
image_analysis_performed: true
transcription_method: faster-whisper   # or platform-captions when TikTok transcript used
```

| Field | Source | Notes |
| --- | --- | --- |
| `extracted_text_from_video` | transcript + OCR | Array of lines — **includes ASR speech and on-screen text** pulled from screenshots |
| `media_extracted` | run | `true` when source video is present |
| `image_analysis_performed` | run | `true` when screenshots/thumbnail were captured |
| `transcription_method` | run | ASR engine name or `platform-captions` |

#### 6. Supporting files

Lists permanent assets under `_assets/tiktok/tiktok-video-<id>/` (paths relative to that folder):

```yaml
supporting_files:
  - filename: source/{video_id}.mp4
    type: video
    description: Downloaded TikTok video
  - filename: thumbnail.jpg
    type: image
    description: Primary thumbnail
  - filename: images/scene_001.jpg
    type: image
    description: Scene screenshot at 00:00:12
  - filename: transcript/transcript.txt
    type: transcript
    description: Plain transcript
  - filename: transcript/transcript.srt
    type: transcript
    description: SRT transcript with timestamps
  - filename: transcript/transcript.json
    type: transcript
    description: Structured transcript with timestamps
  - filename: audio/audio.wav
    type: audio
    description: Extracted audio (16 kHz mono)
```

Must include at least **video or transcript**. Screenshot entries should note capture time in `description`.

#### 7. Quality checks

```yaml
quality_checks:
  all_metadata_extracted: true
  dedup_checked: true
  all_references_valid: true
  extraction_errors: null
  metadata_gaps: []
```

| Sub-field | Meaning |
| --- | --- |
| `all_metadata_extracted` | All required TikTok fields present (or gaps listed) |
| `dedup_checked` | Checked against `done_ids.txt` and `extraction-history.json` |
| `all_references_valid` | URLs and asset paths resolve |
| `extraction_errors` | `null` when clean; error message otherwise |
| `metadata_gaps` | `[]` when complete; otherwise list of missing fields |

#### 8. Other

```yaml
related_assets: []
```

Optional cross-references to other Hive assets. Empty array when none.

### Required markdown body

The body is what Hive indexes for semantic search alongside `extracted_text_from_video`. Structure it as a **timestamped timeline** — maximum detail, chronological order.

```markdown
# TikTok Video: {title}

**Creator:** {display_name} (@{creator})
**Duration:** {duration} seconds
**Source:** {source_url}
**Extracted:** {extracted_at}

## Timeline

[00:00:03] (speech) Opening line of spoken content…

[00:00:12] (on-screen) @someuser — visible handle captured from screenshot
[00:00:12] (screenshot) ![Scene at 00:12](images/scene_001.jpg)

[00:00:18] (speech) Next spoken segment…

[00:00:24] (on-screen) https://example.com — URL visible on screen

## Caption

{full tiktok_caption}

## Assets

Permanent files live under `_assets/tiktok/tiktok-video-{id}/`:

- Video: `_assets/tiktok/tiktok-video-{id}/source/{id}.mp4`
- Transcript: `_assets/tiktok/tiktok-video-{id}/transcript/transcript.srt`
- Audio: `_assets/tiktok/tiktok-video-{id}/audio/audio.wav`
```

**Body rules:**

- Every timeline entry carries a **`[HH:MM:SS]` timestamp**.
- Tag each entry as `(speech)`, `(on-screen)`, or `(screenshot)` so indexers can distinguish source.
- On-screen text from OCR appears at the time it was visible, not only in frontmatter arrays.
- Screenshot images in the staged folder use **relative links** (`images/scene_*.jpg`).
- Permanent asset paths point to `_assets/tiktok/…` (unchanged by finalize).

### What Hive uses for indexing

| Frontmatter field | Hive use |
| --- | --- |
| `source_url` | Link tracking |
| `title` | Search |
| `creator` | Faceting |
| `extracted_text_from_video` | Semantic search |
| `tiktok_hashtags` | Topic faceting |
| `routing_zone` | Lane routing |
| Markdown timeline body | Full-text / semantic indexing |

**Rejection triggers:** missing required fields, `routing_zone` ≠ `work`, critical `metadata_gaps`, or documented errors in `quality_checks`.

### Pre-finalize validation checklist

- [ ] All YAML groups above present and valid
- [ ] `routing_zone` is `work`; `creator` has no `@`
- [ ] `source_hash` is 16-char hex; timestamps are ISO 8601 UTC
- [ ] `supporting_files` non-empty (video and/or transcript listed)
- [ ] `extracted_text_from_video` includes speech **and** OCR/on-screen text
- [ ] Body timeline has timestamps for every speech, on-screen, and screenshot event
- [ ] `quality_checks.extraction_errors` is `null`; `extraction_status` is `complete`

---

## Storage locations

Three top-level locations:

| Location | Role |
| --- | --- |
| `_assets/tiktok/` | Permanent assets, state, queues, and extraction history |
| `_staging/tiktok/` | Temporary holding area — review before Hive intake |
| `Inbox-Raw/tiktok/` | Polled inbox lane — Hive intake reads from here |

Staging lives at the Sync_Data level, **outside** `Inbox-Raw/`, so it is never picked up by the intake poller until you explicitly finalize.

---

## Process overview

```text
TikTok URL or local source
        │
        ▼
   1. EXTRACT ──► permanent assets + metadata  →  _assets/tiktok/tiktok-video-<id>/
        │
        ▼
   2. STAGE    ──► contract markdown + images  →  _staging/tiktok/tiktok-video-<id>/
        │                                         (review here before intake)
        ▼
   3. FINALIZE ──► move entire folder per video  →  Inbox-Raw/tiktok/tiktok-video-<id>/
                   (batch or all, on your signal)     Hive intake polls this lane
```

Before each extract run, the pipeline checks `_assets/tiktok/state/` to decide what to skip, retry, or process next. After a successful finalize, the video ID is added to `state/done_ids.txt` and recorded in `extraction-history.json`.

---

## Permanent storage — `_assets/tiktok/`

Everything durable for the pipeline lives here: per-video assets, process state, the work queue, and the extraction history ledger.

```text
/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/
│
├── extraction-history.json     # persistent ledger — one record per finalized video (IDs, timestamps, hashes)
│
├── state/                      # process tracking (survives reboots; not purged with inbox)
│   ├── done_ids.txt            # video IDs successfully finalized — skip on re-run
│   ├── failed_ids.txt          # video IDs that failed — skip unless manually retried
│   └── *.log                   # batch/run logs (e.g. batch_extract.log)
│
├── queues/                     # work still to do
│   └── favs_raw.txt            # one TikTok URL per line — input queue for batch runs
│
└── tiktok-video-<id>/          # one folder per extracted video
    ├── meta.json               # title, creator, duration, source URL, TikTok metadata
    ├── source/
    │   └── <id>.mp4            # original video file (when downloaded or preserved)
    ├── images/
    │   ├── thumbnail.jpg
    │   ├── scene_*.jpg
    │   └── frame_*.jpg
    ├── transcript/
    │   ├── transcript.txt
    │   ├── transcript.srt
    │   ├── transcript.vtt
    │   └── transcript.json
    └── audio/
        └── audio.wav
```

### Tracking files

| File | Purpose |
| --- | --- |
| `extraction-history.json` | Authoritative history of finalized extractions — used for dedup and audit |
| `state/done_ids.txt` | IDs fully finalized; extract and batch runs skip these |
| `state/failed_ids.txt` | IDs that failed; batch runs skip these until the ID is removed to retry |
| `queues/favs_raw.txt` | URLs waiting to be processed — defines what still needs to be done |

**Dedup rule:** A video ID in `done_ids.txt` or `failed_ids.txt` is not re-processed unless explicitly forced or removed from the failed list.

---

## Step 1 — Extract

Download (or accept) the TikTok video, then run the full capture pipeline:

1. Save the source video and extracted audio.
2. Resolve the transcript (TikTok captions first; ASR from audio as fallback) with timestamps.
3. Capture information-rich screenshots; OCR any URLs, usernames, or on-screen text.
4. Write metadata (`meta.json`, transcript files, screenshot records with capture times and extracted text).
5. Merge on-screen text into the transcript timeline where it was visible.

All durable outputs land in `_assets/tiktok/tiktok-video-<id>/`. Extract does **not** mark a video as done — completion tracking in `state/done_ids.txt` happens at finalize.

---

## Step 2 — Stage

Build the Hive ingestion contract (`{video-name}.md` from `meta.json` title) for each extracted video — see **Hive ingestion contract** above for the full field and body checklist. Staging is non-destructive: it creates a preview tree without moving or deleting the permanent assets in `_assets/tiktok/`.

```text
/Users/joshuawallace/Data/Sync_Data/_staging/tiktok/
└── tiktok-video-<id>/
    ├── {video-name}.md         # slug from meta.json title (≤150 chars);
    │                           # YAML frontmatter + timestamped timeline body,
    │                           # relative image links, and pointers to _assets/tiktok/...
    └── images/
        ├── thumbnail.jpg
        ├── scene_*.jpg
        └── frame_*.jpg
```

Review staged folders here before triggering finalize. Nothing in `_staging/` is visible to Hive intake.

---

## Step 3 — Finalize

Run finalize once staging looks correct and you are ready for the Hive intake process to pick up content.

**Trigger:** You decide when — either move a small batch of videos or move all staged videos at once.

**What happens:** For each video, the **entire folder** `tiktok-video-<id>/` is moved from `_staging/tiktok/` into `Inbox-Raw/tiktok/`. The folder structure is preserved as-is; nothing is split or reassembled.

```text
# Before finalize
/Users/joshuawallace/Data/Sync_Data/_staging/tiktok/tiktok-video-<id>/   ← source

# After finalize
/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/  ← destination (polled by Hive)
    ├── {video-name}.md         # slug from meta.json title (≤150 chars)
    └── images/
        ├── thumbnail.jpg
        ├── scene_*.jpg
        └── frame_*.jpg
```

After a successful finalize:

- The video ID is written to `state/done_ids.txt`
- `extraction-history.json` is updated
- The staged folder no longer exists under `_staging/` (it was moved, not copied)

Permanent assets under `_assets/tiktok/tiktok-video-<id>/` are unchanged — finalize only moves the contract folder into the inbox lane.
