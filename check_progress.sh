#!/bin/bash
while true; do
  ok=$(grep "^\[OK" exports/reprocess_sources.log 2>/dev/null | wc -l)
  fail=$(grep "^\[FAIL" exports/reprocess_sources.log 2>/dev/null | wc -l)
  staged=$(find /Users/joshuawallace/Data/Sync_Data/_staging/tiktok -maxdepth 1 -type d -name "tiktok-video-*" 2>/dev/null | wc -l)
  total_processed=$((ok + fail))
  echo "[$(date +'%H:%M:%S')] Processed: $total_processed/381 (OK:$ok FAIL:$fail) | Staged dirs: $staged"
  sleep 30
done
