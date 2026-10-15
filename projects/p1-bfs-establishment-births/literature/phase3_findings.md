# Phase 3 — Exploratory Analysis Findings

*2026-10-15. Development window only (through 2022Q4) — the test window (2023Q1 onward) was never loaded for this analysis; see the loud confirmation printed by [src/analysis/exploratory_analysis.py](../src/analysis/exploratory_analysis.py). This is descriptive/correlational only — no forecast has been evaluated. Not yet reviewed by the author.*

## Gate question

> Is a BFS-applications → BED-establishment-births signal plausibly present at all, before committing to a full model-comparison design?

**Yes — PASS.** Proceeding to Phase 4 (pre-analysis plan).

## What was done

1. Built an integrated quarterly state panel from the cleaned BFS and BED files ([src/cleaning/build_panel.py](../src/cleaning/build_panel.py)) — 9,116 rows (53 geographies × 2 seasonal adjustments × ~86 quarters), with an explicit `in_test_window` flag so 2023Q1+ can never be accidentally used before Phase 4.
2. Computed year-over-year log changes (NSA) for BED establishment births and the four BFS application series.
3. **National-level lag-correlation table** (BA_BA applications leading births by `lag` quarters):

   | lag (quarters) | n | correlation |
   |---|---|---|
   | 0 | 70 | 0.40 |
   | 1 | 69 | 0.52 |
   | 2 | 68 | 0.55 |
   | 3 | 67 | **0.64** |
   | 4 | 66 | 0.38 |

   Correlation rises with the lag and peaks at 3 quarters, then falls off. This is consistent with applications being an early signal that takes time to convert into a counted, operating establishment — the same shape of relationship Asturias et al. (2024, NBER WP 33224) found between applications and national employment (though they used a dynamic factor model on employment, not establishment births, and did not test lag structure this directly).

4. **Pooled state-level lag-correlation table** (within-state demeaned, so this isn't just picking up level differences across states):

   | lag (quarters) | n | correlation |
   |---|---|---|
   | 0 | 3,570 | 0.22 |
   | 1 | 3,519 | 0.28 |
   | 2 | 3,468 | 0.24 |
   | 3 | 3,417 | 0.26 |
   | 4 | 3,366 | 0.14 |

   Weaker than the national correlation (expected — national aggregation smooths out state-level noise), but positive and non-trivial at every lag tested, peaking around 1 and 3 quarters. This is the first direct evidence (that this project is aware of) of the relationship holding at the state level specifically — the gap identified in Phase 1.

5. **Visual check** ([outputs/figures/national_bfs_vs_bed_yoy.png](../outputs/figures/national_bfs_vs_bed_yoy.png)): the clearest confirming pattern is 2020–2021 — applications (top panel) spike first and sharply in 2020, establishment births (bottom panel) follow with a lag and peak later, after applications had already started to come back down. This lead-lag pattern is visible by eye, not just in the correlation table. *(Chart redrawn 2026-10-15: the original overlaid both series on two separate y-axes, a format that can make any two lines look related. It now uses stacked panels on one shared scale, which also shows the applications spike, about 60%, was larger than the births spike, about 44%.)*

## Data-quality finding: Q1 "lumpiness" in NSA establishment birth counts

A large, state-varying spike in California's 2012Q1 births (55,505, vs. a surrounding ~30,000–41,000 range) created a misleading ~-65% YoY reading in 2013Q1 — not a real decline, a base-effect artifact of comparing against an unusually high prior-year quarter ([outputs/figures/state_examples_bfs_vs_bed_yoy.png](../outputs/figures/state_examples_bfs_vs_bed_yoy.png), CA panel).

Checking whether this was an isolated data error or a broader pattern: across all state-quarters with a >40% quarter-over-quarter jump in births (124 total), **Q1 is disproportionately represented** — 9 of the 15 most-affected year/quarter cells are Q1 (2006, 2007, 2012, 2013, 2015, 2019, 2020, 2021, 2022). This looks like a genuine, if irregular, administrative/registration-timing artifact (e.g., new-establishment registrations clearing into the count in batches around the start of the calendar/tax year), not a data error to be corrected — but the magnitude of the Q1 effect varies year to year, so it is **not a stable seasonal factor**, and plain year-over-year differencing does not fully remove it (hence the artifact in CA 2013Q1).

**Implication for later phases:** this needs to be handled explicitly, not silently absorbed by YoY differencing. Options to evaluate in Phase 4/5:
- Use BLS's own seasonally adjusted (SA) series as a robustness check or possibly primary spec, instead of assuming NSA YoY cleans this up on its own.
- Include quarter fixed effects in the panel models to absorb typical seasonal patterns while still letting state-year deviations be modeled.
- Consider winsorizing extreme quarter-over-quarter swings, with the choice and threshold stated explicitly and tested for sensitivity.

This is flagged here rather than fixed silently, per the program's standard: an anomaly in the data gets investigated and reported, not quietly smoothed over.

**Follow-up check (2026-10-15): does BFS share the same Q1 pattern?** Yes, more strongly. 21% of state-Q1 observations in BA_BA (business applications) show a >40% quarter-over-quarter jump, versus ~0% in Q2 and a smaller share in Q3 — far more concentrated than births' own Q1 pattern. Of the 41 state-quarters where *both* series jump sharply (>30%) at once, 36 are in Q1. **This raises a genuine confound risk:** part of the Phase 3 lagged correlation could reflect both series reacting to a shared calendar-timing effect (plausibly tax-year-aligned business registration timing), not applications genuinely forecasting births. This is addressed directly in [pre_analysis_plan.md](../pre_analysis_plan.md) §4 (pooled quarter-of-year indicator in all models, as the structural fix, not just an outcome-side cleanup) rather than left as an unaddressed risk in the correlation numbers above.

## Summary stats and other outputs

- [outputs/tables/national_lag_correlations.csv](../outputs/tables/national_lag_correlations.csv)
- [outputs/tables/pooled_state_lag_correlations.csv](../outputs/tables/pooled_state_lag_correlations.csv)
- [outputs/tables/panel_summary_stats.csv](../outputs/tables/panel_summary_stats.csv) — per-state counts/means/std for births, deaths, BA_BA

## BDS cross-check (RQ4 covariate, not yet used in a model)

The BDS state × firm-age extraction ([src/cleaning/clean_bds.py](../src/cleaning/clean_bds.py)) gives a mean new-firm share of establishment entry of **77.9%** (std 8.8%) across state-years, i.e. roughly 22% of new establishments come from already-existing firms opening another location, not brand-new firms. This is the same direction as Decker & Haltiwanger's (2022) finding of ~36% existing-firm share nationally during the COVID surge specifically — the gap between 22% (this project's long-run state-year average) and 36% (their COVID-specific national figure) is plausible given the different time periods and the national-vs-state-year averaging, but the two numbers are not directly comparable and this should not be overstated. This variable is parked for RQ4 use in Phase 5; it has not been merged into the forecasting panel or tested against anything yet.

## What this does NOT establish

- No forecast has been evaluated. These are in-sample, full-development-window correlations, not out-of-sample predictive accuracy.
- Correlation direction (applications leading births) is consistent with the hypothesized mechanism, but this analysis does not rule out both series simply responding to a common underlying economic shock contemporaneously filtered through different reporting lags. Phase 5's real-time information-set design is what will actually test predictive value, not this descriptive pass.
- The pooled state correlation is a simple demeaned-pooled statistic, not a formal panel test. The Qu-Timmermann-Zhu / Akgun et al. panel tests selected in Phase 1 are for the actual forecast-comparison stage, not this exploratory pass.
