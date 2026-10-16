# Research Log

Program-level log of decisions, dead ends and AI assistance. Each project also keeps its own log; for Project 1, see [projects/p1-bfs-establishment-births/research_log.md](projects/p1-bfs-establishment-births/research_log.md).

---

## 2026-10-14: Phase 1 roadmap (program-level question selection)

**Done**
- Drafted 8 candidate questions across the data-science (DS) and econometrics (EM) tracks.
- Checked each one against current sources for:
  - literature crowding;
  - whether the public data exist;
  - journal policies.
- Ranked the candidates.
- Drafted a research plan for the recommended first project.
- Files: `roadmap/01_research_roadmap.md`, `roadmap/02_project1_research_plan.md`, `roadmap/sources_verified_2026-10-14.md`.

**Key findings that changed the plan**

| Candidate | What the checks found | Effect |
|---|---|---|
| Gasoline tax-IV elasticity | Bates & Kim (2024, JAE) and Kilian & Zhou (2024, JPubE) already update the estimates. The EIA state volume series ended in 2022 and the all-state price series in 2011. | Downgraded |
| SNAP churn | The SNAP Policy Database ends in Dec 2020; recertification variables are missing from Oct 2019. | Downgraded |
| Inflation inequality | BLS now publishes official research CPI indexes by income quintile (R-CPI-I), and several 2025–26 papers cover the period. | Saturated |
| Public customer-churn data | No usable public data found. | Retention interest redirected to public analogues |
| CE 2025 data | The 2025 shutdown left a collection gap, and BLS will not adjust the PUMD weights. | Any CE work stops at 2024 |

**AI-use record**
- Tool: Claude (Anthropic) via Claude Code, model Claude Opus 5.5.
- What it did:
  - drafted the candidate questions;
  - ran web searches to verify the literature, datasets and journal policies, using four parallel research agents;
  - wrote the scoring and recommendations;
  - drafted the research plan.
- Human verification: not yet reviewed by the author. Citations and policies must be spot-checked before use.

---

## 2026-10-14: Project approvals and repo setup

**Project 1 (data science track): approved.** Nowcasting state establishment births (BLS BED) from Census business applications (BFS), per [roadmap/02_project1_research_plan.md](roadmap/02_project1_research_plan.md).

**Project 2 (econometrics track): approved, Candidate 3 (SIPP income volatility and material hardship), on the AI assistant's recommendation.**

The author's initial preference was Candidate 4 (minimum wage and business dynamism), because it shares data infrastructure with Project 1 and would build a coherent "business dynamics" research identity. The author asked the assistant which option better served the goal of publication, given that tradeoff. The assistant recommended Candidate 3, for three reasons:

1. **Candidate 4 enters an active and contested methodological debate.** Dube, Reich et al. and Jha, Neumark & Rodriguez-Lopez have debated border-pair versus commuting-zone identification in NBER working papers through 2024–2026. Referees at strong outlets will hold a new entrant to the standard of that debate, which is a high bar for a first-time independent author.
2. **Kuroki (2025)** has already published a closely related county-level entry/exit study covering approximately the same period (2010–2023). Candidate 3's gap (no within-household study of volatility and hardship on the redesigned SIPP 2018+ panels) is more clearly open.
3. **Candidate 3 can be published as careful associational work** without having to prevail in a contested identification debate. The realistic venues identified (*Journal of Family and Economic Issues*, *Contemporary Economic Policy*, *Review of Income and Wealth*, *Empirical Economics*) suit that kind of paper. It still offers substantial econometric depth: survey weighting, multiple-imputation combining rules, seam-bias handling, fixed effects and event studies.

This is a judgment call, not a certainty. If the Phase 1 literature review for Candidate 3 finds a closer prior paper, or if no credible instrument for income volatility emerges, Candidate 4 remains the fallback, and the shared-infrastructure argument for it still holds.

**Repository:** moved out of OneDrive (to avoid sync conflicts) to a local, non-synced path and pushed to a private GitHub repository. See the commit history for setup.
