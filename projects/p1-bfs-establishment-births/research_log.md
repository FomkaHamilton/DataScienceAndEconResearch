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
