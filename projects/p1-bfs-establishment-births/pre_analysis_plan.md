# Pre-Analysis Plan — Project 1

**Committed: 2026-10-15.** This plan is written and committed to git *before* any test-window data is used for model fitting or evaluation. Any deviation from this plan during Phase 5+ will be disclosed explicitly in the paper, not silently applied. This is the Phase 4 deliverable described in [research_question.md](research_question.md) and the program's standard workflow.

## 1. Test window (locked)

- **Development window:** 2004Q3–2022Q4. All specification search, hyperparameter tuning (via time-series cross-validation), and the exploratory analysis in [literature/phase3_findings.md](literature/phase3_findings.md) are confined to this window.
- **Test window:** 2023Q1–2025Q4 (births; latest published quarter as of 2026-10-15). 12 quarters. **Not loaded for anything but the final evaluation in Phase 5.**
- Establishment deaths publish with an additional ~3-quarter lag (through 2025Q1 as of this data pull); any model using deaths as a predictor or secondary outcome has a correspondingly shorter effective test window. The primary outcome (births) is not affected.

## 2. Outcome, predictors, and panel

Unchanged from [research_question.md](research_question.md): state × quarter panel, 50 states + DC, outcome = BED establishment births, predictors = BFS application series (BA_BA primary; HBA/WBA/CBA for RQ2).

## 3. Information set (pseudo-real-time on final-vintage data)

