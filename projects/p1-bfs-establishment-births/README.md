# Project 1 — Business Applications and State Establishment Births

**Status: Phases 0–3 complete (setup, literature review, data acquisition, exploratory analysis). All gates passed. Starting Phase 4 (pre-analysis plan).**

Working title: *Do Business Applications Predict Where New Establishments Will Open? State-Level Nowcasts of Establishment Births from the Business Formation Statistics.*

Full design: [research_question.md](research_question.md). Program-level context: [../../roadmap/02_project1_research_plan.md](../../roadmap/02_project1_research_plan.md) and [../../roadmap/sources_verified_2026-10-14.md](../../roadmap/sources_verified_2026-10-14.md).

## Phase gate status

| Phase | Status |
|---|---|
| 0. Setup | Done |
| 1. Literature review | Done — gate passed, see [literature/extraction_table.md](literature/extraction_table.md) |
| 2. Data acquisition | Done (BFS + BED + BDS) — see [data/MANIFEST.md](data/MANIFEST.md). Vintage-data decision for BED still open (deferred to Phase 4). |
| 3. Exploratory analysis | Done — gate passed, see [literature/phase3_findings.md](literature/phase3_findings.md) |
| 4+ | Not started |

## Reproduce (once code exists)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r ../../requirements.txt
```

## AI-use log

See [research_log.md](research_log.md) in this folder.
