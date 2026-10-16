# Literature Extraction: Project 1

*Compiled 2026-10-14 following [search_protocol.md](search_protocol.md), from two parallel AI-assisted searches (content and methods). Each entry was confirmed on an official landing page by the search agent unless marked UNVERIFIED. Not yet reviewed by the author; spot-check each citation before use in a manuscript.*

## Gate verdict

> **Does any existing, findable paper forecast or nowcast state-level BED (or QCEW) establishment births/dynamics from state-level BFS business-application data, with an out-of-sample econometric-vs-ML comparison?**

**No.** The closest paper (Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb, NBER w33224) is national-level, uses only a dynamic factor model, and forecasts nonfarm payroll employment rather than establishment births; it has no state panel and no ML comparison. The existing state and local BFS literature (Dinlersoz et al., NBER w34881) is structural and cross-sectional, not a rolling forecasting exercise. BLS's own birth-death nowcasting work (Grieves, Mance & Witt 2023) does not use BFS and is national only. Census's internal BFS methodology (the PBF4Q/PBF8Q projection model) classifies individual applications rather than forecasting state BED outcomes.

**What distinguishes Project 1 from the papers found:** the state is the unit for both predictor and outcome; out-of-sample evaluation over rolling forecast origins across about 51 states, about 2005–2025; a direct comparison of econometric and ML models; and a decomposition of which BFS series (BA, HBA, WBA, CBA) carries the signal at the state level.

**Caveat:** this was a web-search-based review (Google Scholar, NBER, SSRN, RePEc, Census CES, Federal Reserve series, journal sites), not a full EconLit or Scholar citation-graph search, and two PDFs could not be extracted cleanly (their content was cross-checked against search snippets instead). A targeted Scholar/EconLit search should be re-run before submission, including a check on whether the Census research group (Haltiwanger and coauthors) has extended its work to states (see "Scooping-risk check" below).

## Content literature: core papers (verified)

