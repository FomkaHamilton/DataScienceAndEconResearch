# Manuscript figures: review copy

*2026-10-15. Built by `src/analysis/make_paper_figures.py` (part of `replication/run_all.py`). Proposed placements and draft captions below; none is in the draft yet, pending the author's review.*

All figures are drawn from committed output tables, the committed analysis panel, or the frozen live-forecast file. Nothing is re-estimated, and no new test is run. Each figure is saved as PNG (300 dpi, for review) and PDF (vector, for submission), sized for a 6.5-inch text width.

**Colour.**

- All applications and establishment births are drawn in black.
- Colour is used only to tell apart the three narrower application series (Figures 4–5).
- Every coloured line is also labelled directly, so the figures still read in greyscale print.
- The palette was checked for colour-blind separation.

**Proposed layout:** 7 figures in the main text. Tables 1, 3 and 5 stay in the main text; Tables 2 and 4 move to an appendix, because Figures 2 and 4 carry their message. For figure numbers to follow the order of first mention, the paragraph on the estimated weight should move from Section 6.4 to 6.5, next to the series comparison it supports.

---

## Figure 1 → Section 3 (Data)

![Figure 1](fig1_national_applications_births.png)

**Figure 1.** National year-over-year change in business applications (a) and establishment births (b), 2005Q3–2025Q4, in log points (100 × the log change from the same quarter a year earlier), not seasonally adjusted. Shaded: the pandemic (2020–21) and the test window (2023–25). Applications peaked in 2020Q3 and establishment births three quarters later, in 2021Q2. *Sources: Census Bureau, Business Formation Statistics; BLS, Business Employment Dynamics.*

## Figure 2 → Section 6.2 (replaces Table 2 in the main text)

![Figure 2](fig2_test_window_intervals.png)

**Figure 2.** Test-window comparisons with the benchmark, 2023Q1–2025Q4 (612 state-quarters).

- **Interval types:** grey intervals treat every state-quarter as independent; black intervals are two-way clustered by state and quarter.
- **Panel (a):** Clark–West adjusted loss difference with 90% intervals, so a black interval lying wholly above zero corresponds to rejection at the 5% level in the one-sided information test. The tree-based models are omitted because the adjustment is not meaningful for them (Section 6.3).
- **Panel (b):** reduction in mean squared error with 95% intervals; positive values favour the model.
- **†** Robust interval from the wild cluster bootstrap by quarter, because the two-way clustered standard error was unstable for this model.

*Source: outputs/tables/phase5_comparisons.csv.*

## Figure 3 → Section 6.4 (replaces current Figure 1)

![Figure 3](fig3_cumulative_gain_ba_h3.png)

**Figure 3.** Cumulative accuracy gain from adding applications at a three-quarter lead, 2010Q1–2025Q4.

- **Construction:** each quarter adds the reduction in squared error relative to the benchmark, averaged across states. The running total is expressed as a percentage of the benchmark's total squared error over the whole period, so the final value (3.0%) is the gain over 2010–2025 as a whole.
- **Reading it:** a rising line means the model with applications beat the benchmark that quarter.
- 2010–2022 is pseudo-out-of-sample.

*Source: outputs/tables/rq2_predictions.csv.*

## Figure 4 → Section 6.5 (Table 4 to the appendix)

![Figure 4](fig4_cumulative_gain_by_series.png)

**Figure 4.** Cumulative accuracy gain by application series, constructed as in Figure 3, at the same-quarter (a) and three-quarter (b) leads. Shaded: the pandemic (2020–21) and the test window (2023–25). *Source: outputs/tables/rq2_predictions.csv.*

## Figure 5 → Section 6.5 (replaces current Figure 2)

![Figure 5](fig5_weight_paths_indexed.png)

**Figure 5.** Estimated weight on applications at a three-quarter lead, from each expanding-window re-estimation. Each series is indexed to its own 2010–2019 average (= 100).

- Estimates are dated by forecast quarter; each uses data through three quarters earlier.
- Averages over 2022–2025: all applications 193; planned wages 132; high-propensity 112; corporate 111.
- The 2010 estimates rest on short samples.

*Source: outputs/tables/rq2_coefficient_paths_h3.csv.*

## Figure 6 → Section 6.6 (replaces current Figure 3)

![Figure 6](fig6_gain_vs_new_firm_share.png)

**Figure 6.** State accuracy gain from applications over 2010–2019, against the share of new establishments belonging to new firms (Business Dynamics Statistics, 2010–2019 average). One point per state (51). Holm adjustment is across the two leads. Exploratory. *Source: outputs/tables/rq4_state_data.csv, rq4_correlations.csv.*

## Figure 7 → Section 8

![Figure 7](fig7_live_forecasts_2026.png)

**Figure 7.** Pre-registered forecasts for 2026Q1–Q3, committed before BLS published any 2026 data (tag `prereg-live-forecasts-2026`).

- Each point is the average forecast across the 51 states, with equal weights as in the evaluation.
- Filled points: models estimated on all data. Hollow points: models estimated excluding 2020–2022.
- Actual values will be added as BLS publishes each quarter.
- The pre-registered test compares state-level squared errors, not these averages.

*Source: outputs/live_forecasts/live_forecasts_2026Q1-Q3.csv (read only).*

---

## Notes for the author

1. **Overlap.** Figure 3's line is the black line in Figure 4(b). It is kept as a stand-alone figure because it carries the main story (Section 6.4). Merging the two would save a figure.
2. **Equal versus size weighting in Figure 7.** Added up as a national total, the forecasts are lower and closer together, because large states forecast lower growth than small ones:
   - all-data applications models: 1.6–7.1 log points;
   - benchmark: 0.4–4.2 log points.

   The figure uses equal weights to match the scoring.
3. **Not yet checked:** *Journal of Forecasting*'s current figure requirements (file format, resolution, colour charges).
