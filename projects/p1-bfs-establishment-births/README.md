# Project 1 — Business Applications and State Establishment Births

**Status: Phases 0–5 complete, including pre-analysis plan Addendum 1 (robustness, performance over time, detectable effects). Paper direction: the relationship between business applications and establishment births is regime-dependent (modest before 2020, strong in 2020–21, absent after). See [literature/phase5_findings.md](literature/phase5_findings.md).**

Working title: *Do Business Applications Predict Where New Establishments Will Open? State-Level Nowcasts of Establishment Births from the Business Formation Statistics.*

Full design: [research_question.md](research_question.md). Program-level context: [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md) and [../../roadmap/sources_verified_2026-10-14.md](../../roadmap/sources_verified_2026-10-14.md).

## Phase gate status

| Phase | Status |
|---|---|
| 0. Setup | Done |
| 1. Literature review | Done — gate passed, see [literature/extraction_table.md](literature/extraction_table.md) |
| 2. Data acquisition | Done (BFS + BED + BDS) — see [data/MANIFEST.md](data/MANIFEST.md). Vintage-data decision for BED still open (deferred to Phase 4). |
| 3. Exploratory analysis | Done — gate passed, see [literature/phase3_findings.md](literature/phase3_findings.md) |
| 4. Pre-analysis plan | Committed — see [pre_analysis_plan.md](pre_analysis_plan.md) |
| 5. Baseline + full model set | Done (corrected run) — see [literature/phase5_findings.md](literature/phase5_findings.md) |
| 6. Robustness & sensitivity | Done via [Addendum 1](pre_analysis_plan_addendum_1.md): seasonally adjusted series, winsorizing, performance over time, detectable effects |
| 7. Secondary / exploratory | RQ2 done via [Addendum 2](pre_analysis_plan_addendum_2.md), see [literature/rq2_findings.md](literature/rq2_findings.md). RQ4 (new-firm share, exploratory) not started. |
| 8. Reproducibility audit | Passed 2026-10-15. Fresh clone + pinned environment + one command reproduced all 31 tables (max difference 1.1e-14) and 6 figures. See [Reproduce](#reproduce). |
| 9+ | Not started |

## Reproduce

Tested with Python 3.12.10. Package versions are pinned in [`requirements.txt`](../../requirements.txt).

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
cd projects/p1-bfs-establishment-births
python replication/run_all.py      # about 5 minutes; regenerates every table and figure
python replication/verify_outputs.py   # checks the regenerated outputs match the committed ones
```

On Windows, clone to a short path (for example `C:\src\...`). Long paths can exceed Windows' 260-character limit inside `.git` and `.venv`.

`run_all.py` starts from the committed processed data, so it reproduces the committed numbers exactly. `run_all.py --full` re-downloads the raw data first; because Census and BLS revise their data, that can give slightly different numbers. See [data/MANIFEST.md](data/MANIFEST.md) for sources, retrieval dates, and checksums.

## AI-use log

See [research_log.md](research_log.md) in this folder.
