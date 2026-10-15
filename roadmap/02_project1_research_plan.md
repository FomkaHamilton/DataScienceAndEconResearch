# Research Plan (DRAFT) — Project 1: Business Applications and State Establishment Births

*Drafted 2026-10-14. Status: **draft pending author approval** of the first-project choice (see [01_research_roadmap.md](01_research_roadmap.md) §6).*
*No data has been downloaded into the project or modeled. Everything below is design, not results.*

Working title: *Do Business Applications Predict Where New Establishments Will Open? State-Level Nowcasts of Establishment Births from the Business Formation Statistics.*

---

## 1. Research questions

**Primary (predictive):**

> **RQ1.** Does adding state business-application data (Census BFS) to time-series benchmarks reduce out-of-sample error in nowcasts and short-horizon forecasts of state establishment births (BLS BED)?

**Secondary:**

> **RQ2.** Which application series carries the signal? The candidates are all applications (BA), high-propensity applications (HBA), applications with planned wages (WBA), and corporate applications (CBA).
>
> **RQ3.** Do flexible ML methods (regularized regression, random forests, gradient boosting) improve on well-specified linear econometric models (ARDL, MIDAS/bridge) in this setting: a short, noisy panel of about 51 states × about 84 quarters? Are any gains concentrated in turbulent periods?

**Exploratory (labeled as such in the paper):**

> **RQ4.** Is the predictive gain from BFS larger in states where a larger share of establishment entry comes from *new firms* rather than expansions of existing firms (measured from Census BDS by firm age)? This is the economic-mechanism test.

**What this paper will not claim:** it makes no causal claims. Applications do not "cause" births; they are an early observable step on the same path. All language will be predictive.

---

## 2. Formal design (the checklist from the context document)

| Element | Definition |
|---|---|
| **Outcome** | Primary: state private-sector establishment births, BED, quarterly, expressed as the **year-over-year log change of the not-seasonally-adjusted (NSA) series**. Using NSA year-over-year changes avoids look-ahead from seasonal adjustment and removes seasonality without a filter. Alternatives (robustness): seasonally adjusted (SA) level growth; births rate (births / establishments). |
| **Predictors ("exposure")** | BFS state series (BA, HBA, WBA, CBA), NSA, monthly, aggregated to quarters for ARDL. Monthly values are used directly for MIDAS/bridge models. Lags of the outcome. |
| **Unit of analysis** | State × quarter. Universe: 50 states + DC. Puerto Rico excluded unless both series cover it consistently. |
| **Time period** | Data from 2004Q3 (start of BFS) through the latest BED quarter (2025Q4 as of today; Q1 2026 is due 2026-10-28). |
| **Estimand** | Out-of-sample forecast loss (RMSE/MAE) of model *m* relative to benchmark, at horizons *h*, averaged over states and forecast origins in the evaluation window. |
| **Information set** | At each forecast origin, use **only data that would have been published by that date**. BFS arrives about 2 weeks after month end; BED arrives about 7 months after quarter end. That gap creates *backcast* (BED quarters already over but unpublished), *nowcast*, and *forecast* horizons. **The exact release calendar must be built from BLS/Census archives in Phase 2, because lags may have changed over time.** |
| **Hypotheses** | H1: BFS-augmented models beat the AR benchmark at backcast/nowcast horizons, with gains shrinking with horizon. H2: HBA/WBA beat total BA. RQ3 is treated as an open question, not a hypothesis to confirm. The prior, from short samples, is that ML gains will be small except possibly around 2020–21. |
| **Identification** | Not applicable (predictive). The analog is **evaluation validity**: no leakage, real information sets, and pre-specified comparisons. |

### Threats to validity and how each is handled

