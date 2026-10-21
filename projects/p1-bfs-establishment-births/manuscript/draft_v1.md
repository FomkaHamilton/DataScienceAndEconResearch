<!--
DRAFT v1. Figures placed and text copy-edited 2026-10-15; restructured for the
Journal of Forecasting (title page, statements, Wiley AI disclosures) 2026-10-19.
Not yet reviewed by the author.
Free Format applies at first submission (any consistent reference style; APA at
acceptance). Every number below comes from a committed output table or figure;
sources are listed in the "Source" notes under each table and figure. Text in
square brackets needs the author's input or confirmation before submission.
Word version: python manuscript/build_docx.py (requirements-manuscript.txt).
-->

# Business Applications as a Leading Indicator of New Establishments: Evidence from U.S. States That the Relationship Changed After 2020

**Running title:** Applications and Establishment Births

**Thomas Hamilton**, Independent Researcher, Phoenix, Arizona, USA\
Correspondence: hamiltontja@gmail.com; ORCID: https://orcid.org/0009-0003-4603-3481

**Acknowledgments.** The author used Claude (Anthropic; models Claude Opus 5.5 and Claude Sonnet 5, accessed through the Claude Code tool in October 2026) to draft and edit the manuscript text. [Confirm after your rewrite and adjust the description, for example: "to produce a first draft of the manuscript, which the author rewrote."] The author reviewed and revised all text and takes full responsibility for the content. The use of the same tool in the research itself is described in Section 4.

**Data availability statement.** The code, processed data and outputs that support the findings of this study are openly available in Zenodo at https://doi.org/[DOI to be added] and on GitHub at https://github.com/FomkaHamilton/DataScienceAndEconResearch. The raw data are publicly available from the U.S. Census Bureau (Business Formation Statistics; Business Dynamics Statistics) and the U.S. Bureau of Labor Statistics (Business Employment Dynamics); retrieval dates and checksums are listed in the repository's data manifest.

**Funding statement.** The author received no funding for this research.

**Conflict of interest disclosure.** The author declares no conflicts of interest.

**Ethics approval statement.** Not applicable: the study uses publicly available, aggregate government statistics and involves no human participants.

**Permission to reproduce material from other sources.** Not applicable.

<!-- pagebreak -->

## Abstract

New business applications are published within weeks of being filed, whereas counts of new establishments arrive months later. This makes applications an appealing early indicator. I test whether state-level business applications from the Census Bureau's Business Formation Statistics improve out-of-sample forecasts of establishment births in the BLS Business Employment Dynamics, using a real-time design for the 50 states and the District of Columbia. In a held-out 2023–2025 window, adding applications produces no detectable gain in accuracy over an autoregressive benchmark, and machine-learning models do no better. Naive pooled tests suggest otherwise, but they treat 612 state-quarters as independent observations when much of the variation is shared across states within a quarter; once that dependence is accounted for, the apparent gains largely disappear. Over 2010–2025 the relationship is regime-dependent: modest but real before 2020, large in 2020–21, and absent afterward. Before 2020, the narrower application series that Census constructs to flag likely employers were better predictors than total applications, and gains were larger in states where more new establishments came from brand-new firms. After 2020 those advantages vanished, which argues against a simple change in the mix of applications as the explanation. Forecasts for 2026 were pre-registered before the outcome data were published, to test whether the breakdown persists.

**Keywords:** business formation; leading indicators; nowcasting; forecast evaluation; cross-sectional dependence; machine learning

**JEL codes:** C53, E32, L26, M13, R11

## 1. Introduction

The Bureau of Labor Statistics' Business Employment Dynamics (BED) data are the main source of state-level counts of new private establishments in the United States. They arrive slowly: a quarter's establishment births are published roughly seven months after the quarter ends. The Census Bureau's Business Formation Statistics (BFS) track applications for an Employer Identification Number, the paperwork new businesses file with the IRS, and are published monthly, about two weeks after each month ends. An application is an early, observable step toward a new business. If applications reliably precede establishment births, they offer a timely read on business formation months before the official count.

The evidence at the national level is encouraging. Asturias, Dinlersoz, Haltiwanger and Hutchinson (2023) document that growth in applications likely to become employers leads national employment growth, and Asturias et al. (2024) show that adding these applications to a dynamic factor model improves twelve-month forecasts of nonfarm employment growth, especially in the years following the turning points of the Great Recession and the COVID-19 pandemic. At the state level, Bayard et al. (2018) show that projections built from application characteristics track the number of new employer businesses out of sample, and Decker and Haltiwanger (2023) estimate the elasticity of state establishment births with respect to likely-employer applications in state-by-quarter regressions. No study I am aware of, however, tests whether applications improve real-time, out-of-sample forecasts of establishment births at the state level, which is where the timing gap matters most: BFS publishes state data monthly, while state BED counts arrive with the same seven-month delay as the national ones. Nor, to my knowledge, does any study compare simple econometric models with machine-learning methods for this purpose.

This paper does both. I build a quarterly panel of the 50 states and the District of Columbia from 2004 to 2025 and forecast year-over-year growth in establishment births with and without business applications, using a real-time design in which every forecast uses only information that would have been available when it was made. The 2023–2025 window was held out until the full evaluation design had been committed, so it played no role in model selection.

