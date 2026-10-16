<!--
DRAFT v1 — 2026-10-15; figures placed the same day (manuscript/figures/). Not yet reviewed by the author.
Target format: Journal of Forecasting (full research article). Verify current
author guidelines, length limits, and the AI-disclosure policy before submission.
Every number below comes from a committed output table or figure; sources are
listed in the "Source" notes under each table. Items marked [VERIFY] need
checking before submission.
-->

# Business Applications as a Leading Indicator of New Establishments: Evidence from U.S. States That the Relationship Changed After 2020

**Thomas Hamilton** — Independent Researcher

*Working draft, October 2026*

## Abstract

New business applications are published within weeks of being filed. Counts of new establishments arrive months later. This makes applications an appealing early indicator. I test whether state-level business applications from the Census Bureau's Business Formation Statistics improve out-of-sample forecasts of establishment births in the BLS Business Employment Dynamics, using a real-time design for 51 states. In a held-out 2023–2025 window, adding applications produces no detectable gain in accuracy over an autoregressive benchmark, and machine-learning models do no better. Naive pooled tests suggest otherwise, but they treat 612 state-quarters as independent observations when most of the variation is shared across states within a quarter. Once that dependence is accounted for, the apparent gains largely disappear. Over 2010–2025 the relationship is regime-dependent. It was modest but real before 2020, large in 2020–21, and absent afterwards. Before 2020, the narrower application series that Census designs to flag likely employers were better predictors than total applications, and gains were larger in states where more new establishments came from brand-new firms. After 2020 those advantages vanished, which argues against a simple change in the mix of applications as the explanation. Forecasts for 2026 were pre-registered before publication of the outcome data to test whether the breakdown persists.

**Keywords:** business formation; leading indicators; nowcasting; forecast evaluation; cross-sectional dependence; machine learning

