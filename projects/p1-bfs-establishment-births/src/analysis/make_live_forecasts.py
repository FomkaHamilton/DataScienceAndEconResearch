"""
Pre-registered live forecasts (pre_analysis_plan_addendum_3.md).

Forecasts state establishment births (year-over-year log change, not
seasonally adjusted) for 2026Q1, 2026Q2 and 2026Q3 -- quarters BLS had not
yet published when these forecasts were made -- using exactly the Phase 5
procedure (same models, same real-time training rule).

Two training variants for every model:
  full            all training rows, as in Phase 5
  excl_2020_2022  training rows with target quarters in 2020-2022 dropped
                  (tests the idea that pandemic-era data distort the weights)

Once committed, the forecast file is FROZEN. Re-running this script
recomputes the forecasts and stops with an error if they differ from the
committed file; it never overwrites it.

Usage:
    python make_live_forecasts.py
"""

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cleaning"))

from build_panel import GEO_TO_NAME, _bed_wide, _bfs_to_quarterly  # noqa: E402
from run_phase5_evaluation import (  # noqa: E402
    BENCHMARK_COLS,
    BFS_LAGS,
    OWN_LAGS,
    PROCESSED_DIR,
    PROJECT_ROOT,
    TARGET,
    expanding_window_predict,
    fit_predict_ols,
    qdate,
)

NSA = "Not seasonally adjusted"
TARGET_QUARTERS = [(2026, 1), (2026, 2), (2026, 3)]
EXCLUDED_YEARS = (2020, 2022)
SERIES = {"BA": "BA_BA", "HBA": "BA_HBA"}
LEADS = {"BA": BFS_LAGS, "HBA": [0, 3]}

OUT_DIR = PROJECT_ROOT / "outputs" / "live_forecasts"
OUT_FILE = OUT_DIR / "live_forecasts_2026Q1-Q3.csv"


def feature_panel() -> pd.DataFrame:
    """Same features as build_forecast_dataset.py, but keeping quarters where
    application data exist and BED births do not yet (left join from BFS)."""
    bfs_q = _bfs_to_quarterly(pd.read_csv(PROCESSED_DIR / "bfs_state_applications.csv"))
    bed_w = _bed_wide(pd.read_csv(
        PROCESSED_DIR / "bed_state_establishment_births_deaths.csv", dtype={"state_code": str}
    ))
    b = bfs_q[(bfs_q["seasonal_adj"] == NSA) & bfs_q["geo"].isin(GEO_TO_NAME)
              & ~bfs_q["geo"].isin(["US", "PR"])].copy()
    b["state_name"] = b["geo"].map(GEO_TO_NAME)
    e = bed_w[bed_w["seasonal_adj"] == NSA][["state_name", "year", "quarter", "births"]]
    df = b.merge(e, on=["state_name", "year", "quarter"], how="left")
    df = df.sort_values(["geo", "year", "quarter"]).reset_index(drop=True)

    g = df.groupby("geo")
    for col in ["births"] + list(SERIES.values()):
        df[f"{col}_yoy"] = np.log(df[col].where(df[col] > 0)).groupby(df["geo"]).diff(4)
    g = df.groupby("geo")
    for lag in OWN_LAGS:
        df[f"births_yoy_lag{lag}"] = g["births_yoy"].shift(lag)
    for col in SERIES.values():
        for lag in BFS_LAGS:
            df[f"{col}_yoy_lag{lag}"] = g[f"{col}_yoy"].shift(lag)
    df["quarter_target"] = df["quarter"]
    return df


