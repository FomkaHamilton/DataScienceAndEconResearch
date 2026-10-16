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

## 2026-10-15: Phase 2 continued — BDS acquisition; Phase 3 exploratory analysis (complete)

**BDS:** `src/acquisition/fetch_bds.py` + `src/cleaning/clean_bds.py` pull the state × firm-age cross-tab (no API key, direct CSV) and compute a state-year "new-firm share of establishment entry" for RQ4. Mean 77.9% (std 8.8%) across state-years — same direction as Decker & Haltiwanger's ~36%-from-existing-firms finding, though the two aren't directly comparable (different period, national vs. state-year averaging). Parked for Phase 5; not yet used in any model.

**Phase 3 gate: PASS.** Built the integrated quarterly panel (`src/cleaning/build_panel.py`, 9,116 rows, explicit `in_test_window` flag so 2023Q1+ can't be accidentally used) and ran exploratory correlations (`src/analysis/exploratory_analysis.py`, development window only — the script prints a loud confirmation that test-window rows were dropped before anything else runs).

- National lag-correlation (BA_BA applications leading births): peaks at 0.64 at a 3-quarter lag.
- Pooled, within-state-demeaned state-level correlation: positive at every lag (0.14–0.28), peaking around 1 and 3 quarters — the first evidence (that this project is aware of) that the relationship holds at the state level, which is the gap Phase 1 identified.
- Visual confirmation: 2020–21 shows applications spiking first, establishment births following with a lag.

**New finding requiring a design decision:** NSA establishment-birth counts show irregular, state-varying Q1 "lumpiness" — a disproportionate share of large quarter-over-quarter jumps cluster in Q1 across many years (2006, 2007, 2012, 2013, 2015, 2019–2022). Traced a misleading ~-65% YoY reading in California 2013Q1 to this (base effect off an unusually high 2012Q1, not a real decline). Plain YoY differencing does not fully remove it since the spike magnitude varies year to year. **Phase 4 must address this**: evaluate BLS's seasonally adjusted series, consider quarter fixed effects, and/or test sensitivity to winsorizing. Full writeup: [literature/phase3_findings.md](literature/phase3_findings.md).

**AI-use record:** Claude (Sonnet 5) wrote and ran all Phase 2b/3 scripts, generated the figures/tables, and investigated the CA anomaly (checked whether it was isolated or systematic before writing it up) rather than either ignoring it or over-claiming a cause. Not yet reviewed by the author.

**Next:** Phase 4 — pre-analysis plan (lock the test window, finalize model list, specify the Q1-lumpiness handling, commit before any out-of-sample evaluation).

## 2026-10-15: Phase 4 — pre-analysis plan (committed)

Before finalizing the Q1-lumpiness handling, checked whether BFS applications show the same pattern as BED births (they do, more strongly: 21% of state-Q1 observations jump >40% QoQ vs. ~0% in other quarters; 36 of 41 simultaneous large jumps in both series are in Q1). This is a genuine confound risk — part of the Phase 3 correlation could reflect both series reacting to the same calendar-timing effect, not a real predictive relationship. Reported this to the author along with the handling options (quarter FE, switch to SA series, winsorizing, or a combination), with explicit publication-impact reasoning for each (notably: switching to SA as primary would reintroduce the look-ahead bias problem the NSA choice was meant to avoid). Author chose the combination approach.

**Committed:** [pre_analysis_plan.md](pre_analysis_plan.md) — test window locked at 2023Q1–2025Q4 (births); information-set treatment (pseudo-real-time on final-vintage data, both series, with the BED-vintage-unavailability and BFS-vintage-deferred decisions stated as limitations); seasonality handling (quarter-of-year indicator in all models as the structural fix targeting the newly-found confound; BLS/Census SA series as a robustness line only, explicitly not valid for real-time claims; winsorizing at development-window-only 1st/99th percentiles as a disclosed, pre-specified sensitivity check — thresholds fixed now, not tuned later); full model list; evaluation design (Clark-West/Giacomini-White, Hansen-Lunde-Nason MCS, Qu-Timmermann-Zhu/Akgun panel tests); and primary-vs-secondary-vs-exploratory comparisons specified in advance to prevent fishing.

**AI-use record:** Claude (Sonnet 5) ran the BFS-side diagnostic, presented the options with publication-impact tradeoffs, and drafted the committed plan per the author's chosen approach. Author made the actual decision (AskUserQuestion). Not yet reviewed by the author in full detail.

**Next:** Phase 5 — baseline + full model set, executed exactly per the committed plan.

## 2026-10-15: Phase 5 — model evaluation (major finding, paused for author input)

Built the real-time forecast dataset and ran all pre-specified models (benchmark AR, benchmark+BFS per horizon h=0-4, ElasticNet, RF, GBM, combination) with genuine expanding-window re-estimation against the locked test window (2023Q1-2025Q4), exactly per [pre_analysis_plan.md](pre_analysis_plan.md).

**Headline finding: the apparent signal does not survive correcting for the panel's dependence structure.** Naive pooled Clark-West tests showed BFS significantly improving forecasts at h=1-4 (p as low as 0.0003 at h=3) and RF beating the benchmark (p=0.00006). But 612 "observations" (51 states x 12 quarters) are not 612 independent data points -- a two-way clustered test (Cameron-Gelbach-Miller, clustering by state and by quarter simultaneously) finds **no significant improvement at any horizon, for any model** (p=0.26-0.96 across horizons; RF's point estimate actually turns slightly negative under clustering).

