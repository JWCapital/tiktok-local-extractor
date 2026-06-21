# TikTok Extraction Pipeline — Agent Instructions

Turns TikTok URLs or local video files into ingestion-contract-ready assets for the Hive Brain pipeline.

## Critical constraints

- **Python 3.12 only** — `faster-whisper` requires `ctranslate2` wheels not yet built for 3.14+
- **Venv is outside this repo**: `/Users/joshuawallace/Data/TikTok/.venv`
- **`--rights` is mandatory** — the script refuses to run without `own | permitted | research`

## Running the extractor

```bash
# Single video (URL or local file)
cd /Users/joshuawallace/Data/TikTok
.venv/bin/python extract.py "<URL or /path/to/file.mp4>" --rights research

# Batch from favs_raw.txt
./batch_extract.sh                        # uses exports/favs_raw.txt
./batch_extract.sh /path/to/other.txt    # custom URL list

# Reprocess preserved legacy source videos
./reprocess_sources.sh

# Patch missing metadata (source_url, creator, duration) in already-extracted dirs
.venv/bin/python patch_metadata.py
```

## Dependency check

```bash
which ffmpeg && which yt-dlp   # brew install ffmpeg yt-dlp
test -f /Users/joshuawallace/Data/TikTok/.venv/bin/python || echo "venv missing"
```

## Key files

| File | Purpose |
| --- | --- |
| `extract.py` | Main extractor — single URL or local file |
| `batch_extract.sh` | Batch loop over `exports/favs_raw.txt`; skips done/failed IDs |
| `patch_metadata.py` | Back-fills `source_url`, `creator`, `duration_s` in extracted dirs |
| `reprocess_sources.sh` | Re-runs extractor over legacy `exports/*/source/*.mp4` files |
| `exports/ingest.py` | Ingests export folders into Hive Brain `inbox-raw/` |
| `exports/favs_raw.txt` | Master URL queue (one URL per line) |
| `exports/done_ids.txt` | Persistent dedup ledger — extracted video IDs |
| `exports/failed_ids.txt` | Persistent skip list — remove an ID here to retry |

## Output contract

The extractor writes to `.staging/` first, validates, then atomically moves to the final path:

```text
/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/
  content.md        # YAML frontmatter + ingestion contract fields

/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_assets/tiktok/tiktok-video-<id>/
  meta.json
  source/
  thumbnail.jpg
  transcript/
  audio/
  frames/
```

Errors land in: `Inbox-Raw/_extraction_errors/tiktok/tiktok-video-<id>-error.json`

## Deduplication

- Video ID extracted from URL via regex `[0-9]{17,}`
- `done_ids.txt` and `failed_ids.txt` are checked before each run
- Persistent ledger at `~/.extractors/tiktok/extraction-history.json`
- Re-run a failed video: remove its ID from `failed_ids.txt`

## Legacy exports

`exports/<date>_<creator>_<title-slug>/` folders are the old format. They are **never modified** by the pipeline — use `reprocess_sources.sh` to re-extract them into the contract format, or `exports/ingest.py` to push them into Hive Brain.

## Common pitfalls

- `yt-dlp` breaks when TikTok changes its site — download manually and pass the local `.mp4` path
- First `faster-whisper` run downloads ~500 MB to `~/.cache/huggingface/`
- If TikTok provides platform captions, ASR transcription is skipped automatically
- `--zone work` overrides the default `personal` zone tag in the contract output

## Favorites pull scope (process update)

- When checking for new favorites, only pull recent items from the latest **2–3 pages**.
- Do not backfill older historical favorites unless explicitly requested.

## Skill

The `tiktok-extract` skill (`.claude/skills/tiktok-extract/SKILL.md`) covers both single-video extraction and the "new favorites" browser-scrape + batch workflow. Load it for step-by-step guidance on either flow.

## Further reading

- Full CLI flags and rights policy: [README.md](README.md)
