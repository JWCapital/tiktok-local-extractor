#!/usr/bin/env bash
# Reprocess all preserved source video files into Inbox-Test using contract extractor.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="/Users/joshuawallace/Data/Sync_Data/Inbox-Test"
LOG_FILE="$ROOT/exports/reprocess_sources.log"
DONE_FILE="$ROOT/exports/done_ids.txt"
FAILED_FILE="$ROOT/exports/failed_ids.txt"

cd "$ROOT"
mkdir -p "$(dirname "$LOG_FILE")"
: > "$LOG_FILE"

echo "# Reprocess started $(date)" | tee -a "$LOG_FILE"
echo "Output dir: $OUT_DIR" | tee -a "$LOG_FILE"

TOTAL=$(find exports -mindepth 2 -maxdepth 2 -type d -name source | wc -l | tr -d ' ')
if [[ "$TOTAL" -eq 0 ]]; then
  echo "No source directories found under exports/." | tee -a "$LOG_FILE"
  exit 0
fi

count=0
ok=0
failed=0

while IFS= read -r src_dir; do
  while IFS= read -r vid; do
    count=$((count + 1))
    vid_id=$(echo "$vid" | grep -oE '[0-9]{17,}' | head -1 || true)
    echo "[RUN $count] $vid" | tee -a "$LOG_FILE"

    if /Users/joshuawallace/Data/Ticktok/.venv/bin/python extract.py "$vid" --rights research --out "$OUT_DIR" < /dev/null >> "$LOG_FILE" 2>&1; then
      ok=$((ok + 1))
      if [[ -n "$vid_id" ]]; then
        echo "$vid_id" >> "$DONE_FILE"
      fi
      echo "[OK  $count] $vid" | tee -a "$LOG_FILE"
    else
      failed=$((failed + 1))
      if [[ -n "$vid_id" ]]; then
        echo "$vid_id" >> "$FAILED_FILE"
      fi
      echo "[FAIL $count] $vid" | tee -a "$LOG_FILE"
    fi
  done < <(find "$src_dir" -type f \( -name '*.mp4' -o -name '*.mov' -o -name '*.mkv' -o -name '*.webm' \))
done < <(find exports -mindepth 2 -maxdepth 2 -type d -name source)

echo "" | tee -a "$LOG_FILE"
echo "=== Reprocess complete ===" | tee -a "$LOG_FILE"
echo "Total run: $count | OK: $ok | Failed: $failed" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
