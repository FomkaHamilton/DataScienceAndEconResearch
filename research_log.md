# Research Log

Program-level log of decisions, dead ends and AI assistance. Each project will also keep its own log.

---

## 2026-10-14: Phase 1 roadmap (question selection)

**Done**
- Drafted 8 candidate questions across the data-science (DS) and econometrics (EM) tracks.
- Checked each one against current sources:
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
| Inflation inequality | BLS now publishes official CPI research indexes by income quintile (R-CPI-I), and several 2025–26 papers cover the period. | Saturated |
| Public customer-churn data | No usable public data found. | Retention interest redirected to public analogues |
| CE 2025 data | The 2025 shutdown left a collection gap, and BLS will not adjust the PUMD weights. | Any CE work stops at 2024 |

**AI-use record**
- Tool: Claude (Anthropic) via Claude Code, model Claude Opus 5.5.
- What it did:
  - drafted the candidate questions;
  - ran web searches to verify literature, datasets and journal policies, using four parallel research agents;
  - wrote the scoring and recommendations;
  - drafted the research plan.
- Human verification status: **not yet reviewed by the author.** Citations and policies must be spot-checked before use.

---

## 2026-10-14: Project approvals and repo setup

**Project 1 (data science track): approved.** Census BFS → BLS BED state establishment-birth nowcasting, per [roadmap/02_project1_research_plan.md](roadmap/02_project1_research_plan.md).

**Project 2 (econometrics track): Candidate 3 (SIPP income volatility & hardship), by my recommendation.**

The author's instinct was Candidate 4 (minimum wage & business dynamism), since it shares data infrastructure with Project 1 and would build a coherent "business dynamics" identity. The author asked for my judgment on which better serves getting published, given that tradeoff. My call is Candidate 3, for three reasons:

1. **Candidate 4 sits in an actively contested frontier debate.** Dube, Reich et al. vs. Jha, Neumark & Rodriguez-Lopez have been litigating border-pair vs. commuting-zone identification in NBER working papers through 2024–2026. Any referee at a serious outlet will hold a new entrant to that frontier's standard. That is a hard place for a first-time independent author to clear, regardless of skill.
2. **Kuroki (2025)** already published a close county-level entry/exit study for approximately the same period (2010–2023). Candidate 3's gap — no within-household volatility→hardship study on the SIPP 2018+ redesign — is more clearly open.
3. **Candidate 3 can be published as honest, careful associational work** without needing to win a contested identification argument. The realistic venues identified (*Journal of Family and Economic Issues*, *Contemporary Economic Policy*, *Review of Income and Wealth*, *Empirical Economics*) are a good fit for that kind of paper. Candidate 3 still delivers real econometric depth: survey weighting, multiple-imputation combining rules, seam-bias handling, fixed effects, event studies.

This is a judgment call, not a certainty — if the Phase 1 literature review on Candidate 3 turns up a closer prior paper, or if a credible instrument for income volatility doesn't materialize, Candidate 4 remains the fallback, and the shared-infrastructure argument for it stands.

**Repository:** moved out of OneDrive (sync conflicts) to a local, non-synced path, pushed to a private GitHub repo. See commit history for setup.