| Citation | Data / Period | Method | Finding | Relation to Project 1 |
|---|---|---|---|---|
| Bayard, Dinlersoz, Dunne, Haltiwanger, Miranda & Stevens (2018). "Early-Stage Business Formation." NBER WP 24364. | BFS construction from IRS SS-4 filings, national/state/local | Descriptive | Introduces the BFS dataset; applications are a timely forward signal | Source dataset paper |
| Asturias, Dinlersoz, Haltiwanger & Hutchinson (2023). "Are Business Applications Early Economic Indicators?" *AEA P&P* 113:151–55. doi:10.1257/pandp.20231053 | National, monthly | Descriptive/correlational | Growth in likely-employer applications leads employment growth | National analogue |
| **Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb (2024). NBER WP 33224. "Business Applications as a Leading Economic Indicator?"** | National, monthly, 3 BFS series (BA, likely-employer≈HBA, likely-non-employer) vs. nonfarm payrolls / Principal Federal Economic Indicators | Dynamic factor model only | Applications lead most PFEIs; a DFM with applications improves 12-month employment forecasts, especially around turning points | Closest existing analogue; no state-level analysis and no ML comparison. This is the paper Project 1 most directly extends. |
| Dinlersoz, Dunne, Haltiwanger & Penciakova. NBER WP 34881 (2026) / CES-WP-23-34. "The Local Origins of Business Formation... Entry as a Two-Stage Process." | County/local market, cross-sectional | Structural two-stage model (application → transition) | Local startup rates = ideas (applications) per capita × transition rate | Explains *why* the composition of the BFS signal may differ locally and nationally; background, not a forecasting precedent |
| Decker & Haltiwanger (2023). *Brookings Papers on Economic Activity*, Fall 2023:249–316. | National, plus some state and industry detail | Descriptive, with some causal interpretation | Application surges in 2020–21 linked to employer entry (BED/QCEW), uncertain translation rate | Background on the 2020–21 structural break |
| Decker & Haltiwanger (2022). FEDS Note, 2022-05-06. | National, BFS + BED jointly | Descriptive | Both hit records in 2020–21; existing firms accounted for about 36% of annual establishment births in 2015–2019 (national Census Business Dynamics Statistics data, per the note's footnote 7; re-checked 2026-10-15) | Quantifies the "dilution" mechanism noted in the research plan (births from existing firms weaken the application signal) |
| **Grieves, Mance & Witt (2023). BLS research paper.** "Predicting the Effect of Business Births and Deaths on the CES Survey." | National CES, 2007–2020 | ARIMA-type + forecast combination (44 models) | Nowcasts the CES birth-death adjustment | Confirmed not to use BFS, which indicates that the complementary approach (adding applications) has not been tried in this work, even nationally. |
| Borup & Schütte (2022). *JBES* 40(1):186–200. "In Search of a Job: Forecasting Employment Growth Using Google Trends." | State-panel extension *within the same paper*, high-dimensional variable selection vs. AR benchmarks | Elastic-net/subset-regression style vs. econometric benchmark, out-of-sample R² | Google Trends predicts employment growth at state level too | Best available methodological template for a state-panel econometric-vs-ML design, with a different predictor (search data) and outcome (employment, not births) |
| Galanakis & Savagar (2026). arXiv 2606.01307 (author order as printed on the paper; the arXiv listing shows Savagar first). UK Companies House incorporations → ONS business demography + employment/output. | UK, national/sectoral | SVAR | Incorporations lead official (lagged) demography statistics | Structural analogue: administrative registration data leading lagged official statistics; the same form of question, in a different country with different data |
| Cao, Hyatt, Mukoyama & Sager. CES-WP-26-36 / FEDS 2026-40 (Jun 2026). "New U.S. Business Establishments: Surging or Stalling?" | BLS vs. Census establishment universes | Measurement reconciliation | BLS and Census establishment counts had diverged by about 1.6 million by 2023, driven by frame-coverage differences | Measurement caveat: BED and Census-based establishment counts are not interchangeable; document which is used and why |

## Scooping-risk check

The Census BFS methodology page was fetched directly. It describes only the internal application-to-outcome classifier (PBF4Q/PBF8Q) and does not mention state-level nowcasting or ML. Recent CES working paper listings (through 2026Q2) contained nothing on state-level BED forecasting from BFS. The scooping risk was judged low as of 2026-10-14, but it should be re-checked before submission, because this is an active research group.

## Methods literature

**Nested-model forecast tests:**
- Diebold & Mariano (1995), *JBES* 13(3):253–263. Designed for non-nested comparisons; Diebold's own 2012/2015 retrospective (NBER WP 18391) identifies its application to nested models as a misuse.
- Clark & West (2007), *J. Econometrics* 138(1):291–311. The standard correction for nested models (it adjusts for the noise from estimating parameters that are truly zero).
- McCracken (2007), *J. Econometrics* 140(2):719–752. Non-standard limiting distribution and valid critical values for nested DM and encompassing tests.
- Giacomini & White (2006), *Econometrica* 74(6):1545–1578. Valid for both nested and non-nested models under possible misspecification, so a natural fallback.

**Multiple-comparison control:**
- Hansen, Lunde & Nason (2011), *Econometrica* 79(2):453–497. The Model Confidence Set; chosen as the primary tool for this project.
- White (2000), *Econometrica* 68(5):1097–1126. The "Reality Check", an alternative.
- FDR-specific methods for forecast evaluation are comparatively ad hoc in this literature; the MCS is the better-established primary tool. (A "Moon & Perron (2012)" FDR reference returned by the search could not be independently confirmed: UNVERIFIED, not to be cited without checking.)

**Panel extensions of forecast-comparison tests (directly relevant; not in the original plan):**
- Qu, Timmermann & Zhu (2024), *IJF* 40(3):918–941. "Comparing forecasting performance with panel data." Tests equal forecasting performance pooled over time *and* units, and over subsets or clusters. A close methodological match for the 51-state panel.
- Akgun, Pirotte, Urga & Yang (2024), *IJF* 40(1):202–228. Panel tests of equal predictive ability (pooled "S-statistics" and clustered "C-statistics"), valid under cross-sectional dependence. Relevant because state loss differentials are plausibly correlated (e.g., by Census region).

**MIDAS / bridge equations:**
- Ghysels, Santa-Clara & Valkanov, CIRANO WP 2004s-20 ("The MIDAS Touch") and the peer-reviewed *J. Econometrics* 131(1–2):59–95 (2006) version.
- Bridge-equation references: ECB WP 949 (2008); Bundesbank DP 26/2014; and a direct MIDAS-vs-bridge comparison in *IJF* (ScienceDirect S0169207015001144).
- **Python tooling gap (confirmed):** no mature Python MIDAS package comparable to R's `midasr` exists. The options found (`midaspy`, `midas_pro`, `jstriaukas/midasmlpy`) are works in progress or narrowly scoped to regularized, high-dimensional variants. The choice was between bridge equations (straightforward in Python with statsmodels) as the primary mixed-frequency approach and calling R's `midasr` from Python. Recommendation: bridge equations as primary, noted as a deliberate simplification (adopted; see Decision 4 below).

**Econometric vs. ML on state/regional panels:**
- A small 2026 conference paper (EAI ICIAAI, a minor venue) forecasting state unemployment found that linear regression outperformed random forest and gradient boosting out of sample, with the tree models overfitting on a similarly short state-quarterly panel. It is a useful cautionary prior for RQ3, but not a template to cite heavily given the venue.
- IMF WP 2025/252 (national GDP nowcasting, econometric vs. ML) is a reasonable design template, not state-panel-specific.
- No peer-reviewed paper comparing ML and econometric forecasts on a 51-state panel of establishment-type outcomes was found, consistent with the gate verdict.

**Real-time vintage data (an open question from the research plan):**
- **BFS:** vintages are available on ALFRED (Federal Reserve Bank of St. Louis), release IDs 443 (monthly/quarterly, state-level, confirmed for CA/FL/TX/NY/ID/WA/NC/MI/IL/AL/AZ/LA) and 468 (weekly, state-level, 2006–Oct 2026). Access requires a free FRED/ALFRED API key.
- **BED:** vintages are not available on ALFRED. The BLS source listing and the QCEW release were checked directly; no BED gross-flows release exists there. A real-time BED vintage panel would have to be hand-built from BLS's historical news-release archive (`bls.gov/news.release/archives/cewbd_*.htm`) and annual revision notices, which is more work than the original plan assumed.

## Decisions this resolves (updates to research_question.md)

1. Primary nested-model test: Clark–West (2007), with Giacomini–White (2006) as the fallback. Plain Diebold–Mariano is not used for nested comparisons.
2. Multiple-comparison control: the Hansen–Lunde–Nason Model Confidence Set as the primary tool.
3. Pooled-panel significance: Qu, Timmermann & Zhu (2024) and/or Akgun et al. (2024) for a formal pooled or clustered test across states, rather than ad hoc per-state reporting.
4. Mixed-frequency model: bridge equations, not MIDAS, because Python MIDAS tooling is not mature enough to rely on. Documented as a deliberate scope choice.
5. Data-revision handling: BFS vintages can be pulled from ALFRED (with a free API key). BED has no vintage archive, so Phase 2 had to choose between hand-constructing one from BLS's release archive (substantial added work) and running the pseudo-real-time analysis on final BED data only, with that limitation stated plainly, as the original plan allowed as a fallback.

**Later changes** (noted here so that this Phase 1 record is not read as the final design):

- Decision 1: the Giacomini–White fallback was not implemented. For the tree-based models, only the unadjusted accuracy comparison is interpreted (see the manuscript's list of deviations).
- Decisions 2 and 3: the Model Confidence Set and the panel tests were not implemented, because no vetted reference implementation was available. Holm–Bonferroni correction and cluster-robust tests were used instead, as disclosed in [phase5_findings.md](phase5_findings.md).
- Decision 4: because BFS enters the models at quarterly frequency, the bridge-equation and ARDL specifications coincide (documented in `src/cleaning/build_forecast_dataset.py`).
- Decision 5: the [pre-analysis plan](../pre_analysis_plan.md) (§3) uses final-vintage data for both BFS and BED and states this as a limitation.