- BFS: treated as available ~2 weeks after month-end.
- BED: treated as available ~7 months after quarter-end.
- **Decision:** both series are used at their **final (most recently revised) values**, not true historical vintages, simulated as if released on the above approximate lags. Rationale: BED has no vintage archive anywhere (confirmed in Phase 1 — not on ALFRED, not elsewhere; would require hand-building one from BLS's archived news releases, a substantial side-project on its own). Using final data for BED but true vintages for BFS (which does exist on ALFRED) would be methodologically inconsistent, so both are final-vintage. **This is a stated limitation of the paper, not a hidden one** — a reviewer may reasonably ask for a sensitivity check using BFS's real ALFRED vintages; that is flagged as a natural extension requiring a free FRED/ALFRED API key (not yet obtained), not part of this submission's core design.

## 4. Seasonality / Q1-lumpiness handling (decided 2026-10-15, after user review)

Phase 3 found that NSA establishment-birth counts have irregular, state-varying Q1 spikes, and a follow-up check found **BFS applications show the same pattern even more strongly** (21% of state-Q1 observations show a >40% quarter-over-quarter jump, vs. ~0–3% in other quarters; 36 of 41 state-quarters where both series jump sharply at once are in Q1). This is a genuine confound risk: part of the Phase 3 lagged correlation could reflect both series reacting to the same calendar-timing effect (plausibly tax-year-aligned business registration timing) rather than applications genuinely forecasting births.

**Decision: layered handling, not a single fix.**

1. **Primary/structural fix:** all models (econometric and ML) include a **pooled quarter-of-year indicator** (Q1/Q2/Q3/Q4) as a regressor/feature, in addition to the YoY log-change transform already used. The YoY transform differences out a *stable* seasonal pattern; the quarter indicator absorbs whatever *average* seasonal growth-rate differential remains across calendar quarters in the pooled panel — directly targeting the shared-confound risk just found, not just outcome-side noise.
2. **Robustness line (not primary):** the same model specifications re-estimated on BLS's/Census's officially seasonally adjusted (SA) series, **without** the quarter indicator (redundant once SA). Explicitly labeled as **not valid for real-time forecasting claims** — SA construction can use future data to adjust a historical quarter, which is a look-ahead bias the NSA/pseudo-real-time design is otherwise built to avoid. Used only to check whether the core applications→births relationship survives under the official seasonal-adjustment treatment, not as evidence about genuine forecastability.
3. **Sensitivity check (disclosed, pre-specified now to avoid any appearance of post-hoc tuning):** winsorize the YoY log-change series at the 1st/99th percentiles **computed within the development window only** and held fixed for the test window (never recomputed using test-window data). Thresholds, fixed now:
   - `births_yoy`: winsorize to **[-0.474, +0.580]** (log points)
   - `BA_BA_yoy` (and analogously for HBA/WBA/CBA, computed the same way): winsorize to **[-0.239, +0.549]**
   - Results reported with and without this winsorization; it is a sensitivity check, not a silent data transformation.

## 5. Models

| Role | Specification |
|---|---|
| Benchmark | Seasonal naive; pooled panel AR(p) with state FE + quarter indicator |
| Econometric, with BFS | ARDL (pooled, state FE + quarter indicator); bridge equation for monthly BFS → quarterly BED |
| ML, with BFS | Elastic net / LASSO; random forest; gradient boosting — quarter and state encoded as categorical features, same lag structure as the econometric models |
| Combination | Equal-weight average of the econometric and ML forecasts |

Hyperparameters tuned only within the development window via time-series cross-validation (expanding origin); the test window is never used for tuning.

## 6. Evaluation design

- **Horizons:** h = 0 (nowcast), 1, 2, 3, 4 quarters ahead. h = 3 is a pre-specified horizon of particular interest, motivated directly by the Phase 3 national lag-correlation peak at 3 quarters — not chosen after seeing test-window results.
- **Windowing:** expanding-origin rolling forecasts through the test window.
- **Primary test:** Clark & West (2007) for each nested comparison (benchmark vs. benchmark+BFS); Giacomini & White (2006) as the robust fallback if nesting assumptions are in doubt for a given pair.
- **Multiple-comparison control:** Hansen–Lunde–Nason (2011) Model Confidence Set across the full model × horizon set.
- **Pooled/panel significance:** Qu, Timmermann & Zhu (2024) and/or Akgun, Pirotte, Urga & Yang (2024) for formal pooled and clustered tests across the 51-state panel, valid under cross-sectional dependence.

## 7. Primary vs. secondary comparisons (pre-specified to prevent fishing)

**Primary (report regardless of outcome):**
1. Pooled AR+quarter-FE benchmark vs. ARDL+BFS(BA_BA)+quarter-FE, at h=0 and h=3.
2. Best-performing ML model vs. the same benchmark, at h=0 and h=3.

**Secondary (pre-specified, reported but not the headline result):**
3. h=1, h=2, h=4 versions of the above.
4. RQ2: BA_BA vs. HBA vs. WBA vs. CBA as the predictor — which series carries the signal.
5. Per-state heterogeneity in predictive gains — descriptive, not a formal test per state (51 tests would need FDR correction the project isn't built to prioritize; MCS across models is the main formal multiplicity control).

**Exploratory (labeled as such, not confirmatory):**
6. RQ4: predictive gains vs. BDS new-firm-share (parked covariate, [data/MANIFEST.md](data/MANIFEST.md) item 3).

## Addenda

- [pre_analysis_plan_addendum_1.md](pre_analysis_plan_addendum_1.md) (2026-10-15) — robustness checks, performance over time, and detectable-effect analysis, committed after Phase 5 and before running them.
- [pre_analysis_plan_addendum_2.md](pre_analysis_plan_addendum_2.md) (2026-10-15) — RQ2 (which application series), in the test window and over time, committed before running.
- [pre_analysis_plan_addendum_3.md](pre_analysis_plan_addendum_3.md) (2026-10-15) — pre-registered live forecasts for 2026Q1–Q3, committed before BLS published any 2026 data.

## 8. What would change this plan

Per the program's own rules: if Phase 5 execution reveals a problem with this design (e.g., the quarter-FE/winsorizing choices don't behave as expected, or a model fails to converge), the deviation and the reason for it will be written into the paper and the research log — not quietly substituted.