Follow-up diagnostic: the lag-3 correlation that drove Phase 3's optimistic read drops from 0.26 to 0.10 when the 2020-21 pandemic business-formation surge is excluded from the development window, and is 0.43 within 2020-21 alone. The test window (2023-2025) has no comparable shock, consistent with the relationship not generalizing out of that one episode.

**Disclosed deviations from the PAP** (per its own Sec. 8 rule): Hansen-Lunde-Nason MCS and the Qu-Timmermann-Zhu/Akgun panel tests were not implemented from scratch (no vetted reference implementation available; risk of an unverifiable bespoke bug). Substituted with Holm-Bonferroni (for MCS) and cluster-robust/two-way-clustered tests (for the panel tests) -- standard, well-understood methods serving the same purpose. The cluster-robust substitution is the one that mattered: it directly overturned the naive result, which is itself evidence the Phase 1 instinct to look for those specialized tests was the right one.

Full writeup: [literature/phase5_findings.md](literature/phase5_findings.md). Paused here -- this is a genuine pivot point for the paper's direction, not a routine implementation detail, so it goes to the author before any further phase work.

**AI-use record:** Claude (Sonnet 5) built the forecast infrastructure, ran all models, caught the naive-vs-clustered divergence by checking rather than accepting the first (favorable-looking) result, and ran the COVID-episode diagnostic to explain it. Not yet reviewed by the author.

## 2026-10-15: Phase 5 corrected + pre-analysis plan Addendum 1 (complete)

The author chose to write up the Phase 5 result (option 1) and approved three follow-up analyses that decide whether it is a publishable paper.

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
  - I told the author the stronger version; the corrected version is in the findings doc.

Regression forecasts are unchanged; all 612 match the first run exactly. The new inference code reproduced every original naive and two-way number exactly before being trusted.

**Results** (full write-up: [literature/phase5_findings.md](literature/phase5_findings.md)):

- **Locked test window:** no detectable accuracy gain. 3-quarter lead +1.6% of benchmark MSE (95% CI −6.5% to +9.7%); best ML (elastic net) +2.3%. The data rule out gains above about +2% at the same-quarter lead and about +10% at the 3-quarter lead, but cannot rule out modest gains.
- **Robust** to the seasonally adjusted series and to winsorizing.
- **Over time, the relationship is regime-dependent:**
  - 2010–19: modest real information (robust information test p ≈ 0.004 at h=3), accuracy gains of about 1–4%, positive in about two-thirds of states.
  - 2020–21: large gains, 11–20% at leads 0–3, in 80–92% of states.
  - 2022–25: no gain or slight losses at leads 0–3.
- **The estimated weight on applications roughly doubled after the pandemic entered the training data.** One possible explanation is that post-pandemic models over-weight applications. That is a hypothesis only: per the addendum, no fix is tested on the locked window.
- **Against the addendum's pre-stated rules:** partly supported (large pandemic gains; small pre-2020 accuracy gains), partly undercut (real pre-2020 information), plus an unanticipated post-pandemic deterioration. The findings doc states this mixed outcome rather than forcing it into one bucket.

**Open items before drafting:**

- RQ2 (which application series carries the signal) is pre-specified and not yet run.
- RQ4 (BDS new-firm share) is exploratory and not yet run.
- Citations for the two-way clustering and wild cluster bootstrap methods are not yet verified.
- The Phase 3 national chart uses two y-axes (a charting anti-pattern) and needs redrawing before any manuscript use.
- Reproducibility audit (Phase 8).

**AI-use record:** Claude (Opus 5.5) wrote the addendum and the analysis code, found and fixed the three errors, ran everything, and wrote the findings. Not yet reviewed by the author.

## 2026-10-15: RQ2 (Addendum 2), chart redraw, reproducibility tooling

The author approved four items: RQ2, citation verification, redrawing the dual-axis chart, and a reproducibility audit.

**RQ2: which application series carries the signal.** [Addendum 2](pre_analysis_plan_addendum_2.md) (commit d07a3b4) was committed before running. It fixed in advance:

