# Phase 3: Exploratory Analysis Findings

*2026-10-15. Development window only (through 2022Q4). The test window (2023Q1 onward) was never loaded for this analysis; see the confirmation printed by [src/analysis/exploratory_analysis.py](../src/analysis/exploratory_analysis.py). The analysis is descriptive and correlational only: no forecast has been evaluated. Not yet reviewed by the author.*

## Gate question

> Is a signal from business applications (Census Business Formation Statistics, BFS) to establishment births (BLS Business Employment Dynamics, BED) plausibly present at all, before committing to a full model-comparison design?

**Yes (gate passed).** Proceeding to Phase 4 (pre-analysis plan).

## What was done

1. Built an integrated quarterly state panel from the cleaned BFS and BED files ([src/cleaning/build_panel.py](../src/cleaning/build_panel.py)): 9,116 rows (53 geographies × 2 seasonal adjustments × ~86 quarters), with an explicit `in_test_window` flag so that data from 2023Q1 onward cannot be used by accident before Phase 4.
2. Computed year-over-year (YoY) log changes, not seasonally adjusted (NSA), for BED establishment births and the four BFS application series.
3. **National-level lag-correlation table** (BA_BA, Census's code for all business applications, leading births by `lag` quarters):

   | lag (quarters) | n | correlation |
   |---|---|---|
   | 0 | 70 | 0.40 |
   | 1 | 69 | 0.52 |
   | 2 | 68 | 0.55 |
   | 3 | 67 | **0.64** |
   | 4 | 66 | 0.38 |

   Correlation rises with the lag, peaks at 3 quarters, then falls off. This is consistent with applications being an early signal that takes time to convert into a counted, operating establishment. Asturias et al. (2024, NBER WP 33224) found the same shape of relationship between applications and national employment, although they used a dynamic factor model on employment, not establishment births, and did not test the lag structure this directly.

4. **Pooled state-level lag-correlation table** (within-state demeaned, so it does not merely pick up level differences across states):

   | lag (quarters) | n | correlation |
   |---|---|---|
   | 0 | 3,570 | 0.22 |
   | 1 | 3,519 | 0.28 |
   | 2 | 3,468 | 0.24 |
   | 3 | 3,417 | 0.26 |
   | 4 | 3,366 | 0.14 |

   Weaker than the national correlation (as expected, because national aggregation smooths out state-level noise), but positive and non-trivial at every lag tested, peaking around 1 and 3 quarters. To this project's knowledge, this is the first direct evidence of the relationship at the state level specifically, which is the gap identified in Phase 1.

5. **Visual check** ([outputs/figures/national_bfs_vs_bed_yoy.png](../outputs/figures/national_bfs_vs_bed_yoy.png)): the clearest confirming pattern is in 2020–2021. Applications (top panel) spike first and sharply in 2020; establishment births (bottom panel) follow with a lag and peak later, after applications had already started to fall. This lead-lag pattern is visible by eye, not just in the correlation table. *(Chart redrawn 2026-10-15: the original overlaid both series on two separate y-axes, a format that can make any two lines look related. It now uses stacked panels on one shared scale, which also shows that the applications spike, about 60%, was larger than the births spike, about 44%.)*

## Data-quality finding: irregular first-quarter spikes ("Q1 lumpiness") in NSA establishment birth counts

A large spike in California's 2012Q1 births (55,505, against a surrounding range of about 30,000–41,000) created a misleading YoY reading of about −65% in 2013Q1. This is not a real decline but a base effect from comparing against an unusually high prior-year quarter ([outputs/figures/state_examples_bfs_vs_bed_yoy.png](../outputs/figures/state_examples_bfs_vs_bed_yoy.png), California panel).

To check whether this was an isolated data error or a broader pattern, all state-quarters with a quarter-over-quarter jump in births of more than 40% were examined (124 in total). **The first quarter (Q1) is disproportionately represented:** 9 of the 15 most-affected year-quarter cells are in Q1 (2006, 2007, 2012, 2013, 2015, 2019, 2020, 2021, 2022). This looks like a real, if irregular, artifact of administrative or registration timing (for example, new-establishment registrations entering the count in batches around the start of the calendar or tax year), not a data error to be corrected. However, the size of the Q1 effect varies from year to year, so it is not a stable seasonal factor, and plain year-over-year differencing does not fully remove it (hence the California 2013Q1 reading).

**Implication for later phases:** this needs to be handled explicitly, not left to YoY differencing. Options to evaluate in Phases 4 and 5:

- Use BLS's own seasonally adjusted (SA) series as a robustness check, or possibly as the primary specification, instead of assuming that NSA year-over-year changes remove the effect on their own.
- Include quarter fixed effects in the panel models to absorb typical seasonal patterns while still allowing state-year deviations to be modeled.
- Consider winsorizing extreme quarter-over-quarter swings, with the choice and threshold stated explicitly and tested for sensitivity.

The anomaly is reported here rather than corrected silently, following the research program's standard that data anomalies are investigated and reported, not smoothed over.

**Follow-up check (2026-10-15): do business applications share the same Q1 pattern?** Yes, more strongly. In BA_BA, 21% of state-Q1 observations show a quarter-over-quarter jump of more than 40%, versus about 0% in Q2 and a smaller share in Q3; this is far more concentrated than the Q1 pattern in births. Of the 41 state-quarters where *both* series jump sharply (by more than 30%) at once, 36 are in Q1. **This raises a risk of confounding:** part of the Phase 3 lagged correlation could reflect both series reacting to a shared calendar-timing effect (plausibly business-registration timing aligned with the tax year) rather than applications forecasting births. The risk is addressed directly in [pre_analysis_plan.md](../pre_analysis_plan.md) §4, through a pooled quarter-of-year indicator in all models as the structural fix (not only an adjustment on the outcome side), rather than being left unaddressed in the correlations above.

## Summary statistics and other outputs

- [outputs/tables/national_lag_correlations.csv](../outputs/tables/national_lag_correlations.csv)
- [outputs/tables/pooled_state_lag_correlations.csv](../outputs/tables/pooled_state_lag_correlations.csv)
- [outputs/tables/panel_summary_stats.csv](../outputs/tables/panel_summary_stats.csv): per-state counts, means and standard deviations for births, deaths and BA_BA

## BDS cross-check (covariate for RQ4; not used in any Phase 3 analysis)

The Census Business Dynamics Statistics (BDS) state × firm-age extraction ([src/cleaning/clean_bds.py](../src/cleaning/clean_bds.py)) gives a mean new-firm share of establishment entry of **61%** for 2010–2019 (66.8% across all state-years, 1978–2023). So roughly 39% of new establishments in 2010–2019 came from existing firms opening another location, close to Decker & Haltiwanger's (2022) figure of about 36%.

*Corrected 2026-10-15.* This section originally reported 77.9%. That figure came from a definitional error: openings by firms too old for Census to date ("left-censored") were excluded from the denominator. The error was corrected before the variable was used in any analysis; see [rq4_findings.md](rq4_findings.md). The variable is used in research question 4 (RQ4).

## What this does not establish

- No forecast has been evaluated. These are in-sample correlations over the full development window, not out-of-sample predictive accuracy.
- The direction of the correlation (applications leading births) is consistent with the hypothesized mechanism, but this analysis does not rule out both series responding to a common economic shock that reaches each through different reporting lags. Predictive value is tested by Phase 5's real-time information-set design, not by this descriptive pass.
- The pooled state correlation is a simple demeaned, pooled statistic, not a formal panel test. The Qu–Timmermann–Zhu and Akgun et al. panel tests selected in Phase 1 are for the forecast-comparison stage, not this exploratory pass.