| Threat | Handling |
|---|---|
| **Data revisions.** BED revises 4 quarters NSA each year; BFS revises annually. No real-time vintage archive has been found yet. | Phase 2: search for vintages (BLS news-release archives, ALFRED). If none exist, run a *pseudo-real-time* exercise on final data, say so explicitly, and start archiving vintages from now on. |
| **Seasonal-adjustment look-ahead.** SA series use future data. | Primary spec uses NSA year-over-year changes. SA is robustness only. |
| **2020–21 structural break.** The application surge was driven partly by nonemployer and online businesses. | Pre-specified subperiod reporting (pre-2020, 2020–21, post-2021) and an excluding-COVID sensitivity analysis. |
| **Tuning leakage** (ML hyperparameters, lag selection) | All tuning inside each rolling origin using only past data (time-series cross-validation). The final test window stays locked until the pre-analysis plan is committed. |
| **Multiple comparisons** (many models × 51 states × horizons) | Two pre-specified primary comparisons. Everything else goes through a model confidence set (Hansen, Lunde & Nason 2011). Per-state results are descriptive, with FDR control. |
| **Nested-model testing** | Clark–West (2007) for nested AR vs AR+BFS comparisons; Diebold–Mariano (1995) for non-nested ones. Panel versions to be reviewed in Phase 1. |
| **Small per-state samples** | Pooled panel models with state effects as the main spec. Per-state models are a comparison. ML pooled across states. |
| **Births from existing firms dilute the signal** | This is a substantive feature, not a nuisance; RQ4 exploits it. |
| **Scooping** by the Census/CES research group | Move steadily; post a preprint (SSRN + MPRA) once the core results are stable. |

---

## 3. Models (to be finalized in the pre-analysis plan)

1. **Benchmarks:** seasonal naive / random walk on year-over-year changes; AR(p) per state; pooled panel AR with state fixed effects.
2. **Econometric with BFS:** ARDL (per state and pooled); bridge equations and MIDAS for the monthly→quarterly frequency mismatch.
   - Python MIDAS support is thin. Options: implement restricted-Almon MIDAS directly, or use R `midasr`. Decide in Phase 4 and document.
3. **ML with BFS:** elastic net / LASSO on lag sets; random forest; gradient boosting. All pooled across states with state identifiers or target encoding.
4. **Forecast combination:** equal-weight combination of the econometric and ML forecasts. Combinations often win, and a referee will ask.

Evaluation uses expanding and rolling windows. Development window is about 2010–2022. **The test window (about 2023Q1–latest) is locked until the pre-analysis plan is committed.**

---

## 4. Data sources (verified 2026-10-14; details in [sources_verified_2026-10-14.md](sources_verified_2026-10-14.md))

| Dataset | Provider | Access | Coverage | Role |
|---|---|---|---|---|
| Business Formation Statistics | Census | CSV `census.gov/econ/bfs/csv/bfs_monthly.csv`; API (free key) | Monthly, Jul 2004–Sep 2026, states (totals only) | Predictors |
| Business Employment Dynamics | BLS | `download.bls.gov/pub/time.series/bd/`; BLS API | Quarterly, 1992Q3–2025Q4, states | Outcome |
| Business Dynamics Statistics | Census | API (free key) | Annual, 1978–2023, state × firm age | RQ4 mechanism |
| BLS / Census release calendars & archives | BLS, Census | Web archives | Historical | Information sets |

**Open data questions to resolve in Phase 2:**

- whether BED state births are available by industry or only for the total private sector;
- historical BED release lags;
- availability of historical vintages;
- whether the BFS API serves state geography;
- the exact series IDs and SA/NSA definitions.

---

## 5. Workflow, phases and gates

Each phase ends with a **gate**: a check that must pass before moving on. The effort figures are rough, part-time estimates.

