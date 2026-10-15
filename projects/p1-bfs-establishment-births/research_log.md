# Project 1 Research Log

## 2026-10-14: Phase 0 — setup

- Created the project folder skeleton (literature/, data/, src/, notebooks/, outputs/, manuscript/, references/, replication/) per the program's standard structure.
- Wrote [research_question.md](research_question.md), condensed from the approved program-level plan.
- Environment: shared `requirements.txt` at the repo root; verified a clean install (see commit).
- Wrote the Phase 1 literature search protocol: [literature/search_protocol.md](literature/search_protocol.md).

**AI-use record:** Claude (Opus 5.5 / Sonnet 5 via Claude Code) drafted the folder structure, research_question.md, and search protocol. Not yet reviewed by the author.

## 2026-10-14: Phase 1 — literature review (complete)

Dispatched two parallel AI research passes against the written search protocol. Full results: [literature/extraction_table.md](literature/extraction_table.md).

**Gate verdict: PASS.** No existing paper forecasts state-level BED/QCEW establishment births from state-level BFS data with an econometric-vs-ML comparison. Closest analogue is Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb (NBER WP 33224, 2024) — national-level, dynamic-factor-model only. Scooping-risk check of Census's own methodology page and recent CES working papers (through 2026 Q2) found nothing addressing this at the state level.

**Design decisions made from the methods review** (updates to [research_question.md](research_question.md)):
1. Nested-model test: Clark & West (2007), not plain Diebold–Mariano — applying DM to nested models is a known misuse. Giacomini & White (2006) as a robust fallback.
2. Multiple-comparison control: Hansen–Lunde–Nason Model Confidence Set (2011).
3. Pooled-panel significance: Qu, Timmermann & Zhu (2024, IJF) and/or Akgun et al. (2024, IJF) — recent panel forecast-comparison tests, not in the original plan.
4. Mixed-frequency model: bridge equations instead of MIDAS. No mature Python MIDAS package exists; this is a stated scope simplification, not an oversight.
5. Data revisions: BFS has real vintages on ALFRED (state-level, free API key required, not yet obtained). **BED has no vintage archive anywhere found** — a real gap versus the original plan's assumption. Phase 2 will decide between hand-constructing a BED vintage history from BLS's archived news releases, or running the evaluation on final data only with that limitation stated plainly.

**Caveat:** this was a web-search-based review, not a full EconLit/Scholar citation-graph crawl. Re-verify before submission.

**AI-use record:** Claude (Sonnet 5 via Claude Code) ran both literature searches and drafted the extraction table and design updates. Not yet reviewed by the author.

**Next:** Phase 2 — data acquisition.

## 2026-10-14: Phase 2 — data acquisition (first pass complete)

Verified both access paths directly (robots.txt check, directory listing) before pulling anything, per the program's scraping-ethics rule. Neither host restricts the paths used.

**BFS:** `src/acquisition/fetch_bfs.py` downloads the single published CSV (no API key). `src/cleaning/clean_bfs.py` filters to `naics_sector == "TOTAL"` (state/region rows have no industry detail), reshapes wide-to-long, and keeps the four application series (BA_BA/HBA/WBA/CBA) plus Census's own BF_* projection series for context. Output: 327,636 rows, 2004–2026, 51 states + DC.

**BED:** `src/acquisition/fetch_bed.py` downloads BLS's full flat-file set (253.5 MB data file + series directory + 12 lookup tables, no API key). `src/cleaning/clean_bed.py` decodes `bd.series` to find the 432 series_ids matching state-level, total-private, all-size-class establishment births/deaths, quarterly, both SA/NSA and both rate/level — then filters the 4.6M-row data file down to those. Output: 57,648 rows, 1992 Q3–2025 Q4 (births) / 2025 Q1 (deaths — confirmed 3-quarter publication lag).

Both outputs spot-checked for sanity (magnitudes, date ranges, null patterns fully explained — see [data/MANIFEST.md](data/MANIFEST.md)). Processed CSVs (23.5 MB combined, public and unrestricted) are committed to git as an exception to the default `data/processed` gitignore rule, since they're small and central to reproducibility; raw files stay local/gitignored per the manifest.

**Confirmed from Phase 1:** BFS has real-time vintages on ALFRED (needs a free API key, deferred). BED has none anywhere — this pull is final-vintage only, as expected.

**Not yet done:** BDS (for RQ4) acquisition; the real-time information-set/release-calendar construction; the vintage-data decision for BED. These come next, alongside Phase 3 (exploratory analysis).

**AI-use record:** Claude (Sonnet 5 via Claude Code) wrote and ran the acquisition/cleaning scripts, including fixing one merge-key bug (bd.seasonal's `seasonal_code` vs. bd.series's `seasonal`) caught by actually running the pipeline rather than just reviewing the code. Not yet reviewed by the author.
