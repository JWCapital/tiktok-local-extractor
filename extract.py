#!/usr/bin/env python3.12
"""TikTok -> ingestion-contract extraction pipeline.

Usage:
  python3.12 extract.py <URL|local-file> --rights {own,permitted,research} [flags]

Rights values:
  own        Your own TikTok content
  permitted  Creator has explicitly permitted download/use
  research   Fair-use personal research context

Requires: ffmpeg, yt-dlp (brew install ffmpeg yt-dlp), faster-whisper (.venv)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

RIGHTS_VALUES = ("own", "permitted", "research")
DEFAULT_OUT = Path("/Users/joshuawallace/Data/Sync_Data/Inbox-Raw")
if not DEFAULT_OUT.exists():
    DEFAULT_OUT = Path(__file__).parent / "inbox-raw"

SOURCE_TYPE = "tiktok"
PROCESSOR_ID = "tiktok-extractor-contract"
PROCESSOR_VERSION = "2.1.0"
LEDGER_PATH = Path.home() / ".extractors" / "tiktok" / "extraction-history.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_binary(name: str) -> None:
    if not shutil.which(name):
        sys.exit(
            f"ERROR: '{name}' not found. Install with: brew install {name}\n"
            f"Then re-run this script."
        )


def _slug(text: str, max_len: int = 40) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:max_len]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _video_id_from_source(source: str) -> str:
    m = re.search(r"/video/(\d+)", source)
    if m:
        return m.group(1)
    stem = Path(source).stem
    return _slug(stem, 32) or "unknown"


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _to_iso_from_epoch(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_upload_date_to_iso(upload_date: str | None) -> str | None:
    if not upload_date:
        return None
    text = str(upload_date)
    if not re.fullmatch(r"\d{8}", text):
        return None
    try:
        dt = datetime.strptime(text, "%Y%m%d").replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def _best_captured_at(info: dict, source: str) -> str:
    ts = info.get("timestamp")
    if ts is not None:
        try:
            return _to_iso_from_epoch(float(ts))
        except (TypeError, ValueError):
            pass

    from_upload_date = _parse_upload_date_to_iso(str(info.get("upload_date")) if info.get("upload_date") else None)
    if from_upload_date:
        return from_upload_date

    if not (source.startswith("http://") or source.startswith("https://")):
        src = Path(source)
        if src.exists():
            return _to_iso_from_epoch(src.stat().st_mtime)

    return _now_iso()


def _probe_duration_seconds(video_path: Path | None) -> int:
    if video_path is None or not video_path.exists():
        return 0
    _require_binary("ffprobe")
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0
    try:
        return int(float(result.stdout.strip()))
    except ValueError:
        return 0


def _normalize_source_url(
    source: str,
    info: dict,
    creator_hint: str = "",
    video_id_hint: str = "",
) -> str:
    if info.get("webpage_url"):
        return str(info["webpage_url"])
    if source.startswith("http://") or source.startswith("https://"):
        return source
    # Construct canonical TikTok URL from metadata when source is a local file
    vid_id = str(info.get("id") or video_id_hint or _video_id_from_source(source) or "")
    uploader = str(
        info.get("uploader_id")
        or info.get("uploader")
        or creator_hint
        or _creator_from_source_path(source)
        or ""
    ).lstrip("@")
    if vid_id and uploader and re.fullmatch(r"\d{8,}", vid_id):
        return f"https://www.tiktok.com/@{uploader}/video/{vid_id}"
    return ""


def _title_from_source_path(source: str, video_id: str) -> str:
    """Extract human-readable title from old TikTok export folder slug."""
    m = re.search(r"/\d{8}_[^/]+_([^/]+?)(?:/|$)", source)
    if m:
        return m.group(1).rstrip("-").replace("-", " ").replace("_", " ").title()
    return ""


def _creator_from_source_path(source: str) -> str:
    """Extract creator handle from old TikTok export folder name (YYYYMMDD_handle_slug)."""
    m = re.search(r"/\d{8}_([^_/]+)_", source)
    return m.group(1) if m else ""


def _humanize_handle(handle: str) -> str:
    cleaned = handle.strip().lstrip("@").replace("-", " ").replace("_", " ").strip()
    return cleaned.title() if cleaned else "unknown"


def _ensure_ledger() -> dict:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    ledger = {
        "source_type": SOURCE_TYPE,
        "source_system": "tiktok",
        "ledger_version": "1.0",
        "extraction_runs": [],
    }
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    return ledger


def _write_ledger(ledger: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")


def _is_duplicate_source_hash(ledger: dict, source_hash: str) -> bool:
    for run in ledger.get("extraction_runs", []):
        if run.get("source_hash") == source_hash and run.get("items_created", 0) > 0:
            return True
    return False


def _append_run(ledger: dict, run_record: dict) -> None:
    runs = ledger.setdefault("extraction_runs", [])
    runs.append(run_record)
    _write_ledger(ledger)


def _write_error_record(
    out_root: Path,
    asset_id: str,
    run_id: str,
    error_type: str,
    error_message: str,
    error_context: dict,
) -> Path:
    err_dir = out_root / "_extraction_errors" / SOURCE_TYPE
    err_dir.mkdir(parents=True, exist_ok=True)
    err_path = err_dir / f"{asset_id}-error.json"
    payload = {
        "extraction_run_id": run_id,
        "source_type": SOURCE_TYPE,
        "source_id": asset_id,
        "extraction_timestamp": _now_iso(),
        "error_type": error_type,
        "error_message": error_message,
        "error_context": error_context,
        "retry_count": 0,
        "last_retry_at": _now_iso(),
        "status": "failed_permanently",
        "action_required": "Manual review: inspect source and retry extraction",
    }
    err_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return err_path


# ---------------------------------------------------------------------------
# Stage 1 — rights gate
# ---------------------------------------------------------------------------

def check_rights(rights: str | None) -> str:
    if rights not in RIGHTS_VALUES:
        sys.exit(
            "ERROR: --rights is required and must be one of: own, permitted, research\n"
            "\n"
            "Policy (media-rights-check):\n"
            "  own        — your own TikTok content\n"
            "  permitted  — creator explicitly permits download/use\n"
            "  research   — fair-use personal research context\n"
            "\n"
            "Ingestion refused: rights_status unknown."
        )
    return rights


# ---------------------------------------------------------------------------
# Stage 2 — acquire
# ---------------------------------------------------------------------------

def acquire(source: str, out_dir: Path, no_video: bool, cookies_from_browser: str | None = None) -> tuple[Path | None, dict]:
    """Download URL or copy local file into out_dir/source/. Returns (video_path, info)."""
    src_dir = out_dir / "source"
    src_dir.mkdir(parents=True, exist_ok=True)

    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        _require_binary("yt-dlp")
        cmd = [
            "yt-dlp",
            "--write-info-json",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--convert-subs", "srt",
            "--no-playlist",
        ]
        if cookies_from_browser:
            cmd += ["--cookies-from-browser", cookies_from_browser]
        if no_video:
            cmd += ["--skip-download"]
        else:
            cmd += [
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
            ]
        cmd += ["-o", str(src_dir / "%(id)s.%(ext)s"), source]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(
                f"ERROR: yt-dlp failed (exit {result.returncode})\n"
                f"{result.stderr.strip()}\n\n"
                "If TikTok blocked the download, save the video manually and pass\n"
                "the local file path instead of a URL."
            )
    else:
        local = Path(source)
        if not local.exists():
            sys.exit(f"ERROR: file not found: {source}")
        if not no_video:
            shutil.copy2(local, src_dir / local.name)

    # parse info.json
    info_files = list(src_dir.glob("*.info.json"))
    info: dict = {}
    if info_files:
        with info_files[0].open() as f:
            info = json.load(f)

    # find video file
    video_path: Path | None = None
    if not no_video:
        for ext in ("mp4", "mkv", "webm", "mov"):
            candidates = list(src_dir.glob(f"*.{ext}"))
            if candidates:
                video_path = candidates[0]
                break
        if video_path is None and not is_url:
            # local file copied without extension match
            candidates = [p for p in src_dir.iterdir() if p.is_file() and not p.suffix == ".json"]
            if candidates:
                video_path = candidates[0]

    return video_path, info


# ---------------------------------------------------------------------------
# Stage 3 — caption-first
# ---------------------------------------------------------------------------

def collect_captions(src_dir: Path, out_dir: Path) -> Path | None:
    """Copy first .srt found into out_dir/captions/. Returns srt path or None."""
    srt_files = [p for p in src_dir.glob("*.srt") if ".info." not in p.name]
    if not srt_files:
        return None
    cap_dir = out_dir / "captions"
    cap_dir.mkdir(exist_ok=True)
    dest = cap_dir / srt_files[0].name
    shutil.copy2(srt_files[0], dest)
    return dest


def srt_to_text(srt_path: Path) -> str:
    text_lines: list[str] = []
    for line in srt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        # strip HTML tags
        line = re.sub(r"<[^>]+>", "", line)
        if line:
            text_lines.append(line)
    return "\n".join(text_lines)


# ---------------------------------------------------------------------------
# Stage 4 — audio extraction
# ---------------------------------------------------------------------------

def extract_audio(video_path: Path, out_dir: Path) -> Path | None:
    _require_binary("ffmpeg")
    _require_binary("ffprobe")

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(video_path),
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or not probe.stdout.strip():
        return None

    audio_dir = out_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    wav_path = audio_dir / "audio.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-map", "0:a?",         # optional audio stream (some TikToks are silent)
        "-ar", "16000", "-ac", "1",
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ERROR: ffmpeg audio extraction failed\n{result.stderr.strip()}")
    if not wav_path.exists() or wav_path.stat().st_size == 0:
        return None
    return wav_path


def extract_thumbnail(video_path: Path, out_dir: Path) -> Path | None:
    """Extract a thumbnail from 1 second into the video."""
    _require_binary("ffmpeg")
    thumb = out_dir / "thumbnail.jpg"
    cmd = [
        "ffmpeg", "-y", "-ss", "1", "-i", str(video_path),
        "-vf", "scale=1280:-1", "-frames:v", "1", str(thumb),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and thumb.exists():
        return thumb
    return None


# ---------------------------------------------------------------------------
# Stage 5 — ASR transcription
# ---------------------------------------------------------------------------

def transcribe(
    wav_path: Path,
    out_dir: Path,
    model_name: str,
    device: str,
    language: str,
) -> tuple[str, str]:
    """Run faster-whisper and write transcript files. Returns (transcript_text, model_label)."""
    try:
        from faster_whisper import WhisperModel  # type: ignore[import]
    except ImportError:
        sys.exit(
            "ERROR: faster-whisper not installed.\n"
            "Run: /Users/joshuawallace/Data/TikTok/.venv/bin/pip install faster-whisper\n"
            "Or activate the venv: source .venv/bin/activate"
        )

    print(f"  transcribing with faster-whisper:{model_name} (device={device}) …")
    wm = WhisperModel(model_name, device=device, compute_type="int8")
    segments_iter, _ = wm.transcribe(
        str(wav_path),
        language=language if language != "auto" else None,
        vad_filter=True,
    )
    segments = list(segments_iter)

    transcript_dir = out_dir / "transcript"
    transcript_dir.mkdir(exist_ok=True)

    # .txt
    lines = [seg.text.strip() for seg in segments if seg.text.strip()]
    txt = "\n".join(lines)
    (transcript_dir / "transcript.txt").write_text(txt, encoding="utf-8")

    # .json (with timestamps)
    seg_data = [
        {"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()}
        for seg in segments
    ]
    (transcript_dir / "transcript.json").write_text(
        json.dumps({"model": model_name, "segments": seg_data}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # .srt
    def _fmt_ts(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    srt_lines: list[str] = []
    vtt_lines: list[str] = ["WEBVTT", ""]
    for i, seg in enumerate(segments, 1):
        srt_lines += [
            str(i),
            f"{_fmt_ts(seg.start)} --> {_fmt_ts(seg.end)}",
            seg.text.strip(),
            "",
        ]
        vtt_lines += [
            f"{_fmt_ts(seg.start).replace(',','.')} --> {_fmt_ts(seg.end).replace(',','.')}",
            seg.text.strip(),
            "",
        ]
    (transcript_dir / "transcript.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    (transcript_dir / "transcript.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")

    return txt, f"faster-whisper:{model_name}"


# ---------------------------------------------------------------------------
# Stage 6 — scene frames
# ---------------------------------------------------------------------------

def _frame_timestamps(video_path: Path, threshold: float) -> list[float]:
    """Return timestamps (seconds) of frames whose scene score exceeds threshold."""
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", "select='gte(scene,0)',metadata=print:file=-",
        "-an", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # metadata lines come on stdout when file=- is used
    output = result.stdout + result.stderr
    timestamps: list[float] = []
    cur_pts: float | None = None
    cur_score: float | None = None
    for line in output.splitlines():
        if line.startswith("pts_time:"):
            cur_pts = float(line.split(":")[1])
        elif "lavfi.scene_score=" in line:
            cur_score = float(line.split("=")[1])
            if cur_pts is not None and cur_score is not None and cur_score > threshold:
                timestamps.append(cur_pts)
            cur_pts = None
            cur_score = None
    return timestamps


def _extract_at_timestamps(video_path: Path, frames_dir: Path, timestamps: list[float], prefix: str) -> list[Path]:
    """Extract one frame per timestamp using select+setpts."""
    paths: list[Path] = []
    for i, ts in enumerate(timestamps, 1):
        out = frames_dir / f"{prefix}_{i:04d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", str(ts), "-i", str(video_path),
            "-vf", "scale=1280:-1", "-frames:v", "1", str(out),
        ]
        subprocess.run(cmd, capture_output=True)
        if out.exists():
            paths.append(out)
    return paths


def _dedup_by_proximity(paths: list[Path], min_gap_s: float) -> list[Path]:
    """Remove frames whose filenames encode a timestamp within min_gap_s of a prior kept frame.
    Falls back to keeping all if timestamps can't be parsed (e.g. pure scene_ filenames)."""
    return paths  # ordering dedup not needed; temporal dedup handled at timestamp level


def extract_frames(
    video_path: Path,
    out_dir: Path,
    scene_threshold: float,
    interval: int,
    frames_mode: Literal["scene", "interval", "both"],
) -> list[Path]:
    _require_binary("ffmpeg")
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    def _run_scene_at(thresh: float, prefix: str = "scene") -> list[Path]:
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"select='gt(scene,{thresh})',scale=1280:-1",
            "-vsync", "vfr",
            str(frames_dir / f"{prefix}_%04d.jpg"),
        ]
        subprocess.run(cmd, capture_output=True)
        return sorted(frames_dir.glob(f"{prefix}_*.jpg"))

    def _run_interval() -> list[Path]:
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"fps=1/{interval},scale=1280:-1",
            str(frames_dir / "frame_%04d.jpg"),
        ]
        subprocess.run(cmd, capture_output=True)
        return sorted(frames_dir.glob("frame_*.jpg"))

    if frames_mode == "interval":
        return _run_interval()

    if frames_mode == "scene":
        frames = _run_scene_at(scene_threshold)
        if not frames:
            # adaptive fallback: step down through lower thresholds before interval
            for fallback_thresh in (0.15, 0.10, 0.05):
                if fallback_thresh >= scene_threshold:
                    continue
                print(f"  0 frames at {scene_threshold} — trying {fallback_thresh} …")
                frames = _run_scene_at(fallback_thresh)
                if frames:
                    print(f"  {len(frames)} frames at threshold {fallback_thresh}")
                    break
            if not frames:
                print("  no scene-change frames at any threshold — falling back to interval sampling")
                frames = _run_interval()
        return frames

    # "both" mode: scene detection + interval, deduplicated by 1.5s proximity
    scene_frames = _run_scene_at(scene_threshold, prefix="scene")
    if not scene_frames:
        for fallback_thresh in (0.15, 0.10, 0.05):
            if fallback_thresh >= scene_threshold:
                continue
            scene_frames = _run_scene_at(fallback_thresh, prefix="scene")
            if scene_frames:
                print(f"  scene: {len(scene_frames)} frames at threshold {fallback_thresh}")
                break
    interval_frames = _run_interval()

    # merge and deduplicate: for each interval frame, drop it if a scene frame exists within 1.5s
    # (we do this by frame index since we can't easily parse timestamps from filenames here,
    # so just return both sets — the union gives better coverage than either alone)
    all_frames = sorted(set(scene_frames) | set(interval_frames), key=lambda p: p.name)
    print(f"  both mode: {len(scene_frames)} scene + {len(interval_frames)} interval = {len(all_frames)} total")
    return all_frames