| Phase | Work | Gate (stop / pivot if this fails) | Rough effort |
|---|---|---|---|
| **0. Setup** | Git repo, environment file, folder structure, research log, AI-use log | Clean `pip install -r requirements.txt` | 1 week |
| **1. Literature review** | Systematic search (Google Scholar, EconLit via a library or the AEA, NBER, SSRN, Census CES WPs, Fed series, IJF/JoF) with a written search protocol and an extraction table. Core reading includes the BFS papers, the forecast-evaluation methods papers, and ML-vs-econometrics forecasting. | **No existing paper does state BFS → BED births forecasting.** If one does, pivot to an extension or to Candidate 2. | 2–4 weeks |
| **2. Data acquisition & documentation** | Acquisition scripts with retrieval dates and URLs; codebook; release-timing calendar; vintage investigation | Panel built reproducibly from raw downloads; timing documented | 2–3 weeks |
| **3. Exploratory analysis (development window only)** | Descriptives, series behaviour, cross-correlations. Sanity replication: national applications lead national births/employment, consistent with Asturias et al. | Signal plausibly present, or a clear reason it's absent (which is still a finding) | 2 weeks |
| **4. Pre-analysis plan** | Targets, horizons, models, primary comparisons, tests, robustness list, test-window dates. Committed to git with a timestamp; optionally registered on OSF (verify OSF terms). | PAP committed **before** any test-window evaluation | 1 week |
| **5. Baseline + full model set** | Benchmarks → ARDL/MIDAS → ML → combinations | Code reviewed by you; results reproducible from a clean run | 3–5 weeks |
| **6. Robustness & sensitivity** | SA vs NSA, window type, COVID exclusion, alternative targets (births rate; QCEW employment growth as a secondary outcome), horizon profile | Results stable, or instability documented and explained | 2–3 weeks |
| **7. Heterogeneity (RQ4)** | State-level gains vs BDS new-firm share | Labeled exploratory | 1–2 weeks |
| **8. Reproducibility audit** | Fresh clone → one command → all tables and figures | Byte-for-byte or tolerance-level match | 1 week |
| **9. Drafting** | Paper, figures, tables, appendix, replication README | You can defend every number and choice | 4–6 weeks |
| **10. Submission** | Re-verify journal policies live; preprint (SSRN + MPRA); cover letter; AI disclosure as each journal requires | Policies checked on submission day | 1–2 weeks |

---

## 6. Target venues (fit as of 2026-10-14; re-verify at submission)

| Role | Journal | Why | Notes |
|---|---|---|---|
| **Primary** | *Journal of Forecasting* (Wiley) | Applied business and economic forecasting is core scope | No submission fee; expects data sharing; Wiley AI disclosure policy. Length limits UNVERIFIED. |
| **Primary alternate** | *Business Economics* (NABE / Springer Nature) | Practitioner-relevant; explicitly welcomes practitioners and analysts | No submission fee; EconLit + Scopus |
| **Stretch** | *International Journal of Forecasting*, as a research note | Top field journal; accepts notes | Data/code sharing mandatory per 2023 editor report (current guide wording conflicts; verify) |
| **Alternative** | *Empirical Economics* (Springer) | Broad empirical scope; SSCI | Data/code required for accepted papers |
| **Short version** | *Economics Bulletin* | Free, refereed, fast (about 43-day average lag) | Max 7 pages excluding tables and figures |

Preprints: SSRN (welcomes unaffiliated authors) and MPRA (RePEc route for unaffiliated economists). arXiv econ would need a personal endorser.

---

## 7. Project repository structure (created at Phase 0, after approval)

```
projects/p1-bfs-establishment-births/
    README.md                 # how to reproduce, in one command
    research_question.md      # §1–2 of this plan, kept current
    pre_analysis_plan.md      # committed before test-window evaluation
    literature/               # search protocol, extraction table, notes
    data/raw/                 # downloaded files (gitignored if large; manifest committed)
    data/processed/
    data/MANIFEST.md          # source URL, retrieval date, params, checksums
    src/acquisition/  src/cleaning/  src/analysis/  src/visualization/
    notebooks/                # exploration only; results come from src/
    outputs/tables/  outputs/figures/
    manuscript/
    references/references.bib
    replication/
    requirements.txt
    research_log.md           # decisions, dead ends, AI-use log
```

---

## 8. AI-use transparency for this project

- Every session's substantive AI contributions (literature discovery, code, design suggestions, drafting) are recorded in `research_log.md`.
- You review and approve code and design decisions, and verify every citation against the source before it enters `references.bib`.
- The disclosure statement is written to the target journal's policy. For the publishers checked so far (Wiley, Springer Nature, Elsevier, T&F), AI cannot be an author and substantive use must be disclosed.
