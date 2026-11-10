# Project 1 Research Log

## 2026-10-14: Phase 0 (setup)

- Created the project folder skeleton (literature/, data/, src/, notebooks/, outputs/, manuscript/, references/, replication/), following the research program's standard structure.
- Wrote [research_question.md](research_question.md), condensed from the approved program-level plan.
- Environment: a shared `requirements.txt` at the repository root; verified a clean install (see the commit).
- Wrote the Phase 1 literature search protocol: [literature/search_protocol.md](literature/search_protocol.md).

**AI-use record:** Claude (Opus 5.5 and Sonnet 5, via Claude Code) drafted the folder structure, research_question.md and the search protocol. Not yet reviewed by the author.

## 2026-10-14: Phase 1 (literature review, complete)

Two parallel AI-assisted literature searches were run against the written search protocol. Full results: [literature/extraction_table.md](literature/extraction_table.md).

**Gate verdict: pass.** No existing paper forecasts state-level establishment births (from BLS Business Employment Dynamics, BED, or the Quarterly Census of Employment and Wages, QCEW) from state-level Census Business Formation Statistics (BFS) data with a comparison of econometric and machine-learning (ML) methods. The closest analogue is Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb (NBER WP 33224, 2024), which is national-level and uses only a dynamic factor model. A check for overlapping work on Census's own methodology page and in recent Census Center for Economic Studies (CES) working papers (through 2026Q2) found nothing addressing this question at the state level.

**Design decisions made from the methods review** (updates to [research_question.md](research_question.md)):

1. Nested-model test: Clark & West (2007), not a plain Diebold–Mariano (DM) test, because applying DM to nested models is a known misuse. Giacomini & White (2006) as a fallback.
2. Multiple-comparison control: the Hansen–Lunde–Nason Model Confidence Set (MCS; 2011).
3. Pooled-panel significance: Qu, Timmermann & Zhu (2024, *International Journal of Forecasting*) and/or Akgun et al. (2024, *International Journal of Forecasting*), recent panel forecast-comparison tests not in the original plan.
4. Mixed-frequency model: bridge equations instead of mixed-data sampling (MIDAS) regressions. No mature Python MIDAS package exists; this is a stated scope simplification, not an oversight.
5. Data revisions: BFS has real vintages on ALFRED (the Federal Reserve Bank of St. Louis's archive of data vintages; state-level, free API key required, not yet obtained). No vintage archive for BED was found anywhere, a material gap relative to the original plan's assumption. Phase 2 will decide between hand-constructing a BED vintage history from BLS's archived news releases and running the evaluation on final data only, with that limitation stated plainly.

**Caveat:** this review was based on web searches, not a full citation-graph search of EconLit or Google Scholar. Re-verify before submission.

**AI-use record:** Claude (Sonnet 5, via Claude Code) ran both literature searches and drafted the extraction table and design updates. Not yet reviewed by the author.

**Next:** Phase 2, data acquisition.

## 2026-10-14: Phase 2 (data acquisition, first pass complete)

Both access paths were verified directly (robots.txt check, directory listing) before anything was downloaded, following the program's rule on ethical scraping. Neither host restricts the paths used.

**BFS:** `src/acquisition/fetch_bfs.py` downloads the single published CSV (no API key). `src/cleaning/clean_bfs.py` filters to `naics_sector == "TOTAL"` (state and region rows have no industry detail), reshapes the data from wide to long, and keeps the four application series (BA_BA, all applications; HBA, high-propensity; WBA, with planned wages; CBA, corporate) plus Census's own BF_* projection series for context. Output: 327,636 rows, 2004–2026, 50 states and DC (plus national, regional and Puerto Rico rows).

**BED:** `src/acquisition/fetch_bed.py` downloads BLS's full flat-file set (a 253.5 MB data file, the series directory and 12 lookup tables; no API key). `src/cleaning/clean_bed.py` decodes `bd.series` to find the 432 series IDs for state-level, total-private, all-size-class establishment births and deaths: quarterly, both seasonally adjusted and not seasonally adjusted (SA and NSA), and both rates and levels. It then filters the 4.6-million-row data file to those series. Output: 57,648 rows, 1992Q3–2025Q4 for births and through 2025Q1 for deaths (a confirmed three-quarter publication lag).

Both outputs were spot-checked: magnitudes, date ranges, and null patterns, all of which are explained in [data/MANIFEST.md](data/MANIFEST.md). The processed CSVs (23.5 MB combined, public and unrestricted) are committed to git as an exception to the default rule that excludes `data/processed`, because they are small and central to reproducibility. Raw files stay local and are excluded from git, as recorded in the manifest.

**Confirmed from Phase 1:** BFS has real-time vintages on ALFRED (a free API key is needed; deferred). BED has none, so this download is final-vintage only, as expected.

**Not yet done:** acquisition of the Census Business Dynamics Statistics (BDS), needed for research question 4 (RQ4); construction of the real-time information set and release calendar; and the vintage-data decision for BED. These come next, alongside Phase 3 (exploratory analysis).

**AI-use record:** Claude (Sonnet 5, via Claude Code) wrote and ran the acquisition and cleaning scripts, and fixed one merge-key bug (bd.seasonal's `seasonal_code` vs. bd.series's `seasonal`) that surfaced when the pipeline was run. Not yet reviewed by the author.

## 2026-10-15: Phase 2 continued (BDS acquisition) and Phase 3 (exploratory analysis, complete)

**BDS:** `src/acquisition/fetch_bds.py` and `src/cleaning/clean_bds.py` download the state × firm-age cross-tabulation (direct CSV, no API key) and compute a state-year "new-firm share of establishment entry" for RQ4. Mean 77.9% (std 8.8%) across state-years: the same direction as Decker & Haltiwanger's finding that about 36% of new establishments come from existing firms, though the two are not directly comparable (different period; national vs. state-year averaging). Set aside for Phase 5; not yet used in any model.

**Phase 3 gate: pass.** Built the integrated quarterly panel (`src/cleaning/build_panel.py`, 9,116 rows, with an explicit `in_test_window` flag so that data from 2023Q1 onward cannot be used by accident) and ran exploratory correlations (`src/analysis/exploratory_analysis.py`, development window only; the script prints a confirmation that test-window rows were dropped before anything else runs).

- National lag correlation (BA_BA applications leading births): peaks at 0.64 at a 3-quarter lag.
- Pooled, within-state-demeaned state-level correlation: positive at every lag (0.14–0.28), peaking around 1 and 3 quarters. To this project's knowledge, this is the first evidence that the relationship holds at the state level, which is the gap Phase 1 identified.
- Visual check: in 2020–21, applications spike first and establishment births follow with a lag.

**New finding requiring a design decision:** not-seasonally-adjusted (NSA) establishment-birth counts show irregular, state-varying first-quarter spikes ("Q1 lumpiness"). A disproportionate share of large quarter-over-quarter jumps fall in Q1, across many years (2006, 2007, 2012, 2013, 2015, 2019–2022). A misleading year-over-year (YoY) reading of about −65% for California in 2013Q1 was traced to this (a base effect from an unusually high 2012Q1, not a real decline). Plain YoY differencing does not fully remove the effect, because the size of the spike varies from year to year. **Phase 4 must address this:** evaluate BLS's seasonally adjusted series, consider quarter fixed effects, and/or test sensitivity to winsorizing. Full write-up: [literature/phase3_findings.md](literature/phase3_findings.md).

**AI-use record:** Claude (Sonnet 5, via Claude Code) wrote and ran the BDS acquisition and Phase 3 scripts, generated the figures and tables, and investigated the California anomaly, checking whether it was isolated or systematic before writing it up. Not yet reviewed by the author.

**Next:** Phase 4, the pre-analysis plan (lock the test window, finalize the model list, specify how Q1 lumpiness is handled, and commit before any out-of-sample evaluation).

## 2026-10-15: Phase 4 (pre-analysis plan, committed)

Before the handling of Q1 lumpiness was finalized, BFS applications were checked for the same pattern as BED births. They show it more strongly: 21% of state-Q1 observations jump by more than 40% quarter over quarter, versus about 0% in other quarters, and 36 of 41 simultaneous large jumps in both series are in Q1. This is a real risk of confounding: part of the Phase 3 correlation could reflect both series reacting to the same calendar-timing effect rather than a predictive relationship. This was reported to the author together with the handling options (quarter fixed effects, a switch to seasonally adjusted series, winsorizing, or a combination) and the consequences of each for publication. In particular, making the seasonally adjusted series the primary specification would reintroduce the look-ahead bias that the choice of NSA data was meant to avoid. The author chose the combination approach.

**Committed:** [pre_analysis_plan.md](pre_analysis_plan.md). It specifies:

- the test window, locked at 2023Q1–2025Q4 (births);
- the information-set treatment: pseudo-real-time on final-vintage data for both series, with the unavailability of BED vintages and the deferral of BFS vintages stated as limitations;
- seasonality handling: a quarter-of-year indicator in all models as the structural fix for the newly found confound; BLS and Census seasonally adjusted series as a robustness check only, explicitly not valid for real-time claims; and winsorizing at development-window-only 1st/99th percentiles as a disclosed, pre-specified sensitivity check, with the thresholds fixed now rather than tuned later;
- the full model list;
- the evaluation design (Clark–West and Giacomini–White tests, the Hansen–Lunde–Nason MCS, and the Qu–Timmermann–Zhu and Akgun et al. panel tests);
- primary, secondary and exploratory comparisons, specified in advance to guard against specification search.

**AI-use record:** Claude (Sonnet 5, via Claude Code) ran the BFS diagnostic, set out the options and their consequences for publication, and drafted the committed plan following the author's chosen approach. The author made the decision. Not yet reviewed by the author in full detail.

**Next:** Phase 5, the baseline and full model set, executed exactly as specified in the committed plan.

## 2026-10-15: Phase 5 (model evaluation; major finding, paused for author input)

*Note added later the same day: the headline below was revised after three errors (C1–C3) were found in this run. See the next entry and [literature/phase5_findings.md](literature/phase5_findings.md). The entry is otherwise left as originally written.*

Built the real-time forecast dataset and ran all pre-specified models (an autoregressive (AR) benchmark; the benchmark plus BFS at each horizon h = 0–4; elastic net; random forest (RF); gradient boosting (GBM); and a combination forecast) with expanding-window re-estimation, evaluated on the locked test window (2023Q1–2025Q4), exactly as specified in [pre_analysis_plan.md](pre_analysis_plan.md).

**Headline finding: the apparent signal does not survive correction for the panel's dependence structure.** Naive pooled Clark–West tests showed BFS significantly improving forecasts at h = 1–4 (p as low as 0.0003 at h = 3) and RF beating the benchmark (p = 0.00006). But 612 "observations" (51 states × 12 quarters) are not 612 independent data points. A two-way clustered test (Cameron–Gelbach–Miller, clustering by state and by quarter simultaneously) finds no significant improvement at any horizon, for any model (p = 0.26–0.96 across horizons; RF's point estimate turns slightly negative under clustering).

