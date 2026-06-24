#!/usr/bin/env bash
# Batch extract TikTok favorites - skips already-done, logs progress
set -uo pipefail
# Avoid SIGPIPE from head/tail closing pipes early
trap '' PIPE

URLS_FILE="${1:-exports/favs_raw.txt}"
LOG_FILE="exports/batch_extract.log"
LINKS_FILE="exports/batch_links.tsv"
DONE_FILE="exports/done_ids.txt"       # persistent: survives reboots
FAILED_FILE="exports/failed_ids.txt"   # persistent: remove an ID here to retry it
OUT_DIR="/Users/joshuawallace/Data/Sync_Data/Inbox-Raw"
COOKIE_FILE="exports/tiktok_cookies.txt"

mkdir -p exports

if [[ ! -f "$URLS_FILE" ]]; then
  echo "ERROR: URL list not found: $URLS_FILE"
  echo "Add one TikTok URL per line (or pass a file path as the first arg)."
  exit 1
fi

if [[ ! -s "$URLS_FILE" ]]; then
  echo "ERROR: URL list is empty: $URLS_FILE"
  echo "Populate it with new favorites first, then re-run."
  exit 1
fi

echo "# Batch extraction started $(date)" >> "$LOG_FILE"
echo -e "url\tdescription_links" >> "$LINKS_FILE" 2>/dev/null || true

# Prefer browser cookies if Brave profile exists; otherwise fall back to exported cookie file.
COOKIE_ARGS=("--cookies-from-browser" "brave")
if [[ ! -d "$HOME/Library/Application Support/BraveSoftware/Brave-Browser" ]]; then
  if [[ -f "$COOKIE_FILE" ]]; then
    COOKIE_ARGS=("--cookies" "$COOKIE_FILE")
    echo "[INFO] Brave cookies not found; using cookie file: $COOKIE_FILE" | tee -a "$LOG_FILE"
  else
    echo "[WARN] No Brave cookie DB and no $COOKIE_FILE; continuing without cookie fallback" | tee -a "$LOG_FILE"
  fi
fi

# Read ALL URLs into array first (bash 3.2 compatible) — prevents subprocesses
# (ffmpeg/whisper) from consuming bytes off the while-loop's stdin fd.
URLS=()
while IFS= read -r line || [[ -n "$line" ]]; do
  URLS+=("$line")
done < "$URLS_FILE"

total="${#URLS[@]}"
count=0
skipped=0
failed=0
staged_ok=0

for url in "${URLS[@]}"; do
  [[ -z "$url" ]] && continue
  count=$((count + 1))

  # Skip if already extracted or permanently failed
  vid_id=$(echo "$url" | grep -oE '[0-9]{17,}' | head -1)
  if [ -n "$vid_id" ] && grep -qF "$vid_id" "$DONE_FILE" 2>/dev/null; then
    echo "[SKIP $count/$total] already done: $vid_id"
    skipped=$((skipped + 1))
    continue
  fi
  if [ -n "$vid_id" ] && grep -qF "$vid_id" "$FAILED_FILE" 2>/dev/null; then
    echo "[SKIP $count/$total] previously failed: $vid_id"
    skipped=$((skipped + 1))
    continue
  fi

  echo "[RUN $count/$total] $url"

  # Redirect stdin from /dev/null so no subprocess can steal from our loop
  if .venv/bin/python extract.py "$url" \
      --rights research \
      --stage-only \
      --frames both \
      --interval 3 \
      --out "$OUT_DIR" \
      "${COOKIE_ARGS[@]}" < /dev/null 2>>"$LOG_FILE"; then
    staged_ok=$((staged_ok + 1))

    # Extract links from info.json description
    latest_dir=$(ls -td exports/*/ 2>/dev/null | head -1)
    if [ -n "$latest_dir" ]; then
      info_json=$(ls "$latest_dir"source/*.info.json 2>/dev/null | head -1)
      if [ -n "$info_json" ]; then
        links=$(.venv/bin/python -c "
import json, re
d = json.load(open('$info_json'))
desc = d.get('description', '') + ' ' + d.get('webpage_url', '')
urls = re.findall(r'https?://[^\s\)\"\\']+', desc)
urls += [l.get('url','') for l in d.get('link_in_bio', []) if isinstance(l, dict)]
print('\t'.join(set(u for u in urls if u)))
" 2>/dev/null)
        if [ -n "$links" ]; then
          echo -e "$url\t$links" >> "$LINKS_FILE"
        fi
      fi
    fi
    echo "[OK $count/$total] $url" >> "$LOG_FILE"
  else
    echo "[FAIL $count/$total] $url" >> "$LOG_FILE"
    failed=$((failed + 1))
    if [ -n "$vid_id" ]; then echo "$vid_id" >> "$FAILED_FILE"; fi
  fi

  sleep 1

done

echo ""
echo "=== Finalize staged assets ==="
FINALIZE_OUT=$(mktemp)
if .venv/bin/python extract.py --finalize-all --out "$OUT_DIR" < /dev/null | tee "$FINALIZE_OUT" >> "$LOG_FILE"; then
  finalize_exit=0
else
  finalize_exit=$?
  echo "[FAIL] finalize-all encountered errors" | tee -a "$LOG_FILE"
fi

while IFS= read -r line; do
  case "$line" in
    *"[OK] tiktok-video-"*)
      asset_id=$(echo "$line" | sed -E 's/.*\[OK\] (tiktok-video-[^ ]+).*/\1/')
      vid_id=$(echo "$asset_id" | grep -oE '[0-9]{17,}' | head -1)
      if [ -n "$vid_id" ]; then
        echo "$vid_id" >> "$DONE_FILE"
      fi
      ;;
    *"[FAIL] tiktok-video-"*)
      asset_id=$(echo "$line" | sed -E 's/.*\[FAIL\] (tiktok-video-[^: ]+).*/\1/')
      vid_id=$(echo "$asset_id" | grep -oE '[0-9]{17,}' | head -1)
      if [ -n "$vid_id" ]; then
        echo "$vid_id" >> "$FAILED_FILE"
      fi
      ;;
  esac
done < "$FINALIZE_OUT"

rm -f "$FINALIZE_OUT"

if [ -f "$DONE_FILE" ]; then
  sort -u "$DONE_FILE" -o "$DONE_FILE"
fi
if [ -f "$FAILED_FILE" ]; then
  sort -u "$FAILED_FILE" -o "$FAILED_FILE"
fi

if [ "${finalize_exit:-0}" -ne 0 ]; then
  echo "[WARN] finalize-all exited non-zero; inspect $LOG_FILE" | tee -a "$LOG_FILE"
fi

echo ""
echo "=== Batch complete ==="
echo "Total: $total | Skipped: $skipped | Stage Failed: $failed | Staged OK: $staged_ok"
echo "Links with URLs saved to: $LINKS_FILE"
