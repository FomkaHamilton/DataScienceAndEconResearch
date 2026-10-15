"""
Build the forecast task table for Phase 5, implementing the real-time
information-set convention from pre_analysis_plan.md Sec. 3 and the
horizon structure from Sec. 6.

REAL-TIME CONVENTION (an implementation detail not pinned to the exact
day in the PAP -- stated here explicitly, as the PAP's own Sec. 8 says
any necessary deviation/elaboration must be disclosed, not silent):
  - BED establishment births publish with an effective ~3-quarter lag.
    At a real-time origin anchored to target quarter Q, the most recent
    OWN-HISTORY lag of births actually available is Q-3. Benchmark
    (no-BFS) models therefore use births_yoy lags 3, 4, 5.
  - BFS applications publish with a ~2-week lag -- at quarterly
    granularity this means the full quarter Q's BFS figure is available
    very shortly after Q ends, so it is treated as available at lag 0
    relative to target Q. BFS-augmented models can therefore use BFS
    lags 0 through 4 relative to the target quarter.
  - Under this convention, "ARDL" and "bridge equation" (distinguished
    in the PAP to handle a monthly-vs-quarterly frequency mismatch)
    collapse to the same specification, because BFS's own within-quarter
    monthly detail is not being partially used (the whole quarter is
    just "available" by assumption). This is a disclosed simplification,
    not a silent substitution -- see research_log.md.

HORIZON (h = 0..4): the single BFS lag (relative to the target quarter)
used as the added predictor in each primary nested comparison, matching
the lag structure already used in Phase 3's exploratory correlations.
ML models additionally get a "kitchen sink" feature set with every lag
at once (ML's natural strength), reported as a separate, not primary-per-
horizon comparison.

Seasonality handling (PAP Sec. 4): quarter-of-TARGET dummies included as
features (the primary/structural fix). Winsorized versions and the SA
(seasonally adjusted) series are built as separate, parallel feature
sets for the sensitivity check / robustness line.

Output: data/processed/forecast_dataset.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OWN_LAGS = [3, 4, 5]  # births_yoy lags available in real time (benchmark)
BFS_LAGS = [0, 1, 2, 3, 4]  # BFS lags available in real time (h = 0..4)
BFS_SERIES = ["BA_BA", "BA_HBA", "BA_WBA", "BA_CBA"]

# Winsorization thresholds, fixed from the development window ONLY
# (pre_analysis_plan.md Sec. 4, item 3) -- never recomputed on test data.
WINSOR_BOUNDS = {
    "births_yoy": (-0.4739, 0.5795),
    "BA_BA_yoy": (-0.2389, 0.5491),
}


def _yoy(df: pd.DataFrame, col: str, group_cols: list[str]) -> pd.Series:
    log_col = np.log(df[col].where(df[col] > 0))
    return log_col.groupby([df[g] for g in group_cols]).diff(4)


def _build_for_seasonal_adj(panel: pd.DataFrame, seasonal_adj: str) -> pd.DataFrame:
    df = panel[panel["seasonal_adj"] == seasonal_adj].copy()
    df = df[~df["geo"].isin(["US", "PR"])]  # core state panel only
    df = df.sort_values(["geo", "year", "quarter"]).reset_index(drop=True)

    df["births_yoy"] = _yoy(df, "births", ["geo"])
    for s in BFS_SERIES:
        df[f"{s}_yoy"] = _yoy(df, s, ["geo"])

    # Winsorized versions (dev-window-fixed bounds; applies to both windows
    # identically -- the thresholds themselves are never re-derived from
    # test data, only the function application is).
    for col, (lo, hi) in WINSOR_BOUNDS.items():
        if col in df.columns:
            df[f"{col}_w"] = df[col].clip(lower=lo, upper=hi)

    g = df.groupby("geo")

    for lag in OWN_LAGS:
        df[f"births_yoy_lag{lag}"] = g["births_yoy"].shift(lag)
        df[f"births_yoy_w_lag{lag}"] = g["births_yoy_w"].shift(lag)

    for s in BFS_SERIES:
        for lag in BFS_LAGS:
            df[f"{s}_yoy_lag{lag}"] = g[f"{s}_yoy"].shift(lag)
    # Winsorized BA_BA lag-0 feature, for the sensitivity check (only BA_BA
    # is winsorized per the PAP; other series aren't part of the
    # winsorizing sensitivity check).
    df["BA_BA_yoy_w_lag0"] = g["BA_BA_yoy_w"].shift(0)

    df["quarter_target"] = df["quarter"]  # quarter of the TARGET being forecast
    df["seasonal_adj"] = seasonal_adj
    return df


def build() -> Path:
    panel = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv")

    nsa = _build_for_seasonal_adj(panel, "Not seasonally adjusted")
    sa = _build_for_seasonal_adj(panel, "Seasonally adjusted")

    out = pd.concat([nsa, sa], ignore_index=True)

    keep_cols = (
        ["geo", "state_name", "seasonal_adj", "year", "quarter", "quarter_target",
         "in_test_window", "births_yoy", "births_yoy_w"]
        + [f"births_yoy_lag{l}" for l in OWN_LAGS]
        + [f"births_yoy_w_lag{l}" for l in OWN_LAGS]
        + [f"{s}_yoy_lag{l}" for s in BFS_SERIES for l in BFS_LAGS]
        + ["BA_BA_yoy_w_lag0"]
    )
    out = out[keep_cols].copy()

    out_path = PROCESSED_DIR / "forecast_dataset.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {len(out):,} rows to {out_path}")
    dev = out[~out["in_test_window"]]
    test = out[out["in_test_window"]]
    print(f"Development rows: {len(dev):,}  Test rows: {len(test):,}")
    print(
        f"Test window complete-case rows (births_yoy_lag5 + BA_BA_yoy_lag4 non-null): "
        f"{test.dropna(subset=['births_yoy_lag5', 'BA_BA_yoy_lag4']).shape[0]:,}"
    )
    return out_path


if __name__ == "__main__":
    build()