Follow-up diagnostic: the lag-3 correlation that drove Phase 3's optimistic reading drops from 0.26 to 0.10 when the 2020–21 pandemic surge in business formation is excluded from the development window, and is 0.43 within 2020–21 alone. The test window (2023–2025) has no comparable shock, which is consistent with the relationship not generalizing beyond that one episode.

**Disclosed deviations from the pre-analysis plan** (under its Section 8 rule): the Hansen–Lunde–Nason MCS and the Qu–Timmermann–Zhu/Akgun panel tests were not implemented from scratch, because no vetted reference implementation was available and a bespoke implementation risked errors that could not be verified. They were replaced with Holm–Bonferroni (for the MCS) and cluster-robust, two-way-clustered tests (for the panel tests), which are standard, well-understood methods serving the same purpose. The cluster-robust substitution is the one that mattered: it overturned the naive result, which supports the Phase 1 decision to look for panel-robust tests.

Full write-up: [literature/phase5_findings.md](literature/phase5_findings.md). Work paused here: the result changes the paper's direction and is not a routine implementation detail, so it went to the author before any further work.

**AI-use record:** Claude (Sonnet 5, via Claude Code) built the forecast infrastructure, ran all models, identified the divergence between the naive and clustered tests, and ran the pandemic-episode diagnostic to explain it. Not yet reviewed by the author.

## 2026-10-15: Phase 5 corrected and pre-analysis plan Addendum 1 (complete)

The author chose to write up the Phase 5 result (the first of the options presented) and approved three follow-up analyses that would determine whether it supports a publishable paper.

**Addendum committed before running** ([pre_analysis_plan_addendum_1.md](pre_analysis_plan_addendum_1.md), commit feb59b5). It fixes, in advance:

- the period boundaries;
- what result would support or undercut the pandemic-episode explanation;
- a required consistency check;
- an explicit note that the pandemic hypothesis was formed after seeing the Phase 5 results.

**Three errors in the first Phase 5 run, found while preparing the addendum and corrected.** None let test data into training.

- **C1:** the ML tuning folds split by alphabetical blocks of states, not by time.
- **C2:** "best ML model" was hard-coded to random forest.
- **C3 (changes the headline):** the robust tests were run on the unadjusted error difference, while the naive test used the Clark–West adjusted one.
  - The first write-up said the 3-quarter-lead result was "nowhere near significant (p = 0.70)". That is correct for *accuracy*.
  - The robust *information* test is p ≈ 0.07, which is marginal.
  - The stronger, incorrect statement had been reported to the author; the corrected version is in the findings document.

Regression forecasts are unchanged; all 612 match the first run exactly. The new inference code reproduced every original naive and two-way number exactly before it was relied on.

**Results** (full write-up: [literature/phase5_findings.md](literature/phase5_findings.md)):

- **Locked test window:** no detectable accuracy gain. 3-quarter lead +1.6% of benchmark MSE (mean squared error; 95% CI −6.5% to +9.7%); best ML (elastic net) +2.3%. The data rule out gains above about +2% at the same-quarter lead and about +10% at the 3-quarter lead, but cannot rule out modest gains.
- **Robustness checks:** the results hold with the seasonally adjusted series and with winsorizing.
- **Over time, the relationship is regime-dependent:**
  - 2010–19: modest real information (robust information test p ≈ 0.004 at h = 3), accuracy gains of about 1–4%, positive in about two-thirds of states.
  - 2020–21: large gains, 11–20% at leads 0–3, in 80–92% of states.
  - 2022–25: no gain or slight losses at leads 0–3.
- **The estimated weight on applications roughly doubled after the pandemic entered the training data.** One possible explanation is that post-pandemic models over-weight applications. That is a hypothesis only: as the addendum requires, no fix is tested on the locked window.
- **Against the addendum's pre-stated rules:** partly supported (large pandemic gains; small pre-2020 accuracy gains), partly undercut (real pre-2020 information), plus an unanticipated post-pandemic deterioration. The findings document reports this mixed outcome rather than forcing it into a single category.

**Open items before drafting:**

- RQ2 (which application series carries the signal) is pre-specified and not yet run.
- RQ4 (BDS new-firm share) is exploratory and not yet run.
- Citations for the two-way clustering and wild cluster bootstrap methods are not yet verified.
- The Phase 3 national chart uses two y-axes (a format that can make unrelated series look related) and needs redrawing before any use in the manuscript.
- Reproducibility audit (Phase 8).

