"""
Pre-analysis plan Addendum 5 (pre_analysis_plan_addendum_5.md): analyses for
the pre-submission revision. None is pre-specified except item A, which
completes the reporting of the pre-specified estimand (RMSE and MAE, and the
seasonal naive benchmark). Item F, the live test of Census's projections, is
in make_live_forecasts_pbf.py.

  A. No-change benchmark and mean absolute error, test window and by period.
  B. Periods 2010-19, 2020-21, 2022 and 2023-25 (2022 descriptive only).
  C. Tests of change: quarterly cross-state mean loss differentials regressed
     on period indicators, Newey-West (3 lags); Holm within statistic and
     contrast.
  D. Inference robustness: t(G-1) references for the clustered tests;
     Diebold-Mariano/Clark-West tests on quarterly means with Newey-West
     (3 lags) and the Harvey-Leybourne-Newbold correction.
  E. Census projected business formations (BF_PBF4Q) as a predictor.
  G. State versus national information; births-weighted loss; BED revision
     check.

Inputs: the committed prediction tables and processed data. Outputs:
outputs/tables/a5_*.csv.

Usage:
    python run_addendum5.py
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from scipy.stats import t as tdist

from run_phase5_evaluation import (
    BENCHMARK_COLS,
    BFS_LAGS,
    KEYS,
    PROCESSED_DIR,
    TABLE_DIR,
    TARGET,
    cluster_robust_loss_test,
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

NSA = "Not seasonally adjusted"
APP_SERIES = ["BA", "HBA", "WBA", "CBA"]
PERIODS = [("2010-19", 2010, 2019), ("2020-21", 2020, 2021), ("2022", 2022, 2022), ("2023-25", 2023, 2025)]
DESCRIPTIVE_ONLY = {"2022"}  # four quarters: point estimates only
TEST_MODELS = ["benchmark", "econ_h0", "econ_h1", "econ_h2", "econ_h3", "econ_h4",
               "elasticnet", "rf", "gb", "combo"]
NW_LAGS = 3   # year-over-year targets overlap for up to three quarters
HLN_H = 4     # horizon used in the Harvey-Leybourne-Newbold correction
P_COLS = ["two_way_p", "wcb_p", "ci95_low_pct", "ci95_high_pct", "wcb_ci95_low_pct", "wcb_ci95_high_pct",
          "two_way_below_one_way"]


# ---------------------------------------------------------------- helpers

def period_rows(df: pd.DataFrame, y0: int, y1: int) -> pd.DataFrame:
    return df[(df["year"] >= y0) & (df["year"] <= y1)]


def loss(df: pd.DataFrame, col: str, kind: str) -> pd.Series:
    e = df[TARGET] - df[col]
    return e**2 if kind == "mse" else e.abs()


def compare(df: pd.DataFrame, ref_col: str, model_col: str, kind: str, descriptive: bool = False) -> dict:
    """Model vs. reference on squared ('mse') or absolute ('mae') loss.
    Positive = model better; expressed as % of the reference's mean loss.
    Two-sided two-way clustered and wild cluster bootstrap inference.

    two_way_below_one_way flags comparisons in which the two-way variance
    (state + quarter - heteroskedasticity-robust) is smaller than both
    one-way clustered variances. This happens when the loss differential is
    negatively correlated within states; the two-way p-value is then
    unreliable, and the wild bootstrap p-value should be read instead."""
    df = df.dropna(subset=[TARGET, ref_col, model_col])
    d = loss(df, ref_col, kind) - loss(df, model_col, kind)
    ref_mean = float(loss(df, ref_col, kind).mean())
    pct = 100 / ref_mean
    out = {
        "n": len(d), "n_quarters": quarter_label(df).nunique(),
        "diff_pct_of_reference": float(d.mean()) * pct,
        "share_states_model_better": float((d.groupby(df["geo"]).mean() > 0).mean()),
    }
    if descriptive:
        return {**out, **{c: np.nan for c in P_COLS}}
    qtr = quarter_label(df)
    tw = two_way_cluster_test(d, df["geo"], qtr)
    one_way_se = min(cluster_robust_loss_test(d, df["geo"])["se"], cluster_robust_loss_test(d, qtr)["se"])
    wcb = wild_cluster_bootstrap(d.to_numpy(), qtr.to_numpy(), "two-sided")
    out.update({
        "two_way_below_one_way": bool(tw["se"] < one_way_se),
        "two_way_p": 2 * (1 - norm.cdf(abs(tw["t_stat"]))),
        "wcb_p": wcb["p"],
        "ci95_low_pct": (d.mean() - 1.96 * tw["se"]) * pct,
        "ci95_high_pct": (d.mean() + 1.96 * tw["se"]) * pct,
        "wcb_ci95_low_pct": wcb["ci_low"] * pct,
        "wcb_ci95_high_pct": wcb["ci_high"] * pct,
    })
    return out


def blank_p(row: dict) -> dict:
    for k in ["naive_p", "state_cluster_p", "quarter_cluster_p", "two_way_se", "two_way_t", "two_way_p",
              "wcb_quarter_p", "ci95_low_pct", "ci95_high_pct", "mde80_pct", "wcb_ci95_low_pct", "wcb_ci95_high_pct"]:
        if k in row:
            row[k] = np.nan
    return row


def quarterly_mean_diff(df: pd.DataFrame, model_col: str, kind: str) -> pd.DataFrame:
    """Cross-state mean of the benchmark-minus-model loss differential, per quarter."""
    d = loss_difference(df, TARGET, model_col, kind)
    return df[["year", "quarter"]].assign(d=d).groupby(["year", "quarter"])["d"].mean().reset_index()


def hac_dm(q: pd.Series, alternative: str) -> dict:
    """Diebold-Mariano-type test on a quarterly series of mean loss differentials:
    Newey-West (Bartlett, NW_LAGS lags) variance, Harvey-Leybourne-Newbold
    correction with h = HLN_H, t(T-1) reference."""
    x = np.asarray(q, float)
    T = len(x)
    m = x.mean()
    u = x - m
    lrv = np.sum(u * u) / T
    for k in range(1, NW_LAGS + 1):
        lrv += 2 * (1 - k / (NW_LAGS + 1)) * np.sum(u[k:] * u[:-k]) / T
    dm = m / np.sqrt(lrv / T)
    hln = np.sqrt((T + 1 - 2 * HLN_H + HLN_H * (HLN_H - 1) / T) / T)
    stat = dm * hln
    p = 1 - tdist.cdf(stat, T - 1) if alternative == "greater" else 2 * (1 - tdist.cdf(abs(stat), T - 1))
    return {"T": T, "dm_stat": dm, "hln_stat": stat, "p": p}


def add_holm(df: pd.DataFrame, group_cols: list[str], key_cols: list[str], p_col: str, out_col: str) -> pd.DataFrame:
    df = df.copy()
    df[out_col] = np.nan
    for _, g in df.groupby(group_cols):
        raw = {"|".join(str(v) for v in r[key_cols]): r[p_col] for _, r in g.iterrows() if pd.notna(r[p_col])}
        if not raw:
            continue
        adj = holm_bonferroni(raw)
        for idx, r in g.iterrows():
            k = "|".join(str(v) for v in r[key_cols])
            if k in adj:
                df.loc[idx, out_col] = adj[k]
    return df


def quarterly_yoy_lags(monthly: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """Monthly counts -> quarterly sums (all three months required) -> year-over-year
    log change -> lags 0-4 relative to the target quarter, on a complete quarter grid."""
    m = monthly.copy()
    m["quarter"] = (m["month"] - 1) // 3 + 1
    q = (m.groupby(["geo", "year", "quarter"])["value"]
         .agg(lambda s: s.sum() if s.notna().sum() == 3 else np.nan).reset_index())
    q["qd"] = qdate(q["year"], q["quarter"])
    grid = pd.MultiIndex.from_product([q["geo"].unique(), range(int(q["qd"].min()), int(q["qd"].max()) + 1)],
                                      names=["geo", "qd"]).to_frame(index=False)
    q = grid.merge(q, on=["geo", "qd"], how="left").sort_values(["geo", "qd"])
    q["year"], q["quarter"] = (q["qd"] - 1) // 4, (q["qd"] - 1) % 4 + 1
    logv = np.log(q["value"].where(q["value"] > 0))
    q["yoy"] = logv - logv.groupby(q["geo"]).shift(4)
    for lag in BFS_LAGS:
        q[f"{value_name}_yoy_lag{lag}"] = q.groupby("geo")["yoy"].shift(lag)
    return q[["geo", "year", "quarter"] + [f"{value_name}_yoy_lag{lag}" for lag in BFS_LAGS]]


# ---------------------------------------------------------------- A

def item_a(test: pd.DataFrame, over: pd.DataFrame) -> None:
    acc, comp = [], []
    t = test.assign(pred_naive=0.0)
    for m in TEST_MODELS + ["naive"]:
        e = t[TARGET] - t[f"pred_{m}"]
        acc.append({"window": "test 2023-25", "model": m, "n": len(e), "rmse": float(np.sqrt((e**2).mean())),
                    "mae": float(e.abs().mean()), "mean_error": float(e.mean())})
        if m == "naive":
            continue
        for kind in ["mse", "mae"]:
            for ref in ["naive", "benchmark"]:
                if ref == m:
                    continue
                comp.append({"window": "test 2023-25", "model": m, "reference": ref, "loss": kind,
                             **compare(t, f"pred_{ref}", f"pred_{m}", kind)})
    models = ["benchmark"] + [f"{s}_h{h}" for s in APP_SERIES for h in BFS_LAGS]
    for name, y0, y1 in PERIODS:
        sub = period_rows(over, y0, y1).assign(pred_naive=0.0)
        for m in models + ["naive"]:
            e = sub[TARGET] - sub[f"pred_{m}"]
            acc.append({"window": name, "model": m, "n": len(e), "rmse": float(np.sqrt((e**2).mean())),
                        "mae": float(e.abs().mean()), "mean_error": float(e.mean())})
            if m == "naive":
                continue
            for kind in ["mse", "mae"]:
                for ref in ["naive", "benchmark"]:
                    if ref == m:
                        continue
                    comp.append({"window": name, "model": m, "reference": ref, "loss": kind,
                                 **compare(sub, f"pred_{ref}", f"pred_{m}", kind,
                                           descriptive=name in DESCRIPTIVE_ONLY)})
    pd.DataFrame(acc).to_csv(TABLE_DIR / "a5_A_accuracy.csv", index=False)
    comp = pd.DataFrame(comp)
    comp.to_csv(TABLE_DIR / "a5_A_comparisons.csv", index=False)
    print("\n[A] Test window, vs. no-change (positive = model better; % of no-change loss):")
    show = comp[(comp["window"] == "test 2023-25") & (comp["reference"] == "naive")]
    print(show.pivot_table(index="model", columns="loss", values="diff_pct_of_reference").round(1).to_string())


# ---------------------------------------------------------------- B

def item_b(over: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, y0, y1 in PERIODS:
        sub = period_rows(over, y0, y1)
        for s in APP_SERIES:
            for h in BFS_LAGS:
                for kind in ["cw", "mse"]:
                    r = compare_to_benchmark(sub, TARGET, f"{s}_h{h}", kind)
                    if kind == "mse":
                        d = loss_difference(sub, TARGET, f"pred_{s}_h{h}", "mse")
                        r["share_states_model_better"] = float((d.groupby(sub["geo"]).mean() > 0).mean())
                    r.update({"series": s, "lead": h, "period": name})
                    rows.append(blank_p(r) if name in DESCRIPTIVE_ONLY else r)
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "a5_B_by_period.csv", index=False)
    print("\n[B] Accuracy vs. benchmark by period (% of benchmark MSE):")
    acc = out[out["statistic"] == "mse"]
    print(acc.pivot_table(index=["series", "lead"], columns="period",
                          values="mean_diff_pct_of_benchmark_mse").round(1).to_string())
    return out


# ---------------------------------------------------------------- C

def change_tests(over: pd.DataFrame, labels: list[str], family: str) -> pd.DataFrame:
    base = period_rows(over, 2010, 2019)
    bench_mse_base = float(((base[TARGET] - base["pred_benchmark"]) ** 2).mean())
    rows = []
    for s in labels:
        for h in BFS_LAGS:
            for kind in ["mse", "cw"]:
                q = quarterly_mean_diff(over, f"pred_{s}_h{h}", kind)
                q["y"] = 100 * q["d"] / bench_mse_base
                X = pd.DataFrame({
                    "const": 1.0,
                    "p2020_21": q["year"].between(2020, 2021).astype(float),
                    "p2022": (q["year"] == 2022).astype(float),
                    "p2023_25": (q["year"] >= 2023).astype(float),
                })
                res = sm.OLS(q["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": NW_LAGS})
                for col, label in [("p2020_21", "2020-21 vs 2010-19"), ("p2022", "2022 vs 2010-19"),
                                   ("p2023_25", "2023-25 vs 2010-19")]:
                    rows.append({"family": family, "series": s, "lead": h, "statistic": kind, "contrast": label,
                                 "base_mean_pct": res.params["const"], "change_pct": res.params[col],
                                 "se_pct": res.bse[col], "p": res.pvalues[col], "n_quarters": len(q)})
                qq = q[(q["year"] <= 2019) | (q["year"] >= 2022)]
                X2 = pd.DataFrame({"const": 1.0, "late": (qq["year"] >= 2022).astype(float)})
                r2 = sm.OLS(qq["y"], X2).fit(cov_type="HAC", cov_kwds={"maxlags": NW_LAGS})
                rows.append({"family": family, "series": s, "lead": h, "statistic": kind,
                             "contrast": "2022-25 vs 2010-19 (two periods only)",
                             "base_mean_pct": r2.params["const"], "change_pct": r2.params["late"],
                             "se_pct": r2.bse["late"], "p": r2.pvalues["late"], "n_quarters": len(qq)})
    out = pd.DataFrame(rows)
    return add_holm(out, ["family", "statistic", "contrast"], ["series", "lead"], "p", "p_holm")


# ---------------------------------------------------------------- D

def item_d(test: pd.DataFrame, over: pd.DataFrame, b_table: pd.DataFrame) -> None:
    rows = []
    comp = pd.read_csv(TABLE_DIR / "phase5_comparisons.csv")
    comp = comp[comp["comparison"].isin([m for m in TEST_MODELS if m != "benchmark"])]
    for r in comp.itertuples():
        alt = "greater" if r.statistic == "cw" else "two-sided"
        df = r.n_quarters - 1
        p_t = (1 - tdist.cdf(r.two_way_t, df)) if alt == "greater" else 2 * (1 - tdist.cdf(abs(r.two_way_t), df))
        hac = hac_dm(quarterly_mean_diff(test, f"pred_{r.comparison}", r.statistic)["d"], alt)
        rows.append({"window": "test 2023-25", "model": r.comparison, "statistic": r.statistic,
                     "two_way_p_normal": r.two_way_p, "two_way_p_t": p_t, "t_df": df,
                     "hac_dm_hln_p": hac["p"], "hac_T": hac["T"]})
    for r in b_table.itertuples():
        if r.period in DESCRIPTIVE_ONLY or pd.isna(r.two_way_t):
            continue
        alt = "greater" if r.statistic == "cw" else "two-sided"
        df = r.n_quarters - 1
        p_t = (1 - tdist.cdf(r.two_way_t, df)) if alt == "greater" else 2 * (1 - tdist.cdf(abs(r.two_way_t), df))
        y0, y1 = next((a, b) for n, a, b in PERIODS if n == r.period)
        hac = hac_dm(quarterly_mean_diff(period_rows(over, y0, y1), f"pred_{r.comparison}", r.statistic)["d"], alt)
        rows.append({"window": r.period, "model": r.comparison, "statistic": r.statistic,
                     "two_way_p_normal": r.two_way_p, "two_way_p_t": p_t, "t_df": df,
                     "hac_dm_hln_p": hac["p"], "hac_T": hac["T"]})
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "a5_D_inference_robustness.csv", index=False)
    print("\n[D] Test window: two-way p (normal vs. t(G-1)) and HAC-DM-HLN p:")
    print(out[out["window"] == "test 2023-25"].round(3).to_string(index=False))


# ---------------------------------------------------------------- E

def item_e(nsa: pd.DataFrame, states: list[str], eval_q: list[int], over: pd.DataFrame) -> pd.DataFrame:
    bfs = pd.read_csv(PROCESSED_DIR / "bfs_state_applications.csv")
    # The same construction applied to all applications must reproduce the
    # committed BA_BA features exactly.
    ba = bfs[(bfs["series"] == "BA_BA") & (bfs["seasonal_adj"] == NSA) & bfs["geo"].isin(states)]
    chk = nsa[KEYS + [f"BA_BA_yoy_lag{h}" for h in BFS_LAGS]].merge(quarterly_yoy_lags(ba, "CHK"), on=KEYS, how="left")
    for h in BFS_LAGS:
        a, b = chk[f"BA_BA_yoy_lag{h}"], chk[f"CHK_yoy_lag{h}"]
        if not (a.isna().equals(b.isna()) and np.nanmax(np.abs(a - b)) < 1e-12):
            raise RuntimeError(f"Quarterly construction does not reproduce BA_BA_yoy_lag{h}")
    pbf = bfs[(bfs["series"] == "BF_PBF4Q") & (bfs["seasonal_adj"] == NSA) & bfs["geo"].isin(states)]
    lags = quarterly_yoy_lags(pbf, "PBF")
    df = nsa.merge(lags, on=KEYS, how="left")
    for h in BFS_LAGS:
        miss = df[f"BA_BA_yoy_lag{h}"].notna() & df[f"PBF_yoy_lag{h}"].isna()
        if miss.any():
            raise RuntimeError(f"PBF lag {h} missing on {int(miss.sum())} rows where applications exist")

    preds = expanding_window_predict(df, BENCHMARK_COLS, TARGET, states, fit_predict_ols, eval_quarters=eval_q)
    preds = preds[["geo", "state_name", "year", "quarter", TARGET, "prediction"]].rename(
        columns={"prediction": "pred_benchmark"})
    for h in BFS_LAGS:
        p = expanding_window_predict(df, BENCHMARK_COLS + [f"PBF_yoy_lag{h}"], TARGET, states,
                                     fit_predict_ols, eval_quarters=eval_q)
        preds = preds.merge(p[KEYS + ["prediction"]].rename(columns={"prediction": f"pred_PBF_h{h}"}),
                            on=KEYS, how="left")
    chk = preds[KEYS + ["pred_benchmark"]].merge(over[KEYS + ["pred_benchmark"]], on=KEYS, suffixes=("", "_rq2"))
    diff = float(np.max(np.abs(chk["pred_benchmark"] - chk["pred_benchmark_rq2"])))
    if len(chk) != len(over) or diff > 1e-9:
        raise RuntimeError(f"Benchmark does not reproduce rq2_predictions.csv (max diff {diff})")
    print(f"\n[E] consistency check passed: benchmark reproduces rq2_predictions.csv "
          f"on {len(chk)} state-quarters (max abs difference {diff:.1e})")
    preds.to_csv(TABLE_DIR / "a5_E_pbf_predictions.csv", index=False)

    both = preds.merge(over[KEYS + [f"pred_BA_h{h}" for h in BFS_LAGS]], on=KEYS)
    rows, direct = [], []
    for name, y0, y1 in PERIODS:
        sub = period_rows(both, y0, y1)
        for h in BFS_LAGS:
            for kind in ["cw", "mse"]:
                r = compare_to_benchmark(sub, TARGET, f"PBF_h{h}", kind)
                if kind == "mse":
                    d = loss_difference(sub, TARGET, f"pred_PBF_h{h}", "mse")
                    r["share_states_model_better"] = float((d.groupby(sub["geo"]).mean() > 0).mean())
                r.update({"lead": h, "period": name})
                rows.append(blank_p(r) if name in DESCRIPTIVE_ONLY else r)
            direct.append({"period": name, "lead": h, "reference": "BA",
                           **compare(sub, f"pred_BA_h{h}", f"pred_PBF_h{h}", "mse",
                                     descriptive=name in DESCRIPTIVE_ONLY)})
    by_period = pd.DataFrame(rows)
    cw = by_period[(by_period["statistic"] == "cw") & by_period["period"].isin(["2010-19", "2023-25"])].copy()
    for col in ["two_way_p", "wcb_quarter_p"]:
        raw = {f"{r.period}|h{r.lead}": getattr(r, col) for r in cw.itertuples()}
        adj = holm_bonferroni(raw)
        by_period.loc[cw.index, f"{col}_holm10"] = [adj[f"{r.period}|h{r.lead}"] for r in cw.itertuples()]
    by_period.to_csv(TABLE_DIR / "a5_E_pbf_by_period.csv", index=False)
    pd.DataFrame(direct).to_csv(TABLE_DIR / "a5_E_pbf_vs_ba.csv", index=False)
    print("[E] PBF4Q vs. benchmark (% of benchmark MSE) and Clark-West two-way p (Holm over 10):")
    show = by_period[by_period["statistic"] == "mse"].pivot_table(
        index="lead", columns="period", values="mean_diff_pct_of_benchmark_mse").round(1)
    print(show.to_string())
    print(by_period[by_period["statistic"] == "cw"][["period", "lead", "two_way_p", "two_way_p_holm10"]]
          .round(4).to_string(index=False))
    return preds


# ---------------------------------------------------------------- G

def item_g1(nsa: pd.DataFrame, states: list[str], eval_q: list[int], over: pd.DataFrame) -> None:
    bfs = pd.read_csv(PROCESSED_DIR / "bfs_state_applications.csv")
    us = bfs[(bfs["series"] == "BA_BA") & (bfs["seasonal_adj"] == NSA) & (bfs["geo"] == "US")]
    nat = quarterly_yoy_lags(us, "NAT").drop(columns="geo")
    df = nsa.merge(nat, on=["year", "quarter"], how="left")
    for h in [0, 3]:
        col = f"BA_BA_yoy_lag{h}"
        df[f"DEM_yoy_lag{h}"] = df[col] - df.groupby(["year", "quarter"])[col].transform("mean")
    preds = over[KEYS + [TARGET, "pred_benchmark", "pred_BA_h0", "pred_BA_h3"]].copy()
    for name in ["NAT", "DEM"]:
        for h in [0, 3]:
            p = expanding_window_predict(df, BENCHMARK_COLS + [f"{name}_yoy_lag{h}"], TARGET, states,
                                         fit_predict_ols, eval_quarters=eval_q)
            preds = preds.merge(p[KEYS + ["prediction"]].rename(columns={"prediction": f"pred_{name}_h{h}"}),
                                on=KEYS, how="left")
    preds.to_csv(TABLE_DIR / "a5_G1_predictions.csv", index=False)
    rows = []
    for pname, y0, y1 in PERIODS:
        sub = period_rows(preds, y0, y1)
        desc = pname in DESCRIPTIVE_ONLY
        for name in ["NAT", "DEM"]:
            for h in [0, 3]:
                for kind in ["cw", "mse"]:
                    r = compare_to_benchmark(sub, TARGET, f"{name}_h{h}", kind)
                    r.update({"period": pname, "predictor": name, "lead": h, "reference": "benchmark"})
                    rows.append(blank_p(r) if desc else r)
                c = compare(sub, f"pred_BA_h{h}", f"pred_{name}_h{h}", "mse", descriptive=desc)
                rows.append({"period": pname, "predictor": name, "lead": h, "reference": "state BA",
                             "statistic": "mse", "mean_diff_pct_of_benchmark_mse": np.nan,
                             "diff_pct_of_reference": c["diff_pct_of_reference"], "two_way_p": c["two_way_p"],
                             "wcb_quarter_p": c["wcb_p"], "share_states_model_better": c["share_states_model_better"],
                             "two_way_below_one_way": c["two_way_below_one_way"]})
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "a5_G1_state_vs_national.csv", index=False)
    print("\n[G1] National (NAT) and demeaned state (DEM) applications vs. benchmark (% of benchmark MSE):")
    acc = out[(out["reference"] == "benchmark") & (out["statistic"] == "mse")]
    print(acc.pivot_table(index=["predictor", "lead"], columns="period",
                          values="mean_diff_pct_of_benchmark_mse").round(1).to_string())


def item_g2(test: pd.DataFrame, over: pd.DataFrame) -> None:
    panel = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv")
    dev = panel[(panel["geo_type"] == "state") & (panel["seasonal_adj"] == NSA) & ~panel["in_test_window"]]
    w = dev.groupby("geo")["births"].mean()
    w = (w / w.sum()).rename("weight")
    rows = []

    def weighted(df: pd.DataFrame, model: str, window: str) -> None:
        d = df.merge(w, left_on="geo", right_index=True)
        lb = (d[TARGET] - d["pred_benchmark"]) ** 2
        lm = (d[TARGET] - d[f"pred_{model}"]) ** 2
        rows.append({"window": window, "model": model,
                     "weighted_diff_pct_of_benchmark_mse": 100 * ((lb - lm) * d["weight"]).sum() / (lb * d["weight"]).sum(),
                     "unweighted_diff_pct_of_benchmark_mse": 100 * (lb - lm).mean() / lb.mean()})

    for m in [x for x in TEST_MODELS if x != "benchmark"]:
        weighted(test, m, "test 2023-25")
    for name, y0, y1 in PERIODS:
        for s in APP_SERIES:
            for h in BFS_LAGS:
                weighted(period_rows(over, y0, y1), f"{s}_h{h}", name)
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "a5_G2_weighted_loss.csv", index=False)
    print("\n[G2] Births-weighted vs. unweighted accuracy, test window:")
    print(out[out["window"] == "test 2023-25"].round(2).to_string(index=False))


def yoy_from_levels(test: pd.DataFrame, levels: pd.DataFrame) -> pd.Series:
    """births_yoy for the test rows, recomputed from a table of birth levels
    (columns state_name, year, quarter, births)."""
    lv = levels.set_index(["state_name", "year", "quarter"])["births"]
    return pd.Series([np.log(lv.get((s, y, q), np.nan)) - np.log(lv.get((s, y - 1, q), np.nan))
                      for s, y, q in zip(test["state_name"], test["year"], test["quarter"])], index=test.index)


def item_g3(test: pd.DataFrame) -> None:
    panel = pd.read_csv(PROCESSED_DIR / "analysis_panel_quarterly.csv")
    old = panel[(panel["geo_type"] == "state") & (panel["seasonal_adj"] == NSA)]
    gap_def = float(np.max(np.abs(yoy_from_levels(test, old) - test[TARGET])))
    if gap_def > 1e-12:
        raise RuntimeError(f"Recomputed targets do not reproduce births_yoy (max diff {gap_def})")
    t = test.copy()
    t["births_yoy_new"] = yoy_from_levels(t, pd.read_csv(PROCESSED_DIR / "bed_state_births_nsa_2026-11-04.csv"))
    if t["births_yoy_new"].isna().any():
        raise RuntimeError("Missing state-quarters in the 2026-11-04 vintage")
    pre2025 = t[t["year"] < 2025]
    gap = float(np.max(np.abs(pre2025["births_yoy_new"] - pre2025[TARGET])))
    rev = t.loc[t["year"] == 2025, "births_yoy_new"] - t.loc[t["year"] == 2025, TARGET]
    print(f"\n[G3] Target definition reproduced (max diff {gap_def:.1e}). 2023-24 targets, "
          f"Oct 14 vs Oct 28 release: max abs difference {gap:.2e}. 2025 targets revised by "
          f"{rev.abs().mean():.4f} on average (max {rev.abs().max():.4f}) in log points.")
    rows = []
    for m in [x for x in TEST_MODELS if x != "benchmark"]:
        out = {"model": m}
        for label, col in [("oct14_vintage", TARGET), ("oct28_release", "births_yoy_new")]:
            lb = (t[col] - t["pred_benchmark"]) ** 2
            lm = (t[col] - t[f"pred_{m}"]) ** 2
            out[f"diff_pct_{label}"] = 100 * (lb - lm).mean() / lb.mean()
            out[f"rmse_{label}"] = float(np.sqrt(lm.mean()))
        rows.append(out)
    lb_old = np.sqrt(((t[TARGET] - t["pred_benchmark"]) ** 2).mean())
    lb_new = np.sqrt(((t["births_yoy_new"] - t["pred_benchmark"]) ** 2).mean())
    rows.append({"model": "benchmark", "rmse_oct14_vintage": lb_old, "rmse_oct28_release": lb_new})
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "a5_G3_bed_revision_check.csv", index=False)
    print(out.round(4).to_string(index=False))


# ---------------------------------------------------------------- main

def main() -> None:
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    states = sorted(fc["geo"].unique())
    nsa = fc[fc["seasonal_adj"] == NSA].copy()
    qd = qdate(nsa["year"], nsa["quarter"])
    eval_q = sorted(qd[nsa["year"] >= 2010].unique())

    test = pd.read_csv(TABLE_DIR / "phase5_predictions.csv")
    over = pd.read_csv(TABLE_DIR / "rq2_predictions.csv")

    item_a(test, over)
    b_table = item_b(over)
    item_d(test, over, b_table)
    pbf = item_e(nsa, states, eval_q, over)
    changes = pd.concat([change_tests(over, APP_SERIES, "applications"),
                         change_tests(pbf, ["PBF"], "PBF4Q")], ignore_index=True)
    changes.to_csv(TABLE_DIR / "a5_C_change_tests.csv", index=False)
    print("\n[C] Tests of change, squared-error differential (change in % of 2010-19 benchmark MSE; Holm p):")
    show = changes[(changes["statistic"] == "mse") & (changes["contrast"] != "2022-25 vs 2010-19 (two periods only)")]
    print(show.pivot_table(index=["family", "series", "lead"], columns="contrast",
                           values=["change_pct", "p_holm"]).round(3).to_string())
    item_g1(nsa, states, eval_q, over)
    item_g2(test, over)
    item_g3(test)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
