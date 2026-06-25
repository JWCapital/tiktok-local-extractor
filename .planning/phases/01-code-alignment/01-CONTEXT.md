# Phase 1: Code Alignment - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix the two concrete storage discrepancies in `extract.py` so that staging and image paths exactly match the canonical layout defined in `Revised_process_overview.md`. No new features, no migration of existing content — surgical code changes to new runs only.

</domain>

<decisions>
## Implementation Decisions

### Staging Path Fix

- **D-01:** Use **Option A — one-liner**: change `staged_root = out_root / "_staging" / SOURCE_TYPE` to `staged_root = out_root.parent / "_staging" / SOURCE_TYPE` in `extract.py`.
- **D-02:** No migration of already-staged content. Existing content under `Inbox-Raw/_staging/tiktok/` can stay or be manually cleaned; the fix only affects new extraction runs.
- **D-03:** No new CLI flags, no `--staging-root` arg, no env var changes. Rely on the convention that `out_root` is always one level inside `Sync_Data`.

### Image Subfolder Rename

- **D-04:** Rename `assets/` → `images/` everywhere in `extract.py` for new runs. Both the thumbnail extraction function and scene/frame capture function write to `out_dir / "assets"` — change both to `out_dir / "images"`.
- **D-05:** Apply to new runs only. Do not rename or migrate existing extracted video folders under `_assets/tiktok/`.
- **D-06:** Update any internal path references that copy or glob from `assets/` (e.g., `_copy_hive_image_assets`, `_mirror_stage_images_to_assets`) to use `images/` consistently.

### Claude's Discretion

- Exact line numbers and call sites to patch — identify all `"assets"` string literals and `/ "assets"` path constructions in extract.py and update consistently.
- Whether to add a short inline comment at the renamed paths noting the spec alignment (keep it brief).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Pipeline Specification
- `Revised_process_overview.md` — authoritative 3-step pipeline spec; defines exact storage layout including `_staging/tiktok/` outside Inbox-Raw and `images/` subfolder naming

### Implementation Target
- `extract.py` — primary file to patch; all path changes are in this file
- `batch_extract.sh` — passes `OUT_DIR` as `--out`; no changes needed (Option A is code-side)
- `reprocess_sources.sh` — same; no changes needed

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_extract_thumbnail()` (~line 534): writes to `out_dir / "assets"` — rename to `images/`
- `_extract_frames()` (~line 678+): `frames_dir = out_dir / "assets"` — rename to `images/`
- `_copy_hive_image_assets()` (~line 847): reads from `asset_payload_dir / "assets"` and writes to `inbox_item_dir / "assets"` — both become `images/`
- `_mirror_stage_images_to_assets()` (~line 872): reads `stage_dir / "assets"` and `asset_dir / "assets"` — both become `images/`
- `_offload_nonimage_payload_to_assets()` (~line 891): moves non-image files from stage into `_assets`; references `"assets"` folder — check and update

### Established Patterns
- `SOURCE_TYPE = "tiktok"` (line 33): used to construct all type-specific paths — no change needed
- `CENTRALIZED_ASSETS_ROOT` (line 37): hardcoded to `_assets` dir — already matches spec
- `staged_root = out_root / "_staging" / SOURCE_TYPE` (~line 1053): the exact line to patch to `out_root.parent / "_staging" / SOURCE_TYPE`

### Integration Points
- After the staging path fix, `extract.py --finalize-all` will look for staged content at `Sync_Data/_staging/tiktok/` — scripts require no changes because they pass `--out Sync_Data/Inbox-Raw` and the code now derives staging from its parent
- `batch_extract.sh` line 90: references `$OUT_DIR/_staging/tiktok/tiktok-video-*` for progress checking — this will also need updating to `${OUT_DIR%/*}/_staging/tiktok/tiktok-video-*` or equivalent

</code_context>

<specifics>
## Specific Ideas

- The one-liner fix is at `extract.py` line ~1053: `staged_root = out_root / "_staging" / SOURCE_TYPE`
- All `"assets"` path segments inside `extract.py` functions that build paths within a staged/extracted video folder should become `"images"` — do a targeted search for `/ "assets"` and `"assets"` as a path component (not as a variable name like `assets_dir` or `CENTRALIZED_ASSETS_ROOT`)

</specifics>

<deferred>
## Deferred Ideas

- **OCR + transcript timeline merge** — extract text from screenshots (URLs, handles, on-screen text), merge into the timestamped transcript. Significant new feature; deferred to a future phase.
- **Migration of existing staged content** from `Inbox-Raw/_staging/tiktok/` to `Sync_Data/_staging/tiktok/` — not in scope; existing content unaffected.

</deferred>

---

*Phase: 1-Code Alignment*
*Context gathered: 2026-06-25*