**AI-use record:** Claude (Opus 5.5, via Claude Code) wrote the addendum and the analysis code, found and fixed the three errors, ran the analyses, and wrote the findings. Not yet reviewed by the author.

## 2026-10-15: RQ2 (Addendum 2), chart redraw, reproducibility tooling

The author approved four items: RQ2, citation verification, redrawing the dual-axis chart, and a reproducibility audit.

**RQ2: which application series carries the signal.** [Addendum 2](pre_analysis_plan_addendum_2.md) (commit d07a3b4) was committed before running. It fixed in advance:

- the Holm family;
- the "composition" hypothesis (that the post-2020 breakdown comes from applications that rarely become employers);
- the decision rules for judging it.

Results ([literature/rq2_findings.md](literature/rq2_findings.md)):

- **Before 2020**, the narrower employer-intent series beat all applications:
  - high-propensity applications at the same-quarter lead: +4.8%, Holm p < 0.001;
  - applications with planned wages at the 3-quarter lead: +3.7%, Holm p = 0.012.
- **After 2020 that advantage disappeared.** No series helped, and the narrower series did slightly worse than all applications.
- **The composition explanation is not supported** under the pre-stated rules.
- **High-propensity applications' estimated weight barely changed (+12%), yet their forecasts still got worse.** So the "pandemic-inflated weight" hypothesis from Addendum 1 cannot explain the breakdown alone. The relationship itself appears to have changed.
- **Locked window:** no series improves forecasts (Holm p ≥ 0.54).
- **Consistency check passed:** the all-applications forecasts match Addendum 1 exactly.
- **One coding error, caught by that check:** a column-name collision in the check itself; fixed and re-run.

**Charts.** Redrew the Phase 3 national chart, which had two y-axes, as stacked panels on one shared scale. Recolored the state-example chart with a validated palette (colorblind-separation and contrast checks pass). The Phase 3 tables regenerated byte-for-byte identical.

**Reproducibility tooling.**

- Pinned all package versions in `requirements.txt`. The file was previously unpinned, so a later install could have changed the ML results.
- Moved Jupyter to `requirements-notebooks.txt`.
- Added `replication/run_all.py`, which rebuilds every committed table and figure in one command.
- Added `replication/verify_outputs.py`, which compares regenerated outputs against git HEAD.
- Added SHA-256 checksums of the raw files to `data/MANIFEST.md`.

**Fresh-clone audit: passed.**

- **Setup:** cloned from GitHub at commit a131fb8 into an empty folder, with a new virtual environment installed from the pinned `requirements.txt` (Python 3.12.10).
- **Pipeline:** `replication/run_all.py` ran end to end in 4.1 minutes.
- **Consistency checks:** both internal checks passed; the over-time and RQ2 forecasts match the primary forecasts exactly.
- **Output comparison:** `replication/verify_outputs.py` checked all 31 committed tables and 6 figures and found 0 problems.
  - The largest numeric difference anywhere was 1.1e-14. That is last-digit floating-point variation from multi-threaded arithmetic, not a substantive difference.
  - The ML tuning chose identical settings.
- **Practical notes:**
  - The first attempt failed because the path of the working folder used exceeded Windows' 260-character limit inside `.git` and `.venv`. The audit was re-run in a short temporary folder, which was deleted afterwards.
  - Anyone reproducing this on Windows should clone to a short path.

**AI-use record:** Claude (Opus 5.5, via Claude Code) wrote Addendum 2, the RQ2 code, the reproducibility tooling and the findings; redrew the charts; and ran the analyses and the audit. Not yet reviewed by the author.

## 2026-10-15: Pre-registered live forecasts (Addendum 3) and RQ4 (Addendum 4)

The author approved this order: live forecasts first (they are time-sensitive), then a small RQ4 analysis, then drafting.

### Live forecasts (Addendum 3)

[Addendum 3](pre_analysis_plan_addendum_3.md) was committed together with the forecasts in commit 7a36fe1, tagged `prereg-live-forecasts-2026`. BLS publishes 2026Q1 data on 2026-10-28, so the commit precedes any 2026 establishment-birth data.

**What was forecast:**

- 2,448 forecasts: 51 states × 2026Q1–Q3 × 16 model variants.
- The variants are the benchmark, all applications at leads 0–4, and high-propensity applications at leads 0 and 3.
- Each variant is run twice: trained on all data, and trained without 2020–22.
- Before forecasting, the rebuilt features were checked against the Phase 5 forecast data and matched exactly on all 4,386 rows.

**Safeguards:**

- The forecast file's SHA-256 hash: `8e0751c9…841fc`.
- A `.gitattributes` rule stores the file byte-for-byte, so the hash is the same on every platform. Without it, git's line-ending conversion would have changed the hash on Mac and Linux checkouts. The hash of the stored copy was confirmed after pushing.
- The forecasting script refuses to overwrite the file.

**Scoring:**

