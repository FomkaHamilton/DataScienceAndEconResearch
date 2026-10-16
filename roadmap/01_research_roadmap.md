# Research Roadmap: Question Selection (Program Phase 1)

*Drafted 2026-10-14 with AI assistance (see the AI-use record in [../research_log.md](../research_log.md)) as a proposal for the author's decision. Decided the same day: Candidate 1 was approved as Project 1 and Candidate 3 as Project 2. This document is kept as the original proposal; it contains no analysis, and no data had been modeled when it was written.*

*Every dataset, journal and literature claim below was checked against current sources on 2026-10-14. Evidence and URLs are in [sources_verified_2026-10-14.md](sources_verified_2026-10-14.md). Items marked UNVERIFIED were not confirmed.*

---

## 1. How the shortlist was built

The shortlist started from the author's interest areas. A draft set of candidate questions was written, and three checks were run before anything was ranked:

1. **Literature crowding.** Has someone already done essentially this, recently?
2. **Data reality.** Does a public, reproducible source actually contain the variables at the needed frequency and geography, today?
3. **Venue fit.** Is there a legitimate, realistic journal for an unaffiliated first-time author?

Several candidates that looked promising failed at least one of these checks; those results are reported below rather than omitted.

---

## 2. The shortlist (8 candidates and 1 rejected direction)

Track: **DS** = applied data science / forecasting, **EM** = applied econometrics.

### Candidate 1 (DS): Business applications as a leading indicator of state establishment births

- **Question:** Do Census business applications (BFS) improve out-of-sample nowcasts and short-horizon forecasts of state-level establishment births (BLS BED), relative to time-series benchmarks? Do machine-learning methods add predictive value over linear econometric models in this short, noisy, cross-state panel?
- **Why it matters:**
  - BED state births are published about 7 months after the quarter ends.
  - BFS state data arrive within weeks.
  - A validated nowcast gives state policymakers and analysts a timely read on business formation.
  - Separately, it tests a contested claim: that ML generally outperforms econometric models in forecasting.
- **Mechanism:** An EIN application is an early, mechanical step on the path to an employer establishment. The signal is diluted because:
  - most applications never become employers;
  - about a third of establishment births come from *existing* firms (Decker & Haltiwanger 2022 FEDS Note).
- **What is known:**
  - Bayard et al. (2018) built the BFS.
  - Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb (2024, NBER w33224) show applications lead national indicators, using a dynamic factor model.
  - Decker & Haltiwanger (2023, BPEA) relate application surges to employer entry, descriptively.
  - BLS (Grieves, Mance & Witt 2023) nowcasts the CES birth-death adjustment *without* BFS.
- **Gap (as of this scan):** No paper found doing any of the following:
  - state-level forecasting of BED births from state BFS;
  - an out-of-sample econometric-vs-ML comparison on this problem;
  - a test of which application series (all, high-propensity, with planned wages, corporate) carries the signal.
- **Data (verified):**
  - BFS monthly by state since July 2004 (CSV + API; state totals only, no sector detail).
  - BED quarterly state establishment births since 1992Q3 (BLS flat files + API).
  - Panel: about 51 states × about 84 quarters (2005–2025).
- **Feasibility:** High. Two clean official files, small data, no microdata licensing.
- **Methods:**
  - Benchmarks: seasonal naive, AR, pooled panel AR.
  - Econometric: ARDL and bridge/MIDAS.
  - ML: LASSO / elastic net, random forest, gradient boosting.
  - Design: real-information-set forecasting origins, rolling/expanding windows.
  - Evaluation: Diebold–Mariano / Clark–West tests and a model confidence set.
- **Threats:**
  - data revisions (both series revised annually; no real-time vintage archive found);
  - seasonal-adjustment look-ahead;
  - 2020–21 structural break;
  - tuning leakage;
  - multiple comparisons across models × states;
  - small effective sample per state.
- **Crowding:** Low–Medium. Risk: the Census research group (Haltiwanger and coauthors) extends its work to states first.
- **Venues:**
  - *Journal of Forecasting*
  - *Business Economics* (NABE; explicitly welcomes practitioners)
  - *International Journal of Forecasting* (research note; stretch target)
  - *Small Business Economics* (stretch)
  - *Empirical Economics*
  - a short version in *Economics Bulletin*

