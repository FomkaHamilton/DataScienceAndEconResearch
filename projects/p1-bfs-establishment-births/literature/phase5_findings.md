# Phase 5 — Model Evaluation Findings (corrected) and Addendum 1 Results

*2026-10-15. This is the current version. It supersedes the first write-up (commit 24013c8), which contained three errors described in section 1. Analyses follow [pre_analysis_plan.md](../pre_analysis_plan.md) and [pre_analysis_plan_addendum_1.md](../pre_analysis_plan_addendum_1.md); the addendum was committed (feb59b5) before any of its analyses were run. Not yet reviewed by the author.*

Units used throughout: accuracy differences are expressed as **% of the benchmark's mean squared error (MSE)**. +5% means the model's squared forecast errors were 5% smaller than the benchmark's; negative means the model did worse.

## Summary

1. **Before 2020**, business applications carried real but modest predictive information for state establishment births. The nested information test (Clark–West) is significant even with dependence-robust inference (p ≈ 0.004 at the 3-quarter lead). Accuracy gains were small, about 1–4% depending on the lead, positive in roughly two-thirds of states, and not individually significant. These years are pseudo-out-of-sample (see §6).
2. **During 2020–21**, gains were large: 11–20% at leads of 0–3 quarters, positive in 80–92% of states. Four quarters (2021Q2–2022Q1) account for most of the cumulative forecasting gain across the whole 2010–2025 span. Inference within this period is weak (only 8 quarters).
3. **After the pandemic**, the estimated weight on applications roughly doubled (from about 0.15–0.20 to about 0.32–0.34, re-estimated each quarter), and the models that use applications stopped helping:
   - In the locked 2023–25 test window, accuracy gains are indistinguishable from zero (3-quarter lead: +1.6%, 95% CI −6.5% to +9.7%).
   - Across 2022–25, adding applications made forecasts slightly *worse* at leads of 0–3 quarters, in most states.
4. **Machine learning adds nothing detectable.** With corrected tuning, the best ML model is an elastic net. It is +2.3% more accurate than the benchmark, with a 95% CI of −8.7% to +13.4%.
5. **Naive pooled tests badly overstate significance.** For example, the information test at the 3-quarter lead has p = 0.0003 naive versus p ≈ 0.07 when it accounts for correlated errors.
6. **The test-window results hold** under the two committed robustness checks (seasonally adjusted series; winsorized series).

The pre-specified "pandemic-episode" explanation (Addendum 1) is **partly supported and partly undercut**:

- **Supported:** the pandemic-period gains are large, and the pre-2020 accuracy gains are small and not individually significant.
- **Undercut:** applications did carry statistically detectable information before 2020.
- **Not anticipated:** after the pandemic the relationship didn't just fade back to its pre-2020 level; it stopped helping or slightly hurt.

The accurate description is a **regime-dependent relationship**, not a pure pandemic artifact.

## 1. Corrections to the first Phase 5 write-up

Found while preparing Addendum 1. None of these let test-window data into model training.

| # | Problem | Effect on results |
|---|---|---|
| C1 | The machine-learning tuning step was meant to validate on later years after training on earlier ones. Because the data was sorted by state, it actually split into alphabetical groups of states, each covering 2006–2022. | ML results only. With corrected (time-ordered) tuning, two of the three models chose simpler settings, and the best model by validation error is the elastic net, not random forest. |
| C2 | "Best ML model" was hard-coded to random forest instead of being chosen by validation error. | The primary ML comparison and the combination forecast now use the elastic net. |
| C3 | The dependence-robust tests were run on the *unadjusted* error difference, while the naive test they were compared with used the Clark–West *adjusted* difference. So the "naive vs. robust" comparison changed two things at once. | **This changes the headline.** I reported the 3-quarter-lead result as "nowhere near significant (p = 0.70)." That p-value is for actual accuracy, and it is correct as an accuracy test. The matching robust *information* test is p ≈ 0.07: marginal, not absent. |

The regression forecasts themselves are unchanged. The Addendum 1 consistency check confirmed all 612 test-window regression forecasts match the first run exactly.

## 2. Locked test window, 2023Q1–2025Q4 (primary results, corrected)

