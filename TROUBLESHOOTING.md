<!-- generated-by: gsd-doc-writer -->
# TikTok Extraction — Troubleshooting Guide

**Version:** 2.1.0 | **Updated:** 2026-06-24

## Setup Issues

### Python 3.12 Not Found

**Error:**
```
ERROR: Python 3.12 not found in PATH
```

**Cause:** System Python is 3.14+ or 3.12 not installed

**Fix:**
```bash
# Check installed versions
python3 --version
python3.12 --version

# Install Python 3.12 (via Homebrew)
brew install python@3.12

# Link it
brew unlink python && brew link python@3.12
```

### Venv Path Error

**Error:**
```
ERROR: Cannot find Python interpreter at /Users/joshuawallace/Data/TikTok/.venv/bin/python
```

**Cause:** Venv is in wrong location (legacy path)

**Fix:**
```bash
# Venv is now at project root
cd /Users/joshuawallace/Data/Sync_Data/tools/tittok-local-extactor
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### ffmpeg or yt-dlp Missing

**Error:**
```
ERROR: 'ffmpeg' not found. Install with: brew install ffmpeg
```

**Fix:**
```bash
brew install ffmpeg yt-dlp
which ffmpeg && which yt-dlp  # Verify
```

### Dependency Installation Fails

**Error:**
```
ERROR: pip install failed for faster-whisper
```

**Cause:** Wrong Python version or incomplete system tools

**Fix:**
```bash
# Ensure Python 3.12 is active
.venv/bin/python --version  # Should be 3.12.x

# Force reinstall
.venv/bin/pip install --upgrade pip
.venv/bin/pip install --force-reinstall faster-whisper yt-dlp PyYAML

# Check installation
.venv/bin/pip show faster-whisper
```

---

## Download Issues

### yt-dlp Download Fails

**Error:**
```
ERROR: yt-dlp failed (exit 403)
HTTP 403: Forbidden
```

**Cause:** TikTok blocked yt-dlp (site changes) OR no cookies

**Fix (Option 1: Manual Download)**
```bash
# Download video manually in browser, save as video.mp4
# Then extract using local file
.venv/bin/python extract.py ~/Downloads/video.mp4 --rights research --stage-only
.venv/bin/python extract.py --finalize-all
```

**Fix (Option 2: Use Browser Cookies)**
```bash
# TikTok cookies will be read from Brave browser
# Ensure you're logged in to TikTok in Brave:
# /Users/joshuawallace/Library/Application Support/BraveSoftware/Brave-Browser

# Or export cookies manually:
# 1. Open TikTok in Brave
# 2. Export cookies using Cookie Editor extension
# 3. Save to exports/tiktok_cookies.txt

# Re-run extraction
.venv/bin/python extract.py "URL" --rights research --stage-only
```

**Fix (Option 3: Update yt-dlp)**
```bash
# TikTok often breaks when they update their site
# Update yt-dlp to latest version
.venv/bin/pip install --upgrade yt-dlp

# Re-try
.venv/bin/python extract.py "URL" --rights research --stage-only
```

### Segmentation Fault (ffmpeg)

**Error:**
```
Segmentation fault: 11
```

**Cause:** Corrupted video file or ffmpeg issue

**Fix:**
```bash
# Update ffmpeg
brew upgrade ffmpeg

# Or skip video processing
.venv/bin/python extract.py "URL" --rights research --stage-only --no-video

# Or use local file that works
.venv/bin/python extract.py ~/working_video.mp4 --rights research --stage-only
```

---

## Transcription Issues

### Whisper Model Not Found

**Error:**
```
ERROR: Whisper model 'small' not found in cache
Downloading to ~/.cache/huggingface/...
```

**Cause:** First run (normal) — Whisper downloads ~500 MB

**Fix:**
```bash
# This is expected on first run. Let it download (~5-10 min)
# Subsequent runs will use cached model

# Pre-download if you want to avoid first-run delay:
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small')"

# Check cache size:
du -sh ~/.cache/huggingface/
```

### CUDA Out of Memory

**Error:**
```
CUDA out of memory: GPU memory usage exceeded
```

**Cause:** GPU memory insufficient for transcription

**Fix:**
```bash
# Use CPU instead of GPU
.venv/bin/python extract.py "URL" --rights research --stage-only