### Candidate 2 (DS): Income elasticity of household spending on digital subscription services

- **Question:** How does household spending on streaming and digital subscription services vary with income and household characteristics (Engel curves)? How did that relationship change across the cord-cutting era (2005–2024)?
- **Why it matters:** Subscription spending is a growing budget share. Income elasticities matter for:
  - CPI weighting;
  - distributional analysis of price changes;
  - firms' pricing and targeting.
- **Mechanism:** Standard demand theory. Digital subscriptions may shift from luxury toward necessity as they substitute for cable/satellite TV.
- **What is known:**
  - Structural pay-TV demand (Crawford & Yurukoglu 2012).
  - Cord-cutting behavior (Prince & Greenstein 2017; Malone, Nevo, Nolan & Williams 2023).
  - The CE Engel-curve method (Aguiar & Bils 2015).
  - No peer-reviewed CE-based Engel curves for streaming/subscriptions were found.
- **Data (verified):** CE PUMD 1980–2024; 2025 release due Oct 29, 2026. Relevant expenditure codes (UCCs):
  - video streaming 310240 (2005Q2–2017Q1), then **merged with rentals** as 310243 from 2017Q2;
  - audio streaming 310350;
  - online gaming 620930;
  - cable/satellite 270310;
  - internet 690114.
  - **There is no general "online subscriptions" UCC.**
- **Feasibility:** Medium-High. The data are free and rich, but the 2017 code merge is a measurement break.
- **Methods:**
  - Two-part / hurdle models for the many zeros.
  - Total expenditure instrumented with income to handle measurement error (Engel-curve IV).
  - Multiple-imputation combining rules for income.
  - Survey weights.
- **Threats:**
  - UCC definitional breaks;
  - small budget shares;
  - Diary vs Interview source differences;
  - **2025 shutdown data gap** (BLS will not adjust PUMD weights), so stop at 2024.
- **Crowding:** Low, but this rests on web search only. It needs an EconLit/Scholar sweep.
- **Venues:**
  - *Journal of Consumer Affairs*
  - *Journal of Family and Economic Issues*
  - *Applied Economics Letters*
  - *Economics Bulletin*
  - *Journal of Data Science*

### Candidate 3 (EM): Monthly income volatility and household material hardship (SIPP 2018+)

- **Question:** Holding income level fixed, is month-to-month income volatility associated with missed housing/utility payments and food insecurity within the same household over time? Does that association depend on downside vs upside volatility and on liquid assets?
- **Why it matters:**
  - Volatility, not just low income, plausibly drives hardship.
  - USDA suspended the CPS Food Security Supplement in fall 2025, which raises the value of SIPP-based evidence.
- **Mechanism:**
  - Liquidity constraints plus lumpy obligations (rent, utilities).
  - Precautionary behavior.
  - Volatility that households can predict vs. volatility they cannot.
- **What is known:**
  - Leete & Bania (2010): SIPP, income shocks → food insufficiency.
  - Dahl, DeLeire & Mok (2014): imputation strongly attenuates the link.
  - Heflin (2016): within-household changes, 2008 SIPP.
  - Bania & Leete (2022, *CEP*): volatility → health.
  - **No within-household volatility→hardship study on the 2018+ redesigned SIPP was found.**
- **Data (verified):**
  - SIPP 2018–2025 releases. Monthly person-level income.
  - Hardship (Adult Well-Being module) asked annually: EAWBMORT (rent/mortgage), EAWBGAS (utilities), EFOOD1–6 food security.
  - Monthly SNAP. State identifiers. Longitudinal weights.
  - Presence of the hardship items is confirmed for 2022 and 2025; **2019–21, 2023–24 UNVERIFIED.**
- **Feasibility:** Medium. Large, complex files. The 2019 panel stopped after wave 1. Hardship is annual, so household FE identifies off ≤4 observations.
- **Methods:**
  - Household fixed effects with level, downside-shock, and volatility terms entered separately.
  - Event study around large income drops.
  - Imputation-flag sample restrictions.
  - Longitudinal and replicate weights.
  - Possible extension: 2021 monthly Child Tax Credit as a source of variation in income stability (crowded, so treat cautiously).