### Accuracy

| Model | RMSE | Accuracy vs. benchmark | 95% CI | Two-way p |
|---|---|---|---|---|
| Benchmark (own history only) | 0.1798 | — | — | — |
| + applications, same quarter (h=0) | 0.1824 | −3.0% | −8.1% to +2.2% | 0.26 |
| + applications, 3-quarter lead (h=3) | 0.1784 | +1.6% | −6.5% to +9.7% | 0.70 |
| Elastic net (best ML by validation) | 0.1777 | +2.3% | −8.7% to +13.4% | 0.68 |
| Random forest | 0.1806 | −0.8% | −13.3% to +11.6% | 0.89 |
| Gradient boosting | 0.1824 | −2.9% | −13.8% to +8.0%* | 0.64* |
| Combination (h=3 + elastic net) | 0.1771 | +3.0% | −6.2% to +12.1% | 0.53 |

\*Gradient boosting's two-way clustered standard error was unstable (its interval was 1.6× narrower than the bootstrap's), so the wild-cluster-bootstrap interval and p-value are reported for it, as Addendum 1 specified.

### Information tests (Clark–West, one-sided: does adding applications help?)

| Comparison | Naive p | Clustered by state | Clustered by quarter | Two-way | Wild cluster bootstrap |
|---|---|---|---|---|---|
| h=0 | 0.47 | 0.47 | 0.48 | 0.48 | 0.49 |
| h=3 | 0.0003 | 0.008 | 0.057 | 0.076 | 0.067 |
| Elastic net | 0.0001 | 0.003 | 0.037 | 0.052 | 0.048 |

Holm-adjusted across the three primary comparisons (h=0, h=3, best ML):

- **h=3:** 0.15 (two-way), 0.14 (bootstrap)
- **Elastic net:** 0.15 (two-way), 0.14 (bootstrap)

Neither is significant after adjustment.

**Clark–West is not used to judge the tree models.** Its adjustment assumes the larger model nests the smaller one in a linear way. Random forest's forecasts differ a lot from the benchmark's, so the adjustment inflates the statistic: random forest "passes" Clark–West (two-way p = 0.014) while being *less* accurate than the benchmark. For random forest and gradient boosting, only the accuracy test is meaningful.

Full tables:

- [phase5_comparisons.csv](../outputs/tables/phase5_comparisons.csv)
- [phase5_model_performance.csv](../outputs/tables/phase5_model_performance.csv)
- [phase5_ml_tuning.csv](../outputs/tables/phase5_ml_tuning.csv)
- [phase5_primary_comparisons_holm.csv](../outputs/tables/phase5_primary_comparisons_holm.csv)

## 3. Robustness checks (Addendum 1, Analysis A)

Locked test window, 3-quarter lead and best ML model:

| Variant | h=3 accuracy | h=3 info test (two-way p) | Best-ML accuracy |
|---|---|---|---|
| Primary | +1.6% | 0.076 | +2.3% |
| Seasonally adjusted series (no quarter indicator) | +1.7% | 0.065 | +2.9% |
| Winsorized, scored against winsorized actuals | +0.0% | 0.117 | −0.4% |
| Winsorized, scored against raw actuals | +0.9% | 0.092 | −0.0% |

The conclusion doesn't depend on the seasonal-adjustment choice or on a few extreme quarters. If anything, clipping extremes shrinks the small gains further.

Full table: [phase5x_robustness_comparisons.csv](../outputs/tables/phase5x_robustness_comparisons.csv).

## 4. What the test window could have detected (Addendum 1, Analysis C)

- **Upper end of the 95% intervals (§2 table):** the largest accuracy improvement the data can rule out.
  - Same-quarter applications (h=0): gains above roughly **+2%** are ruled out.
  - 3-quarter lead (h=3): gains above roughly **+10%** are ruled out.
- **Minimum detectable improvement at 80% power:** 7–12% for the regression models, 10–18% for the ML models.
- **So:** the test window rules out *large* gains but cannot rule out *modest* gains of a few percent. That is why the over-time analysis (§5) carries the paper.
- **Few-cluster check:** wild-cluster-bootstrap intervals are within ±13% of the two-way intervals for every model except gradient boosting. The conventional intervals are not overconfident.

