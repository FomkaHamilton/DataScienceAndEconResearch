# Verification Log, 2026-10-14

**Purpose.** This log records where each factual claim in the [roadmap](01_research_roadmap.md) was checked.

**How it was produced.** The checks were carried out by AI research agents (Claude) using live web search and page retrieval. Every item still requires a spot-check by the author before it is used in a manuscript.

**Status labels:**
- **verified**: confirmed on an official page.
- **[archive]**: confirmed only on a Wayback Machine copy of an official page.
- **[search-index]**: confirmed only from a search engine's snippet of an official page.
- **UNVERIFIED**: not confirmed.

Wiley, Taylor & Francis and Elsevier author pages blocked automated access, so those pages should be checked in a browser before they are relied on.

---

## A. Datasets

### BLS Consumer Expenditure Survey PUMD
- Landing page: https://www.bls.gov/cex/pumd.htm
- Coverage: 1980–2024 released; 1982–83 are not available.
- The 2025 PUMD is scheduled for Oct 29, 2026: https://www.bls.gov/cex/notices/2026/2026-2-year-tables.htm
- **2025 shutdown impact.** No data were collected Oct 1–Nov 12, 2025, and BLS will not adjust the PUMD weights: https://www.bls.gov/cex/2025-federal-government-shutdown-impact-ce.htm
- Expenditure codes (UCCs), from the integrated hierarchical grouping files in https://www.bls.gov/cex/pumd/stubs.zip:

  | UCC | Item | Coverage |
  |---|---|---|
  | 310240 | Streaming/downloading video | 2005Q2–2017Q1 |
  | 310243 | Rental, streaming, downloading video | from 2017Q2 |
  | 310350 | Audio streaming | — |
  | 620930 | Online gaming | — |
  | 270310 | Cable/satellite TV | — |
  | 690114 | Internet | — |

  There is no general "online subscriptions" UCC.
- Income has been multiply imputed (5 implicates) since 2004: https://www.bls.gov/cex/csximpute.htm
- Top-coding: https://www.bls.gov/cex/pumd_disclosure.htm
- The STATE variable exists from 2005, but about 14% of values are suppressed and about 4% are recoded.
- State research products are discontinued from 2026: https://www.bls.gov/cex/csxresearchtables.htm

### Census SIPP (2018+)
- Datasets: https://www.census.gov/programs-surveys/sipp/data/datasets.html. Data years 2018–2025 are released; 2025 was released 7/15/2026.
- 2022 Users' Guide: https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2022_SIPP_Users_Guide_SEP23.pdf
  - The 2019 panel was dropped after wave 1.
  - Seam bias is discussed in §2.7.
