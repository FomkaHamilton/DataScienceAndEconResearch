"""
Pre-registered live forecasts from Census's projected business formations
(pre_analysis_plan_addendum_5.md, item F).

Forecasts state establishment births (year-over-year log change, not
seasonally adjusted) for 2026Q2 and 2026Q3 -- quarters BLS had not yet
published when these forecasts were made -- from the committed processed
data used for the Addendum 3 forecasts (BFS through September 2026 and BED
through 2025Q4, both retrieved 14 October 2026), with the same procedure:

  benchmark         births lags 3-5, state and quarter-of-year dummies
  PBF_h0, PBF_h3    benchmark + projected business formations within four
                    quarters (BF_PBF4Q), year-over-year log change at lead
                    0 or 3

Each model is trained twice, on all rows ("full") and without target
quarters in 2020-2022, as in Addendum 3. The run must reproduce the frozen
Addendum 3 benchmark forecasts exactly.

Once committed, the forecast file is FROZEN. Re-running this script
recomputes the forecasts and stops with an error if they differ from the
committed file; it never overwrites it.

Usage:
    python make_live_forecasts_pbf.py
"""

import hashlib

import numpy as np
import pandas as pd

from make_live_forecasts import EXCLUDED_YEARS, OUT_DIR, consistency_check, feature_panel
from make_live_forecasts import OUT_FILE as A3_FILE
from run_addendum5 import quarterly_yoy_lags
from run_phase5_evaluation import (
    BENCHMARK_COLS,
    KEYS,
    PROCESSED_DIR,
    TARGET,
    expanding_window_predict,
    fit_predict_ols,
)

NSA = "Not seasonally adjusted"
TARGET_QUARTERS = [(2026, 2), (2026, 3)]
LEADS = [0, 3]

OUT_FILE = OUT_DIR / "live_forecasts_pbf_2026Q2-Q3.csv"


def in_target_quarters(df: pd.DataFrame) -> pd.Series:
    return df[["year", "quarter"]].apply(tuple, axis=1).isin(TARGET_QUARTERS)


def benchmark_check(out: pd.DataFrame) -> None:
    """The benchmark forecasts must equal the frozen Addendum 3 forecasts."""
    a3 = pd.read_csv(A3_FILE)
    a3 = a3[a3["model"] == "benchmark"]
    ours = out[out["model"] == "benchmark"]
    m = ours.merge(a3, on=KEYS + ["training"], suffixes=("", "_a3"))
    if len(m) != len(ours):
        raise RuntimeError(f"Only {len(m)} of {len(ours)} benchmark forecasts found in {A3_FILE.name}")
    worst = float(np.max(np.abs(m["forecast_births_yoy"] - m["forecast_births_yoy_a3"])))
    if worst > 1e-12 or not (m["train_n"] == m["train_n_a3"]).all():
        raise RuntimeError(f"Benchmark forecasts differ from {A3_FILE.name} (max abs difference {worst})")
    print(f"  benchmark check passed: {len(m)} benchmark forecasts equal the frozen Addendum 3 "
          f"file (max abs difference {worst:.1e})", flush=True)


def make_forecasts() -> pd.DataFrame:
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    fc = fc[fc["seasonal_adj"] == NSA].copy()
    states = sorted(fc["geo"].unique())

    panel = feature_panel()
    consistency_check(panel, fc)

    future = panel[in_target_quarters(panel)].copy()
    if future[TARGET].notna().any():
        raise RuntimeError("A target quarter already has published births -- not a live forecast")
    future["in_test_window"] = True

    bfs = pd.read_csv(PROCESSED_DIR / "bfs_state_applications.csv")
    pbf = bfs[(bfs["series"] == "BF_PBF4Q") & (bfs["seasonal_adj"] == NSA) & bfs["geo"].isin(states)]
    pbf_cols = [f"PBF_yoy_lag{h}" for h in LEADS]
    lags = quarterly_yoy_lags(pbf, "PBF")[KEYS + pbf_cols]

    cols = ["geo", "state_name", "year", "quarter", "quarter_target", "in_test_window", TARGET] + BENCHMARK_COLS
    base = pd.concat([fc[cols], future[cols]], ignore_index=True).merge(lags, on=KEYS, how="left")
    target_rows = base[in_target_quarters(base)]
    if len(target_rows) != len(states) * len(TARGET_QUARTERS) or target_rows[BENCHMARK_COLS + pbf_cols].isna().any().any():
        raise RuntimeError("Missing features for a target quarter")
    eval_q = [int(y * 4 + q) for y, q in TARGET_QUARTERS]

    excl = base.copy()
    excl.loc[excl["year"].between(*EXCLUDED_YEARS), TARGET] = np.nan  # drop from training only
    variants = {"full": base, f"excl_{EXCLUDED_YEARS[0]}_{EXCLUDED_YEARS[1]}": excl}

    specs = [("benchmark", None, None, BENCHMARK_COLS)] + [
        (f"PBF_h{h}", "BF_PBF4Q", h, BENCHMARK_COLS + [f"PBF_yoy_lag{h}"]) for h in LEADS
    ]

    rows = []
    for training, df in variants.items():
        for model, series, lead, feature_cols in specs:
            p = expanding_window_predict(df, feature_cols, TARGET, states, fit_predict_ols, eval_quarters=eval_q)
            p = p[["geo", "state_name", "year", "quarter", "prediction", "train_n"]].assign(
                model=model, series=series or "none", lead=-1 if lead is None else lead, training=training
            )
            rows.append(p)
    out = pd.concat(rows, ignore_index=True).rename(columns={"prediction": "forecast_births_yoy"})

    # Same-quarter births a year earlier, for reference, as in Addendum 3.
    births = panel[["geo", "year", "quarter", "births"]].copy()
    births["year"] = births["year"] + 1
    out = out.merge(births.rename(columns={"births": "births_same_quarter_prior_year"}), on=KEYS, how="left")
    out["implied_births_level"] = out["births_same_quarter_prior_year"] * np.exp(out["forecast_births_yoy"])
    order = ["year", "quarter", "geo", "state_name", "training", "model", "series", "lead",
             "train_n", "forecast_births_yoy", "births_same_quarter_prior_year", "implied_births_level"]
    out = out[order].sort_values(["year", "quarter", "training", "model", "geo"]).reset_index(drop=True)
    benchmark_check(out)
    return out


def main() -> None:
    forecasts = make_forecasts()
    if OUT_FILE.exists():
        committed = pd.read_csv(OUT_FILE)
        same = (list(committed.columns) == list(forecasts.columns) and committed.shape == forecasts.shape
                and np.allclose(committed.select_dtypes("number").to_numpy(float),
                                forecasts.select_dtypes("number").to_numpy(float),
                                rtol=1e-9, atol=1e-12, equal_nan=True))
        if not same:
            raise RuntimeError(f"Recomputed forecasts differ from the committed pre-registered file "
                               f"{OUT_FILE}. It has NOT been overwritten.")
        print("  recomputed forecasts match the committed pre-registered file; left untouched")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    forecasts.to_csv(OUT_FILE, index=False)
    digest = hashlib.sha256(OUT_FILE.read_bytes()).hexdigest()
    print(f"  wrote {len(forecasts):,} forecasts to {OUT_FILE}")
    print(f"  SHA-256: {digest}")
    summary = forecasts.groupby(["training", "model", "year", "quarter"])["forecast_births_yoy"].mean().unstack(["year", "quarter"])
    print("\n  Mean forecast YoY log change across states:")
    print((summary * 100).round(1).to_string())


if __name__ == "__main__":
    main()