Full table: [phase5x_detectable_effects.csv](../outputs/tables/phase5x_detectable_effects.csv).

## 5. Forecast performance over time, 2010–2025 (Addendum 1, Analysis B)

Regression models only, same expanding window and real-time rule. The test-window forecasts reproduce the primary run exactly (maximum difference 1e-16).

| Period | Lead | Accuracy vs. benchmark | Two-way p (accuracy) | Info test, two-way p | States where model was more accurate |
|---|---|---|---|---|---|
| 2010–19 (40 qtrs) | h=0 | +2.6% | 0.19 | 0.0001 | 67% |
| | h=1 | +3.8% | 0.15 | 0.0001 | 76% |
| | h=3 | +0.8% | 0.23 | 0.004 | 65% |
| 2020–21 (8 qtrs) | h=0 | +11.3% | 0.31 | 0.064 | 80% |
| | h=1 | +20.1% | 0.22 | 0.046 | 90% |
| | h=3 | +11.9% | 0.16 | 0.070 | 92% |
| 2022–25 (16 qtrs) | h=0 | −7.1% | 0.079 | 0.85 | 18% |
| | h=1 | −4.7% | 0.37 | 0.44 | 33% |
| | h=3 | −3.7% | 0.66 | 0.27 | 37% |
| | h=4 | +3.5% | 0.43 | 0.058 | 67% |

All horizons and the bootstrap p-values: [phase5x_by_period.csv](../outputs/tables/phase5x_by_period.csv).

**Cumulative gain** ([figure](../outputs/figures/phase5x_cumulative_gain_h3.png)):

- Flat through 2014, then a slow, steady rise from 2015 to 2019.
- Back to zero in 2020, then a near-vertical jump in 2021Q2–2022Q1.
- A sharp loss in 2022Q2, then flat through the test window.
- 2021Q2 alone contributed about seven times the entire 2010–2019 net gain.

**Estimated weight on applications** ([figure](../outputs/figures/phase5x_bfs_coefficient_path_h3.png)):

- Stable at about 0.15–0.20, and clearly above zero from about 2013, through 2021.
- Rises to 0.32–0.41 once the 2020–21 surge enters the training data, and stays around 0.32–0.34 through the test window.
- In plain terms: before 2020, a 10% year-over-year rise in applications was associated with roughly a 1.5–2% rise in establishment births three quarters later. The models trained through the pandemic assume roughly 3.3%.

**Interpretation (hypothesis, not tested):** the post-pandemic models may be over-weighting applications because their estimated weight was learned largely from the 2020–21 surge. Addendum 1 commits to *not* testing a fix (for example, excluding 2020–21 from training) on the locked test window, since that would be specification search on the test data. The fix can be tested on future quarters as BLS publishes them.

## 6. Caveats the paper must carry

- **The pandemic explanation was formed after seeing the Phase 5 results** (stated in Addendum 1). The 2010–2022 forecasts are pseudo-out-of-sample, because those years informed exploratory choices such as emphasizing the 3-quarter lead.
- **Pandemic-period inference rests on 8 quarters.** Point estimates are large and consistent across states, but p-values within that period are weak.
- **Not a causal claim.** Nothing here says what drives the change after 2020.
- **Data are final vintage, not real-time.** The BED vintage limitation from the original plan still applies.
- **Two methods were substituted,** as disclosed in the plan: Holm–Bonferroni instead of the Model Confidence Set, and cluster-robust/bootstrap tests instead of the Qu–Timmermann–Zhu / Akgun panel tests.

## 7. Citations introduced in this phase — verify before manuscript use

- Cameron, Gelbach & Miller — two-way clustered standard errors (believed: *Journal of Business & Economic Statistics*, 2011)
- Cameron, Gelbach & Miller — wild cluster bootstrap for few clusters (believed: *Review of Economics and Statistics*, 2008)
- Webb — six-point weights for the wild cluster bootstrap (believed: *Canadian Journal of Economics*, 2023)

None of these has been checked against a publisher page yet.