- **Threats:**
  - reverse causality (hardship → job loss);
  - time-varying confounders (health, family breakup);
  - imputation;
  - seam bias;
  - attrition;
  - annual outcome vs monthly exposure timing.
- **Identification assessment:** within-household fixed effects give *strong associational* evidence, not a causal effect of volatility. The paper must be written that way unless a credible quasi-experiment is found.
- **Crowding:** Medium. The gap is real but modest.
- **Venues:**
  - *Journal of Family and Economic Issues*
  - *Contemporary Economic Policy* (published Bania & Leete 2022)
  - *Review of Income and Wealth*
  - *Journal of Consumer Affairs*
  - *Empirical Economics*

### Candidate 4 (EM): Minimum wages and establishment entry/exit (heterogeneity-robust staggered DiD)

- **Question:** Do state minimum-wage increases (2010–2023) change establishment entry and exit rates, once estimated with heterogeneity-robust staggered DiD? Do answers differ between border-pair and commuting-zone designs?
- **Why it matters:** Business dynamism is a channel distinct from employment levels. The border-design debate (Jha, Neumark & Rodriguez-Lopez 2024 vs Dube, Reich et al. 2024/26; Jardim et al. 2024) has not been carried to entry/exit outcomes.
- **What is known:**
  - Meer & West (2016): job growth.
  - Aaronson et al. (2018): restaurant entry and exit both rise.
  - Chava et al. (2023); Luca & Luca.
  - **Kuroki (2025): county entry/exit 2010–2023, close to this question.**
  - Lyu & Fossen (2025): nonemployers.
- **Data (verified):** BDS through 2023 (state, county, sector). QCEW county × industry establishment counts. Minimum-wage histories (source to be verified).
- **Feasibility:** Medium. Public data exist, but county-level BDS has noise infusion and suppression.
- **Threats:**
  - spatial trends;
  - cross-border spillovers;
  - announcement timing;
  - continuous / staggered treatment;
  - entry and exit moving together.
- **Crowding:** Medium-High and politically contested. Expert referees will be demanding.
- **Venues:**
  - *Empirical Economics*
  - *Contemporary Economic Policy*
  - *Eastern Economic Journal*
  - *Small Business Economics* (stretch)

### Candidate 5 (EM): Quantity response to the 2022 state gasoline tax holidays

- **Question:** How much did taxable gasoline volumes respond to the 2022 tax suspensions (GA, MD, CT, NY, FL), and how much of the response reflects cross-border shifting and timing rather than consumption?
- **Why it matters:** Price elasticity of demand and tax incidence. It addresses the author's interest in pricing, in a public-data setting.
- **What is known:** This is a heavily studied area.
  - Davis & Kilian (2011); Li, Linn & Muehlegger (2014); Coglianese et al. (2017).
  - **Bates & Kim (2024, JAE) and Kilian & Zhou (2024, JPubE) already update tax-based elasticities past 2010.**
  - The holiday papers found (Tsvetanov 2024; Bradt & Taylor 2026, Dallas Fed) study *prices / pass-through*, not quantities. That is the only open gap.
- **Data (verified), and the problem:**
  - EIA's state sales series (Prime Supplier, EIA-782C) is **discontinued**: last data March 2022.
  - EIA all-state monthly retail prices ended in **2011**. Weekly prices exist for only 9 states.
  - FHWA monthly state gasoline volumes exist (DataHub, 2020–May 2026). But **Georgia's Apr–Dec 2022 rows are FHWA estimates, not reports**, and Maryland April 2022 shows a reporting spike.
  - These are volumes *taxed/distributed*, which mechanically shift during a holiday.
- **Feasibility:** Low–Medium. The outcome variable is distorted by the very policy being studied.
- **Venues:** *Energy Economics* (high bar), *The Energy Journal*, *Economics Bulletin* (note).

### Candidate 6 (EM): SNAP churn and state recertification policy (SIPP + SNAP Policy Database)