The results are less favorable to applications than the national evidence might suggest, but they are informative. First, in the locked test window, applications do not detectably improve forecasts. The best specification, with applications leading births by three quarters, reduces mean squared error by 1.6% (95% CI −6.5% to +9.7%). Machine-learning models, tuned only on the pre-test period, do no better; the best of them, an elastic net, improves accuracy by 2.3% (95% CI −8.7% to +13.4%). Second, naive pooled tests substantially overstate significance. A standard nested-model test that treats each state-quarter as independent gives p = 0.0003 for the three-quarter lead; allowing for correlated errors across states within a quarter and within states over time raises it to about 0.07.

Third, over 2010–2025 the relationship depends on the period. Before 2020, applications carried statistically detectable information and modestly improved accuracy in about two-thirds of states. In 2020–21 the gains were large. From 2022 onward they disappear, and at most leads adding applications slightly worsens forecasts. Fourth, the narrower series held up no better. Before 2020, the narrower application series that Census constructs to flag likely employers were better predictors than total applications, and gains were larger in states where brand-new firms accounted for more new establishments; both patterns are consistent with a relationship that operates through new-firm formation. After 2020 the advantage of the narrower series disappeared, which is hard to reconcile with the most natural explanation for the breakdown: a shift in the mix of applications toward those unlikely to become employers.

Several features of the design limit the scope for specification search. The forecasting design, test window, and primary comparisons were committed to the project repository, in dated version-control commits, before evaluation. Each follow-up analysis was specified in a dated addendum before it was run, and the paper identifies the hypotheses that were formed after earlier results had been seen. Forecasts for 2026Q1–Q3 were committed before BLS published any 2026 data, so they provide a blind test of whether the breakdown persists (Section 8). All code, processed data, and outputs are available, and a fresh clone of the repository reproduces every table and figure with one command.

## 2. Related literature

**Business applications and business formation.** Bayard et al. (2018) construct the BFS from IRS Form SS-4 filings and show that applications, especially those with characteristics associated with hiring, predict which applicants become employer businesses. Dinlersoz, Dunne, Haltiwanger and Penciakova (2021) compare business formation in the Great Recession and the COVID-19 recession, documenting a 2020 surge in applications concentrated among those more likely to remain nonemployers. Decker and Haltiwanger (2022, 2023) relate the application surge to official establishment entry. Decker and Haltiwanger (2023) find that the industries and locations with the largest increases in applications also saw large increases in employer business entry, and Decker and Haltiwanger (2022) report, from the Census Business Dynamics Statistics, that existing firms rather than new ones accounted for about 36% of annual establishment births in 2015–2019. Dinlersoz et al. (2026) decompose local startup rates into the rate of applications and the rate at which applications become employers, a decomposition that helps explain why the information in applications may differ across places.

**Leading indicators of business dynamics.** Asturias et al. (2023, 2024) provide the closest forecasting antecedent: national and monthly, with nonfarm payroll employment as the outcome; the 2023 paper documents lead-lag correlations, and the 2024 paper adds forecasts from a dynamic factor model. Closer in outcome but estimated within sample, Haltiwanger (2022) finds in national quarterly vector autoregressions over 2004–2019 that increases in high-propensity applications are followed by significant increases in establishment births over the following four years. Grieves, Mance and Witt (2023) nowcast the birth-death adjustment in the BLS Current Employment Statistics survey without using applications. Galanakis and Savagar (2026) find that real-time company incorporations in the United Kingdom lead official business-demography statistics. Borup and Schütte (2022) show that internet search data improve out-of-sample forecasts of employment growth nationally and, using state-specific search data, in individual states; their state-by-state evaluation offers a template for forecast comparisons across states.

**Econometric versus machine-learning forecasts.** Goulet Coulombe, Leroux, Stevanovic and Surprenant (2022) find that the gains from machine learning in macroeconomic forecasting come mainly from nonlinearity in uncertain periods. Medeiros, Vasconcelos, Veiga and Zilberman (2021) find large gains from random forests in forecasting inflation. The present setting differs: a short, noisy panel of state-level counts, in which flexible methods have little data to learn from.

**Forecast evaluation with panels.** Comparing nested forecasting models calls for an adjustment such as that of Clark and West (2007): under the null, the larger model estimates parameters whose true values are zero, which adds noise to its forecasts and biases a plain comparison of mean squared errors against it. Diebold and Mariano's (1995) test compares the accuracy of two forecasts taken as given, without reference to the models that produced them, and Giacomini and White (2006) recast the comparison as one between forecasting methods, estimation included. Recent work develops tests of equal predictive accuracy pooled across panel units under cross-sectional dependence (Akgun, Pirotte, Urga & Yang 2024; Qu, Timmermann & Zhu 2024). The evidence in this paper shows why that matters in practice: in a state panel, ignoring dependence across states turns a marginal result into an apparently overwhelming one.

## 3. Data

