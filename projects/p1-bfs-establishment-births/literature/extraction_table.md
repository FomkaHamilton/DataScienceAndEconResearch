# Literature Extraction — Project 1

*Produced 2026-10-14 per [search_protocol.md](search_protocol.md). Two parallel AI-assisted searches (content, methods); not yet reviewed by the author. Every entry below was confirmed on a real landing page by the search agent unless marked UNVERIFIED. Spot-check before citing in a manuscript.*

## Gate verdict

> **Does any existing, findable paper forecast or nowcast state-level BED (or QCEW) establishment births/dynamics from state-level BFS business-application data, with an out-of-sample econometric-vs-ML comparison?**

**No.** The closest paper (Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb, NBER w33224) is national-level, uses only a dynamic factor model, and stops at nonfarm payroll employment — not establishment births, not state panel, not ML. The state/local BFS literature that exists (Dinlersoz et al., NBER w34881) is structural/cross-sectional, not a rolling forecasting exercise. BLS's own birth-death nowcasting work (Grieves, Mance & Witt 2023) deliberately does not use BFS and is national only. Census's internal BFS methodology (the PBF4Q/PBF8Q projection model) classifies individual applications, not state BED outcomes.

**What differentiates Project 1 from everything found:** state as the unit for both predictor and outcome; genuine rolling out-of-sample evaluation across ~51 states, ~2005–2025; a direct econometric-vs-ML comparison; and decomposition of which BFS sub-series (BA/HBA/WBA/CBA) carries signal at the state level specifically.

**Caveat:** this was a web-search-based review (Google Scholar, NBER, SSRN, RePEc, Census CES, Fed series, journal sites), not a full EconLit/Scholar citation-graph crawl, and two PDFs failed to extract cleanly (cross-verified via snippets instead). Re-run a targeted Scholar/EconLit search before submission, and recheck closer to that date in case the Census/Haltiwanger group has moved to states (see "scooping risk" below).

## Content literature — core papers (verified)

| Citation | Data / Period | Method | Finding | Relation to Project 1 |
|---|---|---|---|---|
| Bayard, Dinlersoz, Dunne, Haltiwanger, Miranda & Stevens (2018). "Early-Stage Business Formation." NBER WP 24364. | BFS construction from IRS SS-4 filings, national/state/local | Descriptive | Introduces the BFS dataset; applications are a timely forward signal | Source dataset paper |
| Asturias, Dinlersoz, Haltiwanger & Hutchinson (2023). "Are Business Applications Early Economic Indicators?" *AEA P&P* 113:151–55. doi:10.1257/pandp.20231053 | National, monthly | Descriptive/correlational | Likely-employer application growth leads employment growth | National analogue |
| **Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb (2024). NBER WP 33224. "Business Applications as a Leading Economic Indicator?"** | National, monthly, 3 BFS series (BA, likely-employer≈HBA, likely-non-employer) vs. nonfarm payrolls / Principal Federal Economic Indicators | **Dynamic factor model only** | Applications lead most PFEIs; DFM with applications improves 12-month employment forecasts, especially around turning points | **Closest existing analogue. No state-level analysis. No ML comparison.** This is the paper Project 1 most directly extends. |
| Dinlersoz, Dunne, Haltiwanger & Penciakova. NBER WP 34881 (2026) / CES-WP-23-34. "The Local Origins of Business Formation... Entry as a Two-Stage Process." | County/local market, cross-sectional | Structural two-stage model (application → transition) | Local startup rates = ideas (applications) per capita × transition rate | Explains *why* local/state BFS signal composition may differ from national — background, not a forecasting precedent |
| Decker & Haltiwanger (2023). *Brookings Papers on Economic Activity*, Fall 2023:249–316. | National + some state/industry, descriptive | Descriptive/causal-flavored | Application surges in 2020–21 linked to employer entry (BED/QCEW), uncertain translation rate | Background on the 2020–21 structural break |
| Decker & Haltiwanger (2022). FEDS Note, 2022-05-06. | National, BFS + BED jointly | Descriptive | Both hit records in 2020–21; ~36% of establishment births come from existing firms | Quantifies the "dilution" mechanism noted in the research plan |
| **Grieves, Mance & Witt (2023). BLS research paper.** "Predicting the Effect of Business Births and Deaths on the CES Survey." | National CES, 2007–2020 | ARIMA-type + forecast combination (44 models) | Nowcasts the CES birth-death adjustment | **Confirmed: does not use BFS.** Direct evidence the obvious complementary approach hasn't been tried even nationally. |
| Borup & Schütte (2022). *JBES* 40(1):186–200. "In Search of a Job: Forecasting Employment Growth Using Google Trends." | State-panel extension *within the same paper*, high-dimensional variable selection vs. AR benchmarks | Elastic-net/subset-regression style vs. econometric benchmark, out-of-sample R² | Google Trends predicts employment growth at state level too | **Best available methodological template for a state-panel econometric-vs-ML design** — different predictor (search data) and outcome (employment, not births) |
| Savagar & Galanakis (2026). arXiv 2606.01307. UK Companies House incorporations → ONS business demography + employment/output. | UK, national/sectoral | SVAR | Incorporations lead official (lagged) demography stats | Structural analogue: admin registration data leading lagged official statistics — same shape of question, different country/data |
| Cao, Hyatt, Mukoyama & Sager. CES-WP-26-36 / FEDS 2026-40 (Jun 2026). "New U.S. Business Establishments: Surging or Stalling?" | BLS vs. Census establishment universes | Measurement reconciliation | BLS and Census establishment counts have diverged by ~1.6M by 2023, driven by frame-coverage differences | **Important measurement caveat:** BED and Census-based establishment counts are not interchangeable; document which is used and why |