- the Holm family;
- the "composition" hypothesis — that the post-2020 breakdown comes from applications that rarely become employers;
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
- **One coding slip, caught by that check:** a column-name collision in the check itself. Fixed and re-run.

**Charts.** Redrew the Phase 3 national chart, which had two y-axes, as stacked panels on one shared scale. Recolored the state-example chart with a validated palette (colorblind-separation and contrast checks pass). The Phase 3 tables regenerated byte-identical.

**Reproducibility tooling.**

- Pinned all package versions in `requirements.txt`. The file was previously unpinned, so a later install could have changed the ML results.
- Moved Jupyter to `requirements-notebooks.txt`.
- Added `replication/run_all.py`, which rebuilds every committed table and figure in one command.
- Added `replication/verify_outputs.py`, which compares regenerated outputs against git HEAD.
- Added SHA-256 checksums of the raw files to `data/MANIFEST.md`.

**Fresh-clone audit: passed.**

- **Setup:** cloned from GitHub at commit a131fb8 into an empty folder, with a new virtual environment installed from the pinned `requirements.txt` (Python 3.12.10).
- **Pipeline:** `replication/run_all.py` ran end to end in 4.1 minutes.
- **Consistency checks:** both internal checks passed — the over-time and RQ2 forecasts match the primary forecasts exactly.
- **Output comparison:** `replication/verify_outputs.py` checked all 31 committed tables and 6 figures and found 0 problems.
  - The largest numeric difference anywhere was 1.1e-14. That is last-digit floating-point variation from multi-threaded arithmetic, not a substantive difference.
  - The ML tuning chose identical settings.
- **Practical notes:**
  - The first attempt failed because the session's scratch folder path exceeded Windows' 260-character limit inside `.git` and `.venv`. The audit was re-run in a short temporary folder, which was deleted afterwards.
  - Anyone reproducing this on Windows should clone to a short path.

## 2026-10-15: Pre-registered live forecasts (Addendum 3) and RQ4 (Addendum 4)

The author approved this order: live forecasts first (they have a deadline), then a small RQ4, then drafting.

### Live forecasts (Addendum 3)

[Addendum 3](pre_analysis_plan_addendum_3.md) was committed together with the forecasts in commit 7a36fe1, tagged `prereg-live-forecasts-2026`. BLS publishes 2026Q1 on October 28, so the commit precedes any 2026 establishment-birth data.

**What was forecast:**

- 2,448 forecasts: 51 states × 2026Q1–Q3 × 16 model variants.
- The variants are the benchmark, all applications at leads 0–4, and high-propensity applications at leads 0 and 3.
- Each variant is run twice: trained on all data, and trained without 2020–22.
- Before forecasting, the rebuilt features were checked against the Phase 5 forecast data and matched exactly on all 4,386 rows.

**Safeguards:**

- File SHA-256 `8e0751c9…841fc`.
- A `.gitattributes` rule stores the file byte-for-byte, so the hash is the same on every platform. Without it, git's line-ending conversion would have changed the hash on Mac and Linux checkouts. The hash of the stored copy was confirmed after pushing.
- The forecasting script refuses to overwrite the file.

**Scoring:**