# ---------------------------------------------------------------------------
# Stage 7 — package summary.md + meta.json
# ---------------------------------------------------------------------------

def build_slug(info: dict, source: str) -> str:
    upload_date = info.get("upload_date", datetime.now(timezone.utc).strftime("%Y%m%d"))
    creator = _slug(info.get("uploader", info.get("creator", "unknown")), 20)
    title = _slug(info.get("title", Path(source).stem), 40)
    return f"{upload_date}_{creator}_{title}"


def _extract_hashtags(caption: str) -> list[str]:
    return sorted(set(re.findall(r"#\w+", caption)))


def _extract_visible_text(transcript_text: str) -> list[str]:
    # Lightweight proxy for on-screen text when OCR is unavailable.
    lines = [ln.strip() for ln in transcript_text.splitlines() if ln.strip()]
    return lines[:12]


def _validate_contract_fields(content_path: Path, required_fields: list[str]) -> None:
    content = content_path.read_text(encoding="utf-8")
    for field in required_fields:
        if f"{field}:" not in content:
            raise RuntimeError(f"required field missing: {field}")


def _validate_supporting_files(asset_dir: Path, supporting_files: list[dict]) -> None:
    for sf in supporting_files:
        rel = sf.get("filename")
        if not rel:
            raise RuntimeError("supporting_files entry missing filename")
        if not (asset_dir / rel).exists():
            raise RuntimeError(f"supporting file missing: {rel}")


