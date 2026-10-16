# Research Question 4 (RQ4, Exploratory): Forecasting Gains and the New-Firm Share of Entry

*2026-10-15. Run as specified in [pre_analysis_plan_addendum_4.md](../pre_analysis_plan_addendum_4.md), which was committed (4fd546f) before the analysis was run. Exploratory: reported in an appendix whatever the result. Not yet reviewed by the author.*

## Question

Across states, did business applications improve forecasts of establishment births more where a larger share of new establishments came from brand-new firms, as opposed to existing firms opening another location?

## Result

| Test | Spearman ρ | p | Holm p | OLS: extra gain per 10 points of new-firm share | Reading |
|---|---|---|---|---|---|
| **Primary:** all applications, same-quarter lead, 2010–19 | **0.37** | 0.007 | **0.014** | +10.5 points (p = 0.02) | Consistent with the new-firm mechanism |
| **Primary:** all applications, 3-quarter lead, 2010–19 | 0.11 | 0.44 | 0.44 | +2.7 (p = 0.16) | Inconclusive |
| Secondary: high-propensity, same-quarter lead, 2010–19 | 0.32 | 0.021 | — | +10.2 (p = 0.04) | — |
| Secondary: high-propensity, 3-quarter lead, 2010–19 | 0.22 | 0.12 | — | +6.5 (p = 0.07) | — |
| Secondary: all applications, same-quarter lead, 2022–25 | 0.09 | 0.53 | — | +2.7 (p = 0.60) | — |
| Secondary: all applications, 3-quarter lead, 2022–25 | −0.02 | 0.89 | — | +1.4 (p = 0.88) | — |

The OLS column is the ordinary least squares slope of the accuracy gain on the new-firm share. Its "points" are percentage points of accuracy gain (as % of the benchmark's mean squared error, MSE) per 10 percentage points of new-firm share.

- **Same-quarter lead, before 2020:** states where brand-new firms made up more of the openings saw larger gains from adding applications.
- **[Scatter](../outputs/figures/rq4_gain_vs_new_firm_share.png):** a moderate tendency in a noisy cloud, not a tight relationship. It is not driven by a single state; the two states with the largest losses sit mid-range and work against the correlation.
- **3-quarter lead:** weak relationship.
- **After 2020:** no relationship. That is expected, because the gains themselves disappeared.

Data: [rq4_correlations.csv](../outputs/tables/rq4_correlations.csv), [rq4_state_data.csv](../outputs/tables/rq4_state_data.csv).

## How it fits the paper

This is the one test aimed directly at the mechanism. It supports the reading that the pre-2020 relationship was real and ran through new-firm formation:

- **Where it shows up:** at the same-quarter lead, which is also where the narrower application series had their most durable pre-2020 advantage (RQ2: it survived Census's 2012 redefinition of high-propensity applications).
- **Where it fails:** it disappears after 2020, along with the gains themselves.

## Correction made before running

The new-firm share (`src/cleaning/clean_bds.py`, built in Phase 2 and unused until RQ4) had excluded from its denominator the establishments opened by firms that Census cannot date because they predate the Business Dynamics Statistics (BDS) series ("left-censored" firms). Those are old firms opening new locations, so they belong in it.

| | Before the fix | After the fix |
|---|---|---|
| 2010–19 mean new-firm share | 69% | 61% |
| Implied share of new establishments from existing firms | — | about 39% |

The corrected figure is close to Decker & Haltiwanger's figure of about 36% (FEDS Note, 2022), which resolves the mismatch noted in the original Phase 3 write-up. The fix was made before RQ4 was run and matches the definition written into Addendum 4. RQ4 was not run on the old definition.

## Caveats

- **Exploratory and cross-sectional:** 51 states.
- **Not causal:** the new-firm share is not randomly assigned, so states with high shares may differ in other ways.
- **Different data sources:** the new-firm share comes from Census BDS (annual, March to March), while births come from BLS Business Employment Dynamics (BED), and the two sources' establishment counts have been diverging (Cao et al., CES-WP-26-36).
- **Only one of the two primary tests is significant.**