**Business applications.** I use monthly state-level BFS data from July 2004 to September 2026, not seasonally adjusted and aggregated to quarters. The primary series is all business applications (BA). Census defines three narrower series nested within it. High-propensity applications (HBA) are applications with a high propensity of becoming employer businesses, identified from characteristics such as corporate form, planned wages, intent to hire, and selected industries. Applications with planned wages (WBA) are high-propensity applications that report a first date for paying wages, and corporate applications (CBA) are high-propensity applications from corporations.

Two documented revisions matter here. In November 2021 Census redefined HBA for data from 2012 onward and rescaled earlier years, and in February 2026 it removed internet-sales applications from HBA and CBA after a spike in such filings, citing their low rates of transition to employer businesses. The vintage used here incorporates both revisions.

**Establishment births.** The outcome comes from the BLS Business Employment Dynamics: quarterly state-level counts of private-sector establishment births from 1992Q3 to 2025Q4, not seasonally adjusted. The target is the year-over-year log change. BED has no archive of historical vintages, so the analysis uses the vintage retrieved on 14 October 2026 throughout; Section 9 discusses the implications.

Figure 1 shows both series at the national level. Applications surged in 2020 and peaked in 2020Q3; establishment births peaked three quarters later, in 2021Q2.

![Figure 1](figures/fig1_national_applications_births.png)

**Figure 1.** National year-over-year change in business applications (a) and establishment births (b), 2005Q3–2025Q4, in log points (100 × the log change from the same quarter a year earlier), not seasonally adjusted. Shaded: the pandemic (2020–21) and the test window (2023–25). *Sources: Census Bureau, Business Formation Statistics; BLS, Business Employment Dynamics.*

**New-firm share of entry.** From the Census Business Dynamics Statistics (annual state-by-firm-age tables, through 2023), I compute the share of new establishments that belong to firms in their first year. Over 2010–2019 the state average is 61% (range 54%–69%), implying that about 39% of new establishments belong to existing firms, close to the 36% that Decker and Haltiwanger (2022) report from national Business Dynamics Statistics data for 2015–2019.

**Seasonality.** Establishment births and applications, both not seasonally adjusted, show irregular spikes in the first quarter of the year. For applications, 21% of state first-quarter observations rise by more than 40% from the previous quarter, compared with almost none in other quarters, and of the 41 state-quarters in which both series rise by more than 30% at once, 36 are first quarters. Year-over-year differencing removes a stable seasonal pattern but not one whose size varies from year to year, so every model includes a quarter-of-year indicator. Section 6.7 shows that the results are unchanged when the official seasonally adjusted series are used instead.

*Sources: data/MANIFEST.md (retrieval dates, URLs, SHA-256 checksums); literature/phase3_findings.md; literature/rq2_findings.md §6.*

## 4. Forecasting design

**Target and benchmark.** The target is the year-over-year log change in state establishment births. The benchmark is a pooled panel regression of the target on its own lags at 3, 4 and 5 quarters, with state and quarter-of-year indicators. For reference, I also report a seasonal naive forecast, which predicts that each quarter's births equal those of the same quarter a year earlier; with a year-over-year target, it forecasts no change.

**Adding applications.** For lead h = 0, …, 4, the augmented model adds the year-over-year log change in applications h quarters before the target quarter, so the benchmark is nested in each augmented model. The primary leads, fixed in advance, are h = 0 (same quarter) and h = 3. The choice of h = 3 was motivated by exploratory correlations in the development period.

**Machine learning.** An elastic net, a random forest, and gradient boosting receive the benchmark's own lags, all five application lags, and state and quarter indicators. Tuning parameters are chosen once, by forward-chaining cross-validation over whole quarters within the 2004–2022 development window, and then held fixed. The best of the three by validation error (the elastic net) is the primary machine-learning comparison. An equal-weight combination of the h = 3 regression and the best machine-learning model is also evaluated.

**Real time.** BED births appear about three quarters after the reference quarter, whereas applications appear within weeks. A forecast for quarter t is therefore estimated only on rows whose own target quarter is at least three quarters earlier (t − 3 or before), and uses only lags of births at least three quarters old. Each model is re-estimated for every forecast quarter on an expanding window.

**Windows.** The development window runs to 2022Q4. The test window, 2023Q1–2025Q4, comprises 12 quarters × 51 states = 612 forecasts and was not used until the evaluation design had been committed. Section 6.4 extends the same procedure back to 2010; those years are pseudo-out-of-sample, because they informed exploratory choices.

**Use of AI tools in the research.** The research was carried out with an AI assistant, Claude (Anthropic; models Claude Opus 5.5 and Claude Sonnet 5, accessed through the Claude Code tool in October 2026). The assistant searched and screened the literature, wrote and ran the data-acquisition and analysis code, and checked outputs against the committed results. The author set the research question, approved the design and each follow-up analysis before it was run, and [reviewed the code and results; confirm after your review]. Every citation was checked against a publisher, registry or agency page, and a dated record of the assistant's contributions is kept in the project's research log.

## 5. Evaluation and inference