- The scoring script was committed at the same time and tested on synthetic data only; a hand calculation matched its output.
- **H1** (the paper's claim): applications still do not improve forecasts.
- **H2:** training without 2020–22 improves forecasts.
- **Expected differences between variants:** models trained on all data forecast 4–9% year-over-year growth; the 2020–22-excluded models and the benchmark forecast about 1–3%.

**Pending author decision:** public timestamping. The repository is private, so outsiders cannot verify when the forecasts were made.

### RQ4 (Addendum 4)

[Addendum 4](pre_analysis_plan_addendum_4.md) was committed (4fd546f) before running.

**Correction before running.** The Phase 2 new-firm share had excluded firms too old for Census to date ("left-censored") from its denominator. That overstated the share:

| | Before | After |
|---|---|---|
| 2010–19 mean | 69% | 61% |
| All-years mean | 77.9% | 66.8% |

The corrected figure implies that about 39% of new establishments come from existing firms, close to Decker & Haltiwanger's figure of about 36%. Fixed in `clean_bds.py` before any use. The Phase 3 findings and the data manifest are corrected; the Phase 2 (BDS) log entry above is left as originally written.

**Results** ([literature/rq4_findings.md](literature/rq4_findings.md)):

- **Same-quarter lead, pre-2020:** forecasting gains are larger in states where more entry comes from brand-new firms (Spearman ρ = 0.37, Holm p = 0.014). Under the pre-registered reading, that is consistent with the new-firm mechanism.
- **3-quarter lead:** ρ = 0.11, inconclusive.
- **After 2020:** no relationship.
- **Robustness:** a moderate tendency, not driven by any single state.

### Pipeline

`make_live_forecasts.py` (which checks the frozen file) and `run_rq4.py` were added to `replication/run_all.py`.

**Pipeline re-run.** A full re-run with all 8 steps took 4.3 minutes and reproduced all 34 tables and 7 figures, with 0 problems. The live-forecast step confirmed that the frozen file regenerates exactly.

Ten tables differed from the committed copies only in the 15th–16th significant digit, because the random forest sums trees in parallel. The committed copies were restored, and the README now notes this.

**AI-use record:** Claude (Opus 5.5, via Claude Code) wrote Addenda 3 and 4, the forecast, scoring and RQ4 code, and the findings; and found and fixed the new-firm-share definition and the line-ending risk to the forecast hash. Not yet reviewed by the author.

## 2026-10-15: Manuscript draft v1

Drafted [manuscript/draft_v1.md](manuscript/draft_v1.md): about 4,500 words of main text, 5 tables, 3 figures, references, a data and code statement, an AI-use statement, and a pre-registration and deviations section. It follows the format of the *Journal of Forecasting*, the plan's primary target journal.

**Framing:** the relationship between applications and establishment births is regime-dependent and changed after 2020. That change is not explained by application composition. Naive pooled tests overstate significance in state panels. The live-forecast test is Section 8.

**Checks on the draft:**

- Every number was checked against the committed output tables. That check found and fixed one overstatement ("every lead" corrected to "leads 0–3") and one imprecise claim about the four-quarter contribution.
- An incorrect description of the repository as "public-on-request" was removed.
- An unsupported sentence about policy demand was replaced with a factual one.

**Open items before submission, marked [VERIFY] in the draft:**

- reference author initials;
- the Decker & Haltiwanger (2023) page range;
- one DOI;
- JEL codes;
- the journal's current AI-disclosure wording;
- the repository's public URL.

**AI-use record:** Claude (Opus 5.5, via Claude Code) drafted the manuscript from the project's findings documents. Not yet reviewed by the author; the author's revision is the next step.

## 2026-10-15: Manuscript figures

The author asked whether the draft needed more figures. A small set was proposed, each figure supporting one claim, and the author approved building them. The figures are in [manuscript/figures/](manuscript/figures/README.md), with draft captions and proposed placements. None has been placed in the draft yet; that waits for the author's review.

- **Code:** new script `src/analysis/make_paper_figures.py`, added to `replication/run_all.py`. `verify_outputs.py` now also checks `manuscript/figures/`.
- **Presentation only:** every figure is drawn from committed tables, the committed analysis panel, or the frozen live-forecast file. Nothing is re-estimated.
- **Consistency check:** the script asserts that the quarterly gains it recomputes match the committed `rq2_quarterly_gains_h3.csv`.
- **Determinism:** PDF output is byte-identical across runs.
- **Seven figures:**
  1. national applications and births;
  2. test-window results with naive and robust intervals;
  3. cumulative gain over time;
  4. cumulative gain by application series;
  5. weight on applications, indexed;
  6. gain against new-firm share;
  7. the 2026 live forecasts.

**Draft correction.** Building Figure 5 showed that the draft overstated how stable the weight on applications was. The draft said it was "stable at about 0.15–0.20 through 2021". In fact:

- the 2010 estimates, from short samples, ran from 0.18 to 0.30;
- from 2011 to 2021 it stayed between 0.11 and 0.20, averaging 0.18 over 2010–2019;
- it peaked at 0.41 in 2022 and then settled at 0.32–0.34.

The sentence and the related elasticity bullet in Section 6.4 are corrected. The "roughly doubled" conclusion is unchanged.

**Live-forecast summary, made precise.** The earlier entry said that models trained on all data forecast 4–9% growth for 2026, and the others about 1–3%. Those were averages across states with equal weights, the same weighting the evaluation uses. Exact ranges over 2026Q1–Q3, in log points:

- all-data applications models: 4.0–8.5;
- applications models estimated excluding 2020–22: 1.9–3.4;
- benchmark: 2.5–2.8 on all data, 0.3–0.9 excluding 2020–22.

Summed to a national total, the levels are lower and closer together (all-data applications models 1.6–7.1; benchmark 0.4–4.2), because the forecasts for large states show lower growth.

**Observation recorded before any 2026 outcome data exist (no change to the pre-registered tests).**

National applications rose sharply in 2025, but almost entirely outside the series Census builds to flag likely employers:

| National YoY change, log points | 2025Q2 | 2025Q3 | 2025Q4 |
|---|---|---|---|
| All applications | +6.2 | +12.7 | +20.6 |
| High-propensity | +1.9 | +1.0 | +5.3 |
| Planned wages | −5.3 | −11.9 | −13.9 |
| Corporate | −1.8 | −4.3 | +0.6 |

Implications:

- **The 2026 forecasts.** The all-data applications models weight applications about twice as heavily as before 2020, so they translate this surge into the high 2026 forecasts above.
- **Reading the H1 result.** If 2026 births do not rise to match, the result will be consistent with the paper's H1 reading, but part of the reason may be this 2025 shift in composition, not only the 2022–25 breakdown. Section 8 will need to say so.
- **What helps separate the two.** The secondary high-propensity forecasts in Addendum 3, which are already frozen, will help.
- **A possible explanation, not established.** In February 2026 Census removed internet-sales applications from the high-propensity and corporate series after a spike in such filings, but kept them in all applications. Census did not give the date of the spike (see `literature/rq2_findings.md` §6), so this is unverified.

Addendum 3 and the frozen forecasts are unchanged.

**AI-use record:** Claude (Opus 5.5, via Claude Code) proposed the figure set; wrote the figure script, captions and review notes; found the draft's coefficient-range error and the 2025 divergence; and wrote this entry. Not yet reviewed by the author.

## 2026-10-15: Figures placed in the draft

The author approved the proposed placements and kept Figure 3 as its own figure. The author also delegated the public-timestamp decision and then explicitly authorized posting.

**Draft changes:**

- All seven figures placed, with captions.
- Tables renumbered:
  - main text: 1 (test window), 2 (by period), 3 (robustness);
  - appendix: A1 (information-test p-values, formerly Table 2) and A2 (accuracy by series, formerly Table 4).
- The paragraph on the weight given to applications moved from Section 6.4 to 6.5, so that figure numbers follow the order of first mention.
- Section 6.2 now notes that naive inference also overstates significance in the accuracy comparison. The naive test says same-quarter applications made forecasts significantly worse (p = 0.03); the robust test does not (two-way p = 0.26). Both numbers come from the committed `phase5_comparisons.csv`.
- Fixed a wrong cross-reference: the seasonally adjusted check is in Section 6.7, not 6.6.
- Section 8:
  - corrected "the commit carries the hash" (the SHA-256 is the forecast file's);
  - added Figure 7;
  - added the 2025 composition observation recorded in the entry above.

**Reproducibility:** a full `run_all.py` re-run (9 steps, the figure step included) passed `verify_outputs.py`: 34 tables and 21 figure files, 0 problems. The manuscript figures were byte-identical. Ten tables differed only in the 15th–16th significant digit (random-forest parallel summation) and were restored to the committed copies.

**Public timestamp: not yet posted.** A hash-only public gist was prepared. It contains the forecast file's SHA-256, commit 7a36fe1 (the tag `prereg-live-forecasts-2026`) and commit 9fb1904, with no project name, paths, data or results. The upload could not be completed from the AI coding tool: its permission settings blocked it twice, the second time after the author's explicit authorization. Posting is pending the author. Section 8 of the draft carries a [VERIFY] placeholder for the link. Deadline: before BLS publishes 2026Q1 data on 2026-10-28.

**AI-use record:** Claude (Opus 5.5, via Claude Code) placed the figures, edited the draft text and wrote this entry. Not yet reviewed by the author.

## 2026-10-15: Copy-edit and consistency review of the repository

The author asked for a review of every item in the repository for typos, errors, and wording that reads as unpolished or obviously AI-generated, with fixes committed.

**Manuscript.**

- Rewritten from bullet lists into continuous academic prose, with American spelling throughout. No number changed; this was checked mechanically against the previous version.
- **Corrected claim:** the paper said two inference methods were replaced "as disclosed in the plan itself". The plan promises that deviations will be disclosed but does not itself disclose them, so the sentence was reworded.
- **Undisclosed departures now listed** under "Pre-registration and deviations". Three departures from the pre-analysis plan were recorded in the code or this log but not in the paper:
  - the seasonal naive benchmark was not estimated (with a year-over-year target it amounts to forecasting no change);
  - the ARDL and bridge-equation specifications coincide;
  - the Giacomini–White fallback was not implemented.
- **Placement disclosed:** Addendum 4 anticipated reporting RQ4 in an appendix. It is in Section 6.6 instead, and that is now disclosed.
- **Uncited reference fixed:** Giacomini & White (2006) was listed in the references but not cited; it is now cited.
- **Decker & Haltiwanger (2022) figure re-checked against the FEDS Note.** Existing firms accounted for about 36% of annual establishment births on average over 2015–2019, in national Census Business Dynamics Statistics data (the note's footnote 7). An earlier version of this entry said BED data; that was wrong and is corrected in the next entry. The text now states the period and source. The original Phase 3 write-up had described the figure as specific to the pandemic, which was wrong.
- **Data-availability statement:** it now covers the manuscript figures.

**Repository.**

- **Work email removed from the code.** The author's work email was hard-coded in the User-Agent strings of the three download scripts. They now read a contact address from the `RESEARCH_CONTACT_EMAIL` environment variable, or a git-ignored `.env` file, through `src/acquisition/user_agent.py`. The address remains in earlier commits in the git history.
- **Code comments and docstrings copy-edited.** Comparing the parsed code with the previous commit confirms that only comments and docstrings changed, apart from one printed message.
  - Stale statements were corrected: references to Census and BLS APIs the project does not use; the unit-of-analysis wording; the docstring of `verify_outputs.py`.
  - Citations for the test window now point to `pre_analysis_plan.md` §1.
  - The evaluation script's list of deviations now matches the paper.
- **Documentation copy-edited:** the READMEs, the data manifest, the research question, the literature notes and findings documents, the roadmap documents, and both logs.
  - Current status was brought up to date.
  - Shorthand is now expanded.
  - Informal, second-person and AI-process wording was removed.
  - The AI-use records were kept and their wording standardized.
  - `forecast_dataset.csv` is now documented in the manifest.
- **The pre-analysis plan and its addenda are unchanged,** as timestamped commitments. Known cosmetic slips in them: "after user review" in the plan's §4 heading (meaning the author's review) and the shorthand "Q1-lumpiness".

**AI-use record:** Claude (Opus 5.5, via Claude Code) carried out the review, with three parallel sub-agents copy-editing the code comments and the documentation. The lead session reviewed every change before it was committed. Not yet reviewed by the author.

## 2026-10-15: Seasonal naive benchmark (from the original plan)

The pre-analysis plan (§5) lists a seasonal naive benchmark, which the first implementation omitted (see the previous entry). The author approved adding it.

**Definition, committed before evaluation** (commit 47b60fc, `src/analysis/run_seasonal_naive.py`):

- The forecast is each quarter's births in the same quarter a year earlier, which is already published at the real-time forecast origin. With the year-over-year log-change target, the forecast is zero.
- It is evaluated over the 2023Q1–2025Q4 test window against the AR benchmark, with the same accuracy comparison and inference as Table 1.
- It has no parameters, so there was no specification choice to make.

**Result** (`outputs/tables/seasonal_naive_comparison.csv`, `seasonal_naive_performance.csv`):

| Forecast | RMSE | MAE |
|---|---|---|
| AR benchmark | 0.1798 | 0.125 |
| Seasonal naive (no change) | 0.1812 | 0.117 |

- The seasonal naive forecast's mean squared error is 1.6% higher than the benchmark's (95% CI −8.5% to +5.3% two-way clustered; two-way p = 0.65).
- The wild cluster bootstrap interval is 2.3 times wider: −17.4% to +14.2%, p = 0.92. Under Addendum 1's rule for materially wider bootstrap intervals, the bootstrap interval is the one reported, as already done for gradient boosting (ratio 1.59; every other comparison is at or below 1.13).
- **Reading:** the AR benchmark is not detectably more accurate than forecasting no change, and its mean absolute error is higher. The benchmark is therefore a low bar, and the applications models still do not clear it detectably. This does not change any other result.

**Draft updates.**

- New row in Table 1, and the table note now states the pre-specified bootstrap rule. That rule is also stated in Section 5.
- One sentence in Section 4 introduces the benchmark, and two sentences in Section 6.1 report the result.
- Departure (i) in "Pre-registration and deviations" now says the benchmark was added before submission, with its definition committed before evaluation.
- The Figure 2 caption now gives the rule-based reason for gradient boosting's bootstrap interval, replacing the word "unstable".

**Reproducibility:** a full `run_all.py` re-run with the new step (10 steps) passed `verify_outputs.py`: 36 tables and 21 figure files, 0 problems. The two new tables regenerated byte for byte; nine others differed only in the last digits (random-forest summation) and were restored.

**AI-use record:** Claude (Opus 5.5, via Claude Code) wrote and ran the code and updated the draft. Not yet reviewed by the author.

## 2026-10-15: Reference and citation verification

Before planning submission, three independent checks were run: bibliographic details, the accuracy of every claim attributed to a cited source, and the target journals' current requirements. The lead session re-verified the decision-relevant findings against primary sources before applying them.

**Reference corrections** (Crossref, DataCite, publisher and agency pages; committed in a64c848):

- Asturias et al. (2024): fifth author Plumb, A. (Alyson), not J.
- Grieves, Mance & Witt (2023): third author Witt, C. (Collin); the full title has a subtitle.
- Galanakis & Savagar (2026): the author order printed on the paper reverses the arXiv listing.
- The open [VERIFY] items were resolved; DOIs were added; JEL code R11 was added.

**Claim corrections** (each checked against the source text):

- **Novelty claim narrowed.** Bayard et al. (2018, §4.3) evaluate state-level projections of employer startups out of sample, and Decker & Haltiwanger (2023, appendix Table F4) estimate state-by-quarter elasticities of establishment births with respect to high-propensity applications. The paper now claims novelty only for real-time, out-of-sample forecasting of state establishment births, and cites both.
- **Haltiwanger (2022) added.** Its national quarterly VARs (2004–2019) show high-propensity applications leading establishment births. Confirmed in the NBER working paper text; reference details from Crossref.
- **Decker & Haltiwanger (2023, Table F4) cited in Section 6.5.** Read directly from the table:
  - with state effects, the elasticity rises from 0.32 to 0.57 when 2020–2022 are added;
  - with year-by-quarter time effects, it falls from 0.31 to 0.19.

  This parallels the doubling of the weight on applications reported here.
- **The 36% figure is from the Census Business Dynamics Statistics,** per footnote 7 of the 2022 FEDS Note. An edit earlier today had wrongly said "national BED data", after a summarizing tool misread the note. It is corrected in the manuscript, the extraction table and the copy-edit entry above. The comparison with this project's BDS-based 39% is now like for like.
- **Other corrections:**
  - Asturias et al. (2024): the gains come "in the years following the turning points", not "around" them.
  - The dynamic factor model belongs to the 2024 paper only.
  - The industries-and-locations finding belongs to Decker & Haltiwanger (2023) only.
  - Borup & Schütte (2022) evaluate state by state, not as a pooled panel.
  - The Diebold–Mariano test compares forecasts taken as given; it was not "designed for non-nested comparisons".
  - Clark–West is "an adjustment such as", not a requirement.
  - The HBA redefinition took place in November 2021 and was applied from 2012; Section 6.5 had said "2012 redefinition".
  - Census's stated reason for the February 2026 change (low transition rates) was added.
  - Deviation (iv) now notes that Giacomini–White requires rolling, not expanding, estimation windows.

**No result changed.** All edits concern how prior work is described.

**AI-use record:** Claude (Opus 5.5, via Claude Code) ran the checks with three parallel sub-agents, re-verified the key findings and applied the corrections. Not yet reviewed by the author.

## 2026-10-19: Release and submission preparation (Journal of Forecasting)

The author approved the preparation steps for public release and submission. The target journal's current requirements were verified on 2026-10-15 (see the previous entry).

**Public-release files** (the repository stays private until the author makes it public):

- `LICENSE`: the MIT License, for the code. The root README states that the manuscripts, figures and written documentation are not covered (all rights reserved), so that journal options remain open.
- `CITATION.cff`: citation metadata, which GitHub's "Cite this repository" button reads. Zenodo also reads it when archiving a release. The ORCID iD is to be added.

**Manuscript restructured for the Journal of Forecasting.** No result or number changed.

- **Title page:**
  - a running title of under 40 characters ("Applications and Establishment Births");
  - placeholders for the author's location, email and ORCID iD;
  - the statements the journal asks for: data availability, funding, conflict of interest, ethics approval, and permission to reproduce material.
- **AI disclosure split as Wiley's guidelines require:**
  - help with drafting and editing goes in the Acknowledgments;
  - research use (literature, code, analysis) goes in a Methods paragraph at the end of Section 4.

  Both give the tool, models, dates of use, role and oversight. Both contain bracketed confirmations that become true only after the author's review and rewrite.
- **The former "Data and code availability" and "Use of AI tools" sections** were replaced by the title-page statements and a "Reproducibility" section.
- **Remaining markers:** all [VERIFY] markers are resolved. The remaining bracketed items need the author's input: location, email, ORCID iD, Zenodo DOI, gist link, and the confirmations above.

**Word build.** `manuscript/build_docx.py` (pandoc 3.9 via `pypandoc-binary`, pinned in `requirements-manuscript.txt`) converts the Markdown master to Word.

- It embeds the 7 figures and turns the page-break markers into page breaks.
- Output goes to `manuscript/submission/`, which is git-ignored and also holds the local cover-letter draft, the author's submission checklist and the gist text.

**AI-use record:** Claude (Opus 5.5, via Claude Code) prepared the files, restructured the manuscript, drafted the cover letter and checklist, and verified Wiley's AI-disclosure rules and Zenodo's archiving procedure against their official pages. Not yet reviewed by the author.

## 2026-11-04: Live forecasts, 2026Q1 scored (Addendum 3)

BLS published the 2026Q1 Business Employment Dynamics data on 28 October 2026. No session took place between 21 October and 4 November, so the release was downloaded and scored on 4 November.

**Data.** Retrieved with `src/acquisition/fetch_bed.py` into `data/raw/bed/2026-11-04/`. SHA-256 checksums: `bd.data.1.AllItems` 8fd11308f099f6a1b8b89661b3696e895ad464fb1f452098ea8960a865ed159e; `bd.series` 5a7f48dd14eecfe53bdf0772a6b33260cd9f3bf90778f599d5a9b5577f0087c2. The release contains 2026Q1 births for all 50 states and DC.

- **Revisions to 2025.** The release revised 2025 state births levels. The average revision by quarter was +1.7% (2025Q1), +0.5% (2025Q2), +0.4% (2025Q3) and +0.7% (2025Q4); no earlier quarter changed.
- **As pre-registered,** the actual values are computed within the new release. The paper's main analysis continues to use the vintage retrieved on 14 October 2026.

**Scoring.** Scored with the committed script `src/analysis/evaluate_live_forecasts.py`, unchanged; output in `outputs/live_forecasts/evaluation_2026-11-04.csv`. This was the script's first use on real data. An independent recomputation in a separate script reproduced every primary number exactly.

- **Actual outcome.** Establishment births were essentially flat: an average change of +0.8 log points across the 51 states (median +0.3).
- **Forecasts for comparison** (average across states, log points):
  - all-data applications models: 4.0 (h = 3) and 4.2 (h = 0);
  - the same models estimated excluding 2020–22: 1.9 and 2.5;
  - benchmark: 2.5 on all data, 0.9 excluding 2020–22.

| Pre-registered comparison | Accuracy difference (% of reference MSE) | States where the model was better | Pre-registered reading |
|---|---|---|---|
| H1: BA h = 3, all data, vs. benchmark | −6.7 | 41% | Consistent with the paper |
| H1: BA h = 0, all data, vs. benchmark | −7.6 | 41% | Consistent with the paper |
| H2: BA h = 3 excluding 2020–22 vs. all data | +7.3 | 61% | Supports H2 |
| H2: BA h = 0 excluding 2020–22 vs. all data | +6.9 | 65% | Supports H2 |

**Secondary comparisons** (reported, not read):

- High-propensity applications at h = 3 (all data) were about as accurate as the benchmark: +0.6%, better in 55% of states.
- All applications at h = 1 (all data) were much worse: −37.3%.
- The benchmark estimated excluding 2020–22 was 3.4% more accurate than the all-data benchmark.

These patterns match the observation recorded on 15 October, before any 2026 data existed: the 2025 rise in total applications lay outside the employer-intent series. With one quarter and common national shocks, all of these readings are descriptive, not tests.

**Figure 7.** A new script, `src/analysis/export_live_actuals.py`, writes the state-level actual values to `outputs/live_forecasts/actuals_2026-11-04.csv`. It uses the scoring script's own `actuals_from_release()` and does not modify the scoring script. Figure 7 now marks the actual 2026Q1 average and labels 2026Q2–Q3 as not yet published.

**Public timestamp.** The hash-only public gist was not posted before the 2026Q1 release (it is pending the author).

- **Evidence of timing for 2026Q1** is the repository history plus GitHub's server-side activity log. That log records the push of the forecast commit 7a36fe1 at 2026-10-15T14:28:02Z, 13 days before the release.
- **A snapshot** of the log, retrieved through the GitHub API on 4 November, is saved as `outputs/live_forecasts/github_push_log_retrieved_2026-11-04.json`.
- **For 2026Q2 and 2026Q3,** a gist posted now still predates the outcome data.
- **The paper must state this plainly.**

**AI-use record:** Claude (Opus 5.5, via Claude Code) downloaded and scored the release, recomputed the scores independently, exported the actual values, updated Figure 7 and wrote this entry. Not yet reviewed by the author.

## 2026-11-04: Pre-submission audit, part 1 (number trace and fresh clone)

The author asked for a full double-check before submission. Independent checks were run in parallel: a code audit, a number trace, a mock referee report, a scan of new literature and releases, and a fresh-clone reproduction. The lead session re-verified each finding before acting on it.

**Number trace.** About 305 numbers in the manuscript (outside Section 8) were traced to the output tables. About 301 were exact. Corrections:

- **Four wrong numbers:**
  - Table 1, h = 1 interval upper bound: +6.5, not +6.6.
  - Section 6.5, Holm-adjusted p for planned-wage applications at h = 3: 0.011, not 0.012. The same error is corrected in `literature/rq2_findings.md`.
  - Introduction: the robust information-test p-value is 0.076 (0.067 by bootstrap), not "about 0.07".
  - Section 6.2: the smallest Holm-adjusted primary p-value is 0.15 two-way (0.14 by bootstrap), not 0.14.
- **Nine claims narrowed to what the tables support:**
  - the "four quarters contribute more than the entire net gain" claim holds at h = 3 only;
  - the 2020–21 gains are 11–20% at leads 0–3 only;
  - from 2022 there is a small, non-significant gain at h = 4 (3.5%), and the text now says so;
  - "after 2020" is replaced by "from 2022 onward" where the result is for 2022–2025;
  - the weight settles at 0.31–0.34;
  - "the narrower series mostly did slightly worse";
  - "unadjusted p < 0.001" for the 2013–2019 check;
  - the elasticities are stated in log points;
  - the publication lag is stated consistently.

**Test-window breach found and disclosed.** The seasonality diagnostic recorded in the 2026-10-15 Phase 4 entry above, which motivated the quarter-of-year indicator, is reproduced only on the full 2004–2025 sample. That sample includes the 2023–2025 test window, and the diagnostic was run before the pre-analysis plan was committed.

- It concerns the timing of quarter-to-quarter spikes, not forecast accuracy.
- Restricted to the development window it gives the same result: 21.2% versus 21.5% of state first quarters with a jump above 40%, and 33 of 38 versus 36 of 41 joint jumps in a first quarter.
- The manuscript now reports the development-window figures and lists this as deviation (vi).
- The pre-analysis plan and the Phase 3 findings are left as written.

**2025 revision.** The 2026Q1 release revised 2025 births levels (by 0.4–1.7% on average, by quarter). The Limitations section now says so; the main analysis keeps the 14 October vintage.

**Fresh-clone audit at commit 0115b2f: passed.**

- The pinned install took 116 seconds.
- `run_all.py` completed all 10 steps in 4.6 minutes.
- `verify_outputs.py` reported 36 tables and 21 figure files, 0 problems.
- Every output was rewritten during the run, and all 21 figure files were byte-identical to the committed versions.
- The Word build also worked.

**Follow-ups from the audit:**

- Added `requirements-lock.txt`, with all 32 packages, including indirect dependencies, recorded from a clean environment.
- `verify_outputs.py` now reports, for information, whether each figure is byte-identical, and documents that it needs a git clone.
- The README now gives activation commands for each shell, the reset command after a run, the live-forecast scoring steps, and up-to-date status.

**AI-use record:** Claude (Opus 5.5, via Claude Code) ran the checks with parallel sub-agents, re-verified the findings and applied the corrections. Not yet reviewed by the author.

## 2026-11-04: Pre-submission audit, part 2 (code audit, web scan, mock referee)

**Code audit: no bug changes any reported number.** An independent rebuild reproduced:

- the forecasts and the ML tuning, to about 1e-15;
- all 18 rows of the inference table, including the Clark–West statistics, the clustered and two-way standard errors, the wild bootstrap and Holm;
- RQ4 and the 2026Q1 scoring.

The audit found no look-ahead in the forecasts. It raised the following issues:

- **Two deviations from the plan, now disclosed as (vii) and (viii):**
  - h is the lag of applications at a common forecast origin, not a forecast horizon; the figure labels that said "three quarters ahead" now read "applications lagged three quarters";
  - a single machine-learning comparison was run, not one each at h = 0 and h = 3.
- **Over-statements corrected:**
  - "real-time" is now "pseudo-real-time";
  - "before BLS published any 2026 data" is now "any 2026 establishment-birth data";
  - Figure 2's caption now notes that the combination is also omitted from panel (a);
  - the size of the revision to 2025 is now given over the 51 states: on average 1.0%, 0.5%, 0.4% and 0.6% for 2025Q1–Q4. The earlier entry's +1.7% averaged all 54 BED geographies, including the Virgin Islands.
- **Section 8 was incomplete,** and is now corrected:
  - the high-propensity model at h = 0 was 8.4% worse than the benchmark in 2026Q1;
  - the benchmark estimated without 2020–22 also improved, by 3.4%. Against it (a comparison not pre-registered), the applications models estimated without 2020–22 were still 3.7% (h = 0) and 2.4% (h = 3) worse, so the H2 gain is largely generic.
- **Timing evidence restated precisely:** the repository was private, and GitHub's push record is not an independent registry.
- **Open, not yet acted on:** inference with only 12 quarterly clusters, and the serial correlation induced by overlapping year-over-year targets. A t(G−1) reference distribution or HAC standard errors computed on cross-state means move every p-value toward the null; no conclusion flips.

**Web scan.**

- BLS's 2026Q2 release is scheduled for 27 January 2027; no date for 2026Q3 has been announced.
- The 2025 revision is BLS's standard annual revision.
- Census's annual BFS update on 12 November 2026 revises the seasonally adjusted series.
- The co-editors-in-chief of the Journal of Forecasting are Ngai Hang Chan and Hans-Jörg von Mettenheim. The cover letter now addresses them; their names are to be re-verified on submission day.
- No new competing literature was found. Decker (2026, NBER WP 34924, footnote 31: preliminary, national, birth-death model) is now cited; the footnote was read directly.

**Mock referee report.** It predicts a likely desk rejection as the paper stands: placeholders, and repository files marked "not yet reviewed by the author". It recommends major revision. Its three main points were re-verified today from the committed prediction files:

1. **The benchmark against a no-change (seasonal naive) forecast.** Positive values mean the benchmark is better.

   | Period | MSE | MAE | Mean error (actual − forecast) |
   |---|---|---|---|
   | 2010–19 | −0.5% | −9.5% | +0.048 |
   | 2020–21 | +15.4% | +6.0% | not computed |
   | 2022 | −11.3% | −10.1% | not computed |
   | 2023–25 | +1.6% | −7.0% | −0.078 |

   Mean absolute error is part of the pre-specified estimand.

2. **The change after 2020, split by period.** Gain from all applications over the benchmark, in % of benchmark MSE:

   | Lead | 2010–19 | 2020–21 | 2022 | 2023–25 |
   |---|---|---|---|---|
   | h = 0 | +2.6 | +11.3 | −16.0 | −3.0 |
   | h = 3 | +0.8 | +11.9 | −15.0 | +1.6 |
   | h = 4 | +0.2 | +3.2 | +9.3 | +0.8 |

   Excluding 2021Q2–2022Q1, the net gain at h = 3 over 2010–25 is −2.2%.

   Tests of change (quarterly cross-state mean loss differential regressed on a period dummy, Newey–West with 3 lags), 2010–19 vs. 2022–25:

   | Series and lead | p |
   |---|---|
   | All applications, h = 0 | 0.058 |
   | All applications, h = 3 | 0.49 |
   | High-propensity, h = 0 | 0.014 |
   | Planned wages, h = 0 | 0.023 |
   | Corporate, h = 0 | < 0.001 |

   Against 2023–25 alone: all applications at h = 3, p = 0.82; high-propensity at h = 0, p = 0.034.

   The breakdown at h = 3 is concentrated in 2022; the robust change is in the narrower series at h = 0.

3. **Census's state-level projected business formations** (BF_PBF4Q, BF_PBF8Q) are in the BFS file and are not used.

All of these analyses were computed after the main results had been seen, so if they are reported they must be labeled post hoc. The author's decision on reframing and on any new analyses is pending. No change to the paper's framing has been made.

**AI-use record:** Claude (Opus 5.5, via Claude Code) ran the audit with parallel sub-agents, re-verified the findings and applied the corrections. Not yet reviewed by the author.

## 2026-11-09: Revision analyses (Addendum 5) and live forecasts from Census's projections

**The author's decisions** (in chat, 2026-11-09):

- revise the paper fully before submission;
- reframe it around applications as an *episodic* indicator;
- about 10 hours a week, aiming to submit in late December 2026;
- replace the AI context file with a neutral `AI_USE.md` (not yet done).

**Addendum 5** was committed (4424573) before any of its analyses were run, except those it lists as already seen.

**Implementation.**

- `src/analysis/run_addendum5.py` runs items A–E and G and writes `outputs/tables/a5_*.csv`. It is now a step of `replication/run_all.py`.
- `src/cleaning/extract_bed_vintage.py` writes the births extract from the 28 October BLS release that item G3 uses ([data/MANIFEST.md](data/MANIFEST.md), Section 6).
- **Built-in checks, all passed:**
  - the benchmark reproduces `rq2_predictions.csv` on all 3,264 state-quarters (maximum difference 1e-16);
  - the quarterly construction used for the projections reproduces the committed all-applications features exactly;
  - the recomputed targets reproduce `births_yoy` (maximum difference 2e-16).
- **The audit's numbers reproduce exactly:**
  - the 2022–25 versus 2010–19 change tests (p = 0.058, 0.49, 0.014, 0.023 and < 0.001);
  - the benchmark's MAE loss to the no-change forecast (−9.5% and −7.0%) and its mean errors (+0.048 and −0.078);
  - the test-window h = 3 information test with a t(11) reference (p = 0.089).
- **One diagnostic was added:** a flag for comparisons in which the two-way clustered variance falls below both one-way variances. It affects 17 comparisons against the no-change forecast, all on squared error; their wild bootstrap p-values are the ones to report. No comparison in the paper's primary tables is affected (checked). This and three other implementation notes are appended to Addendum 5.

**Results.** None of these results is pre-specified except item A. 2022 is descriptive.

*A. The no-change forecast* (test window; positive = model better):

- **Absolute error:** every test-window model is 6–9% less accurate than the no-change forecast (two-way p from 0.007 for the benchmark to 0.17).
- **Squared error:** the models range from −1.3% to +4.5%, and none differs significantly (smallest bootstrap p = 0.63).

*B and C. The pattern over time, and tests of change.*

- **The criterion:** a lasting change (2023–25 versus 2010–19) significant at 5% after Holm adjustment across the 20 series × lead tests.
- **Where it holds:** only corporate applications, at h = 0 (−18.9 percentage points of the 2010–19 benchmark MSE; Holm p < 0.001) and h = 1 (−17.0; Holm p = 0.011), with both statistics.
- **Where it does not:**
  - all applications at h = 0 (−6.8; raw p = 0.12) and h = 3 (+1.4; raw p = 0.82);
  - high-propensity applications at h = 0 (−14.6; raw p = 0.034; Holm p = 0.61).
- **The 2020–21 and 2022 contrasts:** none is significant after Holm adjustment.

*D. Inference robustness.*

- **Before 2020,** the information tests survive both checks: at h = 0–3, every series has Clark–West p ≤ 0.006 with the t(G − 1) reference and ≤ 0.005 with the Newey–West/Harvey–Leybourne–Newbold test on quarterly means.
- **In 2020–21** (8 quarters), no Clark–West test reaches 5% with the second test; the smallest p is 0.078.
- **In the test window,** p-values rise under the second test. Normal → t(11) → Newey–West/HLN:

  | Model | Normal | t(11) | Newey–West/HLN |
  |---|---|---|---|
  | All applications, h = 3 | 0.076 | 0.089 | 0.189 |
  | Gradient boosting | 0.001 | 0.006 | 0.047 |
  | Random forest | 0.014 | 0.025 | 0.056 |
  | Elastic net | 0.052 | 0.066 | 0.141 |

*E. Census's projected business formations (BF_PBF4Q)*, compared with the benchmark, % of benchmark MSE:

| Lead | 2010–19 | 2020–21 | 2022 | 2023–25 |
|---|---|---|---|---|
| h = 0 | +5.9 | +21.6 | −10.4 | −5.1 |
| h = 1 | +7.4 | +21.0 | −6.3 | −3.1 |
| h = 2 | +5.1 | +19.3 | −3.2 | −2.5 |
| h = 3 | +2.5 | +11.9 | −3.6 | −2.0 |
| h = 4 | +1.6 | +0.2 | +11.9 | −0.6 |

- **Clark–West in 2010–19:** Holm-adjusted p (over 10 tests) below 0.01 at every lead, with two-way clustering and with the bootstrap. In 2023–25: Holm p = 1.
- **Against all applications at the same lead:**
  - in 2010–19, the projections are better by 3.3% at h = 0 (p < 0.001), and by 1.7% at h = 3 (p = 0.085; bootstrap p = 0.015);
  - in 2023–25, they are worse by 1.4–3.7% (not significant).
- **Change, 2023–25 versus 2010–19, at h = 0:** −13.1 points (raw p = 0.011; Holm over the 5 leads, 0.057).

*G1. State versus national information.*

- **State application growth demeaned by the cross-state mean** is within ±0.3% of the benchmark's MSE in every period, at both leads.
- **National application growth**, % of benchmark MSE:

  | Period | h = 0 | h = 3 |
  |---|---|---|
  | 2010–19 | +4.0 (Clark–West p < 0.001) | +1.6 (p = 0.004) |
  | 2020–21 | +6.0 | +33.8 |
  | 2022 | −24.4 | −51.3 |
  | 2023–25 | −1.3 | +4.6 (Clark–West p = 0.034) |

  At h = 3 in 2023–25, national growth beats the state-applications model by 3.1% (p = 0.042; bootstrap p = 0.012).
- **An independent in-sample check confirms it** (not saved; pooled OLS with state and quarter dummies, errors clustered by quarter, 2006–2019 and 2006–2025):
  - the coefficient on the cross-state mean is 0.30–0.45 (t = 2.4–3.9);
  - the coefficient on the state deviation is 0.02–0.07 (t ≤ 1.84);
  - the correlation between state-specific births growth and state-specific application growth is 0.013 at h = 0 and 0.007 at h = 3.
- **The information in state application counts is national.**

*G2. Births-weighted loss.* Similar to unweighted: at h = 3 in the test window, +1.9% weighted against +1.6% unweighted. The exception is random forest (−5.2% weighted, −0.8% unweighted).

*G3. The BED revision.*

- **The October 28 release** revised the 2025 targets by 0.008 log points on average (at most 0.060) and left 2023–24 unchanged.
- **Against it,** the h = 3 test-window gain is +1.3% (was +1.6%), and the benchmark's RMSE is 0.1791 (was 0.1798).

**What this means for draft v2.**

- **The headline changes.** "The relationship changed after 2020" becomes an episodic description:
  - real but small information before 2020 (larger for the narrower series and for Census's projections);
  - large gains in 2020–21 and losses in 2022;
  - none in 2023–25;
  - a statistically supported lasting change only for corporate applications.
- **The state-level contribution is national.** G1 belongs in the main text. It bears on the novelty claim (state-level forecasting) and on the interpretation of RQ4.
- **The no-change comparison belongs in the main results.** It is part of the pre-specified estimand, and it shows the benchmark is a low bar.
- **Test-window Clark–West significance for the machine-learning models is fragile.**

**Item F (confirmatory): live forecasts from Census's projections.**

- **Scripts:** `src/analysis/make_live_forecasts_pbf.py` and `src/analysis/evaluate_live_forecasts_pbf.py`.
- **Forecast file:** `outputs/live_forecasts/live_forecasts_pbf_2026Q2-Q3.csv`, 612 forecasts, SHA-256 `2fe32076b08657e71cb4cf7ff94ee5515fe6620001822079e8e0da44e4692a3f`.
- **Data:** the same committed processed files as Addendum 3, BFS through September 2026 and BED through 2025Q4, both retrieved 14 October 2026; checked unchanged since commit 9630b2d.
- **The benchmark forecasts reproduce the frozen Addendum 3 file** (maximum difference 1e-16; identical training sizes).
- **Mean forecasts across states**, year-over-year log change × 100:

  | Model | 2026Q2 | 2026Q3 |
  |---|---|---|
  | Benchmark | 2.8 | 2.7 |
  | Projections, h = 0 | 7.3 | 9.1 |
  | Projections, h = 3 | 4.3 | 8.8 |
  | Benchmark, trained without 2020–22 | 0.7 | 0.3 |
  | Projections, h = 0, trained without 2020–22 | 4.1 | 4.7 |
  | Projections, h = 3, trained without 2020–22 | 1.9 | 4.6 |

  For comparison, the frozen all-applications forecasts (full training) are 5.3 and 6.8 at h = 0, and 5.7 and 8.5 at h = 3.
- **Testing the scorer:** it was dry-run on synthetic actual values (output not saved), and run on the 28 October release, where it reports nothing to score yet.
- **Next steps:** the forecasts and the scoring code are committed and tagged `prereg-live-forecasts-pbf-2026q2q3`. Score with the scorer after BLS publishes 2026Q2 (27 January 2027).

**AI-use record:**

- **Who did the work:** Claude (Opus 5.5, via Claude Code) wrote and ran the scripts, checked the results against the audit's independent calculations, and wrote this entry.
- **One exception:** an earlier read-only data check in this working session ran on Claude Fable 5.1, while the session's model was briefly switched; it changed no file.
- **Review status:** not yet reviewed by the author.
