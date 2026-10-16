"""
RQ2: which business-application series carries the signal?
Pre-analysis plan Addendum 2 (pre_analysis_plan_addendum_2.md).

  D1. Locked test window (2023Q1-2025Q4): benchmark vs. benchmark + series
      S lagged h, for S in {BA, HBA, WBA, CBA}, h = 0-4. Holm family =
      4 series x h in {0, 3} Clark-West tests.
  D2. Same comparisons over 2010-2025 by period, plus direct comparisons
      of each narrower series against BA, and coefficient paths.

Regression models only. Run run_phase5_extensions.py first: the BA
forecasts here must reproduce phase5x_overtime_predictions.csv exactly.

Usage:
    python run_rq2.py
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from run_phase5_evaluation import (
    BENCHMARK_COLS,
    BFS_LAGS,
    KEYS,
    PROCESSED_DIR,
    TABLE_DIR,
    TARGET,
    compare_to_benchmark,
    expanding_window_predict,
    fit_predict_ols,
    holm_bonferroni,
    loss_difference,
    qdate,
    quarter_label,
    two_way_cluster_test,
    wild_cluster_bootstrap,
)
from run_phase5_extensions import (
    EVAL_START_YEAR,
    FIG_DIR,
    INK,
    INK_2,
    PERIODS,
    SERIES as SERIES_COLOR,
    SURFACE,
    _quarter_start,
    _shade_periods,
    _style,
    coefficient_path,
)

SERIES = {"BA": "BA_BA", "HBA": "BA_HBA", "WBA": "BA_WBA", "CBA": "BA_CBA"}
SERIES_NAMES = {
    "BA": "All business applications (BA)",
    "HBA": "High-propensity applications (HBA)",
    "WBA": "Applications with planned wages (WBA)",
    "CBA": "Corporate applications (CBA)",
}
HOLM_LEADS = [0, 3]


def model_name(label: str, h: int) -> str:
    return f"{label}_h{h}"


def run_forecasts(nsa: pd.DataFrame, states: list[str], eval_q: list[int]) -> pd.DataFrame:
    print("  benchmark", flush=True)
    merged = expanding_window_predict(
        nsa, BENCHMARK_COLS, TARGET, states, fit_predict_ols, eval_quarters=eval_q
    ).rename(columns={"prediction": "pred_benchmark"})
    merged = merged[["geo", "state_name", "year", "quarter", TARGET, "pred_benchmark"]]
    for label, col in SERIES.items():
        print(f"  {label}, leads 0-4", flush=True)
        for h in BFS_LAGS:
            p = expanding_window_predict(
                nsa, BENCHMARK_COLS + [f"{col}_yoy_lag{h}"], TARGET, states,
                fit_predict_ols, eval_quarters=eval_q,
            )
            merged = merged.merge(
                p[KEYS + ["prediction"]].rename(columns={"prediction": f"pred_{model_name(label, h)}"}),
                on=KEYS, how="left",
            )
    return merged


def consistency_check(merged: pd.DataFrame) -> None:
    """BA forecasts must equal the Addendum 1 over-time run exactly."""
    ref = pd.read_csv(TABLE_DIR / "phase5x_overtime_predictions.csv")
    pairs = [("pred_benchmark", "pred_benchmark")] + [
        (f"pred_{model_name('BA', h)}", f"pred_econ_h{h}") for h in BFS_LAGS
    ]
    ref = ref[KEYS + [b for _, b in pairs]].rename(columns={b: f"ref_{b}" for _, b in pairs})
    chk = merged[KEYS + [a for a, _ in pairs]].merge(ref, on=KEYS)
    max_diff = max(float(np.max(np.abs(chk[a] - chk[f"ref_{b}"]))) for a, b in pairs)
    if len(chk) != len(ref) or max_diff > 1e-9:
        raise RuntimeError(f"Consistency check FAILED: {len(chk)} of {len(ref)} rows, max diff {max_diff}")
    print(f"  consistency check passed: BA forecasts match Addendum 1 for all {len(chk)} "
          f"state-quarters (max abs difference {max_diff:.1e})", flush=True)


def comparisons(sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in SERIES:
        for h in BFS_LAGS:
            for kind in ["cw", "mse"]:
                r = compare_to_benchmark(sub, TARGET, model_name(label, h), kind)
                r.update({"series": label, "lead": h})
                if kind == "mse":
                    d = loss_difference(sub, TARGET, f"pred_{model_name(label, h)}", "mse")
                    r["share_states_model_better"] = float((d.groupby(sub["geo"]).mean() > 0).mean())
                rows.append(r)
    return pd.DataFrame(rows)


def direct_vs_ba(sub: pd.DataFrame, label: str, h: int) -> dict:
    """Accuracy of the series-S model vs. the BA model. The models are not
    nested, so this uses the plain accuracy difference, with two-way
    clustered and wild cluster bootstrap inference."""
    ref, mod = f"pred_{model_name('BA', h)}", f"pred_{model_name(label, h)}"
    s = sub.dropna(subset=[TARGET, ref, mod])
    d = (s[TARGET] - s[ref]) ** 2 - (s[TARGET] - s[mod]) ** 2  # + = S more accurate than BA
    qtr = quarter_label(s)
    tw = two_way_cluster_test(d, s["geo"], qtr)
    wcb = wild_cluster_bootstrap(d.to_numpy(), qtr.to_numpy(), "two-sided")
    ba_mse = float(((s[TARGET] - s[ref]) ** 2).mean())
    pct = 100 / ba_mse
    return {
        "series": label, "lead": h, "n_quarters": qtr.nunique(),
        "diff_pct_of_BA_model_mse": d.mean() * pct,
        "ci95_low_pct": (d.mean() - 1.96 * tw["se"]) * pct,
        "ci95_high_pct": (d.mean() + 1.96 * tw["se"]) * pct,
        "two_way_p": 2 * (1 - norm.cdf(abs(tw["t_stat"]))),
        "wcb_quarter_p": wcb["p"],
        "share_states_series_better": float((d.groupby(s["geo"]).mean() > 0).mean()),
    }


def figures(gains: pd.DataFrame, coefs: pd.DataFrame) -> None:
    for kind, ycol, ylabel, title, fname in [
        ("gain", "cumulative_gain", "Cumulative reduction in squared error",
         "Cumulative accuracy gain vs. the benchmark, by application series (3-quarter lead)",
         "rq2_cumulative_gain_h3.png"),
        ("coef", "coef", "Coefficient (95% band, clustered by state)",
         "Estimated weight on each application series (3-quarter lead), by forecast quarter",
         "rq2_coefficient_paths_h3.png"),
    ]:
        fig, axes = plt.subplots(2, 2, figsize=(11, 6.8), sharex=True, sharey=True, facecolor=SURFACE)
        data = gains if kind == "gain" else coefs
        for i, (ax, label) in enumerate(zip(axes.flat, SERIES)):
            _style(ax)
            _shade_periods(ax, labels=(i == 0))
            d = data[data["series"] == label]
            if kind == "coef":
                ax.fill_between(d["date"], d["coef"] - 1.96 * d["se_state_cluster"],
                                d["coef"] + 1.96 * d["se_state_cluster"],
                                color=SERIES_COLOR, alpha=0.15, linewidth=0, zorder=2)
            ax.plot(d["date"], d[ycol], color=SERIES_COLOR, linewidth=2, zorder=3)
            ax.set_title(SERIES_NAMES[label], loc="left", fontsize=10, color=INK)
        fig.suptitle(title, x=0.01, ha="left", fontsize=11, color=INK)
        fig.supylabel(ylabel, fontsize=9, color=INK_2)
        fig.text(0.01, 0.005, "Each panel uses the same model and procedure; only the application series differs. "
                 "2010–2022 is pseudo-out-of-sample.", fontsize=8, color=INK_2)
        fig.tight_layout(rect=(0.01, 0.03, 1, 0.96))
        fig.savefig(FIG_DIR / fname, dpi=200, facecolor=SURFACE)
        plt.close(fig)


def main() -> None:
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    states = sorted(fc["geo"].unique())
    nsa = fc[fc["seasonal_adj"] == "Not seasonally adjusted"].copy()
    qd = qdate(nsa["year"], nsa["quarter"])
    eval_q = sorted(qd[nsa["year"] >= EVAL_START_YEAR].unique())

    print(f"[RQ2] Forecasting {len(eval_q)} target quarters for 4 series x 5 leads", flush=True)
    merged = run_forecasts(nsa, states, eval_q)
    consistency_check(merged)
    merged.to_csv(TABLE_DIR / "rq2_predictions.csv", index=False)

    # ---- D1: locked test window ----
    test = merged[merged["year"] >= 2023]
    d1 = comparisons(test)
    d1.to_csv(TABLE_DIR / "rq2_test_window_comparisons.csv", index=False)
    cw = d1[(d1["statistic"] == "cw") & d1["lead"].isin(HOLM_LEADS)]
    holm = cw[["series", "lead", "two_way_p", "wcb_quarter_p"]].copy()
    for col in ["two_way_p", "wcb_quarter_p"]:
        raw = {f"{r.series}_h{r.lead}": getattr(r, col) for r in cw.itertuples()}
        adj = holm_bonferroni(raw)
        holm[f"{col}_holm"] = [adj[f"{r.series}_h{r.lead}"] for r in cw.itertuples()]
    holm.to_csv(TABLE_DIR / "rq2_test_window_holm.csv", index=False)

    keep = ["series", "lead", "statistic", "mean_diff_pct_of_benchmark_mse", "two_way_p", "wcb_quarter_p"]
    print("\n[D1] Locked test window, leads 0 and 3 (+ = more accurate than benchmark):")
    print(d1[d1["lead"].isin(HOLM_LEADS)][keep].round(4).to_string(index=False))
    print("\n[D1] Holm family (Clark-West, 4 series x leads 0 and 3):")
    print(holm.round(4).to_string(index=False), flush=True)

    # ---- D2: by period ----
    by_period = []
    direct = []
    for name, y0, y1 in PERIODS:
        sub = merged[(merged["year"] >= y0) & (merged["year"] <= y1)]
        by_period.append(comparisons(sub).assign(period=name))
        for label in ["HBA", "WBA", "CBA"]:
            for h in HOLM_LEADS:
                direct.append({"period": name, **direct_vs_ba(sub, label, h)})
    by_period = pd.concat(by_period, ignore_index=True)
    by_period.to_csv(TABLE_DIR / "rq2_by_period.csv", index=False)
    direct = pd.DataFrame(direct)
    # Holm across all 24 direct comparisons (3 series x 2 leads x 4 periods).
    for col in ["two_way_p", "wcb_quarter_p"]:
        raw = {f"{r.period}|{r.series}|h{r.lead}": getattr(r, col) for r in direct.itertuples()}
        adj = holm_bonferroni(raw)
        direct[f"{col}_holm24"] = [adj[f"{r.period}|{r.series}|h{r.lead}"] for r in direct.itertuples()]
    direct.to_csv(TABLE_DIR / "rq2_vs_BA_direct.csv", index=False)

    # Sensitivity check (not pre-specified; prompted by Census documentation
    # found after the first run): HBA was redefined in November 2021 for data
    # from 2012 on, with 2004-2011 rescaled. Repeat the pre-pandemic direct
    # comparisons using only forecast targets in 2013-2019.
    check = []
    for name, y0, y1 in [("pre_pandemic_2010_19", 2010, 2019), ("pre_pandemic_2013_19", 2013, 2019)]:
        sub = merged[(merged["year"] >= y0) & (merged["year"] <= y1)]
        for label in ["HBA", "WBA", "CBA"]:
            for h in HOLM_LEADS:
                check.append({"window": name, **direct_vs_ba(sub, label, h)})
    pd.DataFrame(check).to_csv(TABLE_DIR / "rq2_hba_definition_check.csv", index=False)

    acc = by_period[(by_period["statistic"] == "mse") & by_period["lead"].isin(HOLM_LEADS)]
    print("\n[D2] Accuracy vs. benchmark by period (% of benchmark MSE; share of states better):")
    print(acc.pivot_table(index=["period", "lead"], columns="series",
                          values="mean_diff_pct_of_benchmark_mse").round(1).to_string())
    print(acc.pivot_table(index=["period", "lead"], columns="series",
                          values="share_states_model_better").round(2).to_string())
    info = by_period[(by_period["statistic"] == "cw") & (by_period["lead"] == 3)]
    print("\n[D2] Information test (Clark-West), lead 3, two-way p by period:")
    print(info.pivot_table(index="period", columns="series", values="two_way_p").round(4).to_string())
    print("\n[D2] Direct comparison vs. the BA model (+ = series more accurate than BA):")
    print(direct.round(3).to_string(index=False), flush=True)

    # ---- Descriptive: quarterly gains and coefficient paths at lead 3 ----
    gains, coefs = [], []
    for label, col in SERIES.items():
        d = loss_difference(merged, TARGET, f"pred_{model_name(label, 3)}", "mse")
        g = merged[["year", "quarter"]].assign(gain=d).groupby(["year", "quarter"])["gain"].mean().reset_index()
        g["cumulative_gain"] = g["gain"].cumsum()
        gains.append(g.assign(series=label))
        coefs.append(coefficient_path(nsa, states, eval_q, h=3, series=col).assign(series=label))
    gains = pd.concat(gains, ignore_index=True)
    coefs = pd.concat(coefs, ignore_index=True)
    gains["date"] = _quarter_start(gains["year"], gains["quarter"])
    coefs["date"] = _quarter_start(coefs["year"], coefs["quarter"])
    gains.to_csv(TABLE_DIR / "rq2_quarterly_gains_h3.csv", index=False)
    coefs.to_csv(TABLE_DIR / "rq2_coefficient_paths_h3.csv", index=False)

    summary = coefs.assign(
        period=np.select([coefs["year"] <= 2019, coefs["year"] <= 2021], ["2010-19", "2020-21"], "2022-25")
    ).groupby(["series", "period"])["coef"].mean().unstack()
    print("\n[D2] Mean estimated weight at lead 3, by forecast period:")
    print(summary.round(3).to_string(), flush=True)

    figures(gains, coefs)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
