# Phase 2: Reprocess Remaining Videos - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Run the 186 queued TikTok URLs from `_assets/tiktok/queues/favs_raw.txt` through the corrected pipeline (post Phase 1 fixes) so each video lands in the right storage locations: permanent assets in `_assets/tiktok/tiktok-video-<id>/`, contract markdown staged at `_staging/tiktok/tiktok-video-<id>/`, and finalized output in `Inbox-Raw/tiktok/tiktok-video-<id>/`.

Scope is strictly the 186 URLs not yet in `done_ids.txt`. Legacy exports (390 folders in `_assets/tiktok/legacy_exports/`) and failed IDs (70 entries) are explicitly out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Rights Policy
- **D-01:** Use `--rights research` for all URLs in `favs_raw.txt` (keep the existing batch_extract.sh default). These are bookmarked/favorited videos for reference use.

### Failed IDs Handling
- **D-02:** Leave `failed_ids.txt` untouched. batch_extract.sh will automatically skip the 70 previously-failed IDs. No retry — they failed for a reason and re-hammering is undesirable.

### Scope: Legacy Exports
- **D-03:** Phase 2 processes only the 186 queued URLs. The 390 folders in `_assets/tiktok/legacy_exports/` are NOT in scope. Legacy reprocessing is deferred to a future phase.

### batch_extract.sh Staging Fix
- **D-04:** Fix the link-extraction staging glob in `batch_extract.sh` line 90 as part of Phase 2. Change `"$OUT_DIR"/_staging/tiktok/tiktok-video-*/` to `"${OUT_DIR%/*}"/_staging/tiktok/tiktok-video-*/` — one-line change, consistent with Phase 1's intent. This is the fix that Phase 1's executor reported as "glob not found at line 90" but the glob does exist in the current committed file.

### Claude's Discretion
- Whether to run all 186 URLs in a single `batch_extract.sh` invocation or break into smaller batches (suggest single run; the script handles failures gracefully and logs progress)
- Exact progress reporting format in the plan

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Pipeline Specification
- `Revised_process_overview.md` — authoritative 3-step pipeline spec; defines Extract → Stage → Finalize flow and storage paths

### Implementation Files
- `batch_extract.sh` — primary batch runner; processes `favs_raw.txt`, calls extract.py with `--stage-only` then `--finalize-all`; fix line 90 staging glob (D-04)
- `extract.py` — extractor (patched in Phase 1); `--stage-only` and `--finalize-all` flags, `--rights`, `--out` path

### State Files
- `_assets/tiktok/queues/favs_raw.txt` — 186 URLs to process
- `_assets/tiktok/state/done_ids.txt` — 313 already-done IDs (skip list)
- `_assets/tiktok/state/failed_ids.txt` — 70 failed IDs (leave untouched, D-02)
- `_assets/tiktok/state/batch_extract.log` — primary run log

### Phase 1 Output
- `.planning/phases/01-code-alignment/01-VERIFICATION.md` — confirms Phase 1 fixes are in place before running

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `batch_extract.sh` — complete batch orchestration: reads `favs_raw.txt`, skips done/failed IDs, runs `extract.py --stage-only`, extracts description links, then runs `--finalize-all`, updates `done_ids.txt`. Already wired to `_assets/tiktok/queues/favs_raw.txt`.
- `extract.py --finalize-all` — scans `out_root.parent / "_staging" / SOURCE_TYPE` for staged directories and finalizes each to `Inbox-Raw/tiktok/`. Uses Phase 1's corrected staging path.

### Established Patterns
- `OUT_DIR` in `batch_extract.sh` = `/Users/joshuawallace/Data/Sync_Data/Inbox-Raw` — `--out` arg passed to extract.py
- `${OUT_DIR%/*}` = `/Users/joshuawallace/Data/Sync_Data` = parent of Inbox-Raw — correct staging prefix after Phase 1 fix
- Cookie strategy: tries Brave browser cookies first, falls back to exported cookie file
- `done_ids.txt` is deduped with `sort -u` after each run

### Integration Points
- After reprocessing: `Inbox-Raw/tiktok/` will be created and populated for the first time — Hive intake polls this lane (Phase 4 validates the end-to-end)
- The batch_extract.sh staging glob fix (D-04) is the only code change in Phase 2; the main extraction logic is already correct from Phase 1

</code_context>

<specifics>
## Specific Ideas

- The single-line fix to `batch_extract.sh` line 90: `"$OUT_DIR"/_staging/` → `"${OUT_DIR%/*}"/_staging/`
- Run all 186 URLs in one `batch_extract.sh` invocation from the project venv; no need to split batches

</specifics>

<deferred>
## Deferred Ideas

- **Legacy exports reprocessing** — 390 folders in `_assets/tiktok/legacy_exports/` need to be re-run through the corrected pipeline. Deferred to a future phase; D-03 scopes Phase 2 to favs_raw.txt only.
- **Failed IDs retry** — 70 entries in `failed_ids.txt` may be retryable (transient network errors). Deferred; D-02 leaves them skipped for this run.

</deferred>

---

*Phase: 2-Reprocess Remaining Videos*
*Context gathered: 2026-06-25*
