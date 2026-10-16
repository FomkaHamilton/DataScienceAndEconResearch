"""
Pre-analysis plan Addendum 1 (pre_analysis_plan_addendum_1.md):
  A. the two robustness checks committed in the original plan
     (seasonally adjusted series; winsorized series)
  B. forecast performance over time, target quarters 2010Q1-2025Q4
  C. what size of effect the locked test window could have detected

Run run_phase5_evaluation.py first: this script reads its outputs
(phase5_predictions.csv, phase5_ml_tuning.csv, phase5_comparisons.csv).

Usage:
    python run_phase5_extensions.py
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from run_phase5_evaluation import (
    BENCHMARK_COLS,
    BFS_LAGS,
    ECON_MODELS,
    KEYS,
    LABEL_LAG_MIN,
    PROCESSED_DIR,
    PROJECT_ROOT,
    TABLE_DIR,
    TARGET,
    build_design,
    comparison_table,
    load_tuning,
    loss_difference,
    performance_table,
    qdate,
    run_models,
    tuning_table,
)

FIG_DIR = PROJECT_ROOT / "outputs" / "figures"

# Fixed in pre_analysis_plan.md Sec. 4 from the development window only.
WINSOR = {"births": (-0.4739, 0.5795), "BA_BA": (-0.2389, 0.5491)}

# Fixed in Addendum 1, Analysis B.
EVAL_START_YEAR = 2010
PERIODS = [
    ("pre_pandemic", 2010, 2019),
    ("pandemic", 2020, 2021),
    ("post_pandemic", 2022, 2025),
    ("locked_test", 2023, 2025),
]

# Chart colors, shared with exploratory_analysis.py.
SURFACE, INK, INK_2, GRID, SERIES = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#2a78d6"
SHADE = "#efeee9"


def _quarter_start(year: pd.Series, quarter: pd.Series) -> pd.Series:
    return pd.to_datetime(year.astype(str) + "-" + ((quarter - 1) * 3 + 1).astype(str) + "-01")


def _summary(comp: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    keep = ["comparison", "statistic", "mean_diff_pct_of_benchmark_mse", "naive_p", "two_way_p", "wcb_quarter_p"]
    return comp[comp["comparison"].isin(models)][keep].round(4)


# ---- Analysis C: detectable effects ----

def analysis_c() -> pd.DataFrame:
    """Detectable effects for the locked test window, from the primary
    comparisons table. Accuracy difference only (the economically
    interpretable quantity), as % of the benchmark's MSE; positive = the
    model is more accurate than the benchmark."""
    comp = pd.read_csv(TABLE_DIR / "phase5_comparisons.csv")
    mse = comp[comp["statistic"] == "mse"].copy()
    mse["wcb_to_two_way_width_ratio"] = (
        (mse["wcb_ci95_high_pct"] - mse["wcb_ci95_low_pct"])
        / (mse["ci95_high_pct"] - mse["ci95_low_pct"])
    )
    cols = [
        "comparison", "mean_diff_pct_of_benchmark_mse", "ci95_low_pct", "ci95_high_pct",
        "mde80_pct", "two_way_p", "wcb_quarter_p", "wcb_ci95_low_pct", "wcb_ci95_high_pct",
        "wcb_to_two_way_width_ratio",
    ]
    out = mse[cols]
    out.to_csv(TABLE_DIR / "phase5x_detectable_effects.csv", index=False)
    print("\n[C] Detectable effects, locked test window (% of benchmark MSE; + = model better):")
    print(out.round(2).to_string(index=False), flush=True)
    return out


# ---- Analysis B: forecast performance over time ----

def coefficient_path(
    nsa: pd.DataFrame, states: list[str], eval_q: list[int], h: int = 3, series: str = "BA_BA"
) -> pd.DataFrame:
    """Coefficient on an application series from each expanding-window
    refit (descriptive only), with standard errors clustered by state."""
    df = nsa.copy()
    df["qd"] = qdate(df["year"], df["quarter"])
    cols = BENCHMARK_COLS + [f"{series}_yoy_lag{h}"]
    rows = []
    for t in eval_q:
        train = df[df["qd"] <= t - LABEL_LAG_MIN].dropna(subset=cols + [TARGET])
        X = sm.add_constant(build_design(train, cols, states), has_constant="add")
        fit = sm.OLS(train[TARGET].to_numpy(), X).fit(
            cov_type="cluster", cov_kwds={"groups": train["geo"].to_numpy()}
        )
        year = (t - 1) // 4
        rows.append({
            "year": year, "quarter": t - 4 * year, "train_n": len(train),
            "coef": fit.params[cols[-1]], "se_state_cluster": fit.bse[cols[-1]],
        })
    return pd.DataFrame(rows)


def _style(ax):
    ax.set_facecolor(SURFACE)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.axhline(0, color=INK_2, linewidth=0.8, zorder=1)


def _shade_periods(ax, labels: bool = True):
    for label, start, end in [
        ("Pandemic\n2020–21", "2020-01-01", "2022-01-01"),
        ("Locked test\nwindow 2023–25", "2023-01-01", "2026-01-01"),
    ]:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=SHADE, linewidth=0, zorder=0)
        if labels:
            ax.text(pd.Timestamp(start) + pd.Timedelta(days=30), 0.98, label,
                    transform=ax.get_xaxis_transform(), va="top", ha="left", fontsize=8, color=INK_2)


def _figures(gains: pd.DataFrame, coefs: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=SURFACE)
    _style(ax)
    _shade_periods(ax)
    ax.plot(gains["date"], gains["cumulative_gain_h3"], color=SERIES, linewidth=2, zorder=3)
    ax.set_title(
        "Cumulative accuracy gain from adding business applications (3-quarter lead)",
        loc="left", fontsize=11, color=INK,
    )
    ax.set_ylabel("Cumulative reduction in squared error\n(averaged across states)", fontsize=9, color=INK_2)
    fig.text(0.01, 0.01,
             "Rising line = the model with applications beat the benchmark that quarter; falling = it did worse. "
             "2010–2022 is pseudo-out-of-sample.",
             fontsize=8, color=INK_2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG_DIR / "phase5x_cumulative_gain_h3.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=SURFACE)
    _style(ax)
    _shade_periods(ax)
    lo = coefs["coef"] - 1.96 * coefs["se_state_cluster"]
    hi = coefs["coef"] + 1.96 * coefs["se_state_cluster"]
    ax.fill_between(coefs["date"], lo, hi, color=SERIES, alpha=0.15, linewidth=0, zorder=2)
    ax.plot(coefs["date"], coefs["coef"], color=SERIES, linewidth=2, zorder=3)
    ax.set_title(
        "Estimated weight on business applications (3-quarter lead), by forecast quarter",
        loc="left", fontsize=11, color=INK,
    )
    ax.set_ylabel("Coefficient (95% band, clustered by state)", fontsize=9, color=INK_2)
    fig.text(0.01, 0.01,
             "Each point is the model refit using only data available for that forecast quarter.",
             fontsize=8, color=INK_2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG_DIR / "phase5x_bfs_coefficient_path_h3.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)


def analysis_b(fc: pd.DataFrame, states: list[str]) -> pd.DataFrame:
    nsa = fc[fc["seasonal_adj"] == "Not seasonally adjusted"].copy()
    qd = qdate(nsa["year"], nsa["quarter"])
    eval_q = sorted(qd[nsa["year"] >= EVAL_START_YEAR].unique())
    print(f"\n[B] Forecasting {len(eval_q)} target quarters, {EVAL_START_YEAR}Q1 onward "
          "(regression models only)", flush=True)
    merged, _ = run_models(nsa, states, eval_quarters=eval_q, include_ml=False)

    # Consistency check required by the addendum: the test-window forecasts
    # must equal the primary run's exactly.
    primary = pd.read_csv(TABLE_DIR / "phase5_predictions.csv")
    cols = ["pred_benchmark"] + [f"pred_{m}" for m in ECON_MODELS]
    chk = primary[KEYS + cols].merge(merged[KEYS + cols], on=KEYS, suffixes=("_primary", "_overtime"))
    max_diff = max(float(np.max(np.abs(chk[f"{c}_primary"] - chk[f"{c}_overtime"]))) for c in cols)
    if len(chk) != len(primary) or max_diff > 1e-9:
        raise RuntimeError(f"Consistency check FAILED: {len(chk)} of {len(primary)} rows, max diff {max_diff}")
    print(f"  consistency check passed: all {len(chk)} test-window forecasts match the primary run "
          f"(max abs difference {max_diff:.1e})", flush=True)
    merged.to_csv(TABLE_DIR / "phase5x_overtime_predictions.csv", index=False)

    # Per-period inference.
    tables = []
    for name, y0, y1 in PERIODS:
        sub = merged[(merged["year"] >= y0) & (merged["year"] <= y1)]
        t = comparison_table(sub, models=ECON_MODELS).assign(period=name)
        for m in ECON_MODELS:
            d = loss_difference(sub, TARGET, f"pred_{m}", "mse")
            t.loc[t["comparison"] == m, "share_states_model_better"] = float(
                (d.groupby(sub["geo"]).mean() > 0).mean()
            )
        tables.append(t)
    by_period = pd.concat(tables, ignore_index=True)
    by_period.to_csv(TABLE_DIR / "phase5x_by_period.csv", index=False)

    keep = ["period", "comparison", "statistic", "n_quarters", "mean_diff_pct_of_benchmark_mse",
            "naive_p", "two_way_p", "wcb_quarter_p", "share_states_model_better"]
    print("\n[B] By period (+ = model with applications more accurate):")
    print(by_period[keep].round(4).to_string(index=False), flush=True)

    # Quarterly cross-state mean gains (all horizons) for the table and figure.
    g = merged[KEYS].copy()
    for m in ECON_MODELS:
        g[f"gain_{m.removeprefix('econ_')}"] = loss_difference(merged, TARGET, f"pred_{m}", "mse")
    gains = g.drop(columns="geo").groupby(["year", "quarter"]).mean().reset_index()
    gains["date"] = _quarter_start(gains["year"], gains["quarter"])
    gains["cumulative_gain_h3"] = gains["gain_h3"].cumsum()
    gains.to_csv(TABLE_DIR / "phase5x_quarterly_gains.csv", index=False)

    coefs = coefficient_path(nsa, states, eval_q, h=3)
    coefs["date"] = _quarter_start(coefs["year"], coefs["quarter"])
    coefs.to_csv(TABLE_DIR / "phase5x_bfs_coefficient_path_h3.csv", index=False)

    _figures(gains, coefs)
    return by_period


# ---- Analysis A: robustness checks ----

def analysis_a(fc: pd.DataFrame, states: list[str]) -> pd.DataFrame:
    nsa = fc[fc["seasonal_adj"] == "Not seasonally adjusted"].copy()
    sa = fc[fc["seasonal_adj"] == "Seasonally adjusted"].copy()

    print("\n[A1] Seasonally adjusted series (no quarter indicator; ML re-tuned on SA data)", flush=True)
    merged_sa, tuning_sa = run_models(sa, states, include_quarter=False)
    merged_sa.to_csv(TABLE_DIR / "phase5x_sa_predictions.csv", index=False)
    tuning_table(tuning_sa).to_csv(TABLE_DIR / "phase5x_sa_ml_tuning.csv", index=False)

    print("\n[A2] Winsorized features and training target (ML settings reused from primary run)", flush=True)
    w = nsa.copy()
    w["births_yoy_raw"] = w[TARGET]
    lo, hi = WINSOR["births"]
    for c in [TARGET] + BENCHMARK_COLS:
        w[c] = w[c].clip(lo, hi)
    lo, hi = WINSOR["BA_BA"]
    for lag in BFS_LAGS:
        w[f"BA_BA_yoy_lag{lag}"] = w[f"BA_BA_yoy_lag{lag}"].clip(lo, hi)
    merged_w, _ = run_models(w, states, ml_tuning=load_tuning(TABLE_DIR / "phase5_ml_tuning.csv"))
    merged_w = merged_w.merge(w[KEYS + ["births_yoy_raw"]], on=KEYS, how="left")
    merged_w.to_csv(TABLE_DIR / "phase5x_winsorized_predictions.csv", index=False)

    comps = {
        "primary": pd.read_csv(TABLE_DIR / "phase5_comparisons.csv"),
        "seasonally_adjusted": comparison_table(merged_sa),
        "winsorized_vs_winsorized_actuals": comparison_table(merged_w),
        "winsorized_vs_raw_actuals": comparison_table(merged_w, target_col="births_yoy_raw"),
    }
    comp = pd.concat([c.assign(variant=k) for k, c in comps.items()], ignore_index=True)
    comp.to_csv(TABLE_DIR / "phase5x_robustness_comparisons.csv", index=False)

    perfs = {
        "primary": pd.read_csv(TABLE_DIR / "phase5_model_performance.csv"),
        "seasonally_adjusted": performance_table(merged_sa),
        "winsorized_vs_winsorized_actuals": performance_table(merged_w),
        "winsorized_vs_raw_actuals": performance_table(merged_w, target_col="births_yoy_raw"),
    }
    perf = pd.concat([p.assign(variant=k) for k, p in perfs.items()], ignore_index=True)
    perf.to_csv(TABLE_DIR / "phase5x_robustness_performance.csv", index=False)

    print("\n[A] Primary comparisons under each variant:")
    for k, c in comps.items():
        print(f"\n  {k}")
        print(_summary(c, ["econ_h0", "econ_h3", "best_ml", "combo"]).to_string(index=False), flush=True)
    return comp


def main() -> None:
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    states = sorted(fc["geo"].unique())
    analysis_c()
    analysis_b(fc, states)
    analysis_a(fc, states)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
