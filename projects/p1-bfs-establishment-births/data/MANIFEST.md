# Data Manifest — Project 1

Documents every acquisition: source, retrieval date, parameters, and transformations, so another researcher can reproduce the processed data from scratch. Raw files are not committed to git (see root `.gitignore`); this manifest plus the acquisition/cleaning scripts are the reproducibility record.

## 1. Census Business Formation Statistics (BFS)

- **Source:** https://www.census.gov/econ/bfs/csv/bfs_monthly.csv
- **Methodology:** https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html
- **Retrieved:** 2026-10-14, via `src/acquisition/fetch_bfs.py`
- **Raw file:** `data/raw/bfs/bfs_monthly_2026-10-14.csv` (2.8 MB, 36,884 rows, wide format)
- **No API key required.** No robots.txt restriction on this path (checked 2026-10-14).
- **Coverage as retrieved:** monthly, 2004–2026 (through September 2026; October–December 2026 present as blank/future). National, 4 Census regions, 50 states + DC + PR. Industry (NAICS) detail is national only — state/region/territory rows are `naics_sector == "TOTAL"` only.
- **Series kept:** BA_BA (all business applications), BA_HBA (high-propensity), BA_WBA (planned-wage), BA_CBA (corporate) — the four candidate predictor series for RQ1/RQ2. Also kept for context (not currently used as predictors): BF_BF4Q, BF_BF8Q, BF_PBF4Q, BF_PBF8Q, BF_SBF4Q, BF_SBF8Q, BF_DUR4Q, BF_DUR8Q (Census's own business-formation projection series).
- **Transformation:** `src/cleaning/clean_bfs.py` filters to `naics_sector == "TOTAL"`, reshapes from wide (one column per month) to long, adds a `geo_type` column (national/region/state/territory; DC is treated as a state), and writes `data/processed/bfs_state_applications.csv` (327,636 rows).
- **Known limitation:** this is the current/final vintage, not a real-time vintage. BFS vintages do exist (ALFRED, Fed. Reserve Bank of St. Louis, release IDs 443 and 468 — confirmed in the Phase 1 literature review), but pulling them requires a free FRED/ALFRED API key, not yet obtained. A real-time-vintage version of BFS can be added later without redoing this step.

## 2. BLS Business Employment Dynamics (BED) — state establishment births/deaths

- **Source:** https://download.bls.gov/pub/time.series/bd/ (bulk flat files)
- **Retrieved:** 2026-10-14, via `src/acquisition/fetch_bed.py`
- **Raw files:** `data/raw/bed/2026-10-14/` — `bd.data.1.AllItems` (253.5 MB, 4,598,544 data rows, ALL published BED series) plus `bd.series` (5.6 MB, series directory) and 12 small lookup/reference files (`bd.state`, `bd.dataclass`, `bd.seasonal`, `bd.ratelevel`, `bd.sizeclass`, `bd.ownership`, `bd.periodicity`, `bd.unitanalysis`, `bd.dataelement`, `bd.industry`, `bd.footnote`, `bd.contacts`).
- **No API key required** for the flat-file bulk download (distinct from the registered, rate-limited BLS API used elsewhere). No robots.txt restriction found on download.bls.gov (checked 2026-10-14).
- **Selection criteria** (`src/cleaning/clean_bed.py`): geography = state-level (`msa_code = 00000`, `county_code = 000`); industry = total private (`industry_code = 000000`); unit of analysis = establishment, not employment; data element = number of establishments (not employment associated with births/deaths); size class = all combined (`00`); data class = Establishment Births (07) and Establishment Deaths (08); periodicity = quarterly. Both seasonal adjustments (SA/NSA) and both rate/level forms are kept — the primary-vs-robustness choice is made in analysis code, not here.
- **Result:** 432 target series_ids → `data/processed/bed_state_establishment_births_deaths.csv`, 57,648 rows. Covers the national total + all 50 states + DC + Puerto Rico + Virgin Islands (54 geographies total); the state-level analysis panel (50 states + DC) is a filtered subset of this file, not a separate file.
- **Coverage:** 1992 Q3 – 2025 Q4 for Establishment Births; 1992 Q3 – 2025 Q1 for Establishment Deaths (BLS publishes deaths with an ~3-quarter lag relative to births — confirmed directly in this pull: Q2–Q4 2025 deaths are null). 1,284 null values total, all explained by (a) this death-reporting lag (648 nulls) and (b) the very first few published quarters (1992 Q3 – 1993 Q1), where some series/state combinations are not yet populated (636 nulls).
- **Known limitation (from the Phase 1 literature review):** no real-time vintage archive for BED was found anywhere (not ALFRED, not elsewhere). This file is final-vintage data only. The pre-analysis plan (Phase 4) must decide whether to hand-construct a vintage history from BLS's archived news releases (`bls.gov/news.release/archives/cewbd_*.htm`) or evaluate on final data with that limitation stated plainly.
- **Separate measurement caveat (from the literature review):** BLS (BED/CES) and Census establishment universes have diverged structurally over time (Cao, Hyatt, Mukoyama & Sager, CES-WP-26-36/FEDS 2026-40) — document which universe is used and do not treat BED and Census establishment counts as interchangeable.

## Reproducing from scratch

```
cd projects/p1-bfs-establishment-births
python src/acquisition/fetch_bfs.py
python src/acquisition/fetch_bed.py
python src/cleaning/clean_bfs.py
python src/cleaning/clean_bed.py
```

Re-running on a later date creates new dated raw files/folders rather than overwriting prior pulls (both source series revise).

## 3. Census Business Dynamics Statistics (BDS) — state × firm-age

- **Source:** https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_st_fa.csv (linked from https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html)
- **Retrieved:** 2026-10-15, via `src/acquisition/fetch_bds.py`
- **Raw file:** `data/raw/bds/bds2023_st_fa_2026-10-15.csv` (3.8 MB)
- **No API key required** for this bulk CSV. No robots.txt restriction found on www2.census.gov (checked 2026-10-14).
- **Coverage:** annual (BDS's March-to-March reference year), 1978–2023, 50 states + DC, 12 firm-age categories.
- **Purpose:** RQ4 only (exploratory heterogeneity question) — not part of the core quarterly forecasting panel.
- **Transformation:** `src/cleaning/clean_bds.py` computes `new_firm_share = estabs_entry[firm age 0] / sum(estabs_entry, all ages except "Left Censored")` per state-year → `data/processed/bds_state_new_firm_share.csv` (2,346 rows). Mean 77.9% (std 8.8%).
- **Status:** parked for Phase 5; not yet merged into the forecasting panel or used in any model.

## 4. Integrated quarterly panel (derived, not a separate source)

- **Built by:** `src/cleaning/build_panel.py` — aggregates BFS from monthly to quarterly (sums 3 months; requires all 3 present, else `NaN`) and merges with BED on state name, seasonal adjustment, year, and quarter.
- **Output:** `data/processed/analysis_panel_quarterly.csv`, 9,116 rows (53 geographies × 2 seasonal adjustments × ~86 quarters).
- **`in_test_window` flag:** `True` for 2023Q1 onward. The file keeps the full history (transparency over deletion), but every Phase 3+ analysis script must filter this flag before using the data — `src/analysis/exploratory_analysis.py` does this and prints an explicit confirmation. The test window stays locked until the Phase 4 pre-analysis plan is committed.
