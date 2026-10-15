# Pre-Analysis Plan — Addendum 1

**Committed: 2026-10-15, before any of the analyses below were run.** Approved by the author after reviewing the Phase 5 results ([literature/phase5_findings.md](literature/phase5_findings.md)). The original [pre_analysis_plan.md](pre_analysis_plan.md) is unchanged; this file adds to it.

## Why this addendum exists, and what it is not

Phase 5 found that the apparent forecasting gain from business applications disappears once the test correctly accounts for correlated errors across states and quarters. An in-sample diagnostic suggested the original signal was concentrated in 2020–21. This addendum specifies three follow-up analyses that decide whether the project is a publishable paper.

**What this is not:** a blind test. The "pandemic-episode" hypothesis below was formed *after* seeing the Phase 5 test-window results and the in-sample correlation diagnostic. What has *not* been computed or viewed is the out-of-sample forecast performance over 2010–2022, which is what Analysis B tests. The paper must say this plainly.

## Analysis A — the two committed robustness checks (from the original plan, §4)

These were specified in the original plan and are run exactly as written there. Implementation details the plan did not pin down, fixed now:

1. **Seasonally adjusted (SA) line.** Same models re-estimated on BLS/Census seasonally adjusted series, **without** the quarter-of-year indicator. ML hyperparameters are re-tuned on the SA development window using the same grids as the primary run. Explicitly not valid for real-time claims (SA construction can use future data).
2. **Winsorizing sensitivity.** Own-lag features, the BFS feature, and the training target are clipped at the fixed development-window bounds already committed (`births_yoy` [-0.474, +0.580]; `BA_BA_yoy` [-0.239, +0.549]). Predictions are evaluated against **both** the winsorized and the raw actual values, and both are reported. ML models reuse the hyperparameters tuned in the primary run (stated as a simplification).

## Analysis B — forecast performance over time (2010–2025)

The same expanding-window procedure, same real-time rule (training labels must be at least 3 quarters old), and same econometric specifications as Phase 5, with forecast targets starting in 2010Q1 instead of 2023Q1.

**Periods, fixed now:**

| Period | Target quarters | Quarters |
|---|---|---|
| Pre-pandemic | 2010Q1–2019Q4 | 40 |
| Pandemic | 2020Q1–2021Q4 | 8 |
| Post-pandemic | 2022Q1–2025Q4 | 16 |
| — of which, the locked test window | 2023Q1–2025Q4 | 12 |

**Consistency check:** the 2023Q1–2025Q4 forecasts from this run must exactly match the Phase 5 primary predictions. If they do not, something in the code changed and nothing from this analysis is reported until that is fixed.

**Models:** benchmark and benchmark + BFS lag h, for h = 0–4 (ordinary least squares, no tuned settings). **Machine-learning models are excluded** from this analysis: their settings were tuned on the full 2004–2022 development window, so using them to forecast 2010–2022 would let information from later years leak into earlier forecasts.

**Not a clean held-out test:** 2010–2022 informed the Phase 3 exploratory work (including the emphasis on a 3-quarter lag). Results for those years are pseudo-out-of-sample and will be labeled that way.

**What would support or undercut the pandemic-episode explanation (primary horizon h = 3):**

- **Supports it:** the benchmark-minus-BFS loss difference is positive in the pandemic period, and small / not distinguishable from zero in the pre-pandemic period.
- **Undercuts it — BFS works in normal times:** a clearly positive, statistically supported gain in the pre-pandemic period. The paper would then be about a relationship that held before 2020 and weakened afterward (or a low-power test window), not about a pandemic artifact.
- **Undercuts it — BFS never helped out of sample:** no gain in the pandemic period either. The paper would then be about an in-sample correlation that never translated into forecasting value.

Whichever of these occurs is what gets written up.

**Inference caveat, stated in advance:** the pandemic period has only 8 quarters, so any statistical test within it is weak. Pandemic-period results are reported with that caveat and treated as indicative.

**Descriptive addition:** the estimated BFS coefficient from each expanding-window refit (h = 3) is recorded and plotted, to show whether it shifts once pandemic-era data enter the training sample. This is descriptive only. If it suggests a fix (for example, excluding 2020–21 from training), that fix will **not** be tested on the 2023–2025 window, which would be specification search on the locked test; it would be noted as a hypothesis for future data.

## Analysis C — what effect size the test window could have detected

For each primary-window comparison (BFS-augmented models at h = 0–4, random forest, gradient boosting, and the combination, each against the benchmark):

1. The 95% confidence interval for the mean loss difference, using the two-way clustered standard error, expressed as a **percentage of the benchmark's mean squared error**. The upper end is the largest improvement the data can rule out.
2. The minimum detectable improvement at 80% power, two-sided 5% test (2.80 × standard error), as a percentage of benchmark mean squared error.
3. **Few-cluster check.** With only 12 quarters, conventional clustered standard errors can be too small, which would make statement 1 overconfident. A wild cluster bootstrap (clustered by quarter, Webb six-point weights, null imposed, 9,999 draws) provides a p-value and a bootstrap-t confidence interval. If the bootstrap interval is materially wider, the bootstrap interval is the one reported as the headline.
