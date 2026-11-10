# Pre-Analysis Plan: Addendum 5, Pre-Submission Revision Analyses

**Committed: 2026-11-09, before any analysis below was run, except those listed under "Already seen".** Approved by the author on 2026-11-09, after the pre-submission audit recorded in [research_log.md](research_log.md) (entries of 2026-11-04). The original plan and Addenda 1–4 are unchanged.

## Why this addendum exists, and its status

The audit found that the paper's framing ("the relationship changed after 2020") runs ahead of its evidence:

- the autoregressive benchmark is weaker than a no-change forecast on mean absolute error in normal years;
- at the three-quarter lead, the post-2020 losses are concentrated in 2022;
- Census's own state-level projections of business formation were never used.

The author decided to revise the paper before submission and to reframe it around business applications as an *episodic* indicator. The analyses below support that revision.

**These analyses are not confirmatory.** They were chosen after the main results, the over-time results and the first live-forecast quarter (2026Q1) were known. The paper labels them "not pre-specified", except item A, which completes the reporting of a pre-specified estimand. The pre-registered results of the plan and Addenda 1–4 remain the paper's primary results and are not changed. The only new confirmatory test is the live test in item F, whose forecasts are frozen before any of their target quarters is published.

### Already seen

These quantities were computed during the 2026-11-04 audit and recorded in the research log:

- **Benchmark versus the no-change forecast:** MSE, MAE and mean error, by period, for the benchmark only.
- **Gains from all applications** over the benchmark at leads 0–4, for 2010–19, 2020–21, 2022 and 2023–25.
- **Tests of change** (Newey–West, 3 lags, on quarterly cross-state mean squared-error differentials) for 2010–19 versus 2022–25 and versus 2023–25:
  - all applications (BA) at leads 0, 1, 3 and 4;
  - high-propensity applications (HBA) and applications with planned wages (WBA) at leads 0 and 3;
  - corporate applications (CBA) at lead 0.
- **The h = 3 net gain** over 2010–2025, excluding 2021Q2–2022Q1: −2.2%.
- **The code audit's recomputation** of the test-window h = 3 information test: p ≈ 0.089 with a t(11) reference; p ≈ 0.097 with Newey–West standard errors on quarterly means.

The mock referee's report also contained indicative calculations of related quantities, which were read:

- no-change comparisons of MAE for the test-window models;
- Diebold–Mariano/Clark–West p-values on quarterly means with HAC and small-sample corrections;
- tests of change for the Clark–West measure.

Nothing else below has been computed.

## A. No-change benchmark and mean absolute error (pre-specified estimand)

The plan (§5) lists a seasonal naive benchmark, and the design (research_question.md) defines the estimand as forecast loss measured by RMSE and MAE. For complete reporting:

- **Models covered:**
  - every test-window model: the benchmark; applications at leads 0–4; elastic net; random forest; gradient boosting; the combination;
  - every regression model in the over-time run: the benchmark; BA, HBA, WBA and CBA at leads 0–4, by period (item B).
- **Statistics reported:** RMSE, MAE, mean error (actual minus forecast), and each model's MSE and MAE relative to the seasonal naive (zero) forecast.
- **Inference:** differences against the seasonal naive forecast and against the benchmark, for squared and absolute loss, use the methods of Table 1 (two-way clustered by state and quarter; wild cluster bootstrap by quarter), two-sided.

## B. Periods (not pre-specified)

Results over time are reported for four periods at leads 0–4 for all four application series:

| Period | Quarters |
|---|---|
| 2010–2019 | 40 |
| 2020–2021 | 8 |
| 2022 | 4 |
| 2023–2025 | 12 |

2022 is separated from 2023–2025 because its year-over-year changes are measured against the 2021 surge (the reasoning in Addendum 3). Within 2022, which has only four quarters, results are descriptive and carry no p-values.

## C. Tests of change (not pre-specified)

For each series (BA, HBA, WBA, CBA) and lead (0–4), the quarterly cross-state mean of the loss differential (benchmark loss minus model loss) over 2010–2025 (64 quarters) is regressed on indicators for 2020–21, 2022 and 2023–25, with 2010–19 as the base period.

- **Standard errors:** Newey–West with 3 lags, because year-over-year targets overlap for up to three quarters.
- **Statistics:** both the squared-error differential and the Clark–West adjusted differential. Contrasts are expressed as a percentage of the 2010–2019 benchmark MSE.
- **Multiple testing:** within each statistic and each contrast, Holm adjustment across the 20 series × lead tests.
- **Reading:** a lasting change is claimed only where the 2023–25 versus 2010–19 contrast is significant at the 5% level after Holm adjustment. The 2022 contrast is described as the unwinding of the 2021 surge.
- **For continuity with the audit,** the single contrast 2022–25 versus 2010–19 (a regression on those two periods only) is also reported.

## D. Inference robustness (not pre-specified)

For the test window (the comparisons in Table 1 and Appendix Table A1) and for each period in B with at least 8 quarters:

1. Clustered tests with t(G − 1) reference distributions instead of the normal, where G is the number of quarter clusters.
2. Diebold–Mariano and Clark–West tests on the cross-state average loss differential (one observation per quarter), with Newey–West (Bartlett) standard errors with 3 lags and the Harvey–Leybourne–Newbold small-sample correction (with h = 4, matching the overlap of year-over-year changes), using a t(T − 1) reference.