# (extract.py defaults to CPU, so this shouldn't happen)

# Or use smaller model:
.venv/bin/python extract.py "URL" --rights research --stage-only --model tiny
```

### Transcription Takes Too Long

**Performance:** Whisper:small should be 1-2 minutes per video

**If slower:**
```bash
# Check for background processes using CPU
ps aux | grep python

# Or use faster (lower quality) model:
.venv/bin/python extract.py "URL" --rights research --stage-only --model tiny  # ~30 sec per video

# Or skip transcription:
.venv/bin/python extract.py "URL" --rights research --stage-only --no-video
```

---

## Contract Compliance Issues

### Zone Compliance Fails

**Error:**
```
ERROR: routing_zone validation failed
Expected: work, Got: personal
```

**Cause:** Old extract.py version (pre-v2.1.0) still running

**Fix:**
```bash
# Upgrade extract.py to v2.1.0+
git log --oneline extract.py | head -5  # Check if a4b1bd5 is present

# If not, pull latest:
git pull origin main

# Verify zone default:
.venv/bin/python extract.py --help | grep zone
# Should show: default: work
```

### Title Not Found

**Error:**
```
WARNING: title extraction failed
Falling back to: TikTok by creator
```

**Cause:** meta.json not available or title field missing

**Fix:**
```bash
# This is expected for local files without TikTok metadata
# Extract will use fallback format

# To provide custom title, edit content.md after finalization:
# Edit: /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/content.md
# Update: title: "..." field
```

### Creator Handle Not Stripped

**Error:**
```
ERROR: creator handle validation failed
Handle '@creator' should be 'creator'
```

**Cause:** Old extract.py version (pre-v2.1.0)

**Fix:**
```bash
# Upgrade extract.py:
git pull origin main

# Verify:
.venv/bin/python extract.py --help | grep -A2 "creator"

# Re-extract with --force:
.venv/bin/python extract.py "URL" --rights research --stage-only --force
.venv/bin/python extract.py --finalize-all
```

---

## Deduplication Issues

### Video Already Extracted

**Error:**
```
ERROR: Video already extracted (in done_ids.txt)
Skipping...
```

**Cause:** Video ID is in `done_ids.txt` from previous extraction

**Fix (Option 1: Skip)** — This is normal behavior, video won't be re-extracted

**Fix (Option 2: Force Re-extraction)**
```bash
# Remove from done_ids.txt:
VIDID="1234567890123456"
sed -i '' "/^$VIDID$/d" exports/done_ids.txt

# Also remove from failed list if present:
sed -i '' "/^$VIDID$/d" exports/failed_ids.txt

# Re-extract with --force flag:
.venv/bin/python extract.py "URL" --rights research --stage-only --force
.venv/bin/python extract.py --finalize-all
```

### Video in Failed List

**Error:**
```
ERROR: Video permanently failed (in failed_ids.txt)
Skipping permanently...
```

**Cause:** Video extraction failed before, was added to `failed_ids.txt`

**Fix:**
```bash
# Remove from failed list to retry:
VIDID="1234567890123456"
sed -i '' "/^$VIDID$/d" exports/failed_ids.txt

# Re-extract:
.venv/bin/python extract.py "URL" --rights research --stage-only
.venv/bin/python extract.py --finalize-all

# If it fails again, error will be logged in:
# /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_extraction_errors/tiktok/tiktok-video-<id>-error.json
```

### Ledger Corruption

**Error:**
```
ERROR: extraction-history.json is invalid JSON
```

**Cause:** Ledger file corrupted or partially written

**Fix:**
```bash
# Backup corrupted ledger:
cp ~/.extractors/tiktok/extraction-history.json ~/.extractors/tiktok/extraction-history.json.corrupted

# Restore from backup (if available):
cp ~/.extractors/tiktok/extraction-history.json.backup ~/.extractors/tiktok/extraction-history.json

# Or reset for fresh reprocessing:
rm ~/.extractors/tiktok/extraction-history.json
# (A new blank ledger will be created on next extraction)
```

---

## Output Issues

### Staging Directory Fills Up Disk

**Symptom:**
```
ERROR: No space left on device
```

**Cause:** `_staging/` directory never cleared

**Check size:**
```bash
du -sh /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging/
```

**Fix:**
```bash
# Finalize all pending staged videos:
.venv/bin/python extract.py --finalize-all