def consistency_check(panel: pd.DataFrame, fc: pd.DataFrame) -> None:
    """Rebuilt features must equal forecast_dataset.csv wherever both exist."""
    cols = [TARGET] + BENCHMARK_COLS + [f"{s}_yoy_lag{l}" for s in SERIES.values() for l in BFS_LAGS]
    keys = ["geo", "year", "quarter"]
    m = fc[keys + cols].merge(panel[keys + cols], on=keys, suffixes=("_fc", "_new"))
    worst = 0.0
    for c in cols:
        a, b = m[f"{c}_fc"].to_numpy(float), m[f"{c}_new"].to_numpy(float)
        if not np.allclose(a, b, rtol=0, atol=1e-12, equal_nan=True):
            raise RuntimeError(f"Feature {c} differs from forecast_dataset.csv")
        both = np.isfinite(a) & np.isfinite(b)
        worst = max(worst, float(np.max(np.abs(a[both] - b[both]))) if both.any() else 0.0)
    if len(m) != len(fc):
        raise RuntimeError(f"Only {len(m)} of {len(fc)} forecast_dataset rows matched")
    print(f"  consistency check passed: rebuilt features match forecast_dataset.csv "
          f"on all {len(m):,} rows (max abs difference {worst:.1e})", flush=True)


def make_forecasts() -> pd.DataFrame:
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    fc = fc[fc["seasonal_adj"] == NSA].copy()
    states = sorted(fc["geo"].unique())

    panel = feature_panel()
    consistency_check(panel, fc)

    future = panel[panel[["year", "quarter"]].apply(tuple, axis=1).isin(TARGET_QUARTERS)].copy()
    if future[TARGET].notna().any():
        raise RuntimeError("A target quarter already has published births -- not a live forecast")
    feature_cols = [TARGET] + BENCHMARK_COLS + [f"{s}_yoy_lag{l}" for s in SERIES.values() for l in BFS_LAGS]
    if future[feature_cols[1:]].isna().any().any():
        raise RuntimeError("Missing features for a target quarter")
    future["in_test_window"] = True

    base = pd.concat([fc[["geo", "state_name", "year", "quarter", "quarter_target",
                          "in_test_window"] + feature_cols], future[["geo", "state_name", "year", "quarter",
                          "quarter_target", "in_test_window"] + feature_cols]], ignore_index=True)
    eval_q = [int(y * 4 + q) for y, q in TARGET_QUARTERS]

    variants = {"full": base}
    excl = base.copy()
    excl.loc[excl["year"].between(*EXCLUDED_YEARS), TARGET] = np.nan  # drop from training only
    variants[f"excl_{EXCLUDED_YEARS[0]}_{EXCLUDED_YEARS[1]}"] = excl

    specs = [("benchmark", None, None, BENCHMARK_COLS)] + [
        (f"{label}_h{h}", label, h, BENCHMARK_COLS + [f"{col}_yoy_lag{h}"])
        for label, col in SERIES.items() for h in LEADS[label]
    ]

    rows = []
    for training, df in variants.items():
        for model, series, lead, cols in specs:
            p = expanding_window_predict(df, cols, TARGET, states, fit_predict_ols, eval_quarters=eval_q)
            p = p[["geo", "state_name", "year", "quarter", "prediction", "train_n"]].assign(
                model=model, series=series or "none", lead=-1 if lead is None else lead, training=training
            )
            rows.append(p)
    out = pd.concat(rows, ignore_index=True).rename(columns={"prediction": "forecast_births_yoy"})

    # Same-quarter births a year earlier (current vintage), for reference:
    # implied level forecast = base x exp(forecast). Evaluation uses the
    # year-over-year change computed within the new BLS release itself.
    births = panel[["geo", "year", "quarter", "births"]].copy()
    births["year"] = births["year"] + 1
    out = out.merge(births.rename(columns={"births": "births_same_quarter_prior_year"}),
                    on=["geo", "year", "quarter"], how="left")
    out["implied_births_level"] = out["births_same_quarter_prior_year"] * np.exp(out["forecast_births_yoy"])
    order = ["year", "quarter", "geo", "state_name", "training", "model", "series", "lead",
             "train_n", "forecast_births_yoy", "births_same_quarter_prior_year", "implied_births_level"]
    return out[order].sort_values(["year", "quarter", "training", "model", "geo"]).reset_index(drop=True)


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
        print(f"  recomputed forecasts match the committed pre-registered file; left untouched")
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