These are robustness checks. The pre-specified inference remains the primary inference; where the conclusions differ, both are reported.

## E. Census projected business formations, PBF4Q (not pre-specified)

Census publishes, monthly for each state, projected employer business formations within four quarters of application (series BF_PBF4Q). The projections come from a linear probability model of each application's chance of becoming an employer business (Bayard et al. 2018) and are as timely as the application counts.

- **Predictor:** BF_PBF4Q, not seasonally adjusted, summed to quarters (all three months required), as a year-over-year log change at leads 0–4. It enters exactly as applications do (the benchmark plus PBF4Q at lead h), in regression models only, using the 2010–2025 expanding-window procedure with the same real-time training rule.
- **Comparisons:**
  - against the benchmark: accuracy and Clark–West, as in Table 2, by period (B);
  - directly against the all-applications model at the same lead: accuracy, two-way clustered and wild bootstrap, by period;
  - tests of change as in C.
- **Multiple testing:** Holm across the 10 Clark–West tests against the benchmark (leads 0–4, in 2010–19 and in 2023–25).
- **Caveat stated in the paper:** Census's documentation does not say whether the projection model is re-estimated or past projections are revised. The history used (retrieved 14 October 2026) may therefore contain information that was not available in real time.
- **Not analyzed:** PBF8Q, to limit the number of comparisons.

## F. Live test of PBF4Q (confirmatory)

This test covers forecasts for 2026Q2 and 2026Q3, which BLS has not yet published (2026Q2 is scheduled for 27 January 2027).

**Data.** The run uses the same committed processed files as the Addendum 3 forecasts: BFS through September 2026 and BED through 2025Q4, both retrieved on 14 October 2026. No data published after 14 October 2026 is used.

**Consistency check (required).** The run must reproduce the frozen Addendum 3 benchmark forecasts exactly; it then adds the PBF4Q models.

**Models:**

- the benchmark;
- the benchmark plus PBF4Q at leads 0 and 3;
- each with full training and with training excluding 2020–2022, as in Addendum 3.

**Freezing.** The forecasts and the scoring code are committed, hashed and tagged (`prereg-live-forecasts-pbf-2026q2q3`) before 2026Q2 is published.

**H3: Census's projections do not improve on the benchmark.** The comparison is PBF4Q at leads 3 and 0, full training, against the full-training benchmark. The readings mirror H1 and apply to the pool of published quarters at each update:

| Result | Reading |
|---|---|
| Accuracy difference ≤ 0 | Consistent with no gain |
| Accuracy difference > 0 and the PBF4Q model better in more than half of states | Gain |
| Otherwise | Mixed |

**Secondary comparisons** (reported, not read): PBF4Q against the all-applications model at the same lead (from the frozen Addendum 3 file), and the variants trained excluding 2020–2022.

**Actual values** are computed within each new BLS release, as in Addendum 3.

## G. Other robustness and exploratory analyses (not pre-specified)

1. **State versus national information.** For leads 0 and 3, by period over 2010–2025 and in the test window, two models are each compared with the benchmark and with the state-applications model:
   - (a) the benchmark plus national application growth (the U.S. total, the same value for every state);
   - (b) the benchmark plus state application growth, demeaned by the cross-state mean in each quarter.
2. **Weighted loss.** Test-window and by-period accuracy comparisons in which each state's squared error is weighted by its share of establishment births over the development window (2004–2022 average). Descriptive.
3. **BED revision check.** The test-window forecasts (2023Q1–2025Q4) are re-scored against actual values recomputed from the BLS release of 28 October 2026 (retrieved 4 November 2026), which revised 2025. Descriptive.

## H. Presentation changes (not analyses)

These follow the author's decision:

- the paper is reframed around applications as an episodic indicator;
- RQ4 moves to an appendix, as Addendum 4 specified;
- the machine-learning comparison becomes a robustness section, with its table in the appendix;
- Section 8 is shortened.

## Reporting commitments

- Every result from items A–G is reported in the paper or its online appendix, whatever it shows.
- Items B–E and G are labeled not pre-specified; item F is the only new confirmatory test.
- If any item cannot be implemented as written, the deviation is recorded in a dated note at the end of this file and in the paper.

## Implementation notes (2026-11-09)

*Added after items A–G were run. Every item was implemented as written. These notes record choices the text left open, and one diagnostic.*

1. **Item C, PBF4Q.** The Holm adjustment of the PBF4Q tests of change runs across its five leads, within each statistic and contrast. The 20-test families of item C cover the four application series only.
2. **Items A, E and G1, the two-way clustered variance.** In 17 of the comparisons against the no-change forecast, all on squared error, the two-way variance (state + quarter − heteroskedasticity-robust) is smaller than both one-way clustered variances. This happens because the loss differential is negatively correlated within states, and it makes the two-way p-value unreliable. The output tables flag these comparisons (`two_way_below_one_way`), and the paper reports the wild bootstrap p-value for them. No comparison against the benchmark or the state-applications model is affected, in these tables or in the paper's primary tables (checked).
3. **Item F.** The run reproduces the frozen Addendum 3 benchmark forecasts for 2026Q2–Q3 to within 1e-16, which is floating-point rounding, with identical training sizes.
4. **Items D and G1, the test window.** The 2023–25 forecasts of the over-time run are identical to the test-window forecasts (checked: maximum difference 0), so the test-window results of item G1 are its 2023–25 rows.
