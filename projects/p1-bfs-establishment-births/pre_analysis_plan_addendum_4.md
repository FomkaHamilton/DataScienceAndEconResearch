# Pre-Analysis Plan — Addendum 4: RQ4 (New-Firm Share), Exploratory

**Committed: 2026-10-15, before RQ4 was run.** Approved by the author.

The original plan (§7, item 6) lists RQ4 as exploratory. This addendum fixes its details, which the original left open.

## Question

Across states, do business applications predict establishment births better where a larger share of new establishments comes from brand-new firms, rather than from existing firms opening another location?

Applications track new firms. If the relationship works through that channel, states where new firms dominate entry should show larger gains.

## Specification (fixed now)

**Gain.** Each state's accuracy improvement from adding all business applications (BA) to the benchmark, over pre-pandemic forecast quarters 2010–2019. It is expressed as a percentage of that state's benchmark mean squared error, for leads h = 0 and h = 3.

- The forecasts come from the existing over-time run (Addendum 1); no new models are estimated.
- Pre-pandemic only, because that is the period in which the relationship existed.

**New-firm share.** Each state's mean share of new establishments that belong to firms in their first year (Census BDS firm age 0), averaged over BDS years 2010–2019.

**Primary tests.**

- Spearman rank correlation between gain and new-firm share across the 51 states, one test each for h = 0 and h = 3.
- Two-sided p-values, Holm-adjusted across the two tests.
- Expected sign: positive.

**Secondary (descriptive only):**

- the same correlation for high-propensity applications (HBA) at h = 0 and h = 3;
- the same correlation for BA over 2022–2025;
- an OLS slope with heteroskedasticity-robust standard errors as a check on the Spearman result.

## Reading the result

| Result | Reading |
|---|---|
| Positive correlation with Holm-adjusted p < 0.05 | Consistent with the new-firm mechanism |
| Anything else | Inconclusive — *not* evidence against the mechanism |

## Why a null result would be inconclusive (stated in advance)

- **Low power.** With 51 states, the test has roughly 80% power only for correlations of about 0.38 or larger.
- **Different data sources.** The new-firm share comes from Census business data; births come from BLS. Their establishment counts have been drifting apart (Cao, Hyatt, Mukoyama & Sager, CES-WP-26-36).
- **Noisy gains.** Per-state gains are estimated from 40 quarters each.

The result goes in an appendix whatever it shows.
