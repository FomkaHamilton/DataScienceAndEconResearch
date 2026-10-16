# Research Question and Design (current)

*This document is the project's current design summary. It supersedes the original proposal in [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md), which is kept for reference. Design changes are logged in [research_log.md](research_log.md).*

**Status (2026-10-15):** data acquisition, exploratory analysis, the pre-analysis plan and Addenda 1–4, the primary evaluation, the robustness analyses, and RQ2 and RQ4 are complete. Manuscript draft v1 is in [manuscript/draft_v1.md](manuscript/draft_v1.md). Pre-registered live forecasts for 2026Q1–Q3 ([Addendum 3](pre_analysis_plan_addendum_3.md)) will first be scored when BLS publishes 2026Q1 data on 2026-10-28. The [pre-analysis plan](pre_analysis_plan.md) and its four addenda are the binding specification; they supersede the design summary below wherever the two differ.

**Where the evidence points** (see [literature/phase5_findings.md](literature/phase5_findings.md), [literature/rq2_findings.md](literature/rq2_findings.md) and [literature/rq4_findings.md](literature/rq4_findings.md)): the predictive relationship is regime-dependent.

- **2010–2019:** modest but real predictive information.
- **2020–21:** large gains.
- **2022–25:** no gain; in the locked 2023–2025 test window, the three-quarter-lead gain is +1.6% of the benchmark's mean squared error (95% CI −6.5% to +9.7%), and machine-learning models do no better.
- **Inference:** naive pooled tests overstate significance relative to tests that allow for dependence across states and quarters.
- **RQ2:** the narrower employer-intent series predicted better than all applications before 2020, but not after.
- **RQ4 (exploratory):** before 2020, same-quarter gains were larger in states with a higher new-firm share of establishment entry (Spearman ρ = 0.37, Holm-adjusted p = 0.014).

The paper's framing changed accordingly. It no longer argues that applications are a useful state-level leading indicator; it asks how stable that relationship is, with the original RQ1 as the vehicle. See [literature/extraction_table.md](literature/extraction_table.md) (Phase 1) and [literature/phase3_findings.md](literature/phase3_findings.md) (Phase 3) for earlier detail.

## Questions

- **RQ1 (primary, predictive):** Does adding state business-application data (Census BFS) to time-series benchmarks reduce out-of-sample error in nowcasts and short-horizon forecasts of state establishment births (BLS BED)?
- **RQ2:** Which application series carries the signal: all applications (BA), high-propensity applications (HBA), applications with planned wages (WBA) or corporate applications (CBA)?
- **RQ3:** Do ML methods (regularized regression, random forest, gradient boosting) improve on well-specified econometric models (ARDL, bridge equations) in this short, noisy state panel? Are gains concentrated in turbulent periods? Prior from the literature (weak but relevant): a 2026 conference paper forecasting state unemployment with a similarly short state-quarterly panel found that linear regression outperformed random forests and gradient boosting, which overfit. The working expectation was therefore that ML might not outperform here; that outcome would be reported as a finding, not treated as a null result to set aside.
- **RQ4 (exploratory):** Is the predictive gain larger in states where more establishment entry comes from new firms rather than from expansions of existing firms (BDS firm-age data)?

**No causal claims.** Applications are an early observable step on the same path as establishment births, not a cause of them. All language is predictive.

## Design summary

| Element | Definition |
|---|---|
| Outcome | State private-sector establishment births (BED), quarterly; primary specification = year-over-year (YoY) log change of the not seasonally adjusted (NSA) series |
| Predictors | BFS state series (BA, HBA, WBA, CBA), NSA; lags of the outcome |
| Unit | State × quarter (50 states and DC) |
| Period | 2004Q3 (BFS start) through the latest BED quarter |
| Estimand | Out-of-sample forecast loss (RMSE/MAE) relative to the benchmark, by horizon |
| Information set | Pseudo-real-time: at each forecast origin, only data that would have been published by then (BFS about 2 weeks after month end; BED about 7 months after quarter end), using final-vintage values for both series ([pre-analysis plan](pre_analysis_plan.md) §3) |

## Forecast-evaluation methods (chosen in Phase 1)

