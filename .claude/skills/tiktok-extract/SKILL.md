---
name: tiktok-extract
description: Extract, transcribe, and screenshot a TikTok video (URL or local file) into an AI-ready folder under Ticktok/exports/. Enforces rights-first and caption-first policy. Produces video, audio, transcript (.txt/.srt/.vtt/.json), scene frames, summary.md, and meta.json.
---

# tiktok-extract

Use this skill whenever the user wants to extract, transcribe, or package a TikTok video
for AI use.

## Rights policy (enforce before every run)

Before running anything, confirm the user's rights status. **Refuse if unknown.**

| Value | When to use |
|---|---|
| `own` | User's own TikTok content |
| `permitted` | Creator has explicitly permitted download/use |
| `research` | Fair-use personal research context |

Caption-first rule: if TikTok provides platform captions, they are used as the transcript
and ASR is skipped. This is surfaced in `meta.json` as `transcript_model: platform-captions`.

## Dep check

Before running, verify:

```bash
which ffmpeg     # brew install ffmpeg
which yt-dlp     # brew install yt-dlp
test -f /Users/joshuawallace/Data/Ticktok/.venv/bin/python || echo "venv missing"
```

If the venv is missing, set it up:

```bash
cd /Users/joshuawallace/Data/Ticktok
python3.12 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install "faster-whisper>=1.0,<2.0" "yt-dlp>=2024.1,<2026.0"
```

## Run

```bash
cd /Users/joshuawallace/Data/Ticktok
.venv/bin/python extract.py "<URL or /path/to/file.mp4>" --rights <own|permitted|research>
```

Common optional flags:

| Flag | Default | Notes |
|---|---|---|
| `--model` | `small` | Whisper model: `tiny`, `small`, `medium`, `large-v3` |
| `--lang` | `en` | Language code or `auto` |
| `--scene-threshold` | `0.20` | Lower = more frames, higher = fewer |
| `--frames` | `scene` | `scene`, `interval`, or `both` (scene+interval merged) |
| `--interval` | `2` | Seconds between frames (interval or both mode) |
| `--no-video` | off | Skip downloading the video file (audio-only) |

## Output

```
exports/<date>_<creator>_<title>/
  source/video.mp4          source video
  source/info.json          yt-dlp metadata
  audio/audio.wav           16 kHz mono
  captions/<lang>.srt       platform captions (if any)
  transcript/transcript.txt
  transcript/transcript.srt
  transcript/transcript.vtt
  transcript/transcript.json  timestamped segments
  frames/scene_0001.jpg ...
  summary.md                AI-ready note (pkm-ingestion compatible frontmatter)
  meta.json                 full provenance
```

## After the run

Report to the user:
1. The `exports/<slug>/` path
2. Transcript length (chars) and source (captions vs ASR model)
3. Frame count
4. Whether `summary.md` is ready

The `summary.md` frontmatter is compatible with `AI_Server/scripts/ingest/` — if the user
later wants to feed it to the Hive Brain, they can drop it in `AI_Server/knowledge/inbox/raw/`
and run `Ingest: normalize inbox`.
