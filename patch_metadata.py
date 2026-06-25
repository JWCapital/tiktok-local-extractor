#!/usr/bin/env python3
"""Patch TikTok metadata for current Inbox-Raw + _assets layout.

Updates:
- _assets/tiktok/tiktok-video-<id>/meta.json
- Inbox-Raw/tiktok/tiktok-video-<id>/*.md metadata file
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

MAX_FILENAME_SLUG_LEN = 150

ROOT = Path("/Users/joshuawallace/Data/Sync_Data/Inbox-Raw")
INBOX = ROOT / "tiktok"
ASSETS = ROOT / "_assets" / "tiktok"
URL_SOURCES = [
    Path("/Users/joshuawallace/Downloads/kwitcom_favorites.txt"),
    Path("/Users/joshuawallace/Data/Sync_Data/_assets/tiktok/queues/favs_raw.txt"),
]


def build_url_map(url_sources: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for fpath in url_sources:
        if not fpath.exists():
            continue
        for line in fpath.read_text(encoding="utf-8", errors="ignore").splitlines():
            url = line.strip()
            m = re.search(r"/video/(\d+)", url)
            if m:
                out[m.group(1)] = url
    return out


def ffprobe_duration(video_path: Path) -> float | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(video_path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            dur = stream.get("duration")
            if dur:
                return round(float(dur), 1)
    except Exception:
        pass
    return None


def patch_frontmatter(md_path: Path, updates: dict[str, str]) -> bool:
    text = md_path.read_text(encoding="utf-8")
    changed = False
    for key, value in updates.items():
        pattern = rf"^({re.escape(key)}:)(.*)$"
        replacement = f"\\1 {value}"
        new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
        if count:
            text = new_text
            changed = True
    if changed:
        md_path.write_text(text, encoding="utf-8")
    return changed


def extract_username(url: str) -> str:
    m = re.search(r"tiktok\.com/@([^/]+)/video/", url)
    return m.group(1) if m else "unknown"


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _slug(text: str, max_len: int = MAX_FILENAME_SLUG_LEN) -> str:
    text = _normalize_whitespace(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:max_len]


def _extract_h1_title(md_path: Path) -> str:
    for line in md_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("# "):
            return _normalize_whitespace(line[2:])
    return ""


def _build_filename_slug(title: str, creator: str = "") -> str:
    parts = [_slug(creator, 32), _slug(title, MAX_FILENAME_SLUG_LEN)]
    value = "-".join(part for part in parts if part)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:MAX_FILENAME_SLUG_LEN].rstrip("-") or "tiktok-video"


def _find_markdown_content_file(directory: Path) -> Path | None:
    markdown_files = sorted(
        [p for p in directory.glob("*.md") if p.is_file()],
        key=lambda p: (p.name != "content.md", p.name),
    )
    return markdown_files[0] if markdown_files else None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--url-source",
        action="append",
        default=[],
        help="Path to URL list file (repeatable). Defaults to built-in URL_SOURCES.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Force-refresh source_url/creator/duration and frontmatter even when already populated.",
    )
    p.add_argument(
        "--master-only",
        action="store_true",
        help="Only process videos whose IDs are present in the URL map (recommended for master-list refresh).",
    )
    return p.parse_args()


def _resolve_video_file(meta_path: Path, meta: dict) -> Path | None:
    video_rel = (((meta.get("files") or {}).get("video") or {}).get("path") or "").strip()
    if video_rel:
        candidate = (meta_path.parent / video_rel).resolve()
        if candidate.exists() and candidate.is_file():
            return candidate
    src_dir = meta_path.parent / "source"
    if src_dir.exists():
        for p in src_dir.glob("*"):
            if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".avi"} and p.is_file():
                return p
    return None


def main() -> None:
    args = parse_args()
    if not INBOX.exists() or not ASSETS.exists():
        raise SystemExit(f"Expected paths not found: {INBOX} and/or {ASSETS}")

    url_source_paths = [Path(p) for p in args.url_source] if args.url_source else URL_SOURCES
    url_map = build_url_map(url_source_paths)

    patched = 0
    skipped = 0
    missing_files = 0
    missing_url = 0
    not_in_master = 0
    touched_ids: list[str] = []

    for content_dir in sorted(INBOX.glob("tiktok-video-*")):
        if not content_dir.is_dir():
            continue
        video_id = content_dir.name.replace("tiktok-video-", "")

        if args.master_only and video_id not in url_map:
            not_in_master += 1
            continue

        meta_path = ASSETS / content_dir.name / "meta.json"
        content_md = _find_markdown_content_file(content_dir)
        if not meta_path.exists() or content_md is None or not content_md.exists():
            missing_files += 1
            continue

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        source_url = url_map.get(video_id, "").strip() or str(meta.get("source_url") or "").strip()
        if not source_url:
            missing_url += 1
            continue

        username = extract_username(source_url)
        human_title = _extract_h1_title(content_md) or _normalize_whitespace(str(meta.get("title") or ""))
        filename_slug = _build_filename_slug(human_title or f"tiktok-video-{video_id}", username)

        changed = False
        if args.force or not meta.get("source_url"):
            if meta.get("source_url") != source_url:
                changed = True
            meta["source_url"] = source_url

        if args.force or not meta.get("creator") or str(meta.get("creator")).lower() == "unknown":
            if meta.get("creator") != username:
                changed = True
            meta["creator"] = username

        duration = None if args.force else meta.get("duration_s")
        if duration is None:
            candidate = _resolve_video_file(meta_path, meta)
            if candidate:
                duration = ffprobe_duration(candidate)
            if duration is not None:
                if meta.get("duration_s") != duration:
                    changed = True
                meta["duration_s"] = duration

        if human_title and meta.get("title") != human_title:
            changed = True
            meta["title"] = human_title
        if meta.get("filename_slug") != filename_slug:
            changed = True
            meta["filename_slug"] = filename_slug
        suggested_name = f"{filename_slug}.md"
        if meta.get("suggested_markdown_filename") != suggested_name:
            changed = True
            meta["suggested_markdown_filename"] = suggested_name

        updates = {
            "source_url": source_url,
            "extracted_from_url": source_url,
            "tiktok_uploader_handle": f'"@{username}"',
            "tiktok_uploader_name": f'"{username.replace("-", " ").replace("_", " ").title()}"',
            "tiktok_video_url": source_url,
        }
        frontmatter_changed = patch_frontmatter(content_md, updates)
        changed = changed or frontmatter_changed

        if changed or args.force:
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            patched += 1
            touched_ids.append(video_id)
        else:
            skipped += 1

        if patched % 50 == 0:
            print(f"  Patched {patched}...")

    print("\nDone:")
    print(f"  patched={patched}")
    print(f"  skipped={skipped}")
    print(f"  missing_files={missing_files}")
    print(f"  missing_url={missing_url}")
    print(f"  not_in_master={not_in_master}")
    if touched_ids:
        print("  touched_ids_sample=" + ",".join(touched_ids[:10]))


if __name__ == "__main__":
    main()
