# RQ2 Findings — Which Business-Application Series Carries the Signal?

*2026-10-15. Run exactly as specified in [pre_analysis_plan_addendum_2.md](../pre_analysis_plan_addendum_2.md), which was committed (d07a3b4) before any RQ2 model was estimated. Regression models only. The all-applications (BA) forecasts reproduce the Addendum 1 run exactly (3,264 state-quarters, maximum difference 1e-16). Not yet reviewed by the author.*

Accuracy differences are in % of mean squared error. "+" means the model is more accurate than the comparison. Results at the 3-quarter lead (h=3) and same-quarter lead (h=0) are the pre-specified ones; the rest are in the tables.

The four series:

- **BA:** all business applications.
- **HBA:** high-propensity applications.
- **WBA:** applications with planned wages.
- **CBA:** corporate applications.

HBA, WBA and CBA are the narrower series Census builds to flag likely employers. Their exact definitions and nesting are still being confirmed from Census documentation; see §6.

## Summary

1. **Before 2020, the narrower series were better predictors than all applications.** This is consistent with what they were designed to do:
   - Head to head, high-propensity applications beat all applications at h=0 (+4.8%, Holm-adjusted p < 0.001, better in 96% of states).
   - Applications with planned wages beat them at h=3 (+3.7%, Holm-adjusted p = 0.012 two-way, < 0.001 bootstrap).
   - These years are pseudo-out-of-sample.
   - **The same-quarter (h=0) advantage survives Census's 2012 redefinition of high-propensity applications; the 3-quarter-lead advantage is weaker after it.** Restricting to 2013–2019 (§6):
     - h=0: high-propensity +4.7%, planned wages +4.7% (both p < 0.001).
     - h=3: high-propensity +1.0% (p = 0.38), planned wages +2.0% (raw p = 0.03).
2. **That advantage disappeared after 2020.** In 2022–25, none of the four series improved forecasts over the benchmark, and the narrower series did slightly *worse* than all applications:
   - High-propensity vs. all applications at h=3: −5.9% (raw p = 0.003; Holm-adjusted 0.07 two-way, 0.06 bootstrap).
   - In the locked 2023–25 window, corporate applications vs. all applications at h=0: −7.0% (Holm-adjusted p = 0.016 two-way, 0.044 bootstrap).
3. **The pre-specified "composition" explanation is not supported.** That explanation was that the breakdown came from a flood of applications unlikely to become employers. If it were right, the series that screen for employer intent should have held up better after 2020. They held up worse.
4. **The estimated weight is not the whole story.** All applications' weight roughly doubled after the pandemic entered the training data, but high-propensity applications' weight barely moved (+12%). Their forecasts still got worse. So the earlier hypothesis that the models are simply over-weighting applications cannot explain the breakdown on its own; the relationship itself appears to have changed.
5. **Locked test window, pre-specified family:** no series significantly improves forecasts. Holm-adjusted information tests over 4 series × 2 leads all have p ≥ 0.54.

## D1 — Locked test window, 2023Q1–2025Q4 (pre-specified in the original plan)

| Series | h=0 accuracy vs benchmark | h=3 accuracy vs benchmark | h=3 info test, two-way p | Holm-adjusted (8 tests) |
|---|---|---|---|---|
| BA (all) | −3.0% | +1.6% | 0.076 | 0.60 |
| HBA (high-propensity) | −5.2% | −3.3% | 0.28 | 1.00 |
| WBA (planned wages) | −4.3% | −3.3% | 0.31 | 1.00 |
| CBA (corporate) | −10.2% | −3.1% | 0.54 | 1.00 |

No series beats the benchmark. All applications is the least-bad series at both leads.

Per Addendum 2, the locked-window results do not change which series is the paper's primary predictor (BA, fixed in advance).

Full table: [rq2_test_window_comparisons.csv](../outputs/tables/rq2_test_window_comparisons.csv). Holm family: [rq2_test_window_holm.csv](../outputs/tables/rq2_test_window_holm.csv).

## D2 — Over time (new in Addendum 2)

### Accuracy vs. the benchmark (% of benchmark MSE)