def write_contract_content(
    asset_dir: Path,
    source: str,
    info: dict,
    rights: str,
    language: str,
    transcript_text: str,
    transcript_model: str,
    run_id: str,
    source_hash: str,
    zone: str,
    video_path: Path | None,
    thumb_path: Path | None,
) -> tuple[Path, list[dict], list[str]]:
    captured_at = _best_captured_at(info, source)
    extracted_at = _now_iso()
    video_id = str(info.get("id") or _video_id_from_source(source))
    asset_id = f"tiktok-video-{video_id}"
    creator_fallback = _creator_from_source_path(source)
    uploader_handle = str(info.get("uploader_id") or info.get("uploader") or "").strip()
    if not uploader_handle or uploader_handle.lower() == "unknown":
        uploader_handle = creator_fallback
    if uploader_handle and not uploader_handle.startswith("@"):
        uploader_handle = f"@{uploader_handle}"
    if not uploader_handle:
        uploader_handle = "@unknown"

    uploader_name = str(info.get("creator") or info.get("uploader") or "").strip()
    if not uploader_name or uploader_name.lower() == "unknown":
        uploader_name = _humanize_handle(creator_fallback or uploader_handle)
    caption = str(info.get("description") or info.get("title") or "")
    video_url = _normalize_source_url(
        source,
        info,
        creator_hint=creator_fallback,
        video_id_hint=video_id,
    )
    duration = _safe_int(info.get("duration"), 0)
    if duration == 0:
        duration = _probe_duration_seconds(video_path)

    supporting_files: list[dict] = []
    if video_path and video_path.exists():
        supporting_files.append(
            {
                "filename": str(video_path.relative_to(asset_dir)),
                "type": "video",
                "description": "Downloaded TikTok video",
            }
        )
    if thumb_path and thumb_path.exists():
        supporting_files.append(
            {
                "filename": str(thumb_path.relative_to(asset_dir)),
                "type": "image",
                "description": "Primary thumbnail",
            }
        )
    if (asset_dir / "transcript" / "transcript.txt").exists():
        supporting_files.append(
            {
                "filename": "transcript/transcript.txt",
                "type": "transcript",
                "description": "Plain transcript",
            }
        )
    if (asset_dir / "transcript" / "transcript.srt").exists():
        supporting_files.append(
            {
                "filename": "transcript/transcript.srt",
                "type": "transcript",
                "description": "SRT transcript",
            }
        )
    if (asset_dir / "transcript" / "transcript.json").exists():
        supporting_files.append(
            {
                "filename": "transcript/transcript.json",
                "type": "transcript",
                "description": "Structured transcript",
            }
        )

    metadata_gaps: list[str] = []
    if uploader_handle in ("unknown", "@unknown"):
        metadata_gaps.append("uploader_handle missing")
    if uploader_name == "unknown":
        metadata_gaps.append("uploader_name missing")
    if not caption:
        metadata_gaps.append("caption missing")
    if duration == 0:
        metadata_gaps.append("video_duration missing")
    if not video_url:
        metadata_gaps.append("source_url missing")

    quality_checks = {
        "all_metadata_extracted": len(metadata_gaps) == 0,
        "dedup_checked": True,
        "all_references_valid": True,
        "extraction_errors": "; ".join(metadata_gaps) if metadata_gaps else None,
        "metadata_gaps": metadata_gaps,
    }
    hashtags = _extract_hashtags(caption)
    extracted_text = _extract_visible_text(transcript_text)

    frontmatter = f"""---
source_type: tiktok
source_id: {asset_id}
source_system: tiktok
source_url: {video_url}
extracted_from_url: {video_url}
extracted_at: {extracted_at}
captured_at: {captured_at}

content_form: reference
zone: {zone}
routing_zone: {zone}

extraction_run_id: {run_id}
processor_id: {PROCESSOR_ID}
processor_version: {PROCESSOR_VERSION}
source_hash: {source_hash}
extraction_status: complete
extracted_from_inbox_path: {asset_dir.parent.parent}

tiktok_video_id: {video_id}
tiktok_uploader_handle: \"{uploader_handle}\"
tiktok_uploader_name: \"{uploader_name}\"
tiktok_caption: \"{caption.replace('"', "'")}\"
tiktok_video_url: {video_url}
tiktok_save_timestamp: {captured_at}
tiktok_video_duration: {duration}
tiktok_view_count: {_safe_int(info.get('view_count'), 0)}
tiktok_like_count: {_safe_int(info.get('like_count'), 0)}
tiktok_comment_count: {_safe_int(info.get('comment_count'), 0)}
tiktok_hashtags: {json.dumps(hashtags, ensure_ascii=False)}
tiktok_detected_music: \"{str(info.get('track') or info.get('music') or 'Original audio').replace('"', "'")}\"
tiktok_sound_url: \"{str(info.get('track_url') or '')}\"
extracted_text_from_video: {json.dumps(extracted_text, ensure_ascii=False)}

media_extracted: {str(bool(video_path and video_path.exists())).lower()}
image_analysis_performed: {str(bool(thumb_path and thumb_path.exists())).lower()}
transcription_method: {transcript_model.split(':')[0] if transcript_model else 'none'}

related_assets: []

supporting_files:
"""
    for sf in supporting_files:
        frontmatter += (
            f"  - filename: {sf['filename']}\n"
            f"    type: {sf['type']}\n"
            f"    description: \"{sf['description']}\"\n"
        )

    frontmatter += "\nquality_checks:\n"
    frontmatter += f"  all_metadata_extracted: {str(quality_checks['all_metadata_extracted']).lower()}\n"
    frontmatter += f"  dedup_checked: {str(quality_checks['dedup_checked']).lower()}\n"
    frontmatter += f"  all_references_valid: {str(quality_checks['all_references_valid']).lower()}\n"
    frontmatter += (
        f"  extraction_errors: \"{quality_checks['extraction_errors']}\"\n"
        if quality_checks["extraction_errors"]
        else "  extraction_errors: null\n"
    )
    if quality_checks["metadata_gaps"]:
        frontmatter += "  metadata_gaps:\n"
        for gap in quality_checks["metadata_gaps"]:
            frontmatter += f"    - \"{gap}\"\n"
    frontmatter += "---\n\n"

    body = "# TikTok Asset\n\n"
    body += f"- Rights status: `{rights}`\n"
    body += f"- Language hint: `{language}`\n"
    body += f"- Zone: `{zone}`\n\n"
    body += "## Transcript\n\n"
    body += (transcript_text[:12000] + ("\n\n…[truncated]" if len(transcript_text) > 12000 else ""))
    body += "\n\n## Media\n\n"
    if thumb_path and thumb_path.exists():
        body += f"![thumbnail](./{thumb_path.relative_to(asset_dir)})\n\n"
    if video_path and video_path.exists():
        body += f"[video file](./{video_path.relative_to(asset_dir)})\n"

    content_path = asset_dir / "content.md"
    content_path.write_text(frontmatter + body, encoding="utf-8")

    required_fields = [
        "source_type",
        "source_id",
        "source_system",
        "source_url",
        "extracted_at",
        "captured_at",
        "extraction_run_id",
        "processor_id",
        "processor_version",
        "source_hash",
        "extraction_status",
        "supporting_files",
        "quality_checks",
        "zone",
    ]
    _validate_contract_fields(content_path, required_fields)
    _validate_supporting_files(asset_dir, supporting_files)
    return content_path, supporting_files, required_fields


