# TikTok — extraction pipeline

Turns a TikTok URL (or local `.mp4`) into an ingestion-contract-ready asset:
video · transcript artifacts · `content.md` · `meta.json`.

## One-time setup

```bash
brew install ffmpeg yt-dlp
cd /Users/joshuawallace/Data/TikTok
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> **Why python3.12?** `faster-whisper` requires `ctranslate2` wheels that are not
> yet available for Python 3.14 (the system default). The venv pins 3.12.

## Usage

```bash
cd /Users/joshuawallace/Data/TikTok

# From a URL (your own video)
.venv/bin/python extract.py "https://www.tiktok.com/@you/video/..." --rights own

# From a local file
.venv/bin/python extract.py ~/Downloads/video.mp4 --rights own

# More options
.venv/bin/python extract.py <source> --rights <own|permitted|research> \
  [--model small]          # Whisper model: tiny, small, medium, large-v3
  [--lang en]              # language code or 'auto'
  [--zone personal]        # default zone; set --zone work for work context
  [--scene-threshold 0.35] # lower = more frames
  [--frames scene]         # scene | interval | both
  [--interval 2]           # seconds between frames (interval mode)
  [--no-video]             # skip video download (audio-only)
  [--out /Users/joshuawallace/Data/Sync_Data/Inbox-Raw]  # contract destination root
```

## Rights values

| Value | When to use |
| --- | --- |
| `own` | Your own TikTok content |
| `permitted` | Creator has explicitly permitted download/use |
| `research` | Fair-use personal research context |

`--rights` is required. The script refuses to run without a valid value.

## Contract output structure

```text
Inbox-Raw/
  _staging/
    tiktok/
      tiktok-video-<video_id>/
  _extraction_errors/
    tiktok/
      tiktok-video-<video_id>-error.json
  tiktok/
    tiktok-video-<video_id>/
      content.md            # only file in polled inbox lane
  _assets/
    tiktok/
      tiktok-video-<video_id>/
        meta.json
        source/
        transcript/
        audio/
        frames/
        thumbnail.jpg
```

The extractor writes to `_staging` first, validates required metadata/files, then
atomically moves `content.md` to `Inbox-Raw/tiktok/tiktok-video-<video_id>/` and places
all supporting assets under `Inbox-Raw/_assets/tiktok/tiktok-video-<video_id>/`.

Persistent dedupe ledger (outside inbox purge lifecycle):

- `~/.extractors/tiktok/extraction-history.json`

## Legacy compatibility

Legacy `exports/` folders remain untouched unless manually migrated.

## Feeding the ingestion pipeline

`content.md` includes contract fields required by the ingestion template, including:

- source identification (`source_type`, `source_id`, `source_system`, `extracted_at`, `captured_at`)
- extraction tracking (`extraction_run_id`, `processor_id`, `processor_version`, `source_hash`, `extraction_status`)
- TikTok metadata (video id, uploader, caption, counts, hashtags, audio)
- `supporting_files` and `quality_checks`

When source metadata is sparse (common with local files), the extractor now:

- computes best-effort `captured_at` (source timestamp -> upload date -> local file mtime -> now)
- probes video duration with `ffprobe` when missing in source metadata
- writes completeness annotations in `quality_checks`:
  - `all_metadata_extracted: false`
  - `extraction_errors: "..."`
  - `metadata_gaps: [...]`

Default zone is `personal`; override with `--zone work` when applicable.

## Notes

- First `faster-whisper` run downloads the model to `~/.cache/huggingface/` (~500 MB for `small`).
- `yt-dlp` + TikTok can break when TikTok changes its site. If it fails, download manually
  and pass the local file path.
- Caption-first: if TikTok provides platform captions, ASR is skipped automatically.
- Duplicate prevention is extractor-owned via `source_hash` in the persistent ledger.
