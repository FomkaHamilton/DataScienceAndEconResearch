# Project 1: Business Applications and State Establishment Births

**Status (2026-10-15):** data acquisition, exploratory analysis, the pre-analysis plan and Addenda 1–4, the primary evaluation, the robustness analyses, and the RQ2 and RQ4 analyses are complete. Manuscript draft v1, with 7 figures, is in [manuscript/draft_v1.md](manuscript/draft_v1.md). Pre-registered live forecasts for 2026Q1–Q3 will first be scored when BLS publishes 2026Q1 data on 2026-10-28.

Paper title: *Business Applications as a Leading Indicator of New Establishments: Evidence from U.S. States That the Relationship Changed After 2020*. Target journal: *Journal of Forecasting*.

Full design: [research_question.md](research_question.md); binding specification: [pre_analysis_plan.md](pre_analysis_plan.md) and its addenda. Program-level context: [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md) (the original proposal, now superseded) and [../../roadmap/sources_verified_2026-10-14.md](../../roadmap/sources_verified_2026-10-14.md).

## Summary of findings

The question is predictive: do Census business applications (BFS) improve out-of-sample forecasts of state establishment births (BLS BED)? The project makes no causal claims.

- **Locked 2023–2025 test window:** no detectable gain from adding applications. At the three-quarter lead the gain is +1.6% of the benchmark's mean squared error (95% CI −6.5% to +9.7%). Machine-learning models do no better.
- **Inference:** naive pooled tests, which treat the 612 test-window state-quarters as independent, overstate significance. For example, the information test at the three-quarter lead gives p = 0.0003 naively but p ≈ 0.07 with dependence-robust inference.
- **Over time, the relationship is regime-dependent:** modest but real in 2010–2019, large in 2020–21, and absent in 2022–25.
- **RQ2 (application series):** the narrower employer-intent series (high-propensity applications and applications with planned wages) predicted better than all applications before 2020, but not after.
- **RQ4 (exploratory):** before 2020, same-quarter gains were larger in states where a higher share of new establishments came from new firms (Spearman ρ = 0.37, Holm-adjusted p = 0.014).

Details: [literature/phase5_findings.md](literature/phase5_findings.md), [literature/rq2_findings.md](literature/rq2_findings.md), [literature/rq4_findings.md](literature/rq4_findings.md).

## Phase status

Each phase ends with a gate: a check, stated in advance in the [research plan](../../roadmap/02_project1_research_plan.md#5-workflow-phases-and-gates), that must pass before the next phase begins.

| Phase | Status |
|---|---|
| 0. Setup | Done |
| 1. Literature review | Done; gate passed. See [literature/extraction_table.md](literature/extraction_table.md). |
| 2. Data acquisition | Done (BFS, BED, BDS). See [data/MANIFEST.md](data/MANIFEST.md). BED has no archive of past data vintages, so the analysis uses final-vintage data; this is stated as a limitation ([pre_analysis_plan.md](pre_analysis_plan.md) §3). |
| 3. Exploratory analysis | Done; gate passed. See [literature/phase3_findings.md](literature/phase3_findings.md). |
| 4. Pre-analysis plan | Committed (commit 08853fc) before any test-window evaluation. See [pre_analysis_plan.md](pre_analysis_plan.md). Addenda 1, 2 and 4 were each committed before the analyses they specify; Addendum 3 was committed with the live forecasts, before any outcome data exist. |
| 5. Baseline and full model set | Done (corrected run; the three errors found in the first run are documented in the findings). See [literature/phase5_findings.md](literature/phase5_findings.md). |
| 6. Robustness and sensitivity | Done via [Addendum 1](pre_analysis_plan_addendum_1.md): seasonally adjusted series, winsorizing, performance over time, detectable effects. |
| 7. Secondary and exploratory questions | RQ2 done via [Addendum 2](pre_analysis_plan_addendum_2.md) ([findings](literature/rq2_findings.md)); RQ4 done via [Addendum 4](pre_analysis_plan_addendum_4.md) ([findings](literature/rq4_findings.md)). |
| 7b. Live forecasts | Forecasts for 2026Q1–Q3 pre-registered via [Addendum 3](pre_analysis_plan_addendum_3.md) (commit 7a36fe1, tag `prereg-live-forecasts-2026`). First scoring when BLS publishes 2026Q1 on 2026-10-28. |
| 8. Reproducibility audit | Passed 2026-10-15. A fresh clone at commit a131fb8, with the pinned environment and one command, reproduced all 31 tables committed at the time (maximum difference 1.1e-14) and all 6 figures. The latest full re-run (2026-10-15) passed with 36 tables and 21 figure files (7 analysis figures, plus 7 manuscript figures in PNG and PDF). See [Reproduce](#reproduce). |
| 9. Drafting | In progress. Draft v1 with 7 figures: [manuscript/draft_v1.md](manuscript/draft_v1.md). |
| 10. Submission | Not started |

## Reproduce

Tested with Python 3.12.10. Package versions are pinned in [`requirements.txt`](../../requirements.txt).

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
cd projects/p1-bfs-establishment-births
python replication/run_all.py          # about 5 minutes; regenerates every table and figure
python replication/verify_outputs.py   # checks that the regenerated outputs match the committed ones
```

On Windows, clone to a short path (for example `C:\src\...`). Long paths can exceed the Windows 260-character path limit inside `.git` and `.venv`.

`run_all.py` starts from the committed processed data, so it reproduces the committed numbers. Some tables may differ from the committed files in about the 15th–16th significant digit, because the random forest sums its trees in parallel and the order varies between runs. `verify_outputs.py` treats these as matches; they are not substantive. `run_all.py --full` re-downloads the raw data first; because Census and BLS revise their data, that can give slightly different numbers. The download scripts identify themselves to Census and BLS with a contact address, read from the `RESEARCH_CONTACT_EMAIL` environment variable (or from a `.env` file at the repository root, which git ignores), so set it before using `--full`. See [data/MANIFEST.md](data/MANIFEST.md) for sources, retrieval dates and checksums.

**Word version of the manuscript.** The Markdown file `manuscript/draft_v1.md` is the master copy. To build a Word version (written to the git-ignored `manuscript/submission/` folder), run `pip install -r requirements-manuscript.txt` from the repository root, then `python projects/p1-bfs-establishment-births/manuscript/build_docx.py`.

## AI-use record

AI assistance is recorded, entry by entry, in this project's [research_log.md](research_log.md).