- The scoring script was committed at the same time and tested on synthetic data only; a hand calculation matched its output.
- **H1** (the paper's claim): applications still don't help.
- **H2:** training without 2020–22 helps.
- **Expected differences between variants:** models trained on all data forecast 4–9% year-over-year growth; the 2020–22-excluded models and the benchmark forecast about 1–3%.

**Pending author decision:** public timestamping. The repo is private, so outsiders can't verify when the forecasts were made.

### RQ4 (Addendum 4)

[Addendum 4](pre_analysis_plan_addendum_4.md) was committed (4fd546f) before running.

**Correction before running.** The Phase 2 new-firm share had excluded firms too old for Census to date ("left-censored") from its denominator. That overstated the share:

| | Before | After |
|---|---|---|
| 2010–19 mean | 69% | 61% |
| All-years mean | 77.9% | 66.8% |

The corrected figure implies about 39% of new establishments come from existing firms, close to Decker & Haltiwanger's ~36%. Fixed in `clean_bds.py` before any use. The Phase 3 findings and the data manifest are corrected; the Phase 2 log entry above is left as originally written.

**Results** ([literature/rq4_findings.md](literature/rq4_findings.md)):

- **Same-quarter lead, pre-2020:** forecasting gains are larger in states where more entry comes from brand-new firms (Spearman ρ = 0.37, Holm p = 0.014). Under the pre-registered reading, that is consistent with the new-firm mechanism.
- **3-quarter lead:** ρ = 0.11, inconclusive.
- **After 2020:** no relationship.
- **Robustness:** a moderate tendency, not driven by any single state.

### Pipeline

`make_live_forecasts.py` (which checks the frozen file) and `run_rq4.py` are added to `replication/run_all.py`.

**AI-use record:** Claude (Opus 5.5) wrote Addenda 3 and 4, the forecast, scoring and RQ4 code, and the findings; found and fixed the new-firm-share definition and the line-ending risk to the forecast hash. Not yet reviewed by the author.

**Pipeline re-run.** A full re-run with all 8 steps took 4.3 minutes and reproduced all 34 tables and 7 figures, with 0 problems. The live-forecast step confirmed the frozen file regenerates exactly.

Ten tables differed from the committed copies only in the 15th–16th significant digit, because the random forest sums trees in parallel. The committed copies were restored, and the README now notes this.

## 2026-10-15: Manuscript draft v1

Wrote [manuscript/draft_v1.md](manuscript/draft_v1.md): about 4,500 words of main text, 5 tables, 3 figures, references, a data/code statement, an AI-use statement, and a pre-registration and deviations section. It uses the *Journal of Forecasting* format, the plan's primary target.

**Framing:** the relationship between applications and establishment births is regime-dependent and changed after 2020. That change is not explained by application composition. Naive pooled tests overstate significance in state panels. The live-forecast test is Section 8.

**Checks on the draft:**

- Every number was checked against the committed output tables. That check found and fixed one overstatement ("every lead" corrected to "leads 0–3") and one imprecise claim about the four-quarter contribution.
- A false description of the repo as "public-on-request" was removed.
- An unsupported sentence about policy demand was replaced with a factual one.

**Open items before submission, marked [VERIFY] in the draft:**

- reference author initials;
- the Decker & Haltiwanger (2023) page range;
- one DOI;
- JEL codes;
- the journal's current AI-disclosure wording;
- the repository's public URL.

**AI-use record:** drafted by Claude (Opus 5.5) from the project's findings documents. Not yet reviewed by the author; the author's revision is the next step.

**AI-use record:** Claude (Opus 5.5) wrote Addendum 2, the RQ2 code, the reproducibility tooling and the findings; redrew the charts; and ran everything. Not yet reviewed by the author.

## 2026-10-15: Manuscript figures

The author asked whether the draft needed more figures. Claude recommended a small set, each carrying one claim, and the author approved building them. The figures are in [manuscript/figures/](manuscript/figures/README.md), with draft captions and proposed placements. None has been placed in the draft yet; that waits for the author's review.

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

Summed to a national total, the levels are lower and closer together (all-data applications models 1.6–7.1; benchmark 0.4–4.2), because large states forecast lower growth.

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

**AI-use record:** Claude (Opus 5.5) proposed the figure set, wrote the figure script, captions and review notes, found the draft's coefficient-range error and the 2025 divergence, and wrote this entry. Not yet reviewed by the author.

## 2026-10-15: Figures placed in the draft

The author approved the proposed placements and kept Figure 3 as its own figure. The author also delegated the public-timestamp decision ("go with your best judgement"), then explicitly authorized posting.

**Draft changes:**

- All seven figures placed, with captions.
- Tables renumbered:
  - main text: 1 (test window), 2 (by period), 3 (robustness);
  - appendix: A1 (information-test p-values, formerly Table 2) and A2 (accuracy by series, formerly Table 4).
- The paragraph on the weight given to applications moved from Section 6.4 to 6.5, so that figure numbers follow the order of first mention.
- Section 6.2 now also notes that naive inference overstates in the accuracy comparison too. The naive test says same-quarter applications made forecasts significantly worse (p = 0.03); the robust test does not (two-way p = 0.26). Both numbers come from the committed `phase5_comparisons.csv`.
- Fixed a wrong cross-reference: the seasonally adjusted check is in Section 6.7, not 6.6.
- Section 8:
  - corrected "the commit carries the hash" (the SHA-256 is the forecast file's);
  - added Figure 7;
  - added the 2025 composition observation recorded in the entry above.

**Reproducibility:** a full `run_all.py` re-run (9 steps, the figure step included) passed `verify_outputs.py`: 34 tables and 21 figure files, 0 problems. The manuscript figures were byte-identical. Ten tables differed only in the 15th–16th significant digit (random-forest parallel summation) and were restored to the committed copies.

**Public timestamp: not yet posted.** A hash-only public gist was prepared. It contains the forecast file's SHA-256, commit 7a36fe1 (the tag `prereg-live-forecasts-2026`) and commit 9fb1904, with no project name, paths, data or results. Claude Code's permission system blocked the upload twice, the second time after the author's explicit authorization. The author needs to post it, or add a permission rule. Section 8 carries a [VERIFY] placeholder for the link. Deadline: before BLS publishes 2026Q1 on 2026-10-28.

**AI-use record:** Claude (Opus 5.5) placed the figures, edited the draft text and wrote this entry. Not yet reviewed by the author.