**JEL codes:** C53, E32, L26, M13 [VERIFY codes against the journal's preferences]

## 1. Introduction

The Bureau of Labor Statistics' Business Employment Dynamics (BED) data are the main source for state-level counts of new private establishments in the United States. They arrive slowly: a quarter's establishment births are published roughly seven months after the quarter ends. The Census Bureau's Business Formation Statistics (BFS) track applications for an Employer Identification Number, the paperwork new businesses file with the IRS. BFS data are published monthly, about two weeks after each month ends. An application is an early, observable step toward a new business. If applications reliably precede establishment births, they offer a timely read on business formation months before the official count.

The evidence for this at the national level is encouraging. Asturias, Dinlersoz, Haltiwanger and Hutchinson (2023) document that growth in applications likely to become employers leads national employment growth. Asturias et al. (2024) show that adding applications to a dynamic factor model improves twelve-month employment forecasts, especially around turning points. No study I am aware of tests whether applications forecast establishment births *at the state level*. That is where the gap matters: BFS publishes state data monthly, while state BED counts arrive with the same seven-month delay as the national ones. Nor does any study compare simple econometric models with machine-learning methods for this purpose.

This paper does both. I build a quarterly panel of 51 states (the 50 states and the District of Columbia) from 2004 to 2025. I forecast year-over-year growth in establishment births with and without business applications, using a real-time design: every forecast uses only information that would have been available when it was made. The 2023–2025 window was locked away until the full evaluation design had been committed, so it was never used for model selection.

The results are less favourable to applications than the national evidence might suggest, but more informative:

1. **In the locked test window, applications do not detectably improve forecasts.** The best version, with applications leading births by three quarters, reduces mean squared error by 1.6% (95% CI −6.5% to +9.7%). Machine-learning models, with tuning confined to the pre-test period, do no better. The best, an elastic net, improves accuracy by 2.3% (95% CI −8.7% to +13.4%).
2. **Naive pooled tests badly overstate significance.** A standard nested-model test that treats each state-quarter as independent gives p = 0.0003 for the three-quarter lead. Allowing for correlated errors across states within a quarter and within states over time raises it to p ≈ 0.07.
3. **Over 2010–2025, the relationship depends on the period.** Before 2020, applications carried statistically detectable information and improved accuracy modestly in about two-thirds of states. In 2020–21, gains were large. From 2022 on they disappear, and at most leads adding applications slightly worsens forecasts.
4. **The narrower series held up no better.** Before 2020, the narrower application series that Census builds to flag likely employers were better predictors than total applications. Gains were also larger in states where brand-new firms accounted for more new establishments. Both point to a real relationship running through new-firm formation. After 2020 the narrower series' advantage disappeared. That is hard to reconcile with the most natural explanation, a shift in the mix of applications toward ones unlikely to become employers.

Several features of the study are aimed at credibility for a single-author, independently conducted analysis. The forecasting design, test window, and primary comparisons were committed, with dated version-control commits, to the project repository before evaluation. Every follow-up analysis was specified in a dated addendum before it was run, and the paper states where hypotheses were formed after seeing earlier results. Forecasts for 2026Q1–Q3 were committed before BLS published any 2026 data, so they provide a genuinely blind test of whether the breakdown persists (Section 8). All code, processed data, and outputs are available, and a fresh clone reproduces every table and figure with one command.

## 2. Related literature

**Business applications and business formation.** Bayard et al. (2018) construct the BFS from IRS Form SS-4 filings and show that applications, and especially applications with characteristics associated with hiring, predict which applicants become employer businesses. Dinlersoz, Dunne, Haltiwanger and Penciakova (2021) compare business formation in the Great Recession and the COVID-19 recession, documenting a 2020 surge in applications concentrated among those more likely to remain nonemployers. Decker and Haltiwanger (2022, 2023) relate the application surge to official establishment entry. They find that industries and places with larger surges saw more employer entry, and that roughly 36% of establishment births come from existing firms rather than new ones. Dinlersoz et al. (2026) decompose local startup rates into the rate of applications and the rate at which applications become employers. That decomposition helps explain why the information in applications may differ across places.

**Leading indicators of business dynamics.** Asturias et al. (2023, 2024) provide the closest antecedent: national, monthly, using a dynamic factor model, with nonfarm payroll employment as the outcome. Grieves, Mance and Witt (2023) nowcast the birth-death adjustment in the BLS Current Employment Statistics survey without using applications. Savagar and Galanakis (2026) find that real-time company incorporations in the United Kingdom lead official business-demography statistics. Borup and Schütte (2022) show that internet search data improve forecasts of employment growth at the state as well as national level, and provide a template for state-panel forecast comparisons.

**Econometric versus machine-learning forecasts.** Goulet Coulombe, Leroux, Stevanovic and Surprenant (2022) find that machine learning's gains in macroeconomic forecasting come mainly from nonlinearity in uncertain periods. Medeiros, Vasconcelos, Veiga and Zilberman (2021) find large gains from random forests in forecasting inflation. The present setting differs: a short, noisy panel of state-level counts, in which flexible methods have little data to learn from.

**Forecast evaluation with panels.** Comparing nested forecasting models requires the adjustment of Clark and West (2007), because the larger model is penalised for estimating parameters that are zero under the null. Diebold and Mariano's (1995) test was designed for non-nested comparisons. Recent work develops tests of equal predictive accuracy pooled across panel units under cross-sectional dependence (Akgun, Pirotte, Urga & Yang 2024; Qu, Timmermann & Zhu 2024). This paper's evidence shows why that matters in practice: in a state panel, ignoring dependence across states turns a marginal result into an apparently overwhelming one.

## 3. Data

**Business applications.** Monthly state-level BFS data, July 2004 to September 2026, not seasonally adjusted, aggregated to quarters. The primary series is all business applications (BA). Three narrower series are nested within it, as defined by the Census Bureau:

- **High-propensity applications (HBA):** applications with a high propensity of becoming employer businesses, based on characteristics such as corporate form, planned wages, intent to hire, and selected industries.
- **Applications with planned wages (WBA):** HBA that report a first wages-paid date.
- **Corporate applications (CBA):** HBA from corporations.

Two documented changes matter here. In November 2021 Census redefined HBA for data from 2012 onward and rescaled earlier years. In February 2026 it removed internet-sales applications from HBA and CBA after a spike in such filings. The data used here postdate both changes.

**Establishment births.** Quarterly state-level counts of private-sector establishment births from the BLS Business Employment Dynamics, 1992Q3 to 2025Q4, not seasonally adjusted. The outcome is the year-over-year log change. BED has no archive of historical vintages, so the analysis uses the vintage retrieved on 14 October 2026 throughout. Section 9 discusses the implications.

Figure 1 shows both series at the national level. Applications surged in 2020 and peaked in 2020Q3. Establishment births peaked three quarters later, in 2021Q2.

![Figure 1](figures/fig1_national_applications_births.png)

**Figure 1.** National year-over-year change in business applications (a) and establishment births (b), 2005Q3–2025Q4, in log points (100 × the log change from the same quarter a year earlier), not seasonally adjusted. Shaded: the pandemic (2020–21) and the test window (2023–25). *Sources: Census Bureau, Business Formation Statistics; BLS, Business Employment Dynamics.*

**New-firm share of entry.** From the Census Business Dynamics Statistics (state × firm age, annual, through 2023): the share of new establishments belonging to firms in their first year. Over 2010–2019 the state average is 61% (range 54%–69%). That implies about 39% of new establishments come from existing firms, close to Decker and Haltiwanger's (2022) figure.

**Seasonality.** Not-seasonally-adjusted establishment births and applications both show irregular spikes in the first quarter of the year. For applications, 21% of state first-quarter observations jump by more than 40% from the previous quarter, compared with almost none in other quarters. Of the 41 state-quarters in which both series jump by more than 30% at once, 36 are first quarters. Year-over-year differencing removes a stable seasonal pattern but not a pattern whose size varies by year. Every model therefore includes a quarter-of-year indicator. Section 6.7 shows the results are unchanged with the official seasonally adjusted series.

*Source: data/MANIFEST.md (retrieval dates, URLs, SHA-256 checksums); literature/phase3_findings.md; literature/rq2_findings.md §6.*

## 4. Forecasting design

**Target and benchmark.** The target is the year-over-year log change in state establishment births. The benchmark is a pooled panel regression of the target on its own lags at 3, 4 and 5 quarters, with state and quarter-of-year indicators.

**Adding applications.** For lead h = 0, …, 4, the augmented model adds the year-over-year log change in applications h quarters before the target quarter. The benchmark is nested in each augmented model. The primary leads, fixed in advance, are h = 0 (same quarter) and h = 3. The choice of h = 3 was motivated by exploratory correlations in the development period.

**Machine learning.** Elastic net, random forest and gradient boosting receive the benchmark's own lags, all five application lags, and state and quarter indicators. Tuning settings are chosen once, by forward-chaining cross-validation over whole quarters within the 2004–2022 development window, and then held fixed. The best of the three by validation error (the elastic net) is the primary machine-learning comparison. An equal-weight combination of the h = 3 regression and the best machine-learning model is also evaluated.

**Real time.** BED births appear about three quarters after the reference quarter; applications appear within weeks. A forecast for quarter t is therefore estimated only on rows whose own target quarter is at least three quarters earlier (t − 3 or before), and uses only lags of births at least three quarters old. Each model is re-estimated for every forecast quarter on an expanding window.

**Windows.** The development window runs to 2022Q4. The test window, 2023Q1–2025Q4, is 12 quarters × 51 states = 612 forecasts; it was not touched until the evaluation design had been committed. Section 6.4 extends the same procedure back to 2010; those years are pseudo-out-of-sample, because they informed exploratory choices.

## 5. Evaluation and inference

Accuracy is compared through the difference in squared forecast errors between the benchmark and a model, reported as a percentage of the benchmark's mean squared error (MSE). A positive value means the model is more accurate. Two related questions are kept separate:

- **Does adding applications carry predictive information?** For nested comparisons, this is assessed with the Clark–West (2007) adjusted statistic, tested one-sided.
- **Did adding applications actually make forecasts more accurate in this sample?** This uses the unadjusted difference, tested two-sided.

The first can be "yes" while the second is "no", because estimating extra parameters adds noise.

The 612 state-quarters are not independent. A national shock moves forecast errors in all states in the same quarter, and each state's errors are correlated over time. I therefore report standard errors that are:

- naive (assuming independence);
- clustered by state;
- clustered by quarter;
- two-way clustered by state and quarter (Cameron, Gelbach & Miller 2011).

With only 12 quarters, conventional clustered standard errors can be too small (Cameron, Gelbach & Miller 2008). I therefore also report a wild cluster bootstrap by quarter, with Webb (2023) six-point weights and 9,999 draws.

The three primary comparisons (applications at h = 0 and h = 3, and the best machine-learning model) are adjusted for multiple testing with Holm's (1979) procedure.

Two methods named in the original plan were replaced, as disclosed in the plan itself. The model confidence set (Hansen, Lunde & Nason 2011) was replaced by Holm adjustment. The panel tests of Qu, Timmermann and Zhu (2024) and Akgun et al. (2024) were replaced by the clustered and bootstrap tests above. In both cases, no reference implementation was available to build on safely.

## 6. Results

### 6.1 The locked test window, 2023–2025

**Table 1. Accuracy in the 2023–2025 test window (612 state-quarters)**

| Model | RMSE | Accuracy vs. benchmark (% of MSE) | 95% CI | Two-way p |
|---|---|---|---|---|
| Benchmark (own lags only) | 0.1798 | — | — | — |
| + applications, h = 0 | 0.1824 | −3.0 | −8.1 to +2.2 | 0.26 |
| + applications, h = 1 | 0.1806 | −0.9 | −8.4 to +6.6 | 0.81 |
| + applications, h = 2 | 0.1800 | −0.2 | −8.2 to +7.8 | 0.96 |
| + applications, h = 3 | 0.1784 | +1.6 | −6.5 to +9.7 | 0.70 |
| + applications, h = 4 | 0.1791 | +0.8 | −6.1 to +7.6 | 0.82 |
| Elastic net (best ML) | 0.1777 | +2.3 | −8.7 to +13.4 | 0.68 |
| Random forest | 0.1806 | −0.8 | −13.3 to +11.6 | 0.89 |
| Gradient boosting | 0.1824 | −2.9 | −13.8 to +8.0† | 0.64† |
| Combination (h = 3 + elastic net) | 0.1771 | +3.0 | −6.2 to +12.1 | 0.53 |

*Notes: Accuracy is the reduction in mean squared error relative to the benchmark; positive values favour the model. †Wild cluster bootstrap interval and p-value; the two-way clustered standard error was unstable for this model. Source: outputs/tables/phase5_model_performance.csv, phase5_comparisons.csv, phase5x_detectable_effects.csv.*

No model detectably improves on the benchmark (Table 1; Figure 2b). The confidence intervals are informative about what can be ruled out:

- Same-quarter applications cannot have improved accuracy by more than about 2%.
- Applications three quarters ahead cannot have improved it by more than about 10%.
- Modest gains of a few percent cannot be excluded.

At 80% power, the minimum detectable improvement is 7–12% for the regression models and 10–18% for the machine-learning models.

### 6.2 Naive versus dependence-robust inference

Figure 2 shows each point estimate with two intervals: one that treats the 612 state-quarters as independent, and one that allows for correlation across states within a quarter and within states over time. The p-values under every method are in Appendix Table A1.

![Figure 2](figures/fig2_test_window_intervals.png)

**Figure 2.** Test-window comparisons with the benchmark, 2023Q1–2025Q4 (612 state-quarters). Grey intervals treat every state-quarter as independent; black intervals are two-way clustered by state and quarter. Panel (a): Clark–West adjusted loss difference, 90% intervals, so a black interval lying wholly above zero corresponds to rejection at the 5% level in the one-sided information test; the tree-based models are omitted because the adjustment is not meaningful for them (Section 6.3). Panel (b): reduction in mean squared error, 95% intervals; positive values favour the model. †Robust interval from the wild cluster bootstrap by quarter, because the two-way clustered standard error was unstable for this model. *Source: outputs/tables/phase5_comparisons.csv.*

Taken at face value, the naive intervals say applications carry significant information at every lead except the same quarter (Figure 2a). Most of that evidence comes from treating 51 states in the same quarter as independent. Clustering by state alone barely changes the picture. Clustering by quarter, or both ways, does: the three-quarter-lead result becomes marginal (p = 0.076 two-way; p = 0.067 by wild bootstrap), and the others are not significant. After Holm adjustment across the three primary comparisons, the smallest p-value is 0.14.

The same problem appears in the accuracy comparison, in the opposite direction. The naive interval for same-quarter applications lies wholly below zero (naive p = 0.03), which would suggest that applications made forecasts significantly *worse*. The robust interval does not (two-way p = 0.26; Figure 2b).

The wild bootstrap and the two-way clustered results agree closely, so the conclusion does not hinge on the few-cluster correction.

### 6.3 Machine learning

None of the three machine-learning models is detectably more accurate than the benchmark. The random forest and gradient boosting are *less* accurate on average. Yet the random forest appears highly significant under the Clark–West statistic (two-way p = 0.014).

The Clark–West adjustment credits the larger model for the dispersion between its forecasts and the benchmark's. That is appropriate when the larger model nests the smaller one linearly, and misleading for a flexible nonlinear model whose forecasts differ substantially from the benchmark's. For the tree-based models only the accuracy comparison is meaningful, and it shows no gain.

### 6.4 Performance over time, 2010–2025

To see whether the test-window result reflects a lasting property or a particular period, I extend the same procedure to forecast every quarter from 2010Q1. The 2023–2025 forecasts from this extended run are identical to those in Section 6.1.

**Table 2. Accuracy and information by period, all applications**

| Period | Lead | Accuracy vs. benchmark (%) | Two-way p (accuracy) | Information test, two-way p | States where model more accurate |
|---|---|---|---|---|---|
| 2010–2019 (40 quarters) | h = 0 | +2.6 | 0.19 | 0.0001 | 67% |
| | h = 1 | +3.8 | 0.15 | 0.0001 | 76% |
| | h = 3 | +0.8 | 0.23 | 0.004 | 65% |
| 2020–2021 (8 quarters) | h = 0 | +11.3 | 0.31 | 0.064 | 80% |
| | h = 1 | +20.1 | 0.22 | 0.046 | 90% |
| | h = 3 | +11.9 | 0.16 | 0.070 | 92% |
| 2022–2025 (16 quarters) | h = 0 | −7.1 | 0.079 | 0.85 | 18% |
| | h = 1 | −4.7 | 0.37 | 0.44 | 33% |
| | h = 3 | −3.7 | 0.66 | 0.27 | 37% |

*Note: 2010–2022 is pseudo-out-of-sample. Inference within 2020–21 rests on 8 quarters. Source: outputs/tables/phase5x_by_period.csv.*

The pattern has three phases (Table 2; Figure 3).

- **2010–2019:** applications carried statistically detectable information at leads of 0–3 quarters, robust to dependence. At the four-quarter lead, p = 0.06. Accuracy gains were small, 1–4%, and positive in about two-thirds of states.
- **2020–2021:** gains were large, 11–20%, positive in 80–92% of states.
- **2022 onward:** gains disappear, and at most leads adding applications makes forecasts slightly worse in most states.

Four quarters, 2021Q2 to 2022Q1, contribute more than the entire net gain over the sixteen years.

![Figure 3](figures/fig3_cumulative_gain_ba_h3.png)

**Figure 3.** Cumulative accuracy gain from adding applications at a three-quarter lead, 2010Q1–2025Q4. Each quarter adds the reduction in squared error relative to the benchmark, averaged across states. The running total is expressed as a percentage of the benchmark's total squared error over the whole period, so the final value (3.0%) is the accuracy gain over 2010–2025 as a whole. A rising line means the model with applications beat the benchmark that quarter. 2010–2022 is pseudo-out-of-sample. *Source: outputs/tables/rq2_predictions.csv.*

### 6.5 Which application series carries the signal?

Figure 4 repeats the cumulative comparison for each of the four application series. Period averages are in Appendix Table A2.

![Figure 4](figures/fig4_cumulative_gain_by_series.png)

**Figure 4.** Cumulative accuracy gain by application series, constructed as in Figure 3, at the same-quarter (a) and three-quarter (b) leads. Shaded: the pandemic (2020–21) and the test window (2023–25). *Source: outputs/tables/rq2_predictions.csv.*

**Before 2020, the narrower series were the better predictors.** In direct comparisons with the all-applications model, Holm-adjusted across 24 comparisons:

- High-propensity applications were 4.8% more accurate at the same-quarter lead (p < 0.001; better in 96% of states).
- Applications with planned wages were 3.7% more accurate at the three-quarter lead (p = 0.012).

The same-quarter advantage holds when the comparison is restricted to 2013–2019, after Census's 2012 redefinition of the high-propensity series: +4.7% for both HBA and WBA, p < 0.001. The three-quarter-lead advantage is weaker there.

**After 2020, the advantage vanished.** No series improved on the benchmark from 2022 on, and the narrower series did slightly worse than total applications. High-propensity applications at the three-quarter lead were 5.9% less accurate than the all-applications model (Holm-adjusted p = 0.07).

**How much weight the models put on applications.** Apart from the first estimates in 2010, which rest on short samples, the estimated weight on all applications at the three-quarter lead stayed between about 0.11 and 0.20 through 2021, averaging 0.18 over 2010–2019. Once the pandemic surge entered the estimation sample it rose sharply, peaking at 0.41 in 2022, and has since settled at about 0.32–0.34, roughly double its pre-2020 level. Put in elasticity terms:

- **Before 2020:** a 10% year-over-year rise in applications was associated with a rise of about 1.8% in establishment births three quarters later.
- **Models estimated through the pandemic:** they assume roughly 3.3%.

The narrower series moved much less (Figure 5). Indexed to each series' own 2010–2019 average, the weight on all applications averaged 193 over 2022–2025. The weights on the narrower series averaged 132 (planned wages), 112 (high-propensity) and 111 (corporate).

![Figure 5](figures/fig5_weight_paths_indexed.png)

**Figure 5.** Estimated weight on applications at a three-quarter lead, from each expanding-window re-estimation, by series. Each series is indexed to its own 2010–2019 average (= 100). Estimates are dated by forecast quarter; each uses data through three quarters earlier. The 2010 estimates rest on short samples. *Source: outputs/tables/rq2_coefficient_paths_h3.csv.*

This bears directly on the most natural explanation for the breakdown. Dinlersoz et al. (2021; Census CES Working Paper 21-01) document that the 2020 surge was concentrated among applications more likely to remain nonemployers. If that compositional shift were the cause, filtering for employer intent should have preserved the signal. It did not. Moreover, the high-propensity series' estimated weight barely changed after 2020 (+12%, against +93% for total applications), yet its forecasts still deteriorated. So a pandemic-inflated weight cannot be the whole story either. The relationship itself appears to have changed.

*Source: outputs/tables/rq2_vs_BA_direct.csv, rq2_hba_definition_check.csv, rq2_coefficient_paths_h3.csv, phase5x_bfs_coefficient_path_h3.csv.*

### 6.6 New-firm share and the mechanism (exploratory)

If applications predict births because they track new firms, gains should be larger where new firms account for more new establishments. Across states, the 2010–2019 same-quarter gain from applications is positively rank-correlated with the state's new-firm share (Spearman ρ = 0.37, Holm p = 0.014; Figure 6). The three-quarter-lead correlation is weak (ρ = 0.11, p = 0.44). After 2020 there is no relationship. This analysis is exploratory and cross-sectional, and the new-firm share comes from a different statistical system than the outcome.

![Figure 6](figures/fig6_gain_vs_new_firm_share.png)

**Figure 6.** State accuracy gain from applications over 2010–2019, against the share of new establishments belonging to new firms (Business Dynamics Statistics, 2010–2019 average). One point per state (51). Holm adjustment is across the two leads. *Source: outputs/tables/rq4_state_data.csv, rq4_correlations.csv.*

### 6.7 Robustness

**Table 3. Robustness, test window**

| Variant | h = 3 accuracy (%) | h = 3 information test, two-way p | Best ML accuracy (%) |
|---|---|---|---|
| Primary | +1.6 | 0.076 | +2.3 |
| Official seasonally adjusted series, no quarter indicator | +1.7 | 0.065 | +2.9 |
| Winsorized, scored against winsorized actuals | +0.0 | 0.117 | −0.4 |
| Winsorized, scored against raw actuals | +0.9 | 0.092 | −0.0 |

*Notes: Winsorizing clips at fixed 1st/99th percentiles from the development window. The seasonally adjusted variant is not a valid real-time exercise, because seasonal factors are estimated with later data; it is reported only as a check. Source: outputs/tables/phase5x_robustness_comparisons.csv.*

The results do not depend on the treatment of seasonality or on a few extreme quarters (Table 3).

## 7. Discussion

Three conclusions follow.

**First, for users of business applications as a state-level indicator, the relationship was useful before 2020 and has not been since.** Before 2020, the narrower series Census designs to flag likely employers were the better predictors. In 2023–2025, adding any application series to a simple autoregressive model did not improve forecasts of establishment births. Models estimated on data through the pandemic weight applications about twice as heavily as the earlier relationship would warrant. The relationship may recover. The pre-registered forecasts in Section 8 are designed to detect that.

**Second, the post-2020 change is not easily explained by the composition of applications.** It affects even the series that screen for employer intent, and those series had been the better predictors. Two other broad candidates remain, and this paper tests neither:

- *A change in the application series themselves.* Applications may relate differently to eventual employer formation, for example because more applicants form businesses that open establishments with a longer or less predictable delay.
- *A change in the outcome.* Cao, Hyatt, Mukoyama and Sager (2026) document a growing divergence between BLS and Census counts of establishments. If the BLS establishment universe has changed in ways that do not track new-business formation, any indicator of business formation would lose predictive power for it.

Separating these explanations is a natural next step.

**Third, for forecast evaluation with state panels, the dependence structure is not a technicality.** In this application, a naive pooled test turned a marginal result into an apparently decisive one. The relevant sample size is closer to the number of quarters than to the number of state-quarters. Studies evaluating forecasts across states or regions should report tests robust to common shocks.

## 8. A pre-registered test with new data

The interpretation in Section 7 was formed after seeing the 2023–2025 results, and the test window is short. The only clean test is data no one has seen. Before BLS published any 2026 establishment-birth data, I committed forecasts for 2026Q1–Q3 for all 51 states, under the tag `prereg-live-forecasts-2026`. The forecast file's SHA-256 hash is `8e0751c9…841fc`. [VERIFY: add the public timestamp record and its date once posted.]

The forecasts were produced with exactly the procedure above, in two variants: one estimated on all data, and one excluding 2020–2022 from estimation (Figure 7). The pre-registered readings are:

- **The paper's claim:** applications still do not improve forecasts.
- **An alternative:** excluding the pandemic years from estimation helps.

The scoring code was committed with the forecasts. 2026Q1 is scheduled for release on 28 October 2026.

![Figure 7](figures/fig7_live_forecasts_2026.png)

**Figure 7.** Pre-registered forecasts for 2026Q1–Q3, committed before BLS published any 2026 data. Each point is the average forecast across the 51 states, with equal weights as in the evaluation. Filled points: models estimated on all data. Hollow points: models estimated excluding 2020–2022. The pre-registered test compares state-level squared errors, not these averages. [Actual values to be added as each quarter is published.] *Source: outputs/live_forecasts/live_forecasts_2026Q1-Q3.csv.*

Before the first release, I recorded one fact that bears on how to read it (project research log, 15 October 2026).

- **What the narrower series did.** Total applications rose sharply through 2025, by 21 log points year over year nationally in 2025Q4. High-propensity applications rose by only 1–5 log points over 2025Q2–Q4, and applications with planned wages fell.
- **Why it matters.** Models estimated on all data weight total applications about twice as heavily as before 2020, so they turn that rise into the high 2026 forecasts in Figure 7.
- **Two causes to separate.** A shortfall of actual births against those forecasts would therefore reflect two things: the post-2020 change documented above, and a 2025 shift in which kinds of applications are rising. The frozen forecasts from the high-propensity series, which are among the pre-registered secondary comparisons, help separate the two.

*[Results to be added as each quarter is published. Report every quarter regardless of outcome.]*

## 9. Limitations

- **Hypotheses formed after seeing results.** The regime interpretation and the composition hypothesis were formed after the test-window results. The follow-up analyses were specified before they were run, but they are not blind tests; Section 8 provides one.
- **Pseudo-out-of-sample years.** The 2010–2022 results informed exploratory choices.
- **Final-vintage data.** BED offers no archive of historical vintages, so the analysis uses final-vintage data. Real-time revisions could change the picture, especially around 2020–21. The live forecasts in Section 8 are genuinely real-time.
- **Few clusters.** The test window and the pandemic period contain 12 and 8 quarters. Conclusions about those periods rest on point estimates and their consistency across states as much as on p-values.
- **Methods replaced.** Two planned methods were replaced by standard alternatives (Section 5).
- **Prediction only.** Nothing here identifies what caused the relationship to change.

## 10. Conclusion

Business applications looked like a natural early indicator of state establishment births, and before 2020 they modestly were one. In 2020–21 they were a strong one. Since then they have not improved forecasts, and the narrower application series that used to predict best have fared no better. Anyone using applications as a state-level signal of new establishments should treat the post-2020 relationship as unreliable until new data show otherwise. The pre-registered forecasts reported in Section 8 will provide that evidence as it arrives.

---

## Data and code availability

All code, processed data, outputs, and the pre-analysis plan with its four addenda are in the project repository [repository URL — VERIFY: currently private; decide on public release before submission]. One command (`replication/run_all.py`) regenerates every table and figure from the committed data.

- On 15 October 2026, a fresh clone with a new, pinned environment reproduced every committed table and figure at that point. The largest numeric difference was 1.1e-14.
- After the final analyses were added, a full re-run reproduced all 34 tables and 7 figures. That run also confirmed the pre-registered forecast file is regenerated exactly. Raw data are public from the Census Bureau and BLS; retrieval dates and SHA-256 checksums are listed in `data/MANIFEST.md`.

## Use of AI tools

[VERIFY wording against the target journal's current policy.] This research used an AI assistant (Claude, Anthropic) through Claude Code, for:

- literature discovery and verification;
- writing analysis code;
- running analyses;
- drafting text.

The author directed the research, made all substantive decisions recorded in the project log, and is responsible for the content. Every citation was checked against a publisher or repository page. A dated record of AI contributions is in the project's research log.

## Pre-registration and deviations

The pre-analysis plan and four addenda are in the repository, each committed before the analyses it governs.

Three errors in an earlier run of the main evaluation were found and corrected before this draft:

- machine-learning tuning folds that were not time-ordered;
- a "best model" that had been fixed in advance instead of selected;
- a mismatch between the naive and robust tests.

None involved test data leaking into training. They are documented in `literature/phase5_findings.md`.

## References

*Each work was confirmed to exist, with the title, venue and year shown, on a publisher, repository, or agency page during the project. DOIs shown were seen on those pages. Before submission, still check: author first names and initials (not systematically verified), and anything marked [VERIFY].*

Akgun, O., Pirotte, A., Urga, G., & Yang, Z. (2024). Equal predictive ability tests based on panel data with applications to OECD and IMF forecasts. *International Journal of Forecasting*, 40(1), 202–228. https://doi.org/10.1016/j.ijforecast.2023.02.001

Asturias, J., Dinlersoz, E., Haltiwanger, J., & Hutchinson, R. (2023). Are business applications early economic indicators? *AEA Papers and Proceedings*, 113, 151–155. https://doi.org/10.1257/pandp.20231053

Asturias, J., Dinlersoz, E., Haltiwanger, J., Hutchinson, R., & Plumb, J. (2024). *Business applications as a leading economic indicator?* NBER Working Paper 33224. https://doi.org/10.3386/w33224

Bayard, K., Dinlersoz, E., Dunne, T., Haltiwanger, J., Miranda, J., & Stevens, J. (2018). *Early-stage business formation: An analysis of applications for employer identification numbers.* NBER Working Paper 24364.

Borup, D., & Schütte, E. C. M. (2022). In search of a job: Forecasting employment growth using Google Trends. *Journal of Business & Economic Statistics*, 40(1), 186–200.

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427. https://doi.org/10.1162/rest.90.3.414

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2011). Robust inference with multiway clustering. *Journal of Business & Economic Statistics*, 29(2), 238–249. https://doi.org/10.1198/jbes.2010.07136

Cao, D., Hyatt, H., Mukoyama, T., & Sager, E. (2026). *New U.S. business establishments: Surging or stalling?* Center for Economic Studies Working Paper 26-36 / FEDS 2026-40. [VERIFY author first names]

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, 138(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Decker, R. A., & Haltiwanger, J. (2022). Business entry and exit in the COVID-19 pandemic: A preliminary look at official data. *FEDS Notes*, Board of Governors of the Federal Reserve System, May 6, 2022.

Decker, R. A., & Haltiwanger, J. (2023). Surging business formation in the pandemic: Causes and consequences? *Brookings Papers on Economic Activity*, Fall 2023. [VERIFY page range: sources disagree, 249–302 vs. 249–316]

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263.

Dinlersoz, E., Dunne, T., Haltiwanger, J., & Penciakova, V. (2021). Business formation: A tale of two recessions. *AEA Papers and Proceedings*, 111, 253–257. Also Center for Economic Studies Working Paper 21-01. [VERIFY DOI]

Dinlersoz, E., Dunne, T., Haltiwanger, J., & Penciakova, V. (2026). *The local origins of business formation: Entry as a two-stage process.* NBER Working Paper 34881.

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica*, 74(6), 1545–1578.

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics*, 37(5), 920–964. https://doi.org/10.1002/jae.2910

Grieves, C., Mance, S., & Witt, R. (2023). *Predicting the effect of business births and deaths on the Current Employment Statistics survey.* BLS research paper. [VERIFY author first names]

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica*, 79(2), 453–497. https://doi.org/10.3982/ECTA5771

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.

Medeiros, M. C., Vasconcelos, G. F. R., Veiga, Á., & Zilberman, E. (2021). Forecasting inflation in a data-rich environment: The benefits of machine learning methods. *Journal of Business & Economic Statistics*, 39(1), 98–119. https://doi.org/10.1080/07350015.2019.1637745

Qu, R., Timmermann, A., & Zhu, Y. (2024). Comparing forecasting performance with panel data. *International Journal of Forecasting*, 40(3), 918–941. https://doi.org/10.1016/j.ijforecast.2023.08.001

Savagar, A., & Galanakis, Y. (2026). *Tracking the economy through firm creation: Evidence from real-time administrative data.* arXiv:2606.01307.

Webb, M. D. (2023). Reworking wild bootstrap-based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858. https://doi.org/10.1111/caje.12661

U.S. Bureau of Labor Statistics. Business Employment Dynamics. https://www.bls.gov/bdm/ (data retrieved 14 October 2026).

U.S. Census Bureau. Business Formation Statistics: Methodology; Definitions. https://www.census.gov/econ/bfs/ (data retrieved 14 October 2026).

U.S. Census Bureau. Business Dynamics Statistics. https://www.census.gov/programs-surveys/bds.html (data retrieved 15 October 2026).

---

## Appendix: additional tables

**Table A1. Information tests (Clark–West, one-sided p-values), test window**

| Comparison | Naive | By state | By quarter | Two-way | Wild bootstrap (quarter) |
|---|---|---|---|---|---|
| Applications, h = 0 | 0.47 | 0.47 | 0.48 | 0.48 | 0.49 |
| Applications, h = 1 | 0.012 | 0.040 | 0.19 | 0.20 | 0.19 |
| Applications, h = 2 | 0.005 | 0.018 | 0.15 | 0.16 | 0.16 |
| Applications, h = 3 | 0.0003 | 0.008 | 0.057 | 0.076 | 0.067 |
| Applications, h = 4 | 0.008 | 0.030 | 0.13 | 0.15 | 0.15 |
| Elastic net | 0.0001 | 0.003 | 0.037 | 0.052 | 0.048 |

*Source: outputs/tables/phase5_comparisons.csv.*

**Table A2. Accuracy vs. benchmark by application series (% of benchmark MSE)**

| Period | Lead | All (BA) | High-propensity (HBA) | Planned wages (WBA) | Corporate (CBA) |
|---|---|---|---|---|---|
| 2010–2019 | h = 0 | +2.6 | +7.3 | +5.3 | +4.6 |
| | h = 3 | +0.8 | +3.9 | +4.5 | +1.8 |
| 2020–2021 | h = 0 | +11.3 | +19.4 | +19.7 | +16.1 |
| | h = 3 | +11.9 | +22.6 | +17.2 | +6.3 |
| 2022–2025 | h = 0 | −7.1 | −10.1 | −7.5 | −9.3 |
| | h = 3 | −3.7 | −9.8 | −4.9 | −2.5 |

*Source: outputs/tables/rq2_by_period.csv.*
