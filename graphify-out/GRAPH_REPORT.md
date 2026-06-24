# Graph Report - /Volumes/Sync_Data/extractors/tittok-local-extactor  (2026-06-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 137 nodes · 207 edges · 17 communities (12 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4bd94e2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Video Extraction Pipeline|Video Extraction Pipeline]]
- [[_COMMUNITY_Contract Content Extraction|Contract Content Extraction]]
- [[_COMMUNITY_Project Summary|Project Summary]]
- [[_COMMUNITY_TikTok Data Extraction Instructions|TikTok Data Extraction Instructions]]
- [[_COMMUNITY_Media File Extraction|Media File Extraction]]
- [[_COMMUNITY_TikTok Extractor Project Overview|TikTok Extractor Project Overview]]
- [[_COMMUNITY_TikTok Data Ingestion Pipeline|TikTok Data Ingestion Pipeline]]
- [[_COMMUNITY_Package and Metadata Extraction|Package and Metadata Extraction]]
- [[_COMMUNITY_Transcription and Frame Extraction|Transcription and Frame Extraction]]
- [[_COMMUNITY_Metadata Patching Script|Metadata Patching Script]]
- [[_COMMUNITY_Project Roadmap|Project Roadmap]]
- [[_COMMUNITY_Project State|Project State]]
- [[_COMMUNITY_Project Plan|Project Plan]]
- [[_COMMUNITY_Batch Extract Script|Batch Extract Script]]
- [[_COMMUNITY_Run Ledger Updates|Run Ledger Updates]]
- [[_COMMUNITY_Caption Collection|Caption Collection]]
- [[_COMMUNITY_Source Reprocessing Script|Source Reprocessing Script]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 21 edges
2. `write_contract_content()` - 15 edges
3. `TikTok Extraction Pipeline — Agent Instructions` - 12 edges
4. `Phase 999.1 Plan 01 Summary` - 10 edges
5. `write_package()` - 9 edges
6. `main()` - 8 edges
7. `B. Check and process new favorites` - 8 edges
8. `TikTok Extractor` - 8 edges
9. `TikTok — extraction pipeline` - 8 edges
10. `_require_binary()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `_probe_duration_seconds()` --calls--> `_require_binary()`  [EXTRACTED]
  extract.py → extract.py  _Bridges community 4 → community 1_
- `_sha256()` --references--> `Path`  [EXTRACTED]
  extract.py → extract.py  _Bridges community 7 → community 8_
- `acquire()` --references--> `Path`  [EXTRACTED]
  extract.py → extract.py  _Bridges community 8 → community 4_
- `_best_captured_at()` --calls--> `Path`  [EXTRACTED]
  extract.py → extract.py  _Bridges community 8 → community 1_
- `collect_captions()` --references--> `Path`  [EXTRACTED]
  extract.py → extract.py  _Bridges community 8 → community 15_

## Import Cycles
- None detected.

## Communities (17 total, 5 thin omitted)

### Community 0 - "Video Extraction Pipeline"
Cohesion: 0.12
Nodes (15): A. Single video extraction, B. Check and process new favorites, Dep check, Notes, Output, Recency window policy, Rights policy (enforce before every run), Step 1 — Open TikTok favorites in browser (+7 more)

### Community 1 - "Contract Content Extraction"
Cohesion: 0.29
Nodes (13): _best_captured_at(), _extract_hashtags(), _extract_visible_text(), _humanize_handle(), _now_iso(), _parse_upload_date_to_iso(), _probe_duration_seconds(), _safe_int() (+5 more)

### Community 2 - "Project Summary"
Cohesion: 0.17
Nodes (11): Accomplishments, Auto-fixed Issues, Decisions Made, Deviations from Plan, Files Created/Modified, Issues Encountered, Next Phase Readiness, Performance (+3 more)

### Community 3 - "TikTok Data Extraction Instructions"
Cohesion: 0.17
Nodes (12): Common pitfalls, Critical constraints, Deduplication, Dependency check, Favorites pull scope (process update), Further reading, Key files, Legacy exports (+4 more)

### Community 4 - "Media File Extraction"
Cohesion: 0.23
Nodes (12): acquire(), check_rights(), _ensure_ledger(), extract_audio(), extract_frames(), extract_thumbnail(), _is_duplicate_source_hash(), main() (+4 more)

### Community 5 - "TikTok Extractor Project Overview"
Cohesion: 0.17
Nodes (11): Active, Constraints, Context, Core Value, Key Decisions, Last updated, Out of Scope, Requirements (+3 more)

### Community 6 - "TikTok Data Ingestion Pipeline"
Cohesion: 0.20
Nodes (8): Contract output structure, Feeding the ingestion pipeline, Legacy compatibility, Notes, One-time setup, Rights values, TikTok — extraction pipeline, Usage

### Community 7 - "Package and Metadata Extraction"
Cohesion: 0.24
Nodes (10): build_slug(), _creator_from_source_path(), _normalize_source_url(), Extract human-readable title from old TikTok export folder slug., Extract creator handle from old TikTok export folder name (YYYYMMDD_handle_slug), _sha256(), _slug(), _title_from_source_path() (+2 more)

### Community 8 - "Transcription and Frame Extraction"
Cohesion: 0.20
Nodes (10): _dedup_by_proximity(), _extract_at_timestamps(), _frame_timestamps(), Path, Run faster-whisper and write transcript files. Returns (transcript_text, model_l, Return timestamps (seconds) of frames whose scene score exceeds threshold., Extract one frame per timestamp using select+setpts., Remove frames whose filenames encode a timestamp within min_gap_s of a prior kep (+2 more)

### Community 9 - "Metadata Patching Script"
Cohesion: 0.42
Nodes (9): Namespace, build_url_map(), extract_username(), ffprobe_duration(), main(), parse_args(), patch_frontmatter(), Path (+1 more)

### Community 10 - "Project Roadmap"
Cohesion: 0.40
Nodes (4): Active Milestone, Backlog, Phase 999.1: Update extractor based on ingestion template contract (BACKLOG), ROADMAP

### Community 11 - "Project State"
Cohesion: 0.50
Nodes (3): Notes, Project Reference, STATE

## Knowledge Gaps
- **56 isolated node(s):** `batch_extract.sh script`, `Namespace`, `reprocess_sources.sh script`, `Rights policy (enforce before every run)`, `Dep check` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TikTok Extraction Pipeline — Agent Instructions` connect `TikTok Data Extraction Instructions` to `TikTok Data Ingestion Pipeline`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `Path` connect `Transcription and Frame Extraction` to `Contract Content Extraction`, `Media File Extraction`, `Caption Collection`, `Package and Metadata Extraction`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `batch_extract.sh script`, `Extract human-readable title from old TikTok export folder slug.`, `Extract creator handle from old TikTok export folder name (YYYYMMDD_handle_slug)` to the rest of the system?**
  _65 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Video Extraction Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._