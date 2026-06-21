---
name: tiktok-extract
description: Extract, transcribe, and screenshot a TikTok video (URL or local file) into an AI-ready folder. Also handles "process new TikTok favorites" — opens TikTok in the browser, scrapes the @kwitcom favorites tab, finds videos not yet in done_ids.txt, appends them to favs_raw.txt, and runs batch_extract.sh.
---

# tiktok-extract

Use this skill for two related tasks:
1. **Single video** — extract/transcribe one URL or local `.mp4`
2. **New favorites** — check @kwitcom favorites for unprocessed videos and batch-extract them

Trigger phrases for **new favorites**: "process new TikTok videos", "check new favs", "any new TikToks", "new TikTok favorites".

---

## Rights policy (enforce before every run)

| Value | When to use |
|---|---|
| `own` | User's own TikTok content |
| `permitted` | Creator has explicitly permitted download/use |
| `research` | Fair-use personal research context |

Favorites batch uses `--rights research` (personal research).

---

## Dep check

```bash
which ffmpeg     # brew install ffmpeg
which yt-dlp     # brew install yt-dlp
test -f /Users/joshuawallace/Data/TikTok/.venv/bin/python || echo "venv missing"
```

If the venv is missing:
```bash
cd /Users/joshuawallace/Data/TikTok
python3.12 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install "faster-whisper>=1.0,<2.0" "yt-dlp>=2024.1,<2026.0"
```

---

## A. Single video extraction

```bash
cd /Users/joshuawallace/Data/TikTok
.venv/bin/python extract.py "<URL or /path/to/file.mp4>" --rights <own|permitted|research>
```

Common optional flags:

| Flag | Default | Notes |
|---|---|---|
| `--model` | `small` | Whisper model: `tiny`, `small`, `medium`, `large-v3` |
| `--lang` | `en` | Language code or `auto` |
| `--scene-threshold` | `0.20` | Lower = more frames, higher = fewer |
| `--frames` | `scene` | `scene`, `interval`, or `both` |
| `--interval` | `2` | Seconds between frames (interval mode) |
| `--no-video` | off | Skip video download (audio-only) |

### Output

```
exports/<date>_<creator>_<title>/
  source/video.mp4
  source/info.json
  audio/audio.wav
  captions/<lang>.srt       (if platform captions exist)
  transcript/transcript.txt
  transcript/transcript.srt
  transcript/transcript.vtt
  transcript/transcript.json
  frames/scene_0001.jpg ...
  summary.md
  meta.json
```

After the run report: export path, transcript length + source (captions vs ASR), frame count, summary.md status.

---

## B. Check and process new favorites

**TikTok account:** `@kwitcom`  
**State files** (all in `/Users/joshuawallace/Data/TikTok/exports/`):
- `favs_raw.txt` — master URL queue (all favorites ever added)
- `done_ids.txt` — video IDs already successfully extracted
- `failed_ids.txt` — IDs to skip (previously failed)
- `live_fav_ids.txt` — scratch file: IDs scraped from favorites tab today
- `tiktok_cookies.txt` — Netscape cookie file for yt-dlp auth

**Batch script:** `/Users/joshuawallace/Data/TikTok/batch_extract.sh`  
**Output dir:** `/Users/joshuawallace/Data/Sync_Data/Inbox-Test`

### Step 1 — Open TikTok favorites in browser

Use browser tools (`mcp__claude-in-chrome__*`):

```
tabs_context_mcp  →  navigate to https://www.tiktok.com/@kwitcom  →  click Favorites tab
```

```javascript
// Click the Favorites tab
const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
const favTab = tabs.find(t => t.textContent.trim() === 'Favorites');
if (favTab) favTab.click();
```

### Step 2 — Scroll to load recent favorites only (2–3 pages)

```javascript
window.scrollTo(0, document.body.scrollHeight);
```

Repeat only **2 to 3 times total** (recent-window pull). Do **not** keep scrolling to historical content.

Recommended default: **3 page loads max**.

### Step 3 — Extract video IDs (avoid URL truncation)

```javascript
// Store URLs and IDs on window
window._favUrls = Array.from(document.querySelectorAll('a[href*="/video/"]'))
  .map(a => a.href.split('?')[0])
  .filter((v,i,arr) => arr.indexOf(v)===i);
window._favIds = window._favUrls.map(u => u.match(/\/video\/(\d+)/)?.[1]).filter(Boolean);
window._idUrlMap = {};
window._favUrls.forEach(u => {
  const m = u.match(/\/video\/(\d+)/);
  if (m) window._idUrlMap[m[1]] = u;
});
window._favIds.length  // confirm count
```

Retrieve IDs in batches of 40 to avoid output truncation:
```javascript
window._favIds.slice(0, 40).join('\n')
window._favIds.slice(40, 80).join('\n')
// ...etc
```

Write all IDs to `exports/live_fav_ids.txt`.

### Step 4 — Find new IDs

```bash
python3 - << 'EOF'
import re

with open('exports/live_fav_ids.txt') as f:
    live_ids = set(l.strip() for l in f if l.strip())
with open('exports/done_ids.txt') as f:
    done_ids = set(l.strip() for l in f if l.strip())
try:
    with open('exports/failed_ids.txt') as f:
        failed_ids = set(l.strip() for l in f if l.strip())
except FileNotFoundError:
    failed_ids = set()

new_ids = sorted(live_ids - done_ids - failed_ids, reverse=True)
print(f"Live: {len(live_ids)} | Done: {len(done_ids)} | New: {len(new_ids)}")
# Print chunks of 10 for JS lookup
for i in range(0, len(new_ids), 10):
    print(','.join(new_ids[i:i+10]))
EOF
```

### Step 5 — Resolve full URLs for new IDs

For each chunk of 10 new IDs, look up in `window._idUrlMap`:
```javascript
['ID1','ID2',...].map(id => window._idUrlMap[id] || 'MISSING:'+id).join('\n')
```

Collect all resolved URLs and append to `exports/favs_raw.txt`:
```bash
cat exports/new_favs_YYYY-MM-DD.txt >> exports/favs_raw.txt
```

### Step 6 — Run batch extraction

```bash
cd /Users/joshuawallace/Data/TikTok
bash batch_extract.sh exports/favs_raw.txt 2>&1 | tee -a exports/batch_extract.log
```

The script skips already-done and failed IDs automatically.

### Step 7 — Report to user

- How many new favorites found
- How many extracted successfully / failed
- Path: `/Users/joshuawallace/Data/Sync_Data/Inbox-Test/tiktok/`

---

## Recency window policy

- Favorites pull is intentionally capped to the most recent **2–3 pages**.
- Older favorites are out of scope unless explicitly requested.

---

## Notes

- `batch_extract.sh` uses `--cookies-from-browser brave` (not Safari — macOS blocks Full Disk Access to Safari cookies)
- If Brave cookies fail (403s), make sure TikTok is logged in inside Brave and retry
- Caption-first: if TikTok provides captions, ASR is skipped (`transcript_model: platform-captions` in meta.json)
- `summary.md` is compatible with `AI_Server/scripts/ingest/` — drop in `AI_Server/knowledge/inbox/raw/` and run `Ingest: normalize inbox`