Accuracy is compared through the difference in squared forecast errors between the benchmark and a model, expressed as a percentage of the benchmark's mean squared error (MSE); positive values mean the model is more accurate. I keep two related questions separate. The first is whether adding applications carries predictive information; for nested comparisons this is assessed with the Clark–West (2007) adjusted statistic, tested one-sided. The second is whether adding applications actually made forecasts more accurate in this sample, assessed with the unadjusted difference, tested two-sided, which treats the forecasts as given in the manner of Diebold and Mariano (1995). The answer to the first can be yes while the answer to the second is no, because estimating additional parameters adds noise.

The 612 state-quarters are not independent. A national shock moves forecast errors in all states in the same quarter, and each state's errors are correlated over time. I therefore report standard errors that assume independence, standard errors clustered by state and by quarter, and standard errors two-way clustered by state and quarter (Cameron, Gelbach & Miller 2011). With only 12 quarters, conventional clustered standard errors can be too small (Cameron, Gelbach & Miller 2008), so I also report a wild cluster bootstrap by quarter, with Webb (2023) six-point weights and 9,999 draws. As specified in advance, where the bootstrap interval is materially wider than the two-way clustered one, the bootstrap interval is reported. The three primary comparisons (applications at h = 0 and h = 3, and the best machine-learning model) are adjusted for multiple testing with Holm's (1979) procedure.

Two inference methods named in the pre-analysis plan were replaced by standard alternatives, because no reference implementation was available to build on safely: Holm adjustment replaces the model confidence set of Hansen, Lunde and Nason (2011), and the clustered and bootstrap tests above replace the panel tests of Qu, Timmermann and Zhu (2024) and Akgun et al. (2024). All departures from the plan are listed at the end of the paper.

## 6. Results

### 6.1 The locked test window, 2023–2025

**Table 1. Accuracy in the 2023–2025 test window (612 state-quarters)**

| Model | RMSE | Accuracy vs. benchmark (% of MSE) | 95% CI | Two-way p |
|---|---|---|---|---|
| Benchmark (own lags only) | 0.1798 | — | — | — |
| Seasonal naive (no year-over-year change) | 0.1812 | −1.6 | −17.4 to +14.2† | 0.92† |
| + applications, h = 0 | 0.1824 | −3.0 | −8.1 to +2.2 | 0.26 |
| + applications, h = 1 | 0.1806 | −0.9 | −8.4 to +6.6 | 0.81 |
| + applications, h = 2 | 0.1800 | −0.2 | −8.2 to +7.8 | 0.96 |
| + applications, h = 3 | 0.1784 | +1.6 | −6.5 to +9.7 | 0.70 |
| + applications, h = 4 | 0.1791 | +0.8 | −6.1 to +7.6 | 0.82 |
| Elastic net (best ML) | 0.1777 | +2.3 | −8.7 to +13.4 | 0.68 |
| Random forest | 0.1806 | −0.8 | −13.3 to +11.6 | 0.89 |
| Gradient boosting | 0.1824 | −2.9 | −13.8 to +8.0† | 0.64† |
| Combination (h = 3 + elastic net) | 0.1771 | +3.0 | −6.2 to +12.1 | 0.53 |

*Notes: Accuracy is the reduction in mean squared error relative to the benchmark; positive values favor the model. †Wild cluster bootstrap interval and p-value, reported where the bootstrap interval is materially wider than the two-way clustered interval, as specified in advance in Addendum 1 of the pre-analysis plan. Sources: outputs/tables/phase5_model_performance.csv, phase5_comparisons.csv, phase5x_detectable_effects.csv, seasonal_naive_performance.csv, seasonal_naive_comparison.csv.*

No model detectably improves on the benchmark (Table 1; Figure 2b). The benchmark itself sets a low bar: it is not detectably more accurate than the seasonal naive forecast of no change, with a mean squared error only 1.6% lower (wild bootstrap p = 0.92) and a slightly higher mean absolute error (0.125 against 0.117). The confidence intervals show what can be ruled out. Same-quarter applications cannot have improved accuracy by more than about 2%, and applications three quarters ahead by more than about 10%; modest gains of a few percent cannot be excluded. At 80% power, the minimum detectable improvement is 7–12% for the regression models and 10–18% for the machine-learning models.

### 6.2 Naive versus dependence-robust inference

Figure 2 shows each point estimate with two intervals: one that treats the 612 state-quarters as independent, and one that allows for correlation across states within a quarter and within states over time. The p-values under every method are reported in Appendix Table A1.

![Figure 2](figures/fig2_test_window_intervals.png)

**Figure 2.** Test-window comparisons with the benchmark, 2023Q1–2025Q4 (612 state-quarters). Gray intervals treat every state-quarter as independent; black intervals are two-way clustered by state and quarter. Panel (a): Clark–West adjusted loss difference with 90% intervals, so that a black interval lying wholly above zero corresponds to rejection at the 5% level in the one-sided information test; the tree-based models are omitted because the adjustment is not meaningful for them (Section 6.3). Panel (b): reduction in mean squared error with 95% intervals; positive values favor the model. †Robust interval from the wild cluster bootstrap by quarter, because it is materially wider than the two-way clustered interval for this model. *Source: outputs/tables/phase5_comparisons.csv.*

