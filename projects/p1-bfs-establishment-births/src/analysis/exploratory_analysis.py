"""
Phase 3 exploratory analysis (DEVELOPMENT WINDOW ONLY).

This script enforces the pre-analysis-plan discipline from
research_question.md: it loads the integrated panel, immediately drops
every row with in_test_window == True, and never touches them again. No
forecast is evaluated here -- this is descriptive/correlational only,
meant to answer the Phase 3 gate question: is a BFS-applications ->
BED-establishment-births signal plausibly present at all, before
committing to a full model-comparison design in Phase 4/5?

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


def load_development_panel() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv", parse_dates=["date"])
    n_total = len(df)
    df = df[~df["in_test_window"]].copy()
    print(
        f"Loaded {n_total:,} total rows; dropped {n_total - len(df):,} "
        f"test-window (2023Q1+) rows. Using {len(df):,} development-window rows only."
    )
    print("TEST WINDOW REMAINS LOCKED: not loaded for any analysis beyond this filter.")
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
    """Same lag-correlation idea, pooled across states, after within-state demeaning
    (removes level differences across states; still a descriptive correlation, not a
    model -- formal panel tests come in Phase 5)."""
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

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(nat["date"], nat["births_yoy"] * 100, color="#1f77b4", label="BED establishment births, YoY %")
    ax1.set_ylabel("Establishment births, YoY %", color="#1f77b4")
    ax2 = ax1.twinx()
    ax2.plot(nat["date"], nat["BA_BA_yoy"] * 100, color="#d62728", alpha=0.7, label="BFS business applications, YoY %")
    ax2.set_ylabel("Business applications, YoY %", color="#d62728")
    ax1.set_title("National: BFS business applications vs. BED establishment births (YoY, NSA)\nDevelopment window only (through 2022Q4)")
    ax1.axhline(0, color="gray", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "national_bfs_vs_bed_yoy.png", dpi=150)
    plt.close(fig)

    # --- Pooled state-level (exclude US total and PR) ---
    states = nsa[~nsa["geo"].isin(["US", "PR"])].copy()
    pooled_corr = pooled_state_lag_correlations(states)
    pooled_corr.to_csv(TABLE_DIR / "pooled_state_lag_correlations.csv", index=False)
    print("\nPooled state-level (within-state-demeaned) lag-correlation table:")
    print(pooled_corr.to_string(index=False))

    # --- Example state plots: 3 largest (by mean births) + 1 small state ---
    mean_births = states.groupby("geo")["births"].mean().sort_values(ascending=False)
    example_states = list(mean_births.head(3).index) + [mean_births.index[-1]]
    fig, axes = plt.subplots(len(example_states), 1, figsize=(10, 3 * len(example_states)), sharex=True)
    for ax, geo in zip(axes, example_states):
        sub = states[states["geo"] == geo].sort_values("date")
        ax.plot(sub["date"], sub["births_yoy"] * 100, label="births YoY %", color="#1f77b4")
        ax.plot(sub["date"], sub["BA_BA_yoy"] * 100, label="BA_BA YoY %", color="#d62728", alpha=0.7)
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.set_title(geo)
        ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("State examples: BFS applications vs. BED births (YoY, NSA), development window only")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "state_examples_bfs_vs_bed_yoy.png", dpi=150)
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