## Scooping-risk check

Fetched the Census BFS methodology page directly: describes only the internal application-to-outcome classifier (PBF4Q/PBF8Q), no mention of state-level nowcasting or ML. Checked recent CES working paper listings (through 2026 Q2): nothing found addressing state-level BED forecasting from BFS. **Low scooping risk as of 2026-10-14**, but re-check before submission — this is an active research group.

## Methods literature

**Nested-model forecast tests:**
- Diebold & Mariano (1995), *JBES* 13(3):253–263 — built for non-nested comparisons; Diebold's own 2012/2015 retrospective (NBER WP 18391) flags applying it to nested models as a misuse.
- **Clark & West (2007), *J. Econometrics* 138(1):291–311** — the standard fix for nested models (adjusts for the noise from estimating parameters that are truly zero).
- McCracken (2007), *J. Econometrics* 140(2):719–752 — non-standard limiting distribution and valid critical values for nested DM/encompassing tests.
- **Giacomini & White (2006), *Econometrica* 74(6):1545–1578** — valid for both nested and non-nested models under possible misspecification; a robust fallback.

**Multiple-comparison control:**
- **Hansen, Lunde & Nason (2011), *Econometrica* 79(2):453–497 — Model Confidence Set.** Primary tool for this project.
- White (2000), *Econometrica* 68(5):1097–1126 — "Reality Check," an alternative.
- FDR-specific methods for forecast evaluation are comparatively ad hoc in this literature; MCS is the better-established primary tool. (A cited "Moon & Perron (2012)" FDR reference could not be independently confirmed — UNVERIFIED, do not cite without checking.)

**Panel extensions of forecast-comparison tests (directly useful — new since the original plan was drafted):**
- **Qu, Timmermann & Zhu (2024), *IJF* 40(3):918–941.** "Comparing forecasting performance with panel data." Tests equal forecasting performance pooled over time *and* units, plus subsets/clusters. Close methodological match for the 51-state panel.
- **Akgun, Pirotte, Urga & Yang (2024), *IJF* 40(1):202–228.** Panel equal-predictive-ability tests ("S-statistics" pooled, "C-statistics" clustered), valid under cross-sectional dependence — relevant since state loss differentials are plausibly correlated (e.g., by Census region).

**MIDAS / bridge equations:**
- Ghysels, Santa-Clara & Valkanov, CIRANO WP 2004s-20 ("The MIDAS Touch") and the peer-reviewed *J. Econometrics* 131(1–2):59–95 (2006) version.
- Bridge-equation references: ECB WP 949 (2008); Bundesbank DP 26/2014; and a direct MIDAS-vs-bridge comparison in *IJF* (ScienceDirect S0169207015001144).
- **Python tooling gap, confirmed:** no mature Python MIDAS package exists comparable to R's `midasr`. Options found (`midaspy`, `midas_pro`, `jstriaukas/midasmlpy`) are work-in-progress or narrowly scoped to regularized/high-dimensional variants. **Decision needed:** use bridge equations (straightforward in Python/statsmodels) as the primary mixed-frequency approach, or call R's `midasr` from Python if true MIDAS is wanted. Recommend **bridge equations as primary**, noted as a deliberate simplification.

**Econometric vs. ML on state/regional panels:**
- A small 2026 conference paper (EAI ICIAAI, not a top venue) forecasting state unemployment found **linear regression beat random forest/GBM out-of-sample**, with RF/GBM overfitting on a similarly short state-quarterly panel — a useful cautionary prior for RQ3, not a template to cite heavily given the venue.
- IMF WP 2025/252 (national GDP nowcasting, econometric vs. ML) is a reasonable design template, not state-panel-specific.
- **No peer-reviewed paper doing "ML vs. econometric on a 51-state establishment-type panel" was found** — consistent with the gate verdict.

**Real-time vintage data (resolves an open question from the research plan):**
- **BFS: vintages ARE available**, on ALFRED (Federal Reserve Bank of St. Louis), release IDs 443 (monthly/quarterly, state-level, confirmed for CA/FL/TX/NY/ID/WA/NC/MI/IL/AL/AZ/LA) and 468 (weekly, state-level, 2006–Oct 2026). Requires a free FRED/ALFRED API key.
- **BED: vintages are NOT available on ALFRED.** Checked the BLS source listing and the QCEW release directly — no BED gross-flows release exists there. A real-time BED vintage panel would have to be hand-built from BLS's historical news-release archive (`bls.gov/news.release/archives/cewbd_*.htm`) and annual revision notices. This is more work than assumed in the original plan.

## Decisions this resolves (updates to research_question.md)

1. Primary nested-model test: **Clark–West (2007)**, with **Giacomini–White (2006)** as the robust fallback. Not plain Diebold–Mariano for nested comparisons.
2. Multiple-comparison control: **Hansen–Lunde–Nason Model Confidence Set** as primary.
3. Pooled-panel significance: **Qu, Timmermann & Zhu (2024)** and/or **Akgun et al. (2024)** for a formal pooled/clustered test across states, rather than ad hoc per-state reporting.
4. Mixed-frequency model: **bridge equations**, not MIDAS — Python MIDAS tooling isn't mature enough to rely on. Document this as a deliberate scope choice.
5. Data-revision handling: BFS vintages can be pulled from ALFRED (needs a free API key). **BED has no existing vintage archive** — Phase 2 must either hand-construct one from BLS's release archive (real added effort) or run the pseudo-real-time analysis on final BED data only, stating that limitation plainly, as the original plan already allowed as a fallback.