- **Question:** Do longer state certification periods reduce SNAP exits among still-eligible households? This is the public-program analogue of customer retention.
- **What is known:** Credible causal work uses administrative data and dominates the literature:
  - Ribar et al. (2008);
  - Gray (2019, JPubE);
  - Homonoff & Somerville (2021, AEJ: Policy);
  - Unrath (2021);
  - Wu & Meyer (2023).
- **Data (verified), and the problem:**
  - The SNAP Policy Database ends **Dec 2020**, with recertification variables **missing from Oct 2019**. Its overlap with SIPP 2018+ is only about 2017–Sep 2019.
  - SIPP underreports SNAP by roughly 23% of recipient households (Meyer, Mittag & Goerge 2022).
  - An older SIPP panel (2008) would work but is dated.
- **Feasibility:** Low–Medium. Identification is weaker than the admin-data papers it would be compared to.
- **Learning value:** High for survival/hazard models, which transfer directly to customer-retention work.

### Candidate 7 (DS): Inflation inequality across household groups, 2021–2025

- **Verdict:** saturated.
  - BLS now publishes official research CPIs by income quintile (R-CPI-I, Dec 2005–Dec 2025).
  - CBO (2025), the Cleveland Fed (2025), BLS/BEA (Gindelsky & Martin 2026), Fed (Orchard 2025), and Cavallo & Kryvtsov (2024) cover the episode.
- A CE-weighted replication would add nothing. It remains a fine *skills exercise* but not a paper.

### Candidate 8 (DS/EM): Promotional dynamics with Dominick's scanner data

- **Verdict:** weak for a first paper.
  - The data are 1989–97 and heavily mined. Recent uses are as methods benchmarks.
  - Terms say "academic research purposes only". **Eligibility for an unaffiliated researcher is UNVERIFIED.**
  - Modern scanner data (NielsenIQ via Kilts) are **closed to independent researchers**: institutional subscription required, and all coauthors must be academic.

### Rejected direction: customer retention / subscription churn with public data

No public, reproducible, *real* longitudinal customer dataset of publication quality was identified.

- Common public churn datasets are synthetic, very small, or competition data with redistribution terms.
- **Implication:** the author's interest in customer retention is best served through public-data *analogues*:
  - SNAP spells (Candidate 6);
  - business survival (BDS/BED);
  - subscription *spending* (Candidate 2).
- Alternatively, a future project could use a data partnership with a firm. That would no longer be public-data research.

---

## 3. Ranking

Scores are judgments made when drafting this roadmap, on a 1–5 scale (5 = best), informed by the verification above. They are not measurements, and the total is unweighted. If learning value or publication potential is weighted more heavily, the ordering shifts slightly, but the top three do not change.

| # | Candidate | Track | Feasibility | Research value | Econometric depth | Data access | Reproducibility | Publication potential | Learning value | **Total /35** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BFS → state establishment births nowcasting | DS | 5 | 4 | 3 | 5 | 5 | 4 | 4 | **30** |
| 3 | Income volatility & hardship (SIPP) | EM | 3 | 4 | 4 | 4 | 4 | 4 | 5 | **28** |
| 2 | Digital-subscription Engel curves (CE) | DS | 4 | 3 | 3 | 5 | 5 | 3 | 4 | **27** |
| 4 | Min wage & business entry/exit | EM | 3 | 3 | 5 | 4 | 4 | 3 | 5 | **27** |
| 7 | Inflation inequality (CE + CPI) | DS | 5 | 2 | 2 | 5 | 5 | 1 | 3 | **23** |
| 5 | Gas-tax-holiday quantity response | EM | 2 | 3 | 4 | 2 | 3 | 3 | 4 | **21** |
| 6 | SNAP churn & recertification | EM | 2 | 3 | 4 | 2 | 4 | 2 | 4 | **21** |
| 8 | Dominick's promotions | DS/EM | 3 | 1 | 3 | 2 | 3 | 1 | 3 | **16** |

---

## 4. Recommendations

### First project (complete the full research cycle): Candidate 1, BFS → state establishment births

Why this one:

