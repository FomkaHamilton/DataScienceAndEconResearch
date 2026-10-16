"""
Seasonal naive benchmark (pre_analysis_plan.md Sec. 5).

The pre-analysis plan lists a seasonal naive forecast alongside the
autoregressive (AR) benchmark. It was omitted from the first
implementation and is added here before submission. The forecast has no
parameters, so adding it involves no specification choice; this
definition was committed before the forecast was evaluated.

Definition. The seasonal naive forecast of a quarter's establishment
births is the count in the same quarter one year earlier. That count is
already published at the real-time forecast origin (BED births appear
with about a three-quarter lag, and the same quarter a year earlier is
four quarters back). Because the target is the year-over-year log
change, the forecast is zero for every state and quarter.

Evaluation. The 2023Q1-2025Q4 test window (612 state-quarters), with the
same target and inference as the accuracy comparisons in Table 1: the
plain squared-error difference against the AR benchmark (benchmark loss
minus naive loss, so positive values favor the naive forecast), tested
two-sided, with naive, state-clustered, quarter-clustered and two-way
clustered standard errors and the wild cluster bootstrap by quarter.
The Clark-West statistic does not apply, because the naive forecast is
not a larger model that nests the benchmark.

Outputs:
  outputs/tables/seasonal_naive_comparison.csv   (naive vs. AR benchmark)
  outputs/tables/seasonal_naive_performance.csv  (RMSE and MAE of both)

Usage:
    python run_seasonal_naive.py
"""

import pandas as pd

from run_phase5_evaluation import KEYS, TABLE_DIR, TARGET, compare_to_benchmark, performance_table


def main() -> None:
    preds = pd.read_csv(TABLE_DIR / "phase5_predictions.csv")
    df = preds[KEYS + [TARGET, "pred_benchmark"]].copy()
    assert len(df) == 612 and df[[TARGET, "pred_benchmark"]].notna().all().all()
    df["pred_seasonal_naive"] = 0.0

    perf = performance_table(df)
    perf.to_csv(TABLE_DIR / "seasonal_naive_performance.csv", index=False)
    comp = pd.DataFrame([compare_to_benchmark(df, TARGET, "seasonal_naive", "mse")])
    comp.to_csv(TABLE_DIR / "seasonal_naive_comparison.csv", index=False)

    print(perf.to_string(index=False))
    cols = ["comparison", "mean_diff_pct_of_benchmark_mse", "ci95_low_pct", "ci95_high_pct",
            "naive_p", "two_way_p", "wcb_quarter_p", "wcb_ci95_low_pct", "wcb_ci95_high_pct"]
    print(comp[cols].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
