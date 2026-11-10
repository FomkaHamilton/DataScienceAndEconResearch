# Data Science and Econometrics Research

An independent research program with two parallel tracks: applied data science (accessible projects built on public data) and applied econometrics (projects with more demanding identification). The goal is a reproducible path from research question to peer-reviewed publication.

The research uses an AI assistant extensively; [AI_USE.md](AI_USE.md) describes how, and the research-integrity rules the work follows.

## Projects and current status

| Project | Track | Status (2026-11-09) |
|---|---|---|
| [Project 1](projects/p1-bfs-establishment-births/README.md): Census business applications (BFS) and BLS state establishment births (BED) | Data science | Main and revision analyses complete; manuscript being revised (draft v2); pre-registered live forecasts being scored (2026Q1 done) |
| Project 2: Household income volatility and material hardship (Census SIPP 2018+ panels) | Econometrics | Approved 2026-10-14; not started |

**Project 1.** Do state-level business applications from the Census Bureau's Business Formation Statistics (BFS) improve out-of-sample forecasts of state establishment births in the BLS Business Employment Dynamics (BED), and do machine-learning methods add value over econometric benchmarks? The question is predictive only; the project makes no causal claims.

- Paper (draft v1): *Business Applications as a Leading Indicator of New Establishments: Evidence from U.S. States That the Relationship Changed After 2020* ([manuscript/draft_v1.md](projects/p1-bfs-establishment-births/manuscript/draft_v1.md)). It is being revised into draft v2, with a new title and framing. Target journal: *Journal of Forecasting*.
- Main finding: no detectable forecasting gain in the locked 2023–2025 test window. Over 2010–2025 the gains are episodic: small but real before 2020, large in 2020–21, negative in 2022 and absent in 2023–25. The information is national rather than state-specific. See the [project README](projects/p1-bfs-establishment-births/README.md) for a fuller summary.
- Forecasts for 2026Q1–Q3 were pre-registered (tag `prereg-live-forecasts-2026`) and are scored as BLS publishes each quarter; 2026Q1 was scored on 2026-11-04. Forecasts for 2026Q2–Q3 from Census's projected business formations were pre-registered on 2026-11-09 (tag `prereg-live-forecasts-pbf-2026q2q3`).

**Project 2.** Using within-household variation (household fixed effects) in the Census Survey of Income and Program Participation (SIPP) 2018+ panels, is month-to-month income volatility associated with material hardship, holding income level fixed? The analysis is associational unless a credible quasi-experiment is identified during the design phase.

## Planning documents

- [research_log.md](research_log.md): program-level decision log and AI-use record. Each project keeps its own log as well.
- [roadmap/01_research_roadmap.md](roadmap/01_research_roadmap.md): the question-selection roadmap (8 candidate questions, ranked, with recommendations).
- [roadmap/02_project1_research_plan.md](roadmap/02_project1_research_plan.md): the original research plan for Project 1, now superseded by the project's [research_question.md](projects/p1-bfs-establishment-births/research_question.md) and pre-analysis plan.
- [roadmap/sources_verified_2026-10-14.md](roadmap/sources_verified_2026-10-14.md): verification log for the datasets, literature and journal facts used in the roadmap, with source URLs.

## Repository structure

Each project lives under `projects/` and follows a common layout, so another researcher can clone the repository and reproduce the results. Folders a project has not yet used may be empty or absent.

```text
projects/<project-slug>/
    README.md
    research_question.md
    pre_analysis_plan.md        (plus any numbered addenda)
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

Raw data files are not committed (see `.gitignore`). Small processed files built from public, unrestricted sources may be committed as listed exceptions. Each project's `data/MANIFEST.md` records source URLs, retrieval dates, parameters and checksums, so the acquisition can be reproduced without redistributing the raw files.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate                     # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt            # pinned direct dependencies (requirements-lock.txt pins everything)
pip install -r requirements-notebooks.txt  # optional: adds Jupyter for exploratory notebooks
pip install -r requirements-manuscript.txt # optional: builds Word versions of manuscripts
```

Each project has a one-command reproduction script; see its README (for example, [Project 1](projects/p1-bfs-establishment-births/README.md#reproduce)).

## License and citation

The code in this repository is released under the [MIT License](LICENSE). The manuscripts, figures and written documentation are copyright (c) 2026 Thomas Hamilton, all rights reserved, so that journal publication options remain open. The processed data are derived from public U.S. government statistics (Census Bureau and Bureau of Labor Statistics). To cite the replication materials, use [CITATION.cff](CITATION.cff); GitHub's "Cite this repository" button reads it.

## AI assistance disclosure

This research program uses AI tools (Anthropic's Claude, via Claude Code) for literature discovery, code generation, analysis and drafting. The author makes the main research decisions and is responsible for the work. See [AI_USE.md](AI_USE.md) for details. The AI-use record is kept in `research_log.md`, both at the repository root and in each project; entries note when work has not yet been reviewed by the author. Disclosure in any manuscript follows the target journal's policy.