- **Lowest risk of failing before completion.**
  - Two official public files, small data, no licensing.
  - A prediction question with a clear scoring rule, so no causal identification is required.
  - It produces a usable result whichever way it comes out: "applications help," "they don't," and "ML doesn't beat ARDL here" are all reportable.
- **Not trivial.** Doing forecast evaluation correctly requires substantive econometrics:
  - real information sets at each forecast origin;
  - nested-model tests;
  - multiple-comparison control;
  - revision and seasonal-adjustment look-ahead issues.
- **It is the one place where the "econometrics vs ML" comparison answers a substantive question** (is this indicator useful, and does flexibility help with short noisy panels?) rather than being a generic horse race. The generic horse race is crowded; see Goulet Coulombe et al. 2022, Medeiros et al. 2021, M4/M5.
- **It draws on the author's professional experience** in forecasting and business analytics.
- **It has a credible practitioner venue** (*Business Economics*) and a credible field venue (*Journal of Forecasting*).

Main risk: the Census research group (Haltiwanger and coauthors) could publish a state-level analysis first. Mitigation:

- move steadily;
- post a preprint (SSRN + MPRA) once results are stable;
- frame the contribution around the cross-state panel, the timing design, and the application-series decomposition.

### Parallel econometrics project: Candidate 3, income volatility and material hardship (SIPP 2018+)

Why this one over the alternatives:

- **Clearer gap** than minimum wage (Candidate 4) or gasoline (Candidate 5), both crowded and with an expert, adversarial referee pool.
- **Deep econometric training:**
  - complex survey panel data, longitudinal and replicate weights;
  - imputation handling, seam bias, attrition;
  - fixed effects and event studies;
  - careful separation of level, shock, and volatility.
- **Fits the author's interests in consumer and household economics,** and has realistic SSCI/EconLit venues.
- **Limitation, stated up front:** absent a credible quasi-experiment, this will be a rigorous *associational* paper. Part of the development work is searching for exogenous variation in income stability, and abandoning causal language if none is found.

**Alternate for the econometrics track:** Candidate 4 (minimum wage and business dynamism).

- It shares data infrastructure with Candidate 1 (BED/BDS/QCEW), which would build a coherent "business dynamics" research identity.
- It offers the deepest training in modern staggered DiD.
- It ranks second only because Kuroki (2025) is close and the literature is contested. Kuroki's methods should be checked before deciding.

**Second DS paper (later):** Candidate 2 (CE subscriptions) is a strong follow-on once the full cycle has been completed once.

---

## 5. A note on replications as a career tool

Replication journals are realistic and respected first outlets. Two constraints (verified):

- **JAE Replication Section** only accepts replications of papers in JAE or one of nine listed journals: Econometrica, AER, JPE, QJE, REStat, REStud, J. Econometrics, JBES, Economic Journal. It has a 12-page limit (per April 2025 rules; current status UNVERIFIED).
- **Journal of Comments and Replications in Economics** (ZBW) accepts broad replications. It has no fees, but requires push-button code from raw public data.

Project 1 includes a replication step: reproduce the national "applications lead employment" result before moving to states. That is good practice, but probably not a standalone paper.

---

## 6. Decisions requested from the author

All three were decided on 2026-10-14; see [../research_log.md](../research_log.md).

1. **Approve, change or reject** the first-project recommendation (Candidate 1). *Decision: approved.*
2. **Choose the econometrics-track project:** Candidate 3 (SIPP volatility) or Candidate 4 (minimum wage and business dynamism). *Decision: Candidate 3.*
3. **Version control:** whether to initialize a git repository in this folder and, later, create a GitHub repository. A public repository is the usual reproducibility standard. This folder was in OneDrive at the time: git works there but can conflict with sync, so a non-synced path with a GitHub remote is cleaner. *Decision: the repository was moved to a local, non-synced path with a private GitHub remote.*

The draft plan for Candidate 1 is in [02_project1_research_plan.md](02_project1_research_plan.md). It was written so it could be adopted or discarded depending on decision 1; it was adopted and has since been superseded by the project's [research_question.md](../projects/p1-bfs-establishment-births/research_question.md).