| Need | Method | Why |
|---|---|---|
| Nested-model comparison (benchmark vs. benchmark + BFS) | Clark & West (2007), with Giacomini & White (2006) as a fallback that is robust to misspecification | Plain Diebold–Mariano (1995) is designed for non-nested comparisons; applying it to nested models, as here, is a known misuse noted in Diebold's own 2015 retrospective |
| Multiple-comparison control across models × horizons × states | Hansen, Lunde & Nason (2011) Model Confidence Set | Standard tool for this setting; better established in this literature than ad hoc FDR corrections |
| Pooled or clustered significance across the 51-state panel | Qu, Timmermann & Zhu (2024, *IJF*) and/or Akgun, Pirotte, Urga & Yang (2024, *IJF*) | Panel forecast-comparison tests designed for this purpose, valid under cross-sectional dependence (plausible across states, e.g. by Census region); found during Phase 1, not in the original plan |
| Mixed-frequency model (monthly BFS → quarterly BED) | Bridge equations, not MIDAS | No mature Python MIDAS package exists (R's `midasr` is the standard implementation; the Python options are works in progress or narrowly scoped). This is a deliberate scope choice, stated as such in the paper. |

**Deviations in implementation** (disclosed in the [Phase 5 findings](literature/phase5_findings.md) and the manuscript):

- The Model Confidence Set and the Qu–Timmermann–Zhu / Akgun et al. panel tests were not implemented, because no vetted reference implementation was available. Holm–Bonferroni correction and cluster-robust tests (clustered by state, by quarter and two-way, with a wild cluster bootstrap) were used instead.
- BFS enters the models at quarterly frequency, with the full quarter treated as available shortly after it ends, so the bridge-equation and ARDL specifications coincide (documented in `src/cleaning/build_forecast_dataset.py`).
- The seasonal naive benchmark listed in the pre-analysis plan was not estimated; with a year-over-year target it amounts to forecasting no change.
- The Giacomini & White (2006) fallback was not implemented. For the tree-based models, only the unadjusted accuracy comparison is interpreted, because the Clark–West adjustment does not suit them.

## Data revisions and real-time handling

- **BFS has real-time vintages**, archived on ALFRED (Federal Reserve Bank of St. Louis), at state level: release IDs 443 (monthly/quarterly) and 468 (weekly, back to 2006). Access requires a free FRED/ALFRED API key, which had not been obtained when the pre-analysis plan was written.
- **BED has no vintage archive** (not on ALFRED, and none found elsewhere). Phase 1 left two options: hand-construct a vintage history from BLS's archived news releases (`bls.gov/news.release/archives/cewbd_*.htm`) and annual revision notices, or evaluate on final BED data and state the limitation.
- **Resolved in the pre-analysis plan (§3):** both series are used at final-vintage values, simulated as if released on the approximate lags above. Using real BFS vintages with final BED data would be inconsistent. The paper states this as a limitation, and a sensitivity check with real-time BFS vintages is noted as a possible extension.

## Phase 3 gate: resolved (2026-10-15)

> Is a BFS-applications → BED-establishment-births signal plausibly present at all?

**Yes.** The national lag correlation peaks at 0.64 (3-quarter lag). The pooled, within-state-demeaned state-level correlation is positive at every lag tested (0.14–0.28), peaking at around 1 and 3 quarters. The 2020–21 episode shows the lead-lag pattern visually: applications spike first, and establishment births follow. Full write-up: [literature/phase3_findings.md](literature/phase3_findings.md).

**New design consideration found in Phase 3:** NSA establishment-birth counts show irregular, state-varying spikes in the first quarter ("Q1 lumpiness"): a disproportionate share of large quarter-over-quarter jumps falls in Q1, across many years. This is plausibly a registration or administrative-timing artifact rather than a stable seasonal factor. Plain YoY differencing does not fully remove it; it produced a misleading reading of about −65% for California in 2013Q1, traced to an unusual spike in 2012Q1. Phase 3 concluded that Phases 4 and 5 must address this explicitly. **Resolved in the pre-analysis plan (§4):** all models include quarter-of-year indicators, and the seasonally adjusted series and winsorizing of extreme changes were run as robustness checks under Addendum 1.

## Phase 1 gate: resolved

> Does any existing, findable paper forecast state-level BED/QCEW establishment births from state-level BFS data, with an econometric-vs-ML comparison?

**No**, confirmed by a dedicated search. The full reasoning, the closest analogue (Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb, NBER WP 33224, which is national-level and uses only a dynamic factor model) and the scooping-risk check are in [literature/extraction_table.md](literature/extraction_table.md). The project then proceeded to Phase 2.

The full threats-to-validity table and the original phase plan are in the program-level plan linked above; the changes made since are recorded in this document, the pre-analysis plan and its addenda.