Taken at face value, the naive intervals indicate that applications carry significant information at every lead except the same quarter (Figure 2a). Most of that evidence comes from treating 51 states in the same quarter as independent. Clustering by state alone barely changes the picture, but clustering by quarter, or in both dimensions, does: the three-quarter-lead result becomes marginal (p = 0.076 two-way; p = 0.067 by wild bootstrap), and the others are not significant. After Holm adjustment across the three primary comparisons, the smallest p-value is 0.14.

The same problem appears in the accuracy comparison, in the opposite direction. The naive interval for same-quarter applications lies wholly below zero (naive p = 0.03), which would suggest that applications made forecasts significantly worse; the robust interval does not (two-way p = 0.26; Figure 2b). The wild bootstrap and two-way clustered results agree closely, so the conclusion does not depend on the choice between them.

### 6.3 Machine learning

None of the three machine-learning models is detectably more accurate than the benchmark, and the random forest and gradient boosting are less accurate on average. Yet the random forest appears highly significant under the Clark–West statistic (two-way p = 0.014). The Clark–West adjustment credits the larger model for the dispersion between its forecasts and the benchmark's. That is appropriate when the larger model nests the smaller one linearly, but misleading for a flexible nonlinear model whose forecasts differ substantially from the benchmark's. For the tree-based models only the accuracy comparison is meaningful, and it shows no gain.

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

*Notes: 2010–2022 is pseudo-out-of-sample. Inference within 2020–21 rests on 8 quarters. Source: outputs/tables/phase5x_by_period.csv.*

The pattern has three phases (Table 2; Figure 3). In 2010–2019, applications carried statistically detectable information at leads of zero to three quarters under dependence-robust inference (at the four-quarter lead, p = 0.06), but the accuracy gains were small, about 1–4%, and positive in about two-thirds of states. In 2020–2021 the gains were large, 11–20%, and positive in 80–92% of states. From 2022 onward the gains disappear, and at most leads adding applications makes forecasts slightly worse in most states. Four quarters, 2021Q2 to 2022Q1, contribute more than the entire net gain over the sixteen years.

![Figure 3](figures/fig3_cumulative_gain_ba_h3.png)

**Figure 3.** Cumulative accuracy gain from adding applications at a three-quarter lead, 2010Q1–2025Q4. Each quarter adds the reduction in squared error relative to the benchmark, averaged across states. The running total is expressed as a percentage of the benchmark's total squared error over the whole period, so the final value (3.0%) is the accuracy gain over 2010–2025 as a whole. A rising line means the model with applications beat the benchmark that quarter. 2010–2022 is pseudo-out-of-sample. *Source: outputs/tables/rq2_predictions.csv.*

### 6.5 Which application series carries the signal?

Figure 4 repeats the cumulative comparison for each of the four application series; period averages are reported in Appendix Table A2.

![Figure 4](figures/fig4_cumulative_gain_by_series.png)

**Figure 4.** Cumulative accuracy gain by application series, constructed as in Figure 3, at the same-quarter (a) and three-quarter (b) leads. Shaded: the pandemic (2020–21) and the test window (2023–25). *Source: outputs/tables/rq2_predictions.csv.*

Before 2020 the narrower series were the better predictors. In direct comparisons with the all-applications model, Holm-adjusted across 24 comparisons, high-propensity applications were 4.8% more accurate at the same-quarter lead (p < 0.001; more accurate in 96% of states), and applications with planned wages were 3.7% more accurate at the three-quarter lead (p = 0.012). The same-quarter advantage holds when the comparison is restricted to 2013–2019, after the 2012 break created by Census's November 2021 redefinition of the high-propensity series (+4.7% for both HBA and WBA, p < 0.001); the three-quarter-lead advantage is weaker in that period.

After 2020 the advantage vanished. No series improved on the benchmark from 2022 onward, and the narrower series did slightly worse than total applications: at the three-quarter lead, high-propensity applications were 5.9% less accurate than the all-applications model (Holm-adjusted p = 0.07).

The weight the models place on applications also changed. Apart from the first estimates in 2010, which rest on short samples, the estimated weight on all applications at the three-quarter lead stayed between about 0.11 and 0.20 through 2021, averaging 0.18 over 2010–2019. Once the pandemic surge entered the estimation sample it rose sharply, peaking at 0.41 in 2022, and has since settled at about 0.32–0.34, roughly double its pre-2020 level. In elasticity terms, before 2020 a 10% year-over-year rise in applications was associated with a rise of about 1.8% in establishment births three quarters later, whereas models estimated through the pandemic assume roughly 3.3%. Decker and Haltiwanger (2023, appendix Table F4) find a related pattern in levels: in state-by-quarter regressions with state effects, the elasticity of establishment births with respect to high-propensity applications rises from 0.32 to 0.57 when 2020–2022 are added to the sample, whereas with year-by-quarter time effects it falls from 0.31 to 0.19. That contrast suggests that the pandemic-era increase reflects common national movements rather than differences across states. The narrower series moved much less (Figure 5). Indexed to each series' own 2010–2019 average, the weight on all applications averaged 193 over 2022–2025, against 132 for applications with planned wages, 112 for high-propensity applications, and 111 for corporate applications.