# Or manually remove if safe:
rm -rf /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_staging/tiktok/tiktok-video-<id>/

# Check remaining:
du -sh /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/
```

### Output Directory Permission Denied

**Error:**
```
ERROR: Permission denied: /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/
```

**Fix:**
```bash
# Check permissions:
ls -la /Users/joshuawallace/Data/Sync_Data/

# Fix ownership:
sudo chown -R joshuawallace:staff /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/

# Or use different output directory:
.venv/bin/python extract.py "URL" --rights research --stage-only --out ~/tmp_inbox
```

---

## Batch Processing Issues

### Batch Script Stops Early

**Symptom:**
```
[RUN 45] https://www.tiktok.com/@creator/video/...
[FAIL 45] ...
Script exited
```

**Cause:** One video failed extraction, batch stopped

**Fix:**
```bash
# batch_extract.sh should continue on errors
# Check if it ran with `set -e`:
head -5 batch_extract.sh  # Should NOT have `set -e`

# Manually resume:
# 1. Check exports/failed_ids.txt for failed video IDs
# 2. Remove IDs you want to retry
# 3. Re-run batch:
./batch_extract.sh

# Or finalize any pending staged videos:
.venv/bin/python extract.py --finalize-all
```

### Batch Extraction Very Slow

**Performance:** 2-3 min per video (typical with Whisper:small)

**For 381 videos:** ~10-20 hours total

**If much slower:**
```bash
# Check for bottleneck:
# 1. CPU? Use smaller Whisper model (tiny)
# 2. Disk? Check disk speed (du -sh output dir)
# 3. Network? Use local files instead of URLs

# Use parallel batch extraction (if available):
# (Current implementation is sequential)

# Or extract manually in parallel:
for URL in $(cat exports/favs_raw.txt); do
  .venv/bin/python extract.py "$URL" --rights research --stage-only &
done
wait
.venv/bin/python extract.py --finalize-all
```

---

## Rights Policy

### --rights Not Provided

**Error:**
```
ERROR: --rights is required and must be one of: own, permitted, research
Ingestion refused: rights_status unknown.
```

**Fix:**
```bash
# Always provide --rights with valid value:
.venv/bin/python extract.py "URL" --rights own        # your content
.venv/bin/python extract.py "URL" --rights permitted  # creator approved
.venv/bin/python extract.py "URL" --rights research   # fair-use research
```

---

## Debugging

### Enable Verbose Output

```bash
# Add python debugging:
.venv/bin/python -v extract.py "URL" --rights research --stage-only

# Or check logs:
tail -f exports/batch_extract.log
tail -f exports/reprocess_sources.log
```

### Check Extraction Error

```bash
# After extraction fails, error logged in:
cat /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/_extraction_errors/tiktok/tiktok-video-<id>-error.json

# Example error:
{
  "extraction_run_id": "...",
  "source_type": "tiktok",
  "source_id": "tiktok-video-1234567890123456",
  "extraction_timestamp": "2026-06-24T14:32:15Z",
  "error_type": "metadata_gap",
  "error_message": "title extraction failed",
  "error_context": {
    "source": "https://www.tiktok.com/@creator/video/...",
    "title_value": "TikTok by creator"
  },
  "retry_count": 0,
  "status": "failed_permanently",
  "action_required": "Manual review: inspect source and retry extraction"
}
```

### Verify Contract Fields

```bash
# Check a finalized video:
cat /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/content.md | head -50

# Verify routing_zone:
grep "routing_zone:" /Users/joshuawallace/Data/Sync_Data/Inbox-Raw/tiktok/tiktok-video-<id>/content.md
# Should output: routing_zone: work
```

---

## Contact & Support

For issues not covered here:
1. Check the extraction error log: `_extraction_errors/tiktok/tiktok-video-<id>-error.json`
2. Review recent git commits to extract.py
3. Check TikTok site changes (yt-dlp may need update)
4. Review [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md) for contract requirements

---

## Related Documentation

- [README.md](./README.md) — Quick start
- [EXTRACTION_CONTRACT.md](./EXTRACTION_CONTRACT.md) — Contract specification
- [AGENTS.md](./AGENTS.md) — Agent instructions
- [.planning/STATE.md](./.planning/STATE.md) — Current state & progress
