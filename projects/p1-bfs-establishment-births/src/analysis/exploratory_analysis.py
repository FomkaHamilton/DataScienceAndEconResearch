"""
Phase 3 exploratory analysis (development window only).

This script enforces the test-window lock (windows defined in
pre_analysis_plan.md Sec. 1): it loads the integrated panel, immediately
drops every row with in_test_window == True, and never uses them again. No forecast is evaluated here. The
analysis is descriptive and correlational only, and answers the Phase 3
gate question: is a signal from business applications (BFS) to
establishment births (BED) plausibly present at all, before committing
to a full model-comparison design in Phases 4-5?

Outputs:
  outputs/figures/national_bfs_vs_bed_yoy.png
  outputs/figures/state_examples_bfs_vs_bed_yoy.png
  outputs/tables/national_lag_correlations.csv
  outputs/tables/pooled_state_lag_correlations.csv
  outputs/tables/panel_summary_stats.csv

Usage:
    python exploratory_analysis.py
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

MAX_LAG = 4  # quarters

# Chart colors (background, text, gridlines, two series). The two series
# colors were checked together for color-vision-deficiency
# distinguishability and contrast on the light background.
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9"
COLOR_BIRTHS, COLOR_APPS = "#2a78d6", "#eb6834"


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.axhline(0, color=INK_2, linewidth=0.8, zorder=1)


def load_development_panel() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv", parse_dates=["date"])
    n_total = len(df)
    df = df[~df["in_test_window"]].copy()
    print(
        f"Loaded {n_total:,} total rows; dropped {n_total - len(df):,} "
        f"test-window (2023Q1+) rows. Using {len(df):,} development-window rows only."
    )
    print("Test window excluded: no test-window rows are used beyond this filter.")
    return df


def add_yoy_log_changes(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    df = df.sort_values(group_cols + ["year", "quarter"]).copy()
    for col in ["births", "deaths", "BA_BA", "BA_HBA", "BA_WBA", "BA_CBA"]:
        if col not in df.columns:
            continue
        log_col = f"log_{col}"
        df[log_col] = np.log(df[col].where(df[col] > 0))
        df[f"{col}_yoy"] = df.groupby(group_cols)[log_col].diff(4)
    return df


def national_sanity_check(nsa_nat: pd.DataFrame) -> pd.DataFrame:
    """Lag-correlation table: corr(births_yoy(t), BA_BA_yoy(t-lag)) for lag=0..MAX_LAG."""
    rows = []
    for lag in range(MAX_LAG + 1):
        x = nsa_nat["BA_BA_yoy"].shift(lag)
        y = nsa_nat["births_yoy"]
        valid = x.notna() & y.notna()
        corr = np.corrcoef(x[valid], y[valid])[0, 1] if valid.sum() > 4 else np.nan
        rows.append({"lag_quarters": lag, "n_obs": int(valid.sum()), "correlation": corr})
    return pd.DataFrame(rows)


def pooled_state_lag_correlations(nsa_states: pd.DataFrame) -> pd.DataFrame:
    """Same lag correlations, pooled across states after within-state demeaning
    (removes level differences across states). Still a descriptive correlation,
    not a model; formal panel tests are in Phase 5."""
    df = nsa_states.copy()
    for col in ["births_yoy", "BA_BA_yoy"]:
        df[f"{col}_demeaned"] = df.groupby("geo")[col].transform(lambda s: s - s.mean())

    rows = []
    for lag in range(MAX_LAG + 1):
        df[f"BA_BA_yoy_demeaned_lag{lag}"] = df.groupby("geo")["BA_BA_yoy_demeaned"].shift(lag)
        x = df[f"BA_BA_yoy_demeaned_lag{lag}"]
        y = df["births_yoy_demeaned"]
        valid = x.notna() & y.notna()
        corr = np.corrcoef(x[valid], y[valid])[0, 1] if valid.sum() > 4 else np.nan
        rows.append({"lag_quarters": lag, "n_obs": int(valid.sum()), "correlation": corr})
    return pd.DataFrame(rows)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    df = load_development_panel()
    nsa = df[df["seasonal_adj"] == "Not seasonally adjusted"].copy()
    nsa = add_yoy_log_changes(nsa, group_cols=["geo"])

    # --- National series (US total) ---
    nat = nsa[nsa["geo"] == "US"].sort_values("date")
    nat_corr = national_sanity_check(nat)
    nat_corr.to_csv(TABLE_DIR / "national_lag_correlations.csv", index=False)
    print("\nNational lag-correlation table (BA_BA leads births by `lag` quarters):")
    print(nat_corr.to_string(index=False))

    # Two stacked panels on one shared y-scale (both series are YoY %), not
    # a dual-axis chart: a second y-axis lets the scales be tuned to make
    # any two lines look related.
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True, sharey=True, facecolor=SURFACE)
    for ax, col, color, name in [
        (axes[0], "BA_BA_yoy", COLOR_APPS, "Business applications (Census BFS)"),
        (axes[1], "births_yoy", COLOR_BIRTHS, "Establishment births (BLS BED)"),
    ]:
        _style(ax)
        ax.plot(nat["date"], nat[col] * 100, color=color, linewidth=2)
        ax.set_title(name, loc="left", fontsize=10, color=INK)
    fig.suptitle("National, year-over-year % change (not seasonally adjusted), development window only (through 2022Q4)",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.supylabel("Year-over-year change, %", fontsize=9, color=INK_2)
    fig.tight_layout(rect=(0.01, 0, 1, 0.97))
    fig.savefig(FIG_DIR / "national_bfs_vs_bed_yoy.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)

    # --- Pooled state-level (exclude US total and PR) ---
    states = nsa[~nsa["geo"].isin(["US", "PR"])].copy()
    pooled_corr = pooled_state_lag_correlations(states)
    pooled_corr.to_csv(TABLE_DIR / "pooled_state_lag_correlations.csv", index=False)
    print("\nPooled state-level (within-state-demeaned) lag-correlation table:")
    print(pooled_corr.to_string(index=False))

    # --- Example state plots: 3 largest and the smallest (by mean births) ---
    mean_births = states.groupby("geo")["births"].mean().sort_values(ascending=False)
    example_states = list(mean_births.head(3).index) + [mean_births.index[-1]]
    fig, axes = plt.subplots(len(example_states), 1, figsize=(10, 2.8 * len(example_states)),
                             sharex=True, facecolor=SURFACE)
    for i, (ax, geo) in enumerate(zip(axes, example_states)):
        sub = states[states["geo"] == geo].sort_values("date")
        _style(ax)
        ax.plot(sub["date"], sub["BA_BA_yoy"] * 100, color=COLOR_APPS, linewidth=2, label="Business applications")
        ax.plot(sub["date"], sub["births_yoy"] * 100, color=COLOR_BIRTHS, linewidth=2, label="Establishment births")
        ax.set_title(geo, loc="left", fontsize=10, color=INK)
        if i == 0:
            ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=INK_2)
    fig.suptitle("State examples, year-over-year % change (not seasonally adjusted), development window only",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.supylabel("Year-over-year change, %", fontsize=9, color=INK_2)
    fig.tight_layout(rect=(0.01, 0, 1, 0.98))
    fig.savefig(FIG_DIR / "state_examples_bfs_vs_bed_yoy.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)

    # --- Summary stats ---
    summary = (
        states.groupby("geo")[["births", "deaths", "BA_BA"]]
        .agg(["count", "mean", "std"])
    )
    summary.to_csv(TABLE_DIR / "panel_summary_stats.csv")

    print(f"\nFigures written to {FIG_DIR}")
    print(f"Tables written to {TABLE_DIR}")


if __name__ == "__main__":
    main()