![Figure 5](figures/fig5_weight_paths_indexed.png)

**Figure 5.** Estimated weight on applications at a three-quarter lead, from each expanding-window re-estimation, by series. Each series is indexed to its own 2010–2019 average (= 100). Estimates are dated by forecast quarter; each uses data through three quarters earlier. The 2010 estimates rest on short samples. *Source: outputs/tables/rq2_coefficient_paths_h3.csv.*

These results bear directly on the most natural explanation for the breakdown. Dinlersoz et al. (2021; Census CES Working Paper 21-01) document that the 2020 surge was concentrated among applications more likely to remain nonemployers. If that compositional shift were the cause, filtering for employer intent should have preserved the signal, and it did not. Moreover, the estimated weight on high-propensity applications barely changed after 2020 (+12%, against +93% for total applications), yet their forecasts still deteriorated, so a pandemic-inflated weight cannot be the whole explanation either. The relationship itself appears to have changed.

*Sources: outputs/tables/rq2_vs_BA_direct.csv, rq2_hba_definition_check.csv, rq2_coefficient_paths_h3.csv, phase5x_bfs_coefficient_path_h3.csv.*

### 6.6 New-firm share and the mechanism (exploratory)

If applications predict births because they track new firms, gains should be larger where new firms account for more new establishments. Across states, the 2010–2019 same-quarter gain from applications is positively rank-correlated with the state's new-firm share (Spearman ρ = 0.37, Holm-adjusted p = 0.014; Figure 6). The three-quarter-lead correlation is weak (ρ = 0.11, Holm-adjusted p = 0.44), and after 2020 there is no relationship. This analysis is exploratory and cross-sectional, and the new-firm share comes from a different statistical system than the outcome.

![Figure 6](figures/fig6_gain_vs_new_firm_share.png)

**Figure 6.** State accuracy gain from applications over 2010–2019, against the share of new establishments belonging to new firms (Business Dynamics Statistics, 2010–2019 average). One point per state (51). Holm adjustment is across the two leads. *Sources: outputs/tables/rq4_state_data.csv, rq4_correlations.csv.*

### 6.7 Robustness

**Table 3. Robustness, test window**

| Variant | h = 3 accuracy (%) | h = 3 information test, two-way p | Best ML accuracy (%) |
|---|---|---|---|
| Primary | +1.6 | 0.076 | +2.3 |
| Official seasonally adjusted series, no quarter indicator | +1.7 | 0.065 | +2.9 |
| Winsorized, scored against winsorized actuals | +0.0 | 0.117 | −0.4 |
| Winsorized, scored against raw actuals | +0.9 | 0.092 | −0.0 |

*Notes: Winsorizing clips at fixed 1st and 99th percentiles from the development window. The seasonally adjusted variant is not a valid real-time exercise, because seasonal factors are estimated with later data; it is reported only as a check. Source: outputs/tables/phase5x_robustness_comparisons.csv.*

The results do not depend on the treatment of seasonality or on a few extreme quarters (Table 3).

## 7. Discussion

Three conclusions follow. First, for users of business applications as a state-level indicator, the relationship was useful before 2020 and has not been since. Before 2020, the narrower series that Census constructs to flag likely employers were the better predictors. In 2023–2025, adding any application series to a simple autoregressive model did not improve forecasts of establishment births, and models estimated on data through the pandemic weight applications about twice as heavily as the earlier relationship would warrant. The relationship may recover; the pre-registered forecasts in Section 8 are designed to detect that.

Second, the post-2020 change is not easily explained by the composition of applications. It affects even the series that screen for employer intent, and those series had been the better predictors. Two other broad explanations remain, and this paper tests neither. One is a change in the application series themselves: applications may relate differently to eventual employer formation, for example because more applicants form businesses that open establishments with a longer or less predictable delay. The other is a change in the outcome. Cao, Hyatt, Mukoyama and Sager (2026) document a growing divergence between BLS and Census counts of establishments; if the BLS establishment universe has changed in ways that do not track new-business formation, any indicator of business formation would lose predictive power for it. Separating these explanations is a natural next step.

Third, for forecast evaluation with state panels, the dependence structure is not a technicality. In this application, a naive pooled test turned a marginal result into an apparently decisive one, and the effective sample size is closer to the number of quarters than to the number of state-quarters. Studies that evaluate forecasts across states or regions should report tests that are robust to common shocks.

## 8. A pre-registered test with new data

The interpretation in Section 7 was formed after the 2023–2025 results had been seen, and the test window is short. A clean test requires data that did not exist when the interpretation was formed. Before BLS published any 2026 establishment-birth data, I committed forecasts for 2026Q1–Q3 for all 51 states to the project repository under the tag `prereg-live-forecasts-2026`; the SHA-256 hash of the forecast file is `8e0751c9…841fc`. [Add the link to the public timestamp record and its date once it is posted.]

