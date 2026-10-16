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
- **Decker & Haltiwanger (2022) figure re-checked against the FEDS Note.** Existing firms accounted for about 36% of annual establishment births on average over 2015–2019, in national BED data. The text now states the period and source. The original Phase 3 write-up had described the figure as specific to the pandemic, which was wrong.
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