- Variables, confirmed in the 2025 dictionary (https://www2.census.gov/programs-surveys/sipp/tech-documentation/data-dictionaries/2025/2025_SIPP_Data_Dictionary.pdf):
  - SNAP: RSNAP_MNYN, TSNAP_AMT
  - Hardship: EAWBMORT, EAWBGAS
  - Food security: EFOOD1–6, RFOODS, RFOODR
  - State: TST_INTV, TEHC_ST
- Hardship items in data years 2019–21 and 2023–24: **UNVERIFIED**.

### Census Business Formation Statistics
- Landing page: https://www.census.gov/econ/bfs/index.html
- CSV: https://www.census.gov/econ/bfs/csv/bfs_monthly.csv
- Coverage: monthly from Jul 2004; national, regions, 50 states + DC + PR; state totals only. The latest release is Sep 2026 data, published 2026-10-14.
- Methodology: https://www.census.gov/econ/bfs/technicaldocumentation/methodology.html
- Revisions: annual, usually with the December release.
- API (key required): https://api.census.gov/data/timeseries/eits/bfs. Whether it serves state geography is **UNVERIFIED**.
- County annual data: https://www.census.gov/econ/bfs/data/county.html

### BLS Business Employment Dynamics
- Landing page: https://www.bls.gov/bdm/
- State tables: https://www.bls.gov/bdm/bdmstate.htm
- Flat files: https://download.bls.gov/pub/time.series/bd/
- Coverage and timing:
  - Quarterly from 1992Q3.
  - The latest quarter is 2025Q4, released 2026-07-29.
  - 2026Q1 is due 2026-10-28, with annual revisions.
  - Establishment deaths lag births by 3 quarters.

### Census Business Dynamics Statistics
- Datasets: https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html
- Coverage: 1978–2023 (released Sep 2025), with state, county and MSA geography and firm-age cross-tabs.

### EIA and FHWA gasoline data
- **EIA-782C Prime Supplier Sales is discontinued.** The last data are for March 2022: https://www.eia.gov/petroleum/marketing/prime/ and https://www.eia.gov/pressroom/releases/press532.php
- EIA's all-state monthly retail price series covered only 1983–2011 (https://www.eia.gov/tools/faqs/faq.php?id=26&t=10). Weekly prices are published for 9 states only.
- FHWA monthly gasoline volumes (DataHub, 2020–May 2026): https://data.transportation.gov/Roadways-and-Bridges/Monthly-Motor-Fuel-Gasoline-Volumes-Distributed/5qxh-t94v
  - Georgia's Apr–Dec 2022 rows are flagged "Estimate".
- FHWA Highway Statistics 2024 (MF-21, MF-33GA, MF-205): https://www.fhwa.dot.gov/policyinformation/statistics/2024/
- 2022 state gas tax holidays:

  | State | Dates | Source |
  |---|---|---|
  | Georgia | Mar 18, 2022–Jan 10, 2023 | https://dor.georgia.gov/2022-suspension-georgia-motor-fuel-taxes-faqs |
  | Maryland | Mar 18–Apr 16, 2022 | https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb1010?ys=2022RS |
  | Connecticut | Apr 1–Dec 31, 2022 | https://portal.ct.gov/drs/news---press-releases/2022/2022-latest-news/fuels-tax-suspension |
  | New York | Jun 1–Dec 31, 2022 | https://tax.ny.gov/pdf/notices/n22-1.pdf |
  | Florida | Oct 2022 | https://floridarevenue.com/MotorFuel/Documents/2022/2022%20Florida%20Motor%20Fuel%20Tax%20Relief%20Act%20-%20External%20FAQs%20-%20Retail%20Dealers.pdf |

### USDA ERS SNAP Policy Database
- Landing page: https://www.ers.usda.gov/data-products/snap-policy-data-sets
- Coverage: Jan 1996–Dec 2020, last updated 2/29/2024. Recertification variables are missing from Oct 2019.

### Kilts Center (Chicago Booth)
- Dominick's (https://www.chicagobooth.edu/research/kilts/research-data/dominicks):
  - Use is restricted to "academic research purposes only".
  - Eligibility of independent researchers: **UNVERIFIED**.
- NielsenIQ: https://www.chicagobooth.edu/research/kilts/research-data/nielseniq/policies
  - Access requires an institutional subscription.
  - All coauthors must be academic.

### BLS CPI by income
- R-CPI-I page: https://www.bls.gov/cpi/research-series/r-cpi-i.htm
- R-CPI-I covers Dec 2005–Dec 2025, all-items only.

---

## B. Literature anchors (confirmed on landing pages by the AI search agents)

As of 2026-10-14, none of these had been read in full by the author or the AI assistant; full reading was scheduled for each project's Phase 1 literature review. Citation details must be re-checked against the publisher page before they enter a `.bib` file.

**Project 1 (BFS):**
- Bayard et al. 2018, NBER w24364: https://www.nber.org/papers/w24364
- Asturias, Dinlersoz, Haltiwanger & Hutchinson 2023, AEA P&P 113, doi:10.1257/pandp.20231053
- Asturias, Dinlersoz, Haltiwanger, Hutchinson & Plumb 2024, NBER w33224: https://www.nber.org/papers/w33224
- Decker & Haltiwanger 2023, BPEA Fall 2023: https://www.brookings.edu/wp-content/uploads/2023/09/Decker-Haltiwanger_16820-BPEA-FA23_WEB.pdf
- Decker & Haltiwanger 2022, FEDS Note: https://www.federalreserve.gov/econres/notes/feds-notes/business-entry-and-exit-in-the-covid-19-pandemic-a-preliminary-look-at-official-data-20220506.html
- Dinlersoz, Dunne, Haltiwanger & Penciakova, NBER w34881 (2026): https://www.nber.org/papers/w34881
- Grieves, Mance & Witt 2023, BLS: https://www.bls.gov/osmr/research-papers/2023/pdf/st230010.pdf
- Borup & Schütte 2022, JBES 40(1): https://ideas.repec.org/a/taf/jnlbes/v40y2022i1p186-200.html
- Goulet Coulombe et al. 2022, JAE, doi:10.1002/jae.2910
- Medeiros et al. 2021, JBES, doi:10.1080/07350015.2019.1637745
- Makridakis et al., M5 results, IJF 38(4) 2022: https://www.sciencedirect.com/science/article/pii/S0169207021001874

Method anchors cited in the plan, not verified by an agent on 2026-10-14 (to be verified in Phase 1; for Project 1 they were subsequently confirmed in the [literature extraction table](../projects/p1-bfs-establishment-births/literature/extraction_table.md)):
- Diebold & Mariano (1995)
- Clark & West (2007)
- Hansen, Lunde & Nason (2011)
- Giacomini & White (2006)

**Candidate 3 (SIPP volatility):**
- Leete & Bania 2010, Rev Econ Household, doi:10.1007/s11150-009-9075-4
- Dahl, DeLeire & Mok 2014, AEPP, doi:10.1093/aepp/ppu009
- Heflin 2016, JFEI: https://link.springer.com/article/10.1007/s10834-016-9503-6
- Bania & Leete 2022, CEP, doi:10.1111/coep.12580
- Iceland & Cho 2026, PRPR, doi:10.1007/s11113-026-10019-1
- Urban Institute 2026 brief on the CPS-FSS suspension: https://www.urban.org/sites/default/files/2026-05/Assessing_National_Survey_Options_for_Food_Security_Measurement_Following_CPS-FSS_Suspension.pdf

**Candidate 4 (minimum wage):**
- Meer & West 2016, JHR: https://jhr.uwpress.org/content/51/2/500
- Kuroki 2025, JICSB: https://www.tandfonline.com/doi/abs/10.1080/26437015.2025.2571671
- Lyu & Fossen 2025, IZA DP 18101
- Jha, Neumark & Rodriguez-Lopez 2024, NBER w32901
- Dube, Reich et al., NBER w32902
- Jardim et al. 2024, JPubE 234

**Candidate 5 (gasoline):**
- Coglianese et al. 2017, JAE, doi:10.1002/jae.2500
- Davis & Kilian 2011, JAE, doi:10.1002/jae.1156
- Bates & Kim 2024, JAE: https://onlinelibrary.wiley.com/doi/10.1002/jae.3042
- Kilian & Zhou 2024, JPubE, doi:10.1016/j.jpubeco.2024.105099
- Tsvetanov 2024, Energy Economics 136
- Bradt & Taylor 2026, Dallas Fed WP 2624

**Candidate 6 (SNAP):**
- Gray 2019, JPubE 179
- Homonoff & Somerville 2021, AEJ: Policy 13(4)
- Meyer, Mittag & Goerge 2022, JHR 57(5)

**Candidate 7 (inflation inequality):**
- Klick & Stockburger 2024, MLR
- Carloni 2025, CBO WP 2025-04
- Luduvice et al. 2025, Cleveland Fed EC 2025-11
- Gindelsky & Martin 2026, Macroeconomic Dynamics
- Orchard 2025, FEDS 2025-085

---

## C. Journals

**Price lists** (amounts confirmed from downloaded files):
- Wiley APC list (updated 12 Oct 2026): https://authors.wiley.com/asset/Wiley-Journal-APCs-OnlineOpen.xlsx
- Elsevier APC list (5 Oct 2026): https://legacyfileshare.elsevier.com/els_com_pricing/article-publishing-charge.xlsx
- EconLit journal list: https://www.aeaweb.org/econlit/journal_list.php

APC means the optional hybrid open-access charge.

| Journal | Key verified facts | Source / status |
|---|---|---|
| Journal of Applied Econometrics, Replication Section | Replicates only papers in JAE + 9 listed journals; ≤12 pages; JAE Data Archive deposit required; no page charge; APC $4,230 | [archive Apr-2025]; https://qed.econ.queensu.ca/jae/author-instructions.html |
| J. Comments & Replications in Economics (ZBW) | No fees or APCs; push-button code checked before review | https://jcr-econ.org/submissions/ |
| Economics Bulletin | Refereed notes ≤7 pages; average lag about 43 days; max 3 submissions per author per year | http://www.accessecon.com/pubs/EB/ |
| Applied Economics Letters | ≤2,000 words; $125 submission fee | [archive Dec-2023] |
| Applied Economics | 8,000 words; $250 submission fee | [archive Oct-2024] |
| Business Economics (NABE) | No submission fee; welcomes practitioners; APC $3,190; EconLit + Scopus | https://link.springer.com/journal/11369/submission-guidelines |
| Journal of Forecasting | No submission fee; expects data sharing; APC $3,570 | [archive Apr-2025] + Wiley list |
| International J. of Forecasting | Double-anonymized; notes and replications accepted; APC $3,500. Data/code mandatory per 2023 editor report vs "encouraged" in 2024 guide (conflict) | Elsevier shop page; https://forecasters.org/wp-content/uploads/IJFreport2023.pdf |
| Small Business Economics | Double-anonymous; explicitly provides for unaffiliated authors; replications welcome; JIF 5.9 | https://link.springer.com/journal/11187 |
| Empirical Economics | Replications as short papers; data/code required; JIF 1.9 | https://link.springer.com/journal/181 |
| J. Family & Economic Issues | Double-blind; JIF 2.5; APC $3,390 | https://link.springer.com/journal/10834 |
| J. Consumer Affairs | $125 submission fee, waived for ACCI members | https://www.consumerinterests.org/submitting-to-jca |
| Contemporary Economic Policy (WEAI) | $90 (member) / $100 (non-member) submission fee | https://www.weai.org/submit-a-manuscript |
| Journal of Data Science | No APCs; LaTeX only; not in EconLit | https://jds-online.org/journal/JDS/information/open-access-policy |
| PLOS ONE | $2,477 fee; "sound science" criteria; not in EconLit | https://www.plos.org/publication-fees |

**Preprint routes:**
- SSRN welcomes independent scholars: https://blog.ssrn.com/2025/11/20/welcome-to-ssrn/
- MPRA is the RePEc route for unaffiliated economists: https://mpra.ub.uni-muenchen.de/
- arXiv requires endorsement: https://info.arxiv.org/help/endorsement.html

**Publisher AI policies:**
- Elsevier: https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
- Wiley: https://authors.wiley.com/ethics-guidelines/index.html
- T&F [search-index]: https://taylorandfrancis.com/our-policies/ai-policy/
- Springer Nature: quoted in each journal's guidelines.