The forecasts were produced with exactly the procedure described above, in two variants: one estimated on all available data and one excluding 2020–2022 from estimation (Figure 7). Two readings were registered in advance. The first is the paper's claim, that applications still do not improve forecasts; the second is an alternative, that excluding the pandemic years from estimation improves the applications model. The scoring code was committed with the forecasts, and 2026Q1 is scheduled for release on 28 October 2026.

![Figure 7](figures/fig7_live_forecasts_2026.png)

**Figure 7.** Pre-registered forecasts for 2026Q1–Q3, committed before BLS published any 2026 data. Each point is the average forecast across the 51 states, with equal weights as in the evaluation. Filled points: models estimated on all data. Hollow points: models estimated excluding 2020–2022. The pre-registered test compares state-level squared errors, not these averages. [Actual values to be added as each quarter is published.] *Source: outputs/live_forecasts/live_forecasts_2026Q1-Q3.csv.*

Before the first release, I recorded one development that bears on how it should be read (project research log, 15 October 2026). Total applications rose sharply through 2025, by 21 log points year over year nationally in 2025Q4, while high-propensity applications rose by only 1–5 log points over 2025Q2–Q4 and applications with planned wages fell. Models estimated on all data weight total applications about twice as heavily as before 2020, so they translate that rise into the high 2026 forecasts shown in Figure 7. A shortfall of actual births relative to those forecasts would therefore reflect two things: the post-2020 change documented above, and a 2025 shift in the kinds of applications that are rising. The frozen forecasts based on high-propensity applications, which are among the pre-registered secondary comparisons, help to separate the two.

*[Results to be added as each quarter is published. Report every quarter regardless of outcome.]*

## 9. Limitations

Several limitations qualify these results. The regime interpretation and the composition hypothesis were formed after the test-window results had been seen; the follow-up analyses were specified before they were run, but they are not blind tests, which is why Section 8 adds one. The 2010–2022 results are pseudo-out-of-sample, because those years informed exploratory choices. BED offers no archive of historical vintages, so the analysis uses final-vintage data, and real-time revisions could change the picture, especially around 2020–21; the live forecasts in Section 8 are the only fully real-time evidence. The test window and the pandemic period contain only 12 and 8 quarters, so conclusions about those periods rest as much on point estimates and their consistency across states as on p-values. Several planned methods were replaced by standard alternatives (Section 5 and the list of departures at the end of the paper). Finally, the analysis concerns prediction only: nothing here identifies what caused the relationship to change.

## 10. Conclusion

Business applications looked like a natural early indicator of state establishment births, and before 2020 they were a modest one. In 2020–21 they were a strong one. Since then they have not improved forecasts, and the narrower application series that used to predict best have fared no better. Users of applications as a state-level signal of new establishments should treat the post-2020 relationship as unreliable until new data show otherwise. The pre-registered forecasts reported in Section 8 will provide that evidence as it arrives.

---

## Pre-registration and deviations

The pre-analysis plan and its four addenda are in the repository, each committed before the analyses it governs. The plan states that any departure from it will be disclosed in the paper. The departures are as follows. (i) The seasonal naive benchmark listed in the plan was omitted from the first implementation. It was added before submission, with its definition committed to the repository before it was evaluated, and is reported in Table 1; because it has no parameters, adding it involved no specification choices. (ii) The plan distinguished an autoregressive distributed-lag model from a bridge equation for monthly applications; under the real-time convention used here, in which a quarter's applications are available shortly after it ends, the two specifications coincide. (iii) The model confidence set and the panel tests of Qu, Timmermann and Zhu (2024) and Akgun et al. (2024) were replaced as described in Section 5. (iv) The Giacomini and White (2006) test, named as a fallback where nesting is in doubt, was not implemented; its asymptotic theory requires a finite, rolling estimation window, whereas the forecasts here use expanding windows. For the tree-based models only the unadjusted accuracy comparison is reported (Section 6.3). (v) Addendum 4 anticipated reporting the new-firm-share analysis in an appendix; it is reported in Section 6.6 and labeled as exploratory.

Three errors in an earlier run of the main evaluation were found and corrected before this draft: the machine-learning tuning folds were not time-ordered, the best machine-learning model had been fixed in advance rather than selected, and the dependence-robust tests had been applied to a different statistic from the naive test they were compared with. None involved test data leaking into training. The corrections are documented in `literature/phase5_findings.md`.

## Reproducibility

All code, processed data, outputs, and the pre-analysis plan with its four addenda are in the replication package (see the data availability statement). A single command (`replication/run_all.py`) regenerates every table and figure from the committed data. On 15 October 2026, a fresh clone with a new, pinned environment reproduced every table and figure committed at that point, with a largest numeric difference of 1.1e-14. After the final analyses and the manuscript figures were added, a full re-run reproduced all 36 tables and every figure, the manuscript figures byte for byte, and confirmed that the pre-registered forecast file is regenerated exactly. Retrieval dates and SHA-256 checksums of the raw data are listed in `data/MANIFEST.md`.

<!-- pagebreak -->

## References

*Bibliographic details, including author names, pages and DOIs, were verified against publisher, registry (Crossref, DataCite) or agency pages on 15 October 2026.*

