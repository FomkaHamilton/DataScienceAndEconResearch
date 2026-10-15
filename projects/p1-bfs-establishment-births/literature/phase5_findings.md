# Phase 5 — Model Evaluation Findings

*2026-10-15. Test window (2023Q1–2025Q4) evaluated for the first time, exactly per [pre_analysis_plan.md](../pre_analysis_plan.md). Not yet reviewed by the author.*

## Headline finding

**The apparent predictive signal does not survive proper statistical treatment of the panel's dependence structure.** A naive pooled test suggests BFS applications significantly improve forecasts of BED establishment births. A correctly clustered version of the same test — accounting for the fact that 612 "observations" (51 states × 12 quarters) are not 612 independent data points — finds **no statistically significant improvement at any horizon, for either the econometric or the machine-learning models.**

A follow-up check traces much of the apparent signal to a single historical episode: the 2020–21 pandemic business-formation surge. Excluding those two years, the in-sample correlation between applications and births **falls by more than half** (lag-3 correlation: 0.26 → 0.10). The test window (2023–2025) contains no comparable shock, which is consistent with the predictive relationship not generalizing out-of-sample.

## What was run

Per the committed plan: pooled panel models (benchmark AR, benchmark+BFS at each horizon h=0–4, ElasticNet, Random Forest, Gradient Boosting, an equal-weight combination), all with quarter-of-target and state fixed effects/features, fit with genuine expanding-window re-estimation, hyperparameters tuned only on the development window, tested against the locked 2023Q1–2025Q4 window.

### Model performance (RMSE/MAE, pooled across the test window)

| Model | RMSE | MAE |
|---|---|---|
| Benchmark (AR only) | 0.1798 | 0.1252 |
| Econometric, BFS lag 3 | 0.1784 | 0.1262 |
| Random Forest | 0.1802 | 0.1241 |
| Gradient Boosting | 0.1796 | 0.1218 |
| Equal-weight combination | **0.1759** | **0.1218** |

Differences are small in absolute terms across the board — none of these look like a dramatic win even before formal testing.

### Naive (uncorrected) Clark & West test — what Phase 3's design anticipated

| Horizon | t-stat | p-value (one-sided) |
|---|---|---|
| 0 | 0.08 | 0.47 |
| 1 | 2.25 | 0.012 |
| 2 | 2.55 | 0.005 |
| 3 | 3.46 | **0.0003** |
| 4 | 2.42 | 0.008 |

Taken at face value, this would say BFS significantly helps at every horizon except the nowcast, peaking at h=3 — matching Phase 3's exploratory correlation almost exactly. **This table is misleading on its own; see below.**

### Cluster-robust and two-way-clustered test — the honest version

Clark & West (and the naive pooled approach generally) assumes something close to 612 independent data points. They are not: a given state's errors are correlated across its own 12 test quarters, and all 51 states share common shocks within the same quarter. Clustering for each of those separately, and then both at once (Cameron–Gelbach–Miller two-way clustering):

| Horizon | Two-way clustered p-value |
|---|---|
| 0 | 0.26 |
| 1 | 0.81 |
| 2 | 0.96 |
| 3 | 0.70 |
| 4 | 0.82 |

**None are close to significant.** The effective sample size here is much closer to 12 (independent quarters) than 612. The same pattern holds for Random Forest vs. the benchmark (naive p = 0.00006; two-way clustered p = 0.94, and the point estimate of the improvement is actually *negative* — RF did very slightly worse than the simple benchmark on average).

Full tables: [outputs/tables/phase5_clark_west.csv](../outputs/tables/phase5_clark_west.csv), [outputs/tables/phase5_cluster_robust_panel_test.csv](../outputs/tables/phase5_cluster_robust_panel_test.csv), [outputs/tables/phase5_two_way_cluster_by_horizon.csv](../outputs/tables/phase5_two_way_cluster_by_horizon.csv).

### Diagnostic: is this driven by 2020–21?

| Sample | lag-0 corr | lag-1 | lag-2 | lag-3 | lag-4 |
|---|---|---|---|---|---|
| Full development window (2004–2022) | 0.22 | 0.27 | 0.24 | 0.26 | 0.13 |
| **Excluding 2020–2021** | 0.12 | 0.17 | 0.09 | **0.10** | 0.10 |
| **2020–2021 only** | 0.14 | 0.27 | 0.26 | **0.43** | 0.19 |

The lag-3 correlation — the headline number from Phase 3 — drops by more than half once the pandemic years are excluded, and is dramatically elevated within those two years specifically. This is a plausible, direct explanation for why the relationship does not hold up in a test window (2023–2025) without a comparable shock.

## Disclosed deviations from the committed plan

Per [pre_analysis_plan.md](../pre_analysis_plan.md) Sec. 8 (any deviation disclosed, not silently substituted):

1. **ARDL and bridge equations collapse to one specification.** Under the real-time convention implemented (BFS treated as available at full-quarter granularity once its ~2-week lag passes), there is no partial-quarter bridging left to do, so these are numerically the same model.
2. **Hansen–Lunde–Nason (2011) Model Confidence Set was not implemented.** No vetted, widely-used Python reference implementation was available to build on with confidence, and a bespoke MCS bootstrap risks a subtle, hard-to-verify bug. Substituted with **Holm–Bonferroni** step-down correction across the primary comparisons — a standard, low-risk method with the same family-wise error-control purpose. (This substitution turned out not to be the binding constraint — the cluster-robust finding above is the one that overturns the naive result, not the multiple-comparison correction.)
3. **Qu, Timmermann & Zhu (2024) / Akgun et al. (2024) were not implemented.** Both are very recent papers without an available reference implementation to build on safely. Substituted with cluster-robust and two-way-clustered tests of the pooled loss differential — a standard, well-understood method for exactly the cross-sectional-dependence problem those papers address. **This substitution is the one that matters**: it's what overturned the naive result, which is itself a demonstration of why those specialized panel tests exist and why Phase 1's choice to look for them was the right instinct, even though a full from-scratch implementation wasn't attempted here.

## What this does and doesn't show

- **Does not show:** that BFS applications have no predictive value for establishment births, in general or in all circumstances. The 2020–21 evidence is real — applications clearly did lead births during that episode. What's shown is that this relationship does not clearly generalize to calmer periods, at least not with enough strength to detect in a 12-quarter test window.
- **Does not show:** that machine learning is useless here. It shows RF/GBM did not meaningfully beat a simple autoregressive benchmark *in this test window, with this feature set and this amount of data* — consistent, incidentally, with the weak non-top-tier state-unemployment-forecasting paper flagged in the Phase 1 methods review, which found the same thing in a similar short, noisy state panel.
- **Does show:** a naive, pooled significance test on this kind of state panel can be substantially overconfident, and checking for cross-sectional/serial dependence is not optional box-ticking — it reversed the conclusion here.
- **Important caveat on power:** "not significant" is not the same as "proven zero effect." With an effective sample closer to 12 independent quarters, this test window has limited power to detect even a real but modest effect. A longer test window, or a test window that happens to include another large shock, could look different.
