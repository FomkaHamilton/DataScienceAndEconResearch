# Research Question and Design (current)

*This document is authoritative for the project's design. It is a condensed, living version of [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md), to be revised as the literature review and data acquisition narrow the design. Changes here should be logged in [research_log.md](research_log.md).*

**Status:** pre-literature-review draft. Not yet finalized — Phase 1 may change the question, benchmarks, or methods below.

## Questions

- **RQ1 (primary, predictive):** Does adding state business-application data (Census BFS) to time-series benchmarks reduce out-of-sample error in nowcasts and short-horizon forecasts of state establishment births (BLS BED)?
- **RQ2:** Which application series carries the signal — all applications (BA), high-propensity (HBA), planned-wage (WBA), or corporate (CBA)?
- **RQ3:** Do ML methods (regularized regression, random forest, gradient boosting) improve on well-specified econometric models (ARDL, MIDAS/bridge) in this short, noisy state panel? Are gains concentrated in turbulent periods?
- **RQ4 (exploratory):** Is the predictive gain larger in states where more establishment entry comes from genuinely new firms rather than expansions of existing firms (BDS firm-age data)?

**No causal claims.** Applications are an early observable step on the same path as establishment births, not a cause of them. All language is predictive/forecasting language.

## Design summary

| Element | Definition |
|---|---|
| Outcome | State private-sector establishment births (BED), quarterly, primary spec = YoY log change of the NSA series |
| Predictors | BFS state series (BA, HBA, WBA, CBA), NSA; lags of the outcome |
| Unit | State × quarter (50 states + DC) |
| Period | 2004Q3 (BFS start) through latest BED quarter |
| Estimand | Out-of-sample forecast loss (RMSE/MAE) vs. benchmark, by horizon |
| Information set | Real-time: only data that would have been published as of each forecast origin (BFS ~2-week lag; BED ~7-month lag — exact calendar to be confirmed in Phase 2) |

Full threat/validity table, model list, and phase plan are in the linked plan document. They will be revisited after the literature review.

## Open questions for Phase 1 to resolve

1. Does any existing paper already forecast state-level BED/QCEW establishment births from state BFS data? (Gate-defining question — see search protocol.)
2. Has anyone tested which BFS series (BA/HBA/WBA/CBA) is the best predictor, at any geographic level?
3. What forecast-evaluation methods are standard for this kind of short panel (nested-model tests, multiple-comparison control)? Are there established alternatives to Clark–West / Diebold–Mariano for panels?
4. Do real-time (vintage) data exist for BFS and BED, or must this be a pseudo-real-time exercise on final data?
5. Does Census or BLS have unpublished/working methodology for state-level nowcasting already underway that would make this redundant?
