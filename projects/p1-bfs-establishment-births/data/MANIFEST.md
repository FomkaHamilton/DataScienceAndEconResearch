# Data Manifest: Project 1

This manifest documents every acquisition (source, retrieval date, parameters and transformations) so that another researcher can rebuild the processed data from scratch. Raw files are not committed to git (see the root `.gitignore`); this manifest and the acquisition and cleaning scripts are the reproducibility record. The processed files described below are small, built from public and unrestricted sources, and are committed as listed exceptions in `.gitignore`.

## 1. Census Business Formation Statistics (BFS)

- **Source:** https://www.census.gov/econ/bfs/csv/bfs_monthly.csv
- **Methodology:** https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html
- **Retrieved:** 2026-10-14, via `src/acquisition/fetch_bfs.py`
- **Raw file:** `data/raw/bfs/bfs_monthly_2026-10-14.csv` (2.8 MB, 36,884 rows, wide format)
- **Access:** no API key required. No robots.txt restriction on this path (checked 2026-10-14).
- **Coverage as retrieved:** monthly, 2004–2026 (through September 2026; October–December 2026 are present as blank future months). National, 4 Census regions, 50 states, DC and Puerto Rico. Industry (NAICS) detail is national only; state, region and territory rows exist only for `naics_sector == "TOTAL"`.
- **Series kept:** BA_BA (all business applications), BA_HBA (high-propensity applications), BA_WBA (applications with planned wages) and BA_CBA (corporate applications), the four candidate predictor series for RQ1 and RQ2. Also kept for context, but not used as predictors: BF_BF4Q, BF_BF8Q, BF_PBF4Q, BF_PBF8Q, BF_SBF4Q, BF_SBF8Q, BF_DUR4Q and BF_DUR8Q (Census's own business-formation series and projections).
- **Transformation:** `src/cleaning/clean_bfs.py` filters to `naics_sector == "TOTAL"`, reshapes from wide (one column per month) to long, adds a `geo_type` column (national, region, state or territory; DC is treated as a state), and writes `data/processed/bfs_state_applications.csv` (327,636 rows).
- **Known limitation:** this is the current (final) vintage, not a real-time vintage. BFS vintages do exist on ALFRED (Federal Reserve Bank of St. Louis, release IDs 443 and 468, confirmed in the Phase 1 literature review), but pulling them requires a free FRED/ALFRED API key. The pre-analysis plan (§3) uses final-vintage data for both BFS and BED, for consistency, because BED has no vintage archive. A sensitivity check using real-time BFS vintages is noted there as a possible extension.

## 2. BLS Business Employment Dynamics (BED): state establishment births and deaths

- **Source:** https://download.bls.gov/pub/time.series/bd/ (bulk flat files)
- **Retrieved:** 2026-10-14, via `src/acquisition/fetch_bed.py`
- **Raw files:** `data/raw/bed/2026-10-14/` contains `bd.data.1.AllItems` (253.5 MB, 4,598,544 data rows, all published BED series), `bd.series` (5.6 MB, the series directory) and 12 small lookup and reference files (`bd.state`, `bd.dataclass`, `bd.seasonal`, `bd.ratelevel`, `bd.sizeclass`, `bd.ownership`, `bd.periodicity`, `bd.unitanalysis`, `bd.dataelement`, `bd.industry`, `bd.footnote`, `bd.contacts`).
- **Access:** no API key required for the bulk flat-file download (distinct from the registered, rate-limited BLS API). No robots.txt restriction found on download.bls.gov (checked 2026-10-14).
- **Selection criteria** (`src/cleaning/clean_bed.py`): geography = state level (`msa_code = 00000`, `county_code = 000`); industry = total private (`industry_code = 000000`); unit of analysis = establishment, not employment; data element = number of establishments (not employment associated with births or deaths); size class = all sizes combined (`00`); data class = Establishment Births (07) and Establishment Deaths (08); periodicity = quarterly. Both seasonal adjustments (SA and NSA) and both rate and level forms are kept; the choice between primary and robustness series is made in the analysis code, not here.
- **Result:** 432 target series IDs, written to `data/processed/bed_state_establishment_births_deaths.csv` (57,648 rows). The file covers the national total, all 50 states, DC, Puerto Rico and the Virgin Islands (54 geographies). The state-level analysis panel (50 states and DC) is a filtered subset of this file, not a separate file.
- **Coverage:** 1992Q3–2025Q4 for establishment births and 1992Q3–2025Q1 for establishment deaths. BLS publishes deaths with a lag of about 3 quarters relative to births, which this pull confirms: 2025Q2–Q4 deaths are null. All 1,284 null values are explained by (a) this death-reporting lag (648 nulls) and (b) the first few published quarters (1992Q3–1993Q1), in which some series and state combinations are not yet populated (636 nulls).
- **Known limitation:** the Phase 1 literature review found no real-time vintage archive for BED (not on ALFRED or elsewhere), so this file contains final-vintage data only. The pre-analysis plan (§3) resolved this by evaluating on final-vintage data and stating the limitation; no vintage history was hand-constructed from the BLS news-release archive (`bls.gov/news.release/archives/cewbd_*.htm`).
- **Separate measurement caveat (from the literature review):** BLS (BED/CES) and Census establishment universes have diverged structurally over time (Cao, Hyatt, Mukoyama & Sager, CES-WP-26-36 / FEDS 2026-40). BED and Census establishment counts should not be treated as interchangeable. The forecasting outcome in this project comes from the BLS (BED) universe; the Census BDS data (Section 3) are used only for the RQ4 new-firm share.

## 3. Census Business Dynamics Statistics (BDS): state × firm age

- **Source:** https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_st_fa.csv (linked from https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html)
- **Retrieved:** 2026-10-15, via `src/acquisition/fetch_bds.py`
- **Raw file:** `data/raw/bds/bds2023_st_fa_2026-10-15.csv` (3.8 MB)
- **Access:** no API key required for this bulk CSV. No robots.txt restriction found on www2.census.gov (checked 2026-10-14).
- **Coverage:** annual (BDS's March-to-March reference year), 1978–2023, 50 states and DC, 12 firm-age categories.
- **Purpose:** RQ4 only (the exploratory heterogeneity question); not part of the quarterly forecasting panel.
- **Transformation:** `src/cleaning/clean_bds.py` computes `new_firm_share = estabs_entry[firm age 0] / sum(estabs_entry, all firm ages)` for each state-year and writes `data/processed/bds_state_new_firm_share.csv` (2,346 rows). The mean is 66.8% across all state-years and 61.1% for 2010–2019.
  - The denominator includes "left-censored" firms: firms that already existed when the BDS series begins, so their exact age is unknown.
  - An earlier version excluded them, giving a 77.9% mean, which overstated the share. This was corrected on 2026-10-15, before the file was used in any analysis.
- **Status:** used in the RQ4 analysis ([Addendum 4](../pre_analysis_plan_addendum_4.md); `src/analysis/run_rq4.py`), which reads this file directly. It is not merged into the quarterly forecasting panel.

## 4. Integrated quarterly panel (derived, not a separate source)

- **Built by:** `src/cleaning/build_panel.py`, which aggregates BFS from monthly to quarterly (summing the 3 months; all 3 must be present, otherwise `NaN`) and merges with BED on state name, seasonal adjustment, year and quarter.
- **Output:** `data/processed/analysis_panel_quarterly.csv`, 9,116 rows (53 geographies × 2 seasonal adjustments × about 86 quarters).
- **`in_test_window` flag:** `True` for 2023Q1 onward. The file keeps the full history rather than deleting the test window. Development-window analyses filter on this flag: `src/analysis/exploratory_analysis.py` (Phase 3) drops test-window rows before running and prints a confirmation. The test window stayed locked until the pre-analysis plan was committed and was first used in the Phase 5 evaluation.

## 5. Forecast dataset (derived)

- **Built by:** `src/cleaning/build_forecast_dataset.py` from the integrated panel, implementing the pseudo-real-time information set and forecast horizons of the pre-analysis plan (§3 and §6). The conventions are documented in the script's header.
- **Output:** `data/processed/forecast_dataset.csv` (8,772 rows, NSA and SA series as separate rows): year-over-year log changes of establishment births and of the four BFS series, with the lags used by the forecasting models, winsorized versions for reference, and the `in_test_window` flag.

## Reproducing from scratch

Use the one-command pipeline, [../replication/run_all.py](../replication/run_all.py):

- **Default mode** starts from the committed processed files and reproduces the committed numbers.
- **`--full`** re-downloads the raw data first. The download scripts send a contact address to Census and BLS, read from the `RESEARCH_CONTACT_EMAIL` environment variable (or a git-ignored `.env` file at the repository root).

Re-downloading creates new dated raw files rather than overwriting earlier pulls. Both source agencies revise their data, so a later download can differ from the vintage used here.

### Raw-file checksums (SHA-256) for the vintage used in the analysis

| File | Retrieved | SHA-256 |
|---|---|---|
| `raw/bfs/bfs_monthly_2026-10-14.csv` | 2026-10-14 | `8b759b60dc7518ae6ae3d1cf1e80fc3f0ed5295ab4eb6a263bfb26ae742c06c4` |
| `raw/bed/2026-10-14/bd.data.1.AllItems` | 2026-10-14 | `88ff1e867c714f85d68d565f14b1a98e616e6eb91d894544743d58623bcd4055` |
| `raw/bed/2026-10-14/bd.series` | 2026-10-14 | `ea09556dc0e36a37b3946c56913a2007125e1f61e70938482b64f8768da7a8ed` |
| `raw/bds/bds2023_st_fa_2026-10-15.csv` | 2026-10-15 | `adb23fccea76d1cbcc27291b43054f366151f146174979c11b9eeadedd9c679b` |

The raw files are not committed: BED alone is 253 MB, and the agencies host the files publicly. A freshly downloaded file that matches these checksums is the same vintage.
