# Pre-Analysis Plan — Addendum 2: Which Application Series Carries the Signal (RQ2)

**Committed: 2026-10-15, before any RQ2 model was estimated.** Approved by the author. The original plan and Addendum 1 are unchanged.

## Background

The original plan (§7, secondary comparison 4) pre-specified RQ2: does all business applications (BA), high-propensity applications (HBA), applications with planned wages (WBA), or corporate applications (CBA) carry the most predictive signal?

Addendum 1 then found the relationship between BA and establishment births is regime-dependent: modest before 2020, strong in 2020–21, absent after. That gives RQ2 a sharper purpose.

Census builds HBA, WBA, and CBA as narrower series that are more likely to become employer businesses. Exact definitions and nesting are being checked against Census documentation and will be cited from it, not assumed.

## D1 — RQ2 in the locked test window (as pre-specified in the original plan)

For each series S in {BA, HBA, WBA, CBA} and lead h = 0–4, compare the benchmark against the benchmark + S lagged h quarters. Everything else is identical to Phase 5:

- same expanding window
- same real-time label rule
- same quarter-of-year and state indicators
- same inference: naive, clustered by state, clustered by quarter, two-way, and wild cluster bootstrap by quarter

BA has already been run; it is repeated here only so all four series appear in one table.

**Multiple testing.** The family is 4 series × the two pre-specified leads (h = 0, h = 3) = 8 Clark–West information tests. These are Holm-adjusted using the two-way and the bootstrap p-values. All other leads are reported unadjusted, as descriptive results.

RQ2 is a secondary comparison. No single result from it becomes the paper's headline.

## D2 — RQ2 over time (new; beyond the original plan)

Same periods and procedure as Addendum 1, Analysis B. Regression models only.

| Period | Target quarters |
|---|---|
| Pre-pandemic | 2010–2019 |
| Pandemic | 2020–2021 |
| Post-pandemic | 2022–2025 |
| Locked test (subset of post-pandemic) | 2023–2025 |

**Hypothesis, stated before running.** If the post-2020 breakdown reflects a shift in the mix of applications toward ones that rarely become employer businesses, the narrower employer-intent series (HBA, WBA) should hold up better after 2020 than BA. Specifically:

1. Their estimated weight should rise less once 2020–21 enters the training data.
2. Their post-pandemic accuracy difference against the benchmark should be less negative than BA's.

**Decision rules (lead h = 3 primary, h = 0 secondary):**

- **Supports the composition explanation:** HBA and/or WBA show a post-pandemic accuracy difference at or above zero while BA's is negative, *and* the direct comparison of the S-augmented model against the BA-augmented model favors S. (The direct comparison uses the plain accuracy difference with two-way clustering. Clark–West does not apply, because the two models are not nested.)
- **No support:** all four series deteriorate after 2020 by similar amounts.
- **Mixed:** report it as mixed.

With 16 post-pandemic quarters these tests have low power. Results are reported as indicative, with confidence intervals, not as confirmatory findings.

**Descriptive additions.** For each series at h = 3, show the coefficient path and the cumulative accuracy gain over time, as small-multiple panels with shared axes.

## Restrictions carried forward from Addendum 1

- No fix is tested on the locked 2023–25 window. That includes choosing a series because it did well there.
- A series that looks best in the locked window does not replace BA as the paper's primary predictor. The primary predictor was fixed before any results.
- The pre-pandemic and pandemic results are pseudo-out-of-sample, for the same reasons given in Addendum 1.