Akgun, O., Pirotte, A., Urga, G., & Yang, Z. (2024). Equal predictive ability tests based on panel data with applications to OECD and IMF forecasts. *International Journal of Forecasting*, 40(1), 202–228. https://doi.org/10.1016/j.ijforecast.2023.02.001

Asturias, J., Dinlersoz, E., Haltiwanger, J., & Hutchinson, R. (2023). Are business applications early economic indicators? *AEA Papers and Proceedings*, 113, 151–155. https://doi.org/10.1257/pandp.20231053

Asturias, J., Dinlersoz, E., Haltiwanger, J., Hutchinson, R., & Plumb, A. (2024). *Business applications as a leading economic indicator?* NBER Working Paper 33224. https://doi.org/10.3386/w33224

Bayard, K., Dinlersoz, E., Dunne, T., Haltiwanger, J., Miranda, J., & Stevens, J. (2018). *Early-stage business formation: An analysis of applications for employer identification numbers.* NBER Working Paper 24364. https://doi.org/10.3386/w24364

Borup, D., & Schütte, E. C. M. (2022). In search of a job: Forecasting employment growth using Google Trends. *Journal of Business & Economic Statistics*, 40(1), 186–200. https://doi.org/10.1080/07350015.2020.1791133

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427. https://doi.org/10.1162/rest.90.3.414

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2011). Robust inference with multiway clustering. *Journal of Business & Economic Statistics*, 29(2), 238–249. https://doi.org/10.1198/jbes.2010.07136

Cao, D., Hyatt, H., Mukoyama, T., & Sager, E. (2026). *New U.S. business establishments: Surging or stalling?* Center for Economic Studies Working Paper 26-36, U.S. Census Bureau; also Finance and Economics Discussion Series 2026-040, Board of Governors of the Federal Reserve System. https://doi.org/10.17016/FEDS.2026.040

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, 138(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Decker, R. A., & Haltiwanger, J. (2022). Business entry and exit in the COVID-19 pandemic: A preliminary look at official data. *FEDS Notes*, Board of Governors of the Federal Reserve System, May 6, 2022. https://doi.org/10.17016/2380-7172.3129

Decker, R. A., & Haltiwanger, J. (2023). Surging business formation in the pandemic: Causes and consequences? *Brookings Papers on Economic Activity*, Fall 2023, 249–302. https://doi.org/10.1353/eca.2023.a935424

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Dinlersoz, E., Dunne, T., Haltiwanger, J., & Penciakova, V. (2021). Business formation: A tale of two recessions. *AEA Papers and Proceedings*, 111, 253–257. https://doi.org/10.1257/pandp.20211055. Also Center for Economic Studies Working Paper 21-01.

Dinlersoz, E., Dunne, T., Haltiwanger, J., & Penciakova, V. (2026). *The local origins of business formation: Entry as a two-stage process.* NBER Working Paper 34881. https://doi.org/10.3386/w34881

Galanakis, Y., & Savagar, A. (2026). *Tracking the economy through firm creation: Evidence from real-time administrative data.* arXiv:2606.01307. https://doi.org/10.48550/arXiv.2606.01307

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica*, 74(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics*, 37(5), 920–964. https://doi.org/10.1002/jae.2910

Grieves, C., Mance, S., & Witt, C. (2023). *Predicting the effect of business births and deaths on the Current Employment Statistics survey: Using sample information to minimize coverage error.* Statistical Survey Paper, Office of Survey Methods Research, U.S. Bureau of Labor Statistics. https://www.bls.gov/osmr/research-papers/2023/st230010.htm

Haltiwanger, J. C. (2022). Entrepreneurship during the COVID-19 pandemic: Evidence from the Business Formation Statistics. *Entrepreneurship and Innovation Policy and the Economy*, 1, 9–42. https://doi.org/10.1086/719249

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica*, 79(2), 453–497. https://doi.org/10.3982/ECTA5771

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70. https://www.jstor.org/stable/4615733

Medeiros, M. C., Vasconcelos, G. F. R., Veiga, Á., & Zilberman, E. (2021). Forecasting inflation in a data-rich environment: The benefits of machine learning methods. *Journal of Business & Economic Statistics*, 39(1), 98–119. https://doi.org/10.1080/07350015.2019.1637745

Qu, R., Timmermann, A., & Zhu, Y. (2024). Comparing forecasting performance with panel data. *International Journal of Forecasting*, 40(3), 918–941. https://doi.org/10.1016/j.ijforecast.2023.08.001

Webb, M. D. (2023). Reworking wild bootstrap-based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858. https://doi.org/10.1111/caje.12661

U.S. Bureau of Labor Statistics. Business Employment Dynamics. https://www.bls.gov/bdm/ (data retrieved 14 October 2026).

U.S. Census Bureau. Business Formation Statistics. https://www.census.gov/econ/bfs/ (data retrieved 14 October 2026). Methodology: https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html. Definitions: https://www.census.gov/econ/bfs/definitions.html.

U.S. Census Bureau. Business Dynamics Statistics. https://www.census.gov/programs-surveys/bds.html (data retrieved 15 October 2026).

<!-- pagebreak -->

## Appendix: Additional tables

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
