# Research Question and Design (current)

*This document is authoritative for the project's design. It is a condensed, living version of [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md), to be revised as the literature review and data acquisition narrow the design. Changes here should be logged in [research_log.md](research_log.md).*

**Status:** Phases 0–5 complete as of 2026-10-15, plus [pre-analysis plan Addendum 1](pre_analysis_plan_addendum_1.md). The pre-analysis plan and its addendum are the authoritative specification; they supersede the design summary below wherever the two differ.

**Where the evidence points (see [literature/phase5_findings.md](literature/phase5_findings.md)):** the predictive relationship is regime-dependent.

- **Before 2020:** modest but real information.
- **2020–21:** large gains.
- **2023–25 (locked test window):** no detectable accuracy gain.

The paper's framing has shifted accordingly. It is no longer "applications are a useful state-level leading indicator". It is now about how stable that relationship is, with the original RQ1 as the vehicle. See [literature/extraction_table.md](literature/extraction_table.md) (Phase 1) and [literature/phase3_findings.md](literature/phase3_findings.md) (Phase 3) for full detail.

## Questions

- **RQ1 (primary, predictive):** Does adding state business-application data (Census BFS) to time-series benchmarks reduce out-of-sample error in nowcasts and short-horizon forecasts of state establishment births (BLS BED)?
- **RQ2:** Which application series carries the signal — all applications (BA), high-propensity (HBA), planned-wage (WBA), or corporate (CBA)?
- **RQ3:** Do ML methods (regularized regression, random forest, gradient boosting) improve on well-specified econometric models (ARDL, bridge equations) in this short, noisy state panel? Are gains concentrated in turbulent periods? **Prior from the literature (weak but relevant): a 2026 conference paper forecasting state unemployment with a similarly short state-quarterly panel found linear regression beat RF/GBM, which overfit. Go in expecting ML may not win here — that would itself be a finding, not a null result to hide.**
- **RQ4 (exploratory):** Is the predictive gain larger in states where more establishment entry comes from genuinely new firms rather than expansions of existing firms (BDS firm-age data)?

**No causal claims.** Applications are an early observable step on the same path as establishment births, not a cause of them. All language is predictive/forecasting language.

## Design summary

| Element | Definition |
|---|---|
| Outcome | State private-sector establishment births (BED), quarterly, primary spec = YoY log change of the NSA series |
| Predictors | BFS state series (BA, HBA, WBA, CBA), NSA; lags of the outcome |
| Unit | State × quarter (50 states + DC) |
| Period | 2004Q3 (BFS start) through latest BED quarter |
| Estimand | Out-of-sample forecast loss (RMSE/MAE) vs. benchmark, by horizon |
| Information set | Real-time: only data that would have been published as of each forecast origin (BFS ~2-week lag; BED ~7-month lag — exact calendar to be confirmed in Phase 2) |

## Forecast-evaluation methods (finalized in Phase 1)

| Need | Method | Why |
|---|---|---|
| Nested-model comparison (benchmark vs. benchmark+BFS) | **Clark & West (2007)**, with **Giacomini & White (2006)** as a robust fallback | Plain Diebold–Mariano (1995) is built for non-nested comparisons; applying it to nested models (as here) is a known misuse flagged by Diebold's own 2015 retrospective |
| Multiple-comparison control across many models × horizons × states | **Hansen, Lunde & Nason (2011) Model Confidence Set** | Standard tool for exactly this setting; better-established than ad hoc FDR corrections in this literature |
| Pooled/clustered significance across the 51-state panel | **Qu, Timmermann & Zhu (2024, IJF)** and/or **Akgun, Pirotte, Urga & Yang (2024, IJF)** | Purpose-built panel forecast-comparison tests, valid under cross-sectional dependence (plausible across states, e.g. by Census region) — found during Phase 1, not in the original plan |
| Mixed-frequency model (monthly BFS → quarterly BED) | **Bridge equations**, not MIDAS | No mature Python MIDAS package exists (R's `midasr` is the real standard; Python options are WIP or narrowly scoped). This is a deliberate scope choice, stated as such in the paper. |

## Data-revision / real-time handling (resolved in Phase 1)

- **BFS has real vintages**, archived on ALFRED (Federal Reserve Bank of St. Louis), state-level, release IDs 443 (monthly/quarterly) and 468 (weekly, back to 2006). Requires a free FRED/ALFRED API key (not yet obtained).
- **BED has no existing vintage archive** — not on ALFRED, not elsewhere found. Phase 2 must choose: (a) hand-construct a vintage history from BLS's archived news releases (`bls.gov/news.release/archives/cewbd_*.htm`) and annual revision notices — real added effort — or (b) run the evaluation on final BED data only and state that limitation plainly (the fallback the original plan already allowed for). **Decision deferred to Phase 2**, once the hand-construction effort is scoped.

## Phase 3 gate: resolved (2026-10-15)

> Is a BFS-applications → BED-establishment-births signal plausibly present at all?

**Yes.** National lag-correlation peaks at 0.64 (3-quarter lag); pooled, within-state-demeaned state-level correlation is positive at every lag tested (0.14–0.28), peaking around 1 and 3 quarters. The 2020–21 episode shows the lead-lag pattern visually: applications spike first, establishment births follow. Full writeup: [literature/phase3_findings.md](literature/phase3_findings.md).

**New design consideration found in Phase 3:** NSA establishment-birth counts show irregular, state-varying Q1 "lumpiness" (a disproportionate share of large quarter-over-quarter jumps cluster in Q1 across many years) — plausibly a registration/administrative-timing artifact, not a stable seasonal factor. Plain YoY differencing does not fully remove it (it produced a misleading ~-65% reading in California 2013Q1, traced to an unusual 2012Q1 spike). **Phase 4/5 must address this explicitly**: evaluate BLS's seasonally adjusted series as a robustness check, consider quarter fixed effects in panel models, and/or test sensitivity to winsorizing extreme QoQ swings.

## Phase 1 gate: resolved

> Does any existing, findable paper forecast state-level BED/QCEW establishment births from state-level BFS data, with an econometric-vs-ML comparison?

**No** — confirmed by a dedicated search. Full reasoning, the closest analogue (Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb, NBER WP 33224 — national-level, dynamic-factor-model only), and the scooping-risk check are in [literature/extraction_table.md](literature/extraction_table.md). **Proceeding to Phase 2.**

Full threat/validity table and phase plan remain in the linked program-level plan document, updated above where Phase 1 changed them.
