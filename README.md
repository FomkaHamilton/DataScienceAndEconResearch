# Data Science & Econometrics Research

Independent research program spanning two parallel tracks: applied data science (accessible, public-data projects) and applied econometrics (deeper identification, capstone-level work). Goal: a reproducible path from research question to peer-reviewed publication.

Full operating context / collaboration ground rules: [research_partner_context_v2.txt](research_partner_context_v2.txt).

## Current status

See [research_log.md](research_log.md) for the decision log and [roadmap/](roadmap/) for the Phase 1 question-selection roadmap:

- [01_research_roadmap.md](roadmap/01_research_roadmap.md) — shortlist of 8 candidate questions, ranked, with recommendations
- [02_project1_research_plan.md](roadmap/02_project1_research_plan.md) — draft research plan for the approved first project
- [sources_verified_2026-10-14.md](roadmap/sources_verified_2026-10-14.md) — verification log (datasets, literature, journals) with source URLs

**Approved (2026-10-14):**
- **Project 1 (data science track):** Do Census Business Formation Statistics (state-level business applications) improve nowcasts/forecasts of BLS Business Employment Dynamics (state establishment births), and does ML add value over econometric benchmarks? Predictive only — no causal claims.
- **Project 2 (econometrics track):** Household income volatility and material hardship using Census SIPP 2018+ panels (within-household fixed effects). Associational unless a credible quasi-experiment is identified during design.

## Repository structure

Each project lives under `projects/`, following a standard layout so another researcher can clone and reproduce the results:

```
projects/<project-slug>/
    README.md
    research_question.md
    pre_analysis_plan.md
    literature/
    data/raw/  data/processed/  data/MANIFEST.md
    src/acquisition/  src/cleaning/  src/analysis/  src/visualization/
    notebooks/
    outputs/tables/  outputs/figures/
    manuscript/
    references/references.bib
    replication/
    research_log.md
```

Raw/processed data files are not committed by default (see `.gitignore`); each project's `data/MANIFEST.md` documents source URLs, retrieval dates, and parameters so the acquisition is reproducible without redistributing restricted data.

## Setup

```
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## AI assistance disclosure

This project uses AI (Claude / Claude Code) as a research tool for literature discovery, code generation, analysis support, and drafting. The author reviews and approves substantive research decisions, verifies citations and code, and retains full responsibility for the final work. See `research_log.md` in this repo and in each project for a running AI-use record. Disclosure in any manuscript follows the target journal's specific policy.
