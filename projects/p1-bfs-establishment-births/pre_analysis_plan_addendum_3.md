# Pre-Analysis Plan — Addendum 3: Pre-Registered Live Forecasts

**Committed: 2026-10-15, before BLS published any 2026 establishment-birth data.** Approved by the author.

BLS's release calendar (checked 2026-10-14) schedules 2026Q1 for **October 28, 2026**. The forecasts, the code that produced them, and the code that will score them are all committed in this same commit and tagged `prereg-live-forecasts-2026`.

## Why

The paper's central claim was formed after looking at the data. The claim is that the link between business applications and establishment births has been absent since 2020. The 2023–25 test window is short.

Quarters nobody has seen are the only clean test of a claim like that. Each 2026 quarter BLS publishes becomes one.

## What was forecast

| Item | Detail |
|---|---|
| Outcome | Year-over-year log change in establishment births, not seasonally adjusted |
| Coverage | 51 states (50 + DC) × target quarters 2026Q1, 2026Q2, 2026Q3 |
| Procedure | Exactly the Phase 5 procedure: same models, same quarter and state indicators, same real-time training rule (training labels at least 3 quarters older than the target) |
| Code | [src/analysis/make_live_forecasts.py](src/analysis/make_live_forecasts.py) |
| Data | The committed processed files (BFS through September 2026; BED through 2025Q4) |

The rebuilt features match the Phase 5 forecast data exactly (4,386 rows) before any forecast is made.

**Models:**

- The benchmark.
- Benchmark + all applications (BA) at leads 0–4.
- Benchmark + high-propensity applications (HBA) at leads 0 and 3.

**Two training variants per model:**

- **full** — as in Phase 5.
- **excl_2020_2022** — training rows whose target quarter falls in 2020–2022 are dropped. 2022 is included because its year-over-year changes are measured against the 2021 surge, so they carry the surge's mirror image. This is the "pandemic-distorted weights" idea from Addendum 1. That addendum ruled out testing it on the locked window; new quarters are the honest place to test it.

**Output:** [outputs/live_forecasts/live_forecasts_2026Q1-Q3.csv](outputs/live_forecasts/live_forecasts_2026Q1-Q3.csv). It has 2,448 forecasts.

**SHA-256:** `8e0751c9e1182437630e60a225a240fa866dd8f7a7b1c8f7027251ec98a841fc`

**The file is frozen.** Re-running the script recomputes the forecasts and stops with an error if anything differs; it never overwrites the file.

## How the forecasts will be scored

**Code:** [src/analysis/evaluate_live_forecasts.py](src/analysis/evaluate_live_forecasts.py), committed now and tested on synthetic data only.

**Actual values** are computed *within each new BLS release*. Each is the 2026 quarter's log births minus the same 2025 quarter's log births, using that release's revised 2025 figures. The forecasts used the 2025 data available today, before BLS's annual revision. That is what a real forecaster would face, so this test is genuinely real-time, unlike the paper's main results.

**Accuracy difference** is the reduction in mean squared error relative to the reference model, as a percentage of the reference model's MSE. It is reported for each published quarter and pooled across all published quarters, together with the share of states where the model was more accurate.

## Hypotheses and pre-registered readings

The readings apply to the "all published" pool at each update. They are descriptive labels, not significance tests.

**H1 — the paper's claim: business applications still do not improve forecasts.**

Comparison: BA at leads 3 and 0, full training, against the full-training benchmark.

| Result | Reading |
|---|---|
| Accuracy difference ≤ 0 | Consistent with the paper |
| Accuracy difference > 0 and the BA model is better in more than half of states | Against the paper — the relationship may be recovering |
| Otherwise | Mixed |

**H2 — training without 2020–22 improves the applications model.**

Comparison: BA at leads 3 and 0, excl_2020_2022 training, against the same model with full training.

| Result | Reading |
|---|---|
| Accuracy difference > 0 and better in more than half of states | Supports H2 |
| Accuracy difference ≤ 0 and better in half of states or fewer | Against H2 |
| Otherwise | Mixed |

**Secondary, reported but not read:**

- the other leads;
- HBA;
- the excluded-training models against the benchmark;
- the excluded-training benchmark against the full one.

**Note on H2:** RQ2 found that HBA's estimated weight barely changed after 2020, yet its forecasts still degraded. That suggests H2 may fail. It is registered anyway, because the over-weighting idea was never tested directly.

## Commitments

- **Every published 2026 quarter is scored and reported**, whatever the result.
  - 2026Q1: October 28, 2026.
  - 2026Q2 and 2026Q3: expected roughly late January and late April 2027, following BLS's usual ~7-month lag. These dates are not yet confirmed.
- **The forecast file and the readings above will not be changed.** If the scoring code turns out to have a bug, the fix and its effect will be disclosed alongside the original output.
- **No model will be added after any 2026 data are seen and then presented as pre-registered.**

## Limitations, stated in advance

- **Small numbers.** One to three quarters is very little data. Every state is hit by the same national conditions each quarter, so 51 states in one quarter are not 51 independent tests. These results cannot be statistically decisive, and will not be presented as if they were.
- **Mixed vintages.** Forecasts were built on the pre-revision vintage and are scored against post-revision data. That is intentional (real-time), but it differs from the paper's final-vintage design.
- **Credibility to outside readers depends on public timestamping.** This repository is private, so its commit timestamp does not show outsiders when the forecasts were made. Public timestamping is pending the author's decision; options are noted in the research log.
