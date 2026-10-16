"""
RQ4 (exploratory): are business applications' forecasting gains larger in
states where more new establishments come from brand-new firms?
Pre-analysis plan Addendum 4 (pre_analysis_plan_addendum_4.md).

Uses the existing over-time forecasts (rq2_predictions.csv); estimates no
new forecasting models. Run run_rq2.py first.

Usage:
    python run_rq4.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cleaning"))

from build_panel import GEO_TO_NAME  # noqa: E402
from run_phase5_evaluation import PROCESSED_DIR, TABLE_DIR, TARGET, holm_bonferroni, loss_difference  # noqa: E402
from run_phase5_extensions import FIG_DIR, INK, INK_2, SERIES as COLOR, SURFACE, _style  # noqa: E402

PRE = (2010, 2019)
POST = (2022, 2025)
PRIMARY = [("BA", 0), ("BA", 3)]
SECONDARY = [("HBA", 0, PRE), ("HBA", 3, PRE), ("BA", 0, POST), ("BA", 3, POST)]


def state_gains(pred: pd.DataFrame, series: str, lead: int, years: tuple[int, int]) -> pd.Series:
    """Per-state accuracy gain over the benchmark, % of that state's benchmark MSE."""
    col = f"pred_{series}_h{lead}"
    sub = pred[pred["year"].between(*years)].dropna(subset=[TARGET, "pred_benchmark", col])
    d = loss_difference(sub, TARGET, col, "mse")
    bench = (sub[TARGET] - sub["pred_benchmark"]) ** 2
    g = pd.DataFrame({"geo": sub["geo"], "d": d, "b": bench}).groupby("geo").mean()
    return 100 * g["d"] / g["b"]


def new_firm_share() -> pd.Series:
    """Mean BDS new-firm share of establishment entry, 2010-2019, by state."""
    bds = pd.read_csv(PROCESSED_DIR / "bds_state_new_firm_share.csv", dtype={"st": str})
    bed = pd.read_csv(PROCESSED_DIR / "bed_state_establishment_births_deaths.csv", dtype={"state_code": str})
    fips_to_name = bed.drop_duplicates("state_code").set_index("state_code")["state_name"]
    name_to_geo = {v: k for k, v in GEO_TO_NAME.items()}
    share = bds[bds["year"].between(*PRE)].groupby("st")["new_firm_share"].mean()
    share.index = share.index.map(fips_to_name).map(name_to_geo)
    return share.rename("new_firm_share")


def correlate(gain: pd.Series, share: pd.Series) -> dict:
    d = pd.concat([gain.rename("gain"), share], axis=1).dropna()
    rho, p = spearmanr(d["new_firm_share"], d["gain"])
    # OLS check: gain (% of benchmark MSE) on the share in percentage points.
    ols = sm.OLS(d["gain"], sm.add_constant(100 * d["new_firm_share"])).fit(cov_type="HC1")
    return {
        "n_states": len(d), "spearman_rho": rho, "spearman_p": p,
        "ols_slope_per_10pp_share": 10 * ols.params.iloc[1],
        "ols_slope_se_per_10pp": 10 * ols.bse.iloc[1], "ols_p": ols.pvalues.iloc[1],
    }


def main() -> None:
    pred = pd.read_csv(TABLE_DIR / "rq2_predictions.csv")
    share = new_firm_share()
    print(f"[RQ4] New-firm share 2010-19, {share.notna().sum()} states: mean {share.mean():.3f}, "
          f"range {share.min():.3f}-{share.max():.3f}", flush=True)

    rows, state_data = [], pd.DataFrame({"new_firm_share_2010_19": share})
    for series, lead in PRIMARY:
        g = state_gains(pred, series, lead, PRE)
        state_data[f"gain_{series}_h{lead}_2010_19"] = g
        rows.append({"role": "primary", "series": series, "lead": lead, "period": "2010-2019", **correlate(g, share)})
    for series, lead, years in SECONDARY:
        g = state_gains(pred, series, lead, years)
        label = f"{years[0]}-{years[1]}"
        state_data[f"gain_{series}_h{lead}_{years[0]}_{years[1] % 100:02d}"] = g
        rows.append({"role": "secondary", "series": series, "lead": lead, "period": label, **correlate(g, share)})
    res = pd.DataFrame(rows)

    prim = res[res["role"] == "primary"]
    adj = holm_bonferroni({f"h{r.lead}": r.spearman_p for r in prim.itertuples()})
    res["spearman_p_holm"] = [adj[f"h{r.lead}"] if r.role == "primary" else np.nan for r in res.itertuples()]
    res["reading"] = [
        ("consistent with the new-firm mechanism" if r.spearman_rho > 0 and r.spearman_p_holm < 0.05
         else "inconclusive") if r.role == "primary" else "" for r in res.itertuples()
    ]
    res.to_csv(TABLE_DIR / "rq4_correlations.csv", index=False)
    state_data.index.name = "geo"
    state_data.reset_index().sort_values("geo").to_csv(TABLE_DIR / "rq4_state_data.csv", index=False)

    print(res[["role", "series", "lead", "period", "n_states", "spearman_rho", "spearman_p",
               "spearman_p_holm", "ols_slope_per_10pp_share", "ols_p", "reading"]].round(3).to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True, facecolor=SURFACE)
    for ax, (series, lead) in zip(axes, PRIMARY):
        col = f"gain_{series}_h{lead}_2010_19"
        r = res[(res["role"] == "primary") & (res["lead"] == lead)].iloc[0]
        _style(ax)
        ax.scatter(100 * state_data["new_firm_share_2010_19"], state_data[col], s=36, color=COLOR,
                   edgecolor=SURFACE, linewidth=1, zorder=3)
        ax.set_title(f"{'Same-quarter' if lead == 0 else '3-quarter'} lead  (Spearman ρ = {r.spearman_rho:.2f}, "
                     f"Holm p = {r.spearman_p_holm:.2f})", loc="left", fontsize=10, color=INK)
        ax.set_xlabel("New establishments from brand-new firms, 2010–19 (%)", fontsize=9, color=INK_2)
    axes[0].set_ylabel("Accuracy gain from applications,\n2010–19 (% of benchmark MSE)", fontsize=9, color=INK_2)
    fig.suptitle("RQ4 (exploratory): forecasting gain vs. share of entry from new firms, by state",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIG_DIR / "rq4_gain_vs_new_firm_share.png", dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
