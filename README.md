# TikTok Extraction Pipeline — Ingestion Contract Extractor

Turns TikTok URLs or local video files into Hive-compliant ingestion-contract assets: normalized metadata, ASR transcripts, keyframes, and YAML frontmatter (`content.md`).

**Status:** Active | **Version:** 2.1.0 | **Updated:** 2026-06-24

## One-time Setup

```bash
brew install ffmpeg yt-dlp      # System binaries for video processing
cd /Users/joshuawallace/Data/Sync_Data/tools/tittok-local-extactor
python3.12 -m venv .venv        # Create isolated Python 3.12 environment
.venv/bin/pip install -r requirements.txt  # Install dependencies
```

> **Python 3.12 required** — `faster-whisper` needs `ctranslate2` wheels not available for Python 3.14+
>
> **Venv location:** `.venv` (project root) — NOT `~/Data/TikTok/.venv`

## Usage

```bash
cd /Users/joshuawallace/Data/Sync_Data/tools/tittok-local-extactor

# From a URL (your own content)
.venv/bin/python extract.py "https://www.tiktok.com/@creator/video/..." --rights own

# From a local file
.venv/bin/python extract.py ~/Downloads/video.mp4 --rights own

# Detailed options
.venv/bin/python extract.py <source> --rights <own|permitted|research> \
  [--stage-only]           # Stage only; validates but does not finalize
  [--finalize-all]         # Finalize all staged assets (separate run)
  [--finalize <id|path>]   # Finalize one staged asset
  [--model small]          # Whisper model: tiny, small, medium, large-v3 (default: small)
  [--lang en]              # Language code or 'auto' (default: auto-detect)
  [--zone work]            # Routing zone: personal, work, bridge (default: work)
  [--scene-threshold 0.35] # Scene detection threshold (lower = more frames)
  [--frames scene]         # Frame mode: scene | interval | both (default: scene)
  [--interval 2]           # Seconds between interval frames (default: 2)
  [--no-video]             # Skip video download (audio-only mode)
  [--force]                # Bypass dedup ledger (reprocess forced)
  [--out /Users/joshuawallace/Data/Sync_Data/Inbox-Raw]  # Output root (default: $HIVE_INBOX_RAW)
```

## Two-Step Workflow (Recommended)

### Step 1: Stage — validate without promoting

```bash
.venv/bin/python extract.py "https://www.tiktok.com/@creator/video/..." \
  --rights research \
  --stage-only
```

This:
- Downloads/copies video to `_staging/tiktok/tiktok-video-<id>/source/`
- Extracts audio, transcribes, extracts frames
- Generates YAML frontmatter in `_staging/tiktok/tiktok-video-<id>/content.md`
- Validates all required contract fields
- **Does NOT update `done_ids.txt`** (staging is non-destructive)

### Step 2: Finalize — promote all staged assets

```bash
# Finalize all staged videos in one operation
.venv/bin/python extract.py --finalize-all

# Or finalize one staged video
.venv/bin/python extract.py --finalize tiktok-video-<video_id>
```

This:
- Atomically moves `content.md` to `tiktok/tiktok-video-<id>/` (polled inbox lane)
- Moves video, audio, transcripts, frames to `_assets/tiktok/tiktok-video-<id>/`
- Updates `done_ids.txt` and persistent ledger (`/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/extraction-history.json`)
- **Only finalized videos are marked as done** (retryable on stage failure)

**Batch scripts automatically follow this pattern:** stage all → validate → finalize all

## Contract Compliance (Hive Indexer Ready)

All extractions produce **Hive-compliant ingestion contracts** with:
- **routing_zone:** `work` (public TikTok content — enforced)
- **source_type:** `tiktok`
- **content_form:** `reference` (source preserved on TikTok)
- **YAML frontmatter:** All required fields validated
- **Quality checks:** Metadata completeness, dedup status, validation errors

For full contract specification, see [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md).

## Output Directory Structure

```text
/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/
  _staging/tiktok/
    tiktok-video-<video_id>/
      content.md            # Staged frontmatter (not yet polled)
      source/
        *.mp4               # Downloaded video
        *.info.json         # yt-dlp metadata
      thumbnail.jpg
      transcript/
        transcript.txt, .json, .srt, .vtt
      audio/
        audio.wav
      frames/
        *.jpg               # Scene keyframes
  
  tiktok/                   # ← POLLED INBOX LANE
    tiktok-video-<video_id>/
      content.md            # Frontmatter (after finalize)
  
  _assets/tiktok/           # ← Asset storage
    tiktok-video-<video_id>/
      meta.json
      source/
      transcript/
      audio/
      frames/
      thumbnail.jpg
  
  _extraction_errors/tiktok/
    tiktok-video-<video_id>-error.json
```

The extractor writes to `_staging/` first and validates required fields. On successful finalization, all assets move to their final locations.
finalization mode, it atomically moves `content.md` to
`Inbox-Raw/tiktok/tiktok-video-<video_id>/` and places all supporting assets under
`Inbox-Raw/_assets/tiktok/tiktok-video-<video_id>/`.

Persistent dedupe ledger (outside inbox purge lifecycle):

- `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/extraction-history.json`

## Legacy compatibility

Legacy source archives are stored under `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/legacy_exports/`.

## Feeding the ingestion pipeline

`content.md` includes contract fields required by the ingestion template, including:

- source identification (`source_type`, `source_id`, `source_system`, `extracted_at`, `captured_at`)
- extraction tracking (`extraction_run_id`, `processor_id`, `processor_version`, `source_hash`, `extraction_status`)
- TikTok metadata (video id, uploader, caption, counts, hashtags, audio)
- `supporting_files` and `quality_checks`

## Batch Processing

For extracting multiple videos from a URL list:

```bash
# Extract all URLs in /Users/joshuawallace/Data/Sync_Data/_assets/tiktok/queues/favs_raw.txt
./batch_extract.sh

# Extract from custom URL list
./batch_extract.sh /path/to/urls.txt

# Reprocess all legacy source videos (_assets/tiktok/legacy_exports/*/source/)
./reprocess_sources.sh
```

Batch scripts:
- Stage all videos (parallel or sequential)
- Skip videos in `done_ids.txt` (already extracted)
- Skip videos in `failed_ids.txt` (permanently failed)
- Log progress to `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/state/batch_extract.log` or `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/state/reprocess_sources.log`
- Finalize all in one run
- Update `done_ids.txt` only after successful finalize

## Ledger & Deduplication

**Persistent ledger:** `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/extraction-history.json`
- Records extraction runs (one entry per finalized video)
- Tracks source hash for dedup detection

**Local dedup files:**
- `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/state/done_ids.txt` — extracted video IDs (do not re-extract)
- `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/state/failed_ids.txt` — permanently failed IDs (skip by default)

**Retry a failed video:**
```bash
# Remove ID from failed list
sed -i '' '/^<video_id>$/d' /Users/joshuawallace/Data/Sync_Data/_assets/tiktok/state/failed_ids.txt

# Re-extract (with --force to bypass ledger)
.venv/bin/python extract.py /path/to/video.mp4 --rights research --stage-only --force
.venv/bin/python extract.py --finalize-all
```

## Troubleshooting

Common issues and solutions are documented in [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

## Related Documentation

- [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md) — Full contract specification
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) — Common issues and fixes
- [AGENTS.md](./AGENTS.md) — Agent instructions for automation
- [.planning/PROJECT.md](./.planning/PROJECT.md) — Project overview
- [.planning/ROADMAP.md](./.planning/ROADMAP.md) — Phase timeline
- [.planning/STATE.md](./.planning/STATE.md) — Current extraction state
