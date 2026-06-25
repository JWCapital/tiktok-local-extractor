# TikTok Extraction Pipeline — Agent Instructions

Turns TikTok URLs or local video files into Hive-compliant ingestion-contract assets.

**Version:** 2.1.0 | **Updated:** 2026-06-24

## Critical Constraints

- **Python 3.12 only** — `faster-whisper` requires `ctranslate2` wheels not available for Python 3.14+
- **Venv location:** `./.venv` (project root, NOT `/Users/joshuawallace/Data/TikTok/.venv`)
- **`--rights` mandatory** — script refuses to run without `own | permitted | research`
- **Zone compliance:** `routing_zone: work` enforced (changed from personal, 2026-06-24)

## Running the extractor

```bash
# Single video (URL or local file)
cd /Users/joshuawallace/Data/TikTok

# Step 1: stage only
.venv/bin/python extract.py "<URL or /path/to/file.mp4>" --rights research --stage-only

# Step 2: finalize staged assets (separate run)
.venv/bin/python extract.py --finalize-all

# Batch from favs_raw.txt
./batch_extract.sh                        # uses _assets/tiktok/queues/favs_raw.txt
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
| `batch_extract.sh` | Batch loop over `_assets/tiktok/queues/favs_raw.txt`; skips done/failed IDs |
| `patch_metadata.py` | Back-fills `source_url`, `creator`, `duration_s` in extracted dirs |
| `reprocess_sources.sh` | Re-runs extractor over legacy `_assets/tiktok/legacy_exports/*/source/*.mp4` files |
| `_assets/tiktok/queues/favs_raw.txt` | Master URL queue (one URL per line) |
| `_assets/tiktok/state/done_ids.txt` | Persistent dedup ledger — extracted video IDs |
| `_assets/tiktok/state/failed_ids.txt` | Persistent skip list — remove an ID here to retry |

## Contract Output Structure

Two-step workflow:
1. **Stage:** Write to `_staging/tiktok/tiktok-video-<id>/` (validate, non-destructive)
2. **Finalize:** Atomically move to final lanes (polled + asset storage)

```text
/Users/joshuawallace/Data/Sync_Data/Inbox-Raw/
  tiktok/tiktok-video-<id>/
    content.md        # YAML frontmatter (polled inbox lane)
  _assets/tiktok/tiktok-video-<id>/
    meta.json
    source/
    thumbnail.jpg
    transcript/
    audio/
    frames/
  _extraction_errors/tiktok/
    tiktok-video-<id>-error.json
```

**Hive Compliance:**
- All required fields present and validated
- `routing_zone: work` (public TikTok content)
- Quality checks: metadata_completeness, dedup_status, extraction_errors

See [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md) for full specification.

## Deduplication

- Video ID extracted from URL via regex `[0-9]{17,}`
- `_assets/tiktok/state/done_ids.txt` and `_assets/tiktok/state/failed_ids.txt` are checked before each run
- In batch/reprocess workflows, `done_ids.txt` is written only after successful finalize
- Persistent ledger at `/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/extraction-history.json`
- Re-run a failed video: remove its ID from `_assets/tiktok/state/failed_ids.txt`

## Legacy exports

Legacy source folders are stored under `_assets/tiktok/legacy_exports/<date>_<creator>_<title-slug>/`. They are **never modified** by the pipeline — use `reprocess_sources.sh` to re-extract them into the contract format.

## Common Issues & Workarounds

| Issue | Cause | Fix |
|-------|-------|-----|
| `yt-dlp` download fails | TikTok site changes | Download manually, pass local `.mp4` path |
| Whisper model missing | First run | Accept ~500 MB download to `~/.cache/huggingface/` |
| Platform captions ignored | By design | ASR only if no platform captions |
| Zone compliance fails | Old code | Upgrade extract.py (v2.1.0+) |
| Venv path error | Wrong location | Use `./.venv` (project root, not TikTok/) |

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions.

## Favorites pull scope (process update)

- When checking for new favorites, only pull recent items from the latest **2–3 pages**.
- Do not backfill older historical favorites unless explicitly requested.

## Recent Changes (v2.1.0 — 2026-06-24)

- ✅ `routing_zone: work` enforced (changed from `personal` for Hive indexer compliance)
- ✅ Title extraction: use `meta.json` title (not generic fallback)
- ✅ Creator handles: strip `@` prefix for dedup consistency
- ✅ Venv paths corrected to `./.venv`
- ✅ Default `--zone` changed from `personal` to `work`
- ✅ Extraction ledger reset (2026-06-24) for reprocessing 381 legacy videos

## Skill & Automation

The `tiktok-extract` skill (`.claude/skills/tiktok-extract/SKILL.md`) covers:
- Single-video extraction (URL or local file)
- "Process new favorites" browser-scrape + batch workflow
- Metadata patching and legacy reprocessing

Load the skill for step-by-step guidance on any workflow.

## Further reading

- Full CLI flags and rights policy: [README.md](README.md)