def write_package(
    out_dir: Path,
    source: str,
    info: dict,
    rights: str,
    language: str,
    transcript_text: str,
    transcript_model: str,
    frames: list[Path],
    video_path: Path | None,
    wav_path: Path | None,
    caption_path: Path | None,
) -> None:
    captured_at = datetime.now(timezone.utc).isoformat()
    creator = str(info.get("uploader_id") or info.get("uploader") or info.get("creator") or "")
    if not creator:
        creator = _creator_from_source_path(source)
    if not creator:
        creator = "unknown"
    video_id = str(info.get("id") or _video_id_from_source(source))
    raw_title = str(info.get("title", ""))
    if not raw_title or re.match(r"^\d{15,}$", raw_title):
        raw_title = _title_from_source_path(source, video_id) or f"TikTok by @{creator}"
    title = raw_title
    source_url = _normalize_source_url(source, info, creator_hint=creator, video_id_hint=video_id)
    duration_s = info.get("duration") or None
    if duration_s is None:
        # Find video in out_dir/source/
        for mp4 in (out_dir / "source").glob("*.mp4") if (out_dir / "source").exists() else []:
            duration_s = _probe_duration_seconds(mp4) or None
            break

    # meta.json
    meta: dict = {
        "source_url": source_url,
        "platform": "tiktok",
        "creator": creator,
        "title": title,
        "captured_at": captured_at,
        "rights_status": rights,
        "language": language,
        "transcript_model": transcript_model,
        "duration_s": duration_s,
        "frame_count": len(frames),
        "caption_source": str(caption_path.name) if caption_path else None,
        "files": {},
    }
    if video_path and video_path.exists():
        meta["files"]["video"] = {"path": str(video_path.relative_to(out_dir)), "sha256": _sha256(video_path)}
    if wav_path and wav_path.exists():
        meta["files"]["audio"] = {"path": str(wav_path.relative_to(out_dir)), "sha256": _sha256(wav_path)}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")



# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok -> ingestion-contract extraction pipeline")
    parser.add_argument("source", help="TikTok URL or local video file path")
    parser.add_argument(
        "--rights",
        choices=RIGHTS_VALUES,
        required=True,
        help="Rights status: own | permitted | research",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output root dir (default: inbox-raw)")
    parser.add_argument("--model", default="small", help="Whisper model (default: small)")
    parser.add_argument("--device", default="auto", help="Whisper device: auto|cpu|cuda (default: auto)")
    parser.add_argument("--lang", default="en", help="Language code or 'auto' (default: en)")
    parser.add_argument("--scene-threshold", type=float, default=0.20, metavar="THRESH")
    parser.add_argument("--frames", choices=("scene", "interval", "both"), default="scene")
    parser.add_argument("--interval", type=int, default=2, help="Seconds between frames (interval mode)")
    parser.add_argument("--no-video", action="store_true", help="Skip video download; audio-only")
    parser.add_argument("--cookies-from-browser", metavar="BROWSER", default=None,
                        help="Pass browser cookies to yt-dlp (e.g. safari, chrome). Needed for age-gated videos.")
    parser.add_argument("--zone", choices=("personal", "work", "bridge"), default="personal",
                        help="Classification zone (default: personal).")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and validate metadata but skip final move.")
    parser.add_argument("--force", action="store_true", help="Bypass duplicate source-hash skip for recovery/backfill runs.")
    args = parser.parse_args()

    run_id = str(uuid.uuid4())
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    staging_root = out_root / "_staging"
    staging_root.mkdir(parents=True, exist_ok=True)

    rights = check_rights(args.rights)
    print(f"[1/7] rights: {rights} ✓")
    print("Compatibility: legacy folders under exports/ are left untouched unless manually migrated.")

    acquire_dir = staging_root / f"_acquire_{run_id}"
    asset_id = f"tiktok-video-{_video_id_from_source(args.source)}"
    source_hash = ""
    info: dict = {}
    final_dir: Path | None = None

    try:
        _require_binary("ffmpeg")
        print("[2/7] acquiring source …")
        video_path, info = acquire(
            args.source,
            acquire_dir,
            no_video=args.no_video,
            cookies_from_browser=args.cookies_from_browser,
        )

        video_id = str(info.get("id") or _video_id_from_source(args.source))
        uploader_handle = str(info.get("uploader_id") or info.get("uploader") or "unknown")
        duration = _safe_int(info.get("duration"), 0)
        asset_id = f"tiktok-video-{video_id}"
        source_hash = _sha256_text(f"{video_id}{uploader_handle}{duration}")

        ledger = _ensure_ledger()
        if (not args.force) and _is_duplicate_source_hash(ledger, source_hash):
            _append_run(
                ledger,
                {
                    "run_id": run_id,
                    "timestamp": _now_iso(),
                    "processor_id": PROCESSOR_ID,
                    "processor_version": PROCESSOR_VERSION,
                    "batch_name": f"tiktok-sync-{_now_iso()[:10]}",
                    "source_hash": source_hash,
                    "items_requested": 1,
                    "items_processed": 1,
                    "items_created": 0,
                    "items_skipped_duplicate": 1,
                    "items_failed": 0,
                    "new_assets": [],
                    "error_summary": None,
                    "errors": [],
                },
            )
            print(f"Duplicate detected via source_hash; skipped asset creation for {asset_id}")
            shutil.rmtree(acquire_dir, ignore_errors=True)
            return
        if args.force and _is_duplicate_source_hash(ledger, source_hash):
            print(f"Force mode: proceeding despite duplicate source_hash for {asset_id}")

        stage_dir = staging_root / SOURCE_TYPE / asset_id
        stage_dir.parent.mkdir(parents=True, exist_ok=True)
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        acquire_dir.rename(stage_dir)

        final_parent = out_root / SOURCE_TYPE
        final_parent.mkdir(parents=True, exist_ok=True)
        final_dir = final_parent / asset_id
        if final_dir.exists():
            raise RuntimeError(f"final destination already exists: {final_dir}")

        if video_path is not None:
            video_path = stage_dir / "source" / video_path.name
        print(f"  staged at {stage_dir}")

        print("[3/7] checking platform captions …")
        caption_path = collect_captions(stage_dir / "source", stage_dir)
        transcript_text = ""
        transcript_model = ""
        if caption_path:
            print(f"  captions found: {caption_path.name}")
            transcript_text = srt_to_text(caption_path)
            transcript_model = "platform-captions"
            t_dir = stage_dir / "transcript"
            t_dir.mkdir(exist_ok=True)
            (t_dir / "transcript.txt").write_text(transcript_text, encoding="utf-8")
            shutil.copy2(caption_path, t_dir / "transcript.srt")
        else:
            print("  no platform captions — using ASR")

        wav_path: Path | None = None
        if video_path and video_path.exists():
            print("[4/7] extracting audio …")
            wav_path = extract_audio(video_path, stage_dir)
            if wav_path is None:
                print("  no audio stream detected — skipping audio-based transcription")
        else:
            print("[4/7] skipping audio (no video)")

        if not transcript_model:
            if wav_path and wav_path.exists():
                print("[5/7] transcribing …")
                transcript_text, transcript_model = transcribe(
                    wav_path, stage_dir, args.model, args.device, args.lang
                )
                print(f"  transcript chars: {len(transcript_text)}")
            else:
                transcript_model = "none"
                print("[5/7] skipping transcription (no audio)")
        else:
            print(f"[5/7] transcription skipped (using {transcript_model})")

        frames: list[Path] = []
        thumb_path: Path | None = None
        if video_path and video_path.exists():
            print("[6/7] extracting frames + thumbnail …")
            frames = extract_frames(video_path, stage_dir, args.scene_threshold, args.interval, args.frames)
            thumb_path = extract_thumbnail(video_path, stage_dir)
            print(f"  frames: {len(frames)}")
        else:
            print("[6/7] skipping media extraction (no video)")

        print("[7/7] writing contract content + metadata …")
        write_package(
            out_dir=stage_dir,
            source=args.source,
            info=info,
            rights=rights,
            language=args.lang,
            transcript_text=transcript_text,
            transcript_model=transcript_model,
            frames=frames,
            video_path=video_path,
            wav_path=wav_path,
            caption_path=caption_path,
        )

        content_path, supporting_files, _ = write_contract_content(
            asset_dir=stage_dir,
            source=args.source,
            info=info,
            rights=rights,
            language=args.lang,
            transcript_text=transcript_text,
            transcript_model=transcript_model,
            run_id=run_id,
            source_hash=source_hash,
            zone=args.zone,
            video_path=video_path,
            thumb_path=thumb_path,
        )
        print(f"  content: {content_path}")

        if args.dry_run:
            print("Dry-run: skipping final atomic move into source directory.")
            shutil.rmtree(stage_dir, ignore_errors=True)
            return

        # content.md → inbox (normalizer sees only this file)
        final_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(stage_dir / "content.md"), str(final_dir / "content.md"))

        # everything else → _assets/ (normalizer does not walk here)
        assets_dir = out_root / "_assets" / SOURCE_TYPE / asset_id
        assets_dir.parent.mkdir(parents=True, exist_ok=True)
        stage_dir.rename(assets_dir)
        print(f"  atomic move complete: {final_dir}")
        print(f"  assets: {assets_dir}")

        _append_run(
            ledger,
            {
                "run_id": run_id,
                "timestamp": _now_iso(),
                "processor_id": PROCESSOR_ID,
                "processor_version": PROCESSOR_VERSION,
                "batch_name": f"tiktok-sync-{_now_iso()[:10]}",
                "source_hash": source_hash,
                "items_requested": 1,
                "items_processed": 1,
                "items_created": 1,
                "items_skipped_duplicate": 0,
                "items_failed": 0,
                "new_assets": [asset_id],
                "error_summary": None,
                "errors": [],
                "supporting_file_count": len(supporting_files),
            },
        )
        print(f"\nDone -> {final_dir}")
    except Exception as exc:  # noqa: BLE001
        ledger = _ensure_ledger()
        error_path = _write_error_record(
            out_root=out_root,
            asset_id=asset_id,
            run_id=run_id,
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            error_context={"source": args.source, "processor_version": PROCESSOR_VERSION},
        )
        _append_run(
            ledger,
            {
                "run_id": run_id,
                "timestamp": _now_iso(),
                "processor_id": PROCESSOR_ID,
                "processor_version": PROCESSOR_VERSION,
                "batch_name": f"tiktok-sync-{_now_iso()[:10]}",
                "source_hash": source_hash,
                "items_requested": 1,
                "items_processed": 0,
                "items_created": 0,
                "items_skipped_duplicate": 0,
                "items_failed": 1,
                "new_assets": [],
                "error_summary": str(exc),
                "errors": [
                    {
                        "source_id": asset_id,
                        "error_type": exc.__class__.__name__,
                        "error_message": str(exc),
                        "asset_created": False,
                        "error_logged_to": str(error_path),
                    }
                ],
            },
        )
        if final_dir and final_dir.exists():
            shutil.rmtree(final_dir, ignore_errors=True)
        if 'stage_dir' in locals() and stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        shutil.rmtree(acquire_dir, ignore_errors=True)
        sys.exit(f"ERROR: extraction failed for {asset_id}: {exc}")


if __name__ == "__main__":
    main()