| Period | Lead | BA | HBA | WBA | CBA |
|---|---|---|---|---|---|
| 2010–19 | h=0 | +2.6 | **+7.3** | +5.3 | +4.6 |
| | h=3 | +0.8 | +3.9 | **+4.5** | +1.8 |
| 2020–21 | h=0 | +11.3 | +19.4 | **+19.7** | +16.1 |
| | h=3 | +11.9 | **+22.6** | +17.2 | +6.3 |
| 2022–25 | h=0 | **−7.1** | −10.1 | −7.5 | −9.3 |
| | h=3 | −3.7 | −9.8 | −4.9 | **−2.5** |

Bold marks the best series in each row. The information test at h=3 is highly significant before 2020 for every series (two-way p ≤ 0.004) and not significant after 2020 for any series (p ≥ 0.27).

### Head-to-head: each narrower series vs. all applications

24 comparisons, Holm-adjusted across all of them. "+" = the narrower series was more accurate than BA.

| Period | Series | h | Difference | 95% CI | Holm p (two-way / bootstrap) | States where it beat BA |
|---|---|---|---|---|---|---|
| 2010–19 | HBA | 0 | +4.8% | +3.0 to +6.5 | <0.001 / <0.001 | 96% |
| 2010–19 | WBA | 3 | +3.7% | +1.6 to +5.7 | 0.012 / <0.001 | 78% |
| 2010–19 | HBA | 3 | +3.1% | +0.7 to +5.5 | 0.22 / 0.10 | 73% |
| 2022–25 | HBA | 3 | −5.9% | −9.9 to −2.0 | 0.07 / 0.06 | 18% |
| 2023–25 (locked) | CBA | 0 | −7.0% | −11.1 to −3.0 | 0.016 / 0.044 | 31% |

All 24 comparisons: [rq2_vs_BA_direct.csv](../outputs/tables/rq2_vs_BA_direct.csv).

### Estimated weight at h=3 (mean over forecast quarters in each period)

| Series | 2010–19 | 2020–21 | 2022–25 | Change, 2010–19 → 2022–25 |
|---|---|---|---|---|
| BA | 0.18 | 0.16 | 0.34 | +93% |
| HBA | 0.36 | 0.33 | 0.41 | +12% |
| WBA | 0.26 | 0.26 | 0.35 | +32% |
| CBA | 0.22 | 0.18 | 0.25 | +11% |

Figures:

