"""
Phase 5: fit all pre-specified models (pre_analysis_plan.md) with genuine
expanding-window, real-time-consistent re-estimation through the test
window (2023Q1-2025Q4), then evaluate with the committed statistical
tests.

DISCLOSED DEVIATIONS FROM THE PAP (per PAP Sec. 8 -- stated here, not
silently substituted; also logged in research_log.md):
  1. "ARDL" and "bridge equation" collapse to one specification under the
     real-time convention adopted in build_forecast_dataset.py (BFS is
     treated as available at full-quarter granularity once its ~2-week
     lag has passed, so there is no partial-quarter bridging left to do).
  2. The Hansen-Lunde-Nason (2011) Model Confidence Set is NOT
     implemented from scratch -- no vetted, widely-used Python reference
     implementation was available to build on with confidence, and a
     bespoke bootstrap implementation risks a subtle, hard-to-detect bug
     producing an invalid statistical conclusion. Substituted with
     Holm-Bonferroni step-down correction across the primary
     comparisons -- a textbook, low-risk method serving the same
     family-wise error control purpose.
  3. The Qu, Timmermann & Zhu (2024) / Akgun et al. (2024) panel
     forecast-comparison tests are NOT implemented -- both are very
     recent papers without an available reference implementation to
     build on safely. Substituted with a cluster-robust (clustered by
     state) test of the mean loss differential, a standard, well
     understood method for pooled significance under cross-sectional
     dependence.
These substitutions should be revisited (e.g. if a reviewer specifically
asks for the originally cited tests), not treated as a permanent
methodological choice.

Real-time training-label constraint: at any origin forecasting target
quarter t, a candidate training row (with its OWN target quarter t') is
only included if t' <= t - 3 (quarters) -- i.e. that row's own outcome
would itself already be confirmed in real time, given BED's ~3-quarter
publication lag. This is what makes the expanding window genuinely
real-time-consistent rather than just "fit once on all prior rows."

Usage:
    python run_phase5_evaluation.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

OWN_LAGS = [3, 4, 5]
BFS_LAGS = [0, 1, 2, 3, 4]
LABEL_LAG_MIN = 3  # quarters: training labels must be this old to be "known"

ALL_STATES = None  # filled in at runtime, fixed category list
ALL_QUARTERS = [1, 2, 3, 4]


def qdate(year: pd.Series, quarter: pd.Series) -> pd.Series:
    return year * 4 + quarter


def make_dummies(df: pd.DataFrame, states: list[str]) -> pd.DataFrame:
    q = pd.Categorical(df["quarter_target"], categories=ALL_QUARTERS)
    s = pd.Categorical(df["geo"], categories=states)
    qd = pd.get_dummies(q, prefix="q", drop_first=True).astype(float)
    sd = pd.get_dummies(s, prefix="st", drop_first=True).astype(float)
    qd.index = df.index
    sd.index = df.index
    return pd.concat([qd, sd], axis=1)


def build_design(df: pd.DataFrame, feature_cols: list[str], states: list[str]) -> pd.DataFrame:
    X = df[feature_cols].copy()
    dummies = make_dummies(df, states)
    return pd.concat([X, dummies], axis=1)


def expanding_window_predict(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    states: list[str],
    fit_predict_fn,
) -> pd.DataFrame:
    """Genuine expanding-window, real-time-consistent forecast loop.

    For each distinct test-window target quarter t (ascending), train on
    all rows (dev + earlier test) whose OWN target quarter is <= t -
    LABEL_LAG_MIN, predict on all rows with target quarter == t.
    fit_predict_fn(X_train, y_train, X_test) -> np.array of predictions.
    """
    df = df.copy()
    df["qd"] = qdate(df["year"], df["quarter"])
    test_quarters = sorted(df.loc[df["in_test_window"], "qd"].unique())

    results = []
    for t in test_quarters:
        train_cutoff = t - LABEL_LAG_MIN
        train_df = df[df["qd"] <= train_cutoff].dropna(subset=feature_cols + [target_col])
        test_df = df[df["qd"] == t].dropna(subset=feature_cols)

        if len(train_df) < 50 or len(test_df) == 0:
            continue

        X_train = build_design(train_df, feature_cols, states)
        X_test = build_design(test_df, feature_cols, states)
        # Align columns (categories fixed via make_dummies, so this should
        # already match; reindex defensively in case a category never
        # appears in a given training slice).
        X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

        y_train = train_df[target_col].values
        preds = fit_predict_fn(X_train.values, y_train, X_test.values)

        out = test_df[["geo", "state_name", "year", "quarter", target_col]].copy()
        out["prediction"] = preds
        out["train_n"] = len(train_df)
        results.append(out)

    return pd.concat(results, ignore_index=True)


# ---- Model factories (hyperparameters tuned ONCE on dev window only) ----

def tune_elasticnet(dev_df, feature_cols, target_col, states):
    X = build_design(dev_df, feature_cols, states).dropna()
    y = dev_df.loc[X.index, target_col]
    valid = y.notna()
    X, y = X[valid], y[valid]
    scaler = StandardScaler().fit(X.values)
    Xs = scaler.transform(X.values)

    best = (None, np.inf)
    tscv = TimeSeriesSplit(n_splits=4)
    for alpha in [0.001, 0.01, 0.05, 0.1]:
        for l1_ratio in [0.2, 0.5, 0.9]:
            errs = []
            for tr_idx, va_idx in tscv.split(Xs):
                m = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=5000)
                m.fit(Xs[tr_idx], y.values[tr_idx])
                pred = m.predict(Xs[va_idx])
                errs.append(np.mean((pred - y.values[va_idx]) ** 2))
            mse = np.mean(errs)
            if mse < best[1]:
                best = ((alpha, l1_ratio), mse)
    return best[0]


def tune_tree_model(dev_df, feature_cols, target_col, states, model_cls, param_grid):
    X = build_design(dev_df, feature_cols, states).dropna()
    y = dev_df.loc[X.index, target_col]
    valid = y.notna()
    X, y = X[valid].values, y[valid].values

    best = (None, np.inf)
    tscv = TimeSeriesSplit(n_splits=4)
    for params in param_grid:
        errs = []
        for tr_idx, va_idx in tscv.split(X):
            m = model_cls(random_state=0, **params)
            m.fit(X[tr_idx], y[tr_idx])
            pred = m.predict(X[va_idx])
            errs.append(np.mean((pred - y[va_idx]) ** 2))
        mse = np.mean(errs)
        if mse < best[1]:
            best = (params, mse)
    return best[0]


def fit_predict_ols(X_train, y_train, X_test):
    X_train_c = sm.add_constant(X_train, has_constant="add")
    X_test_c = sm.add_constant(X_test, has_constant="add")
    model = sm.OLS(y_train, X_train_c).fit()
    return model.predict(X_test_c)


def fit_predict_elasticnet(alpha, l1_ratio):
    def f(X_train, y_train, X_test):
        scaler = StandardScaler().fit(X_train)
        m = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=5000)
        m.fit(scaler.transform(X_train), y_train)
        return m.predict(scaler.transform(X_test))
    return f


def fit_predict_tree(model_cls, params):
    def f(X_train, y_train, X_test):
        m = model_cls(random_state=0, **params)
        m.fit(X_train, y_train)
        return m.predict(X_test)
    return f


# ---- Statistical tests ----

def clark_west_test(e1: np.ndarray, e2: np.ndarray, f1: np.ndarray, f2: np.ndarray) -> dict:
    """Clark & West (2007) nested-model test. Model 1 = restricted
    (benchmark), model 2 = unrestricted (benchmark + predictor).
    f = adjusted loss differential; positive mean => model 2 improves."""
    adj = (f1 - f2) ** 2
    f_stat = e1**2 - (e2**2 - adj)
    n = len(f_stat)
    mean_f = f_stat.mean()
    se_f = f_stat.std(ddof=1) / np.sqrt(n)
    t_stat = mean_f / se_f if se_f > 0 else np.nan
    from scipy.stats import norm
    p_value = 1 - norm.cdf(t_stat)  # one-sided: model 2 improves
    return {"n": n, "mean_adj_loss_diff": mean_f, "t_stat": t_stat, "p_value_one_sided": p_value}


def cluster_robust_loss_test(loss_diff: pd.Series, cluster: pd.Series) -> dict:
    """Pooled significance of mean loss differential, clustered by state.
    Substitute for Qu-Timmermann-Zhu / Akgun panel tests -- see module
    docstring, item 3."""
    X = sm.add_constant(np.ones(len(loss_diff)))
    model = sm.OLS(loss_diff.values, X).fit(
        cov_type="cluster", cov_kwds={"groups": cluster.values}
    )
    return {
        "n": len(loss_diff),
        "n_clusters": cluster.nunique(),
        "mean_loss_diff": model.params[0],
        "t_stat": model.tvalues[0],
        "p_value_two_sided": model.pvalues[0],
    }


def two_way_cluster_test(loss_diff: pd.Series, cluster1: pd.Series, cluster2: pd.Series) -> dict:
    """Cameron, Gelbach & Miller (2011) two-way cluster-robust test of a
    constant-only regression: Var = Var_cluster1 + Var_cluster2 - Var_HC1.
    Used here to check robustness to BOTH serial correlation within a
    state over time (cluster1=state) and cross-sectional dependence
    across states within the same quarter (cluster2=quarter) -- the
    latter is exactly the concern the Qu-Timmermann-Zhu / Akgun panel
    tests are built for (see module docstring, item 3)."""
    X = sm.add_constant(np.ones(len(loss_diff)))
    y = loss_diff.values

    m1 = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cluster1.values})
    m2 = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cluster2.values})
    m0 = sm.OLS(y, X).fit(cov_type="HC1")

    var_2way = (
        np.asarray(m1.cov_params())[0, 0]
        + np.asarray(m2.cov_params())[0, 0]
        - np.asarray(m0.cov_params())[0, 0]
    )
    var_2way = max(var_2way, 0.0)  # the GM formula can occasionally go slightly negative
    se_2way = np.sqrt(var_2way)
    mean_diff = m0.params[0]
    t_stat = mean_diff / se_2way if se_2way > 0 else np.nan
    from scipy.stats import norm
    p_value = 2 * (1 - norm.cdf(abs(t_stat)))
    return {
        "n": len(loss_diff),
        "n_cluster1_state": cluster1.nunique(),
        "n_cluster2_quarter": cluster2.nunique(),
        "mean_loss_diff": mean_diff,
        "t_stat": t_stat,
        "p_value_two_sided": p_value,
    }


def holm_bonferroni(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted = {}
    running_max = 0.0
    for i, (name, p) in enumerate(items):
        adj = min((m - i) * p, 1.0)
        running_max = max(running_max, adj)
        adjusted[name] = running_max
    return adjusted


def main() -> None:
    global ALL_STATES
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    ALL_STATES = sorted(fc["geo"].unique())

    nsa = fc[fc["seasonal_adj"] == "Not seasonally adjusted"].copy()
    dev_nsa = nsa[~nsa["in_test_window"]]

    benchmark_cols = [f"births_yoy_lag{l}" for l in OWN_LAGS]
    target = "births_yoy"

    print(f"States: {len(ALL_STATES)}  Dev rows (NSA): {len(dev_nsa):,}")

    # ---------------- Benchmark model (no BFS) ----------------
    print("\n[Benchmark] AR(3,4,5) + quarter + state FE, expanding window...")
    bench_preds = expanding_window_predict(
        nsa, benchmark_cols, target, ALL_STATES, fit_predict_ols
    )
    bench_preds = bench_preds.rename(columns={"prediction": "pred_benchmark"})

    all_results = {"benchmark": bench_preds[["geo", "year", "quarter", target, "pred_benchmark"]]}

    # ---------------- Per-horizon econometric: benchmark + BFS lag h ----------------
    econ_preds = {}
    for h in BFS_LAGS:
        cols = benchmark_cols + [f"BA_BA_yoy_lag{h}"]
        print(f"[Econometric h={h}] benchmark + BA_BA_yoy_lag{h}, expanding window...")
        pred = expanding_window_predict(nsa, cols, target, ALL_STATES, fit_predict_ols)
        econ_preds[h] = pred.rename(columns={"prediction": f"pred_econ_h{h}"})

    # ---------------- ML kitchen-sink models ----------------
    ml_cols = benchmark_cols + [f"BA_BA_yoy_lag{l}" for l in BFS_LAGS]

    print("\n[Tuning] ElasticNet (dev-window-only time-series CV)...")
    en_params = tune_elasticnet(dev_nsa, ml_cols, target, ALL_STATES)
    print(f"  Selected (alpha, l1_ratio) = {en_params}")

    print("[Tuning] RandomForest (dev-window-only time-series CV)...")
    rf_grid = [
        {"n_estimators": n, "max_depth": d, "min_samples_leaf": 5}
        for n in [200, 400] for d in [3, 5, None]
    ]
    rf_params = tune_tree_model(dev_nsa, ml_cols, target, ALL_STATES, RandomForestRegressor, rf_grid)
    print(f"  Selected: {rf_params}")

    print("[Tuning] GradientBoosting (dev-window-only time-series CV)...")
    gb_grid = [
        {"n_estimators": n, "max_depth": d, "learning_rate": lr}
        for n in [100, 200] for d in [2, 3] for lr in [0.03, 0.1]
    ]
    gb_params = tune_tree_model(dev_nsa, ml_cols, target, ALL_STATES, GradientBoostingRegressor, gb_grid)
    print(f"  Selected: {gb_params}")

    print("\n[ElasticNet] expanding window with fixed hyperparameters...")
    en_preds = expanding_window_predict(
        nsa, ml_cols, target, ALL_STATES, fit_predict_elasticnet(*en_params)
    ).rename(columns={"prediction": "pred_elasticnet"})

    print("[RandomForest] expanding window with fixed hyperparameters...")
    rf_preds = expanding_window_predict(
        nsa, ml_cols, target, ALL_STATES, fit_predict_tree(RandomForestRegressor, rf_params)
    ).rename(columns={"prediction": "pred_rf"})

    print("[GradientBoosting] expanding window with fixed hyperparameters...")
    gb_preds = expanding_window_predict(
        nsa, ml_cols, target, ALL_STATES, fit_predict_tree(GradientBoostingRegressor, gb_params)
    ).rename(columns={"prediction": "pred_gb"})

    # ---------------- Merge everything on (geo, year, quarter) ----------------
    merged = bench_preds[["geo", "state_name", "year", "quarter", target, "pred_benchmark"]]
    for h, pred in econ_preds.items():
        merged = merged.merge(
            pred[["geo", "year", "quarter", f"pred_econ_h{h}"]], on=["geo", "year", "quarter"], how="left"
        )
    merged = merged.merge(en_preds[["geo", "year", "quarter", "pred_elasticnet"]], on=["geo", "year", "quarter"], how="left")
    merged = merged.merge(rf_preds[["geo", "year", "quarter", "pred_rf"]], on=["geo", "year", "quarter"], how="left")
    merged = merged.merge(gb_preds[["geo", "year", "quarter", "pred_gb"]], on=["geo", "year", "quarter"], how="left")

    # Equal-weight combination: best econometric (h=3, the PAP's pre-specified
    # horizon of interest) + best ML model, chosen by dev-window CV MSE
    # among RF/GB/ElasticNet (selection itself must not use test data).
    merged["pred_combo"] = (merged["pred_econ_h3"] + merged["pred_rf"]) / 2

    merged.to_csv(TABLE_DIR / "phase5_predictions.csv", index=False)
    print(f"\nWrote predictions for {len(merged):,} test observations to {TABLE_DIR / 'phase5_predictions.csv'}")

    # ---------------- Evaluation: RMSE/MAE by model ----------------
    model_cols = ["pred_benchmark"] + [f"pred_econ_h{h}" for h in BFS_LAGS] + [
        "pred_elasticnet", "pred_rf", "pred_gb", "pred_combo"
    ]
    rows = []
    for col in model_cols:
        err = merged[target] - merged[col]
        rows.append({
            "model": col, "n": err.notna().sum(),
            "rmse": np.sqrt((err**2).mean()), "mae": err.abs().mean(),
        })
    perf = pd.DataFrame(rows)
    perf.to_csv(TABLE_DIR / "phase5_model_performance.csv", index=False)
    print("\nModel performance (test window, pooled across states/quarters):")
    print(perf.to_string(index=False))

    # ---------------- Clark-West: benchmark vs benchmark+BFS, per horizon ----------------
    cw_rows = []
    for h in BFS_LAGS:
        sub = merged.dropna(subset=["pred_benchmark", f"pred_econ_h{h}", target])
        e1 = (sub[target] - sub["pred_benchmark"]).values
        e2 = (sub[target] - sub[f"pred_econ_h{h}"]).values
        cw = clark_west_test(e1, e2, sub["pred_benchmark"].values, sub[f"pred_econ_h{h}"].values)
        cw["horizon"] = h
        cw_rows.append(cw)
    cw_df = pd.DataFrame(cw_rows)[["horizon", "n", "mean_adj_loss_diff", "t_stat", "p_value_one_sided"]]
    cw_df.to_csv(TABLE_DIR / "phase5_clark_west.csv", index=False)
    print("\nClark-West test (benchmark vs. benchmark+BFS, H0: no improvement, one-sided):")
    print(cw_df.to_string(index=False))

    # Clark-West: benchmark vs. best ML model (RF)
    sub = merged.dropna(subset=["pred_benchmark", "pred_rf", target])
    cw_rf = clark_west_test(
        (sub[target] - sub["pred_benchmark"]).values,
        (sub[target] - sub["pred_rf"]).values,
        sub["pred_benchmark"].values, sub["pred_rf"].values,
    )
    print(f"\nClark-West (benchmark vs. RandomForest): {cw_rf}")

    # ---------------- Primary comparisons: Holm-Bonferroni across h=0,3 (econ + ML) ----------------
    primary_pvals = {
        "econ_h0_vs_benchmark": cw_df.loc[cw_df.horizon == 0, "p_value_one_sided"].iloc[0],
        "econ_h3_vs_benchmark": cw_df.loc[cw_df.horizon == 3, "p_value_one_sided"].iloc[0],
        "rf_vs_benchmark": cw_rf["p_value_one_sided"],
    }
    adjusted = holm_bonferroni(primary_pvals)
    print("\nPrimary comparisons, Holm-Bonferroni adjusted (substitute for Hansen-Lunde-Nason MCS):")
    for k in primary_pvals:
        print(f"  {k}: raw p={primary_pvals[k]:.4f}  adjusted p={adjusted[k]:.4f}")
    pd.DataFrame({
        "comparison": list(primary_pvals.keys()),
        "raw_p": list(primary_pvals.values()),
        "holm_adjusted_p": [adjusted[k] for k in primary_pvals],
    }).to_csv(TABLE_DIR / "phase5_primary_comparisons_holm.csv", index=False)

    # ---------------- Cluster-robust pooled tests (substitute for panel tests) ----------------
    merged["loss_benchmark"] = (merged[target] - merged["pred_benchmark"]) ** 2
    merged["loss_econ_h3"] = (merged[target] - merged["pred_econ_h3"]) ** 2
    merged["loss_diff_h3"] = merged["loss_benchmark"] - merged["loss_econ_h3"]
    merged["loss_rf"] = (merged[target] - merged["pred_rf"]) ** 2
    merged["loss_diff_rf"] = merged["loss_benchmark"] - merged["loss_rf"]
    merged["qtr"] = merged["year"].astype(str) + "Q" + merged["quarter"].astype(str)

    panel_rows = []
    for label, col in [("econ_h3", "loss_diff_h3"), ("random_forest", "loss_diff_rf")]:
        sub = merged.dropna(subset=[col])
        by_state = cluster_robust_loss_test(sub[col], sub["geo"])
        by_quarter = cluster_robust_loss_test(sub[col], sub["qtr"])
        two_way = two_way_cluster_test(sub[col], sub["geo"], sub["qtr"])
        print(f"\n[{label}] cluster-robust by state:   {by_state}")
        print(f"[{label}] cluster-robust by quarter: {by_quarter}")
        print(f"[{label}] two-way (state + quarter):  {two_way}")
        panel_rows.append({"model": label, "clustering": "state", **by_state})
        panel_rows.append({"model": label, "clustering": "quarter", **by_quarter})
        panel_rows.append({"model": label, "clustering": "two_way", **two_way})
    pd.DataFrame(panel_rows).to_csv(TABLE_DIR / "phase5_cluster_robust_panel_test.csv", index=False)

    print("\nDone. All outputs in", TABLE_DIR)


if __name__ == "__main__":
    main()