- [Cumulative accuracy gain by series](../outputs/figures/rq2_cumulative_gain_h3.png): HBA and WBA build steady gains through the 2010s (about four times BA's), jump in 2021, then give some back during the locked window.
- [Weight paths by series](../outputs/figures/rq2_coefficient_paths_h3.png).

## Verdict against Addendum 2's pre-stated rules

- **"Supports composition"** required HBA and/or WBA to have a post-pandemic accuracy difference at or above zero while BA's was negative, *and* the head-to-head comparison to favor them. **Not met:** both are negative after 2020, and the head-to-head comparisons favor BA.
- **"No support"** required all four series to deteriorate by similar amounts. All four did deteriorate. HBA deteriorated more than BA (−9.8% vs −3.7% at h=3); WBA and CBA by similar amounts.
- **Overall: no support for the composition explanation.**
- **Partial exception:** the weight-based prediction (that the narrower series' weights would rise less) did hold. But the decision rule rests on accuracy, and accuracy contradicts it.

## What this means for the paper

This sharpens the paper's central finding. The breakdown after 2020 is not confined to "low-quality" applications. Even the series Census designs to identify likely employers stopped helping, and they lost a clear pre-2020 advantage.

The evidence now points to a change in how applications of every kind relate to measured establishment births. That leaves the cause open. Candidates to investigate, none tested here:

- **Something about the application series themselves.**
- **Something about BED establishment births.** The literature review flagged growing divergence between BLS and Census establishment counts (Cao, Hyatt, Mukoyama & Sager, CES-WP-26-36).

## Caveats

- The 2010–2022 results are pseudo-out-of-sample, as in Addendum 1.
- The over-time RQ2 analysis was new in Addendum 2. It was specified before running, but was motivated by the Addendum 1 results.
- The post-2020 head-to-head result for HBA (Holm p ≈ 0.06–0.07) is suggestive, not conclusive.
- The 2012 definition-change check in §6 was not pre-specified. It was prompted by Census documentation found after the run, and is reported as a sensitivity check.

## 6. Series definitions and documented breaks

Sources, checked 2026-10-15:

- Census BFS [Methodology](https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html)
- Census BFS [Definitions](https://www.census.gov/econ/bfs/definitions.html)
- Census BFS [About the Data](https://www.census.gov/econ/bfs/about_the_data.html)

**Definitions** (Census Methodology page):

- **BA:** EIN applications, excluding tax liens, estates, trusts, certain financial filings, applications without a state/county geocode, and applications in low-transition industries.
- **HBA:** "Business Applications (BA) that have a high propensity of turning into businesses with payroll," identified from IRS Form SS-4 characteristics. An application qualifies if any of these holds:
  - it is from a corporation;
  - it indicates hiring employees;
  - it gives a first wages-paid date;
  - it is in one of a listed set of industries (NAICS 72, 237, 238, 312, 321, 322, 332, 44, 452, 5411, 5413, 6111, 621, 623).
- **WBA:** HBA "that indicate a first wages-paid date."
- **CBA:** HBA "from a corporation or personal service corporation."

**Nesting** (confirmed by About the Data and the Methodology page's Venn diagram): BA ⊃ HBA ⊃ WBA and CBA, and WBA and CBA overlap. One caveat: raking seasonally adjusted industry estimates can occasionally push HBA above BA. That affects only the seasonally adjusted industry series, not the not-seasonally-adjusted state totals used here.

**Documented breaks that matter for this analysis:**

1. **November 2021 HBA redefinition**, applied to data from 2012 onward.
   - 2004–2011 HBA uses the original definition. That definition had broader hiring criteria and a different industry list.
   - It is rescaled to the new level by each state's 2012 ratio of new to old definition.
   - A constant rescaling leaves year-over-year growth unchanged, so before 2012 HBA growth reflects the *old* definition.
   - Whether WBA and CBA were also redefined is not stated by Census.
   - **Check:** re-running the head-to-head comparisons on 2013–2019 forecasts only (every forecast target in the new-definition period; table below) leaves the same-quarter advantage intact. The 3-quarter-lead advantage shrinks. Full table: [rq2_hba_definition_check.csv](../outputs/tables/rq2_hba_definition_check.csv).
2. **2025 annual update (published February 2026):** Census "removed internet sales applications from both CBA and HBA time series" after "noticing a spike in these cases."
   - Our data were downloaded 2026-10-14, after this revision, so the HBA and CBA series used here already exclude them.
   - Census does not say this revision touched BA.
   - The date of the spike is not stated.
   - **Relevance:** the narrower series lost their advantage after 2020 even with that spike removed.
3. **Seasonal factors and industry codes are revised annually.** This does not affect the primary analysis, which uses not-seasonally-adjusted state totals.

| Window | Series | h | vs. BA | 95% CI | Two-way p | Bootstrap p |
|---|---|---|---|---|---|---|
| 2010–19 | HBA | 0 | +4.8% | +3.0 to +6.5 | <0.001 | <0.001 |
| 2013–19 | HBA | 0 | +4.7% | +2.7 to +6.6 | <0.001 | <0.001 |
| 2010–19 | HBA | 3 | +3.1% | +0.7 to +5.5 | 0.012 | 0.005 |
| 2013–19 | HBA | 3 | +1.0% | −1.2 to +3.2 | 0.38 | 0.37 |
| 2010–19 | WBA | 0 | +2.8% | +0.1 to +5.5 | 0.045 | 0.030 |
| 2013–19 | WBA | 0 | +4.7% | +2.2 to +7.3 | <0.001 | <0.001 |
| 2010–19 | WBA | 3 | +3.7% | +1.6 to +5.7 | <0.001 | <0.001 |
| 2013–19 | WBA | 3 | +2.0% | +0.2 to +3.8 | 0.033 | 0.009 |

(p-values in this table are not Holm-adjusted.)

**Related research (Census staff; the views are the authors', not Census's):** Dinlersoz, Dunne, Haltiwanger & Penciakova, CES Working Paper 21-01 (2021; also *AEA Papers & Proceedings* 111, verified in the Phase 1 literature review).

- They report that by week 40 of 2020, HBA was up 17% and non-HBA applications up 30% from 2019.
- They describe "a change in the composition of applications in 2020 towards applications that are more likely to be nonemployers."

That compositional shift is real. The finding here is that filtering it out with HBA did not preserve the predictive relationship after 2020.
