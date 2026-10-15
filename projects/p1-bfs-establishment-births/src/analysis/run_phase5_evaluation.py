"""
Phase 5: fit all pre-specified models (pre_analysis_plan.md) with genuine
expanding-window, real-time-consistent re-estimation through the test
window (2023Q1-2025Q4), then evaluate.

Real-time training-label rule: when forecasting target quarter t, a
training row (with its own target quarter t') is used only if
t' <= t - 3, because BED establishment births publish with a roughly
3-quarter lag. This is what makes the expanding window real-time
consistent rather than "fit once on all earlier rows".

DISCLOSED DEVIATIONS FROM THE PAP (per its Sec. 8):
  1. "ARDL" and "bridge equation" collapse to one specification under the
     real-time convention in build_forecast_dataset.py (BFS is treated as
     available for the whole quarter once its ~2-week lag passes, so there
     is no partial-quarter bridging left to do).
  2. The Hansen-Lunde-Nason (2011) Model Confidence Set is not
     implemented: no vetted Python reference implementation was available,
     and a bespoke bootstrap risks an unverifiable bug. Substituted with
     Holm-Bonferroni across the primary comparisons.
  3. The Qu, Timmermann & Zhu (2024) / Akgun et al. (2024) panel tests are
     not implemented (no reference implementation). Substituted with
     cluster-robust tests (by state, by quarter, and two-way) and a wild
     cluster bootstrap by quarter for the few-cluster case.

CORRECTIONS TO THE FIRST PHASE 5 RUN (commit 24013c8). Found while
preparing pre_analysis_plan_addendum_1.md. None let test-window data into
training. Disclosed in research_log.md and literature/phase5_findings.md.
  C1. Machine-learning tuning folds were not time-ordered. The tuning
      data was sorted by state, so TimeSeriesSplit cut it into
      alphabetical blocks of states, each spanning 2006-2022. Now:
      forward-chaining folds over whole quarters, with a gap matching the
      real-time label rule. Affects ML models only.
  C2. The "best ML model" used in the primary comparison and in the
      combination forecast was hard-coded to random forest. It is now
      chosen by development-window cross-validation error, as intended.
  C3. The dependence-robust tests were applied to the unadjusted
      squared-error difference, while the naive test they were compared
      against (Clark-West) used the adjusted difference, so the two
      comparisons differed in two ways at once. Both statistics are now
      reported under every inference method, which isolates the effect
      of clustering.
  Also: the ElasticNet scaler is now fit on each tuning training fold
  only (it was fit on the whole development window).

Usage:
    python run_phase5_evaluation.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
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
ALL_QUARTERS = [1, 2, 3, 4]

TARGET = "births_yoy"
KEYS = ["geo", "year", "quarter"]
BENCHMARK_COLS = [f"births_yoy_lag{l}" for l in OWN_LAGS]
ML_COLS = BENCHMARK_COLS + [f"BA_BA_yoy_lag{l}" for l in BFS_LAGS]

ML_GRIDS = {
    "elasticnet": [
        {"alpha": a, "l1_ratio": r} for a in [0.001, 0.01, 0.05, 0.1] for r in [0.2, 0.5, 0.9]
    ],
    "rf": [
        {"n_estimators": n, "max_depth": d, "min_samples_leaf": 5}
        for n in [200, 400] for d in [3, 5, None]
    ],
    "gb": [
        {"n_estimators": n, "max_depth": d, "learning_rate": lr}
        for n in [100, 200] for d in [2, 3] for lr in [0.03, 0.1]
    ],
}
ECON_MODELS = [f"econ_h{h}" for h in BFS_LAGS]
ML_COMPARISONS = ["elasticnet", "rf", "gb", "best_ml", "combo"]

# Webb six-point weights for the wild cluster bootstrap (recommended when
# the number of clusters is small).
WEBB_WEIGHTS = np.array(
    [-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)]
)


def qdate(year: pd.Series, quarter: pd.Series) -> pd.Series:
    return year * 4 + quarter


def quarter_label(df: pd.DataFrame) -> pd.Series:
    return df["year"].astype(str) + "Q" + df["quarter"].astype(str)


# ---- Design matrix and the expanding-window loop ----

def make_dummies(df: pd.DataFrame, states: list[str], include_quarter: bool = True) -> pd.DataFrame:
    s = pd.Categorical(df["geo"], categories=states)
    sd = pd.get_dummies(s, prefix="st", drop_first=True).astype(float)
    sd.index = df.index
    if not include_quarter:
        return sd
    q = pd.Categorical(df["quarter_target"], categories=ALL_QUARTERS)
    qd = pd.get_dummies(q, prefix="q", drop_first=True).astype(float)
    qd.index = df.index
    return pd.concat([qd, sd], axis=1)


def build_design(
    df: pd.DataFrame, feature_cols: list[str], states: list[str], include_quarter: bool = True
) -> pd.DataFrame:
    X = df[feature_cols].copy()
    dummies = make_dummies(df, states, include_quarter)
    return pd.concat([X, dummies], axis=1)


def expanding_window_predict(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    states: list[str],
    fit_predict_fn,
    include_quarter: bool = True,
    eval_quarters: list[int] | None = None,
) -> pd.DataFrame:
    """Expanding-window, real-time-consistent forecast loop.

    For each target quarter t (ascending), train on all rows whose own
    target quarter is <= t - LABEL_LAG_MIN and predict all rows with
    target quarter == t. fit_predict_fn(X_train, y_train, X_test) ->
    predictions.

    eval_quarters: quarter codes (year*4 + quarter) to forecast; defaults
    to the locked test window. include_quarter=False drops the
    quarter-of-year indicator (seasonally adjusted line).
    """
    df = df.copy()
    df["qd"] = qdate(df["year"], df["quarter"])
    if eval_quarters is None:
        test_quarters = sorted(df.loc[df["in_test_window"], "qd"].unique())
    else:
        test_quarters = sorted(eval_quarters)

    results = []
    for t in test_quarters:
        train_df = df[df["qd"] <= t - LABEL_LAG_MIN].dropna(subset=feature_cols + [target_col])
        test_df = df[df["qd"] == t].dropna(subset=feature_cols)
        if len(train_df) < 50 or len(test_df) == 0:
            continue

        X_train = build_design(train_df, feature_cols, states, include_quarter)
        X_test = build_design(test_df, feature_cols, states, include_quarter)
        X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

        preds = fit_predict_fn(X_train.values, train_df[target_col].values, X_test.values)

        out = test_df[["geo", "state_name", "year", "quarter", target_col]].copy()
        out["prediction"] = preds
        out["train_n"] = len(train_df)
        results.append(out)

    return pd.concat(results, ignore_index=True)


# ---- Models ----

def fit_predict_ols(X_train, y_train, X_test):
    X_train_c = sm.add_constant(X_train, has_constant="add")
    X_test_c = sm.add_constant(X_test, has_constant="add")
    return sm.OLS(y_train, X_train_c).fit().predict(X_test_c)


def _fit_predict_ml(name: str, params: dict, X_train, y_train, X_test):
    if name == "elasticnet":
        scaler = StandardScaler().fit(X_train)
        X_train, X_test = scaler.transform(X_train), scaler.transform(X_test)
        model = ElasticNet(max_iter=5000, **params)
    elif name == "rf":
        model = RandomForestRegressor(random_state=0, n_jobs=-1, **params)
    elif name == "gb":
        model = GradientBoostingRegressor(random_state=0, **params)
    else:
        raise ValueError(name)
    model.fit(X_train, y_train)
    return model.predict(X_test)


def fit_predict_ml(name: str, params: dict):
    return lambda X_train, y_train, X_test: _fit_predict_ml(name, params, X_train, y_train, X_test)


def time_ordered_folds(df: pd.DataFrame, n_splits: int = 4):
    """Forward-chaining CV folds over whole quarters (not rows). Each
    validation fold lies after its training fold, separated by a gap so
    the newest training label is LABEL_LAG_MIN quarters older than the
    first validation target -- the same rule the forecast loop uses.
    Yields positional index arrays into df."""
    qd = qdate(df["year"], df["quarter"]).to_numpy()
    quarters = np.unique(qd)
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=LABEL_LAG_MIN - 1)
    for tr_q, va_q in tscv.split(quarters):
        yield (
            np.flatnonzero(np.isin(qd, quarters[tr_q])),
            np.flatnonzero(np.isin(qd, quarters[va_q])),
        )


def tune_ml(
    dev_df: pd.DataFrame, states: list[str], target_col: str = TARGET, include_quarter: bool = True
) -> dict:
    """Pick each ML model's settings by time-ordered CV on the development
    window only. Returns {name: {"params": ..., "cv_mse": ...}}."""
    d = dev_df.dropna(subset=ML_COLS + [target_col])
    X = build_design(d, ML_COLS, states, include_quarter).to_numpy()
    y = d[target_col].to_numpy()
    folds = list(time_ordered_folds(d))

    tuning = {}
    for name, grid in ML_GRIDS.items():
        best_params, best_mse = None, np.inf
        for params in grid:
            mse = np.mean([
                np.mean((_fit_predict_ml(name, params, X[tr], y[tr], X[va]) - y[va]) ** 2)
                for tr, va in folds
            ])
            if mse < best_mse:
                best_params, best_mse = params, float(mse)
        tuning[name] = {"params": best_params, "cv_mse": best_mse}
    return tuning


def run_models(
    df: pd.DataFrame,
    states: list[str],
    target_col: str = TARGET,
    include_quarter: bool = True,
    ml_tuning: dict | None = None,
    eval_quarters: list[int] | None = None,
    include_ml: bool = True,
    verbose: bool = True,
) -> tuple[pd.DataFrame, dict | None]:
    """Benchmark, benchmark + BFS lag h (h = 0-4), and (optionally) the ML
    models, all through the same expanding window. ML settings are tuned
    on df's development window unless ml_tuning is supplied. Returns the
    merged predictions and the ML tuning used."""
    def log(msg):
        if verbose:
            print(msg, flush=True)

    def predict(cols, fn, name):
        p = expanding_window_predict(
            df, cols, target_col, states, fn, include_quarter, eval_quarters
        )
        return p.rename(columns={"prediction": f"pred_{name}"})

    log("  benchmark (own lags 3-5)")
    merged = predict(BENCHMARK_COLS, fit_predict_ols, "benchmark")[
        ["geo", "state_name", "year", "quarter", target_col, "pred_benchmark"]
    ]
    for h in BFS_LAGS:
        log(f"  benchmark + BA_BA_yoy_lag{h}")
        p = predict(BENCHMARK_COLS + [f"BA_BA_yoy_lag{h}"], fit_predict_ols, f"econ_h{h}")
        merged = merged.merge(p[KEYS + [f"pred_econ_h{h}"]], on=KEYS, how="left")

    if include_ml:
        if ml_tuning is None:
            log("  tuning ML models (development window, time-ordered folds)")
            ml_tuning = tune_ml(df[~df["in_test_window"]], states, target_col, include_quarter)
        for name, info in ml_tuning.items():
            log(f"  {name}: {info['params']} (CV MSE {info['cv_mse']:.5f})")
            p = predict(ML_COLS, fit_predict_ml(name, info["params"]), name)
            merged = merged.merge(p[KEYS + [f"pred_{name}"]], on=KEYS, how="left")
        best = min(ml_tuning, key=lambda k: ml_tuning[k]["cv_mse"])
        log(f"  best ML by development-window CV: {best}")
        merged["pred_best_ml"] = merged[f"pred_{best}"]
        merged["pred_combo"] = (merged["pred_econ_h3"] + merged["pred_best_ml"]) / 2

    return merged, ml_tuning


def tuning_table(ml_tuning: dict) -> pd.DataFrame:
    best = min(ml_tuning, key=lambda k: ml_tuning[k]["cv_mse"])
    return pd.DataFrame([
        {"model": k, "params": json.dumps(v["params"]), "cv_mse": v["cv_mse"], "selected_as_best": k == best}
        for k, v in ml_tuning.items()
    ])


def load_tuning(path: Path) -> dict:
    t = pd.read_csv(path)
    return {r.model: {"params": json.loads(r.params), "cv_mse": r.cv_mse} for r in t.itertuples()}


# ---- Inference ----

def cluster_robust_loss_test(loss_diff: pd.Series, cluster: pd.Series) -> dict:
    """Mean of a loss-difference series with one-way cluster-robust SE."""
    X = np.ones((len(loss_diff), 1))
    model = sm.OLS(np.asarray(loss_diff, float), X).fit(
        cov_type="cluster", cov_kwds={"groups": np.asarray(cluster)}
    )
    return {
        "n": len(loss_diff),
        "n_clusters": pd.Series(cluster).nunique(),
        "mean_loss_diff": float(model.params[0]),
        "se": float(model.bse[0]),
        "t_stat": float(model.tvalues[0]),
    }


def two_way_cluster_test(loss_diff: pd.Series, cluster1: pd.Series, cluster2: pd.Series) -> dict:
    """Cameron, Gelbach & Miller two-way cluster-robust SE for a mean:
    Var = Var_cluster1 + Var_cluster2 - Var_HC1. Here cluster1 = state
    (serial correlation within a state) and cluster2 = quarter (common
    shocks across states in the same quarter)."""
    X = np.ones((len(loss_diff), 1))
    y = np.asarray(loss_diff, float)
    v1 = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": np.asarray(cluster1)}).cov_params()
    v2 = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": np.asarray(cluster2)}).cov_params()
    v0 = sm.OLS(y, X).fit(cov_type="HC1").cov_params()
    var_2way = max(np.asarray(v1)[0, 0] + np.asarray(v2)[0, 0] - np.asarray(v0)[0, 0], 0.0)
    se = float(np.sqrt(var_2way))
    mean_diff = float(y.mean())
    return {
        "n": len(y),
        "n_cluster1_state": pd.Series(cluster1).nunique(),
        "n_cluster2_quarter": pd.Series(cluster2).nunique(),
        "mean_loss_diff": mean_diff,
        "se": se,
        "t_stat": mean_diff / se if se > 0 else np.nan,
    }


def _cr1_se(resid_cluster_sums: np.ndarray, n: int, n_clusters: int) -> np.ndarray:
    """CR1 cluster-robust SE of a mean, from per-cluster residual sums.
    Matches statsmodels' cov_type="cluster" for an intercept-only model."""
    return np.sqrt(n_clusters / (n_clusters - 1) * np.sum(resid_cluster_sums**2, axis=-1)) / n


def wild_cluster_bootstrap(
    d: np.ndarray, cluster: np.ndarray, alternative: str, B: int = 9999, seed: int = 0
) -> dict:
    """Wild cluster bootstrap for H0: mean(d) = 0, null imposed, Webb
    weights, one-way clustering. Returns the bootstrap p-value and a 95%
    confidence interval built from the bootstrap critical value
    (an approximation to inverting the bootstrap test)."""
    d = np.asarray(d, float)
    codes, uniques = pd.factorize(pd.Series(cluster))
    G, n = len(uniques), len(d)
    T = np.bincount(codes, weights=d, minlength=G)  # cluster sums of d
    n_g = np.bincount(codes, minlength=G)

    m = d.mean()
    se = _cr1_se(T - n_g * m, n, G)
    t_obs = m / se

    rng = np.random.default_rng(seed)
    W = rng.choice(WEBB_WEIGHTS, size=(B, G))
    TW = W * T  # cluster sums of y* = d_i * w_g (restricted residuals = d under H0)
    m_star = TW.sum(axis=1) / n
    t_star = m_star / _cr1_se(TW - n_g * m_star[:, None], n, G)

    if alternative == "greater":
        p = float(np.mean(t_star >= t_obs))
    else:
        p = float(np.mean(np.abs(t_star) >= abs(t_obs)))
    crit = float(np.quantile(np.abs(t_star), 0.95))
    return {"t": t_obs, "se": se, "p": p, "crit_95": crit, "ci_low": m - crit * se, "ci_high": m + crit * se}


def loss_difference(df: pd.DataFrame, target_col: str, model_col: str, kind: str) -> pd.Series:
    """Benchmark loss minus model loss (positive = model better).
    kind="mse": plain squared-error difference (actual accuracy).
    kind="cw": Clark & West (2007) adjusted difference for nested models,
    which corrects the larger model's penalty from estimating extra
    parameters."""
    e1 = df[target_col] - df["pred_benchmark"]
    e2 = df[target_col] - df[model_col]
    if kind == "mse":
        return e1**2 - e2**2
    if kind == "cw":
        return e1**2 - (e2**2 - (df["pred_benchmark"] - df[model_col]) ** 2)
    raise ValueError(kind)


def compare_to_benchmark(
    merged: pd.DataFrame, target_col: str, model: str, kind: str, B: int = 9999
) -> dict:
    """Every inference method for one model-vs-benchmark comparison.
    Clark-West ("cw") is tested one-sided (H1: model better); the plain
    accuracy difference ("mse") is tested two-sided."""
    col = f"pred_{model}"
    sub = merged.dropna(subset=[target_col, "pred_benchmark", col])
    d = loss_difference(sub, target_col, col, kind)
    qtr = quarter_label(sub)
    alt = "greater" if kind == "cw" else "two-sided"

    def p_of(t):
        return 1 - norm.cdf(t) if alt == "greater" else 2 * (1 - norm.cdf(abs(t)))

    naive_t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
    by_state = cluster_robust_loss_test(d, sub["geo"])
    by_qtr = cluster_robust_loss_test(d, qtr)
    two_way = two_way_cluster_test(d, sub["geo"], qtr)
    wcb = wild_cluster_bootstrap(d.to_numpy(), qtr.to_numpy(), alt, B=B)
    bench_mse = float(((sub[target_col] - sub["pred_benchmark"]) ** 2).mean())

    row = {
        "comparison": model,
        "statistic": kind,
        "n": len(d),
        "n_quarters": qtr.nunique(),
        "benchmark_mse": bench_mse,
        "mean_diff": float(d.mean()),
        "mean_diff_pct_of_benchmark_mse": 100 * d.mean() / bench_mse,
        "naive_t": naive_t,
        "naive_p": p_of(naive_t),
        "state_cluster_p": p_of(by_state["t_stat"]),
        "quarter_cluster_p": p_of(by_qtr["t_stat"]),
        "two_way_se": two_way["se"],
        "two_way_t": two_way["t_stat"],
        "two_way_p": p_of(two_way["t_stat"]),
        "wcb_quarter_p": wcb["p"],
    }
    if kind == "mse":
        # Detectable-effect quantities (Addendum 1, Analysis C), as % of
        # the benchmark's MSE. Positive = model more accurate.
        pct = 100 / bench_mse
        row.update({
            "ci95_low_pct": (d.mean() - 1.96 * two_way["se"]) * pct,
            "ci95_high_pct": (d.mean() + 1.96 * two_way["se"]) * pct,
            "mde80_pct": 2.80 * two_way["se"] * pct,
            "wcb_ci95_low_pct": wcb["ci_low"] * pct,
            "wcb_ci95_high_pct": wcb["ci_high"] * pct,
        })
    return row


def comparison_table(merged: pd.DataFrame, target_col: str = TARGET, models: list[str] | None = None) -> pd.DataFrame:
    if models is None:
        models = [m for m in ECON_MODELS + ML_COMPARISONS if f"pred_{m}" in merged.columns]
    return pd.DataFrame([
        compare_to_benchmark(merged, target_col, m, kind) for m in models for kind in ["cw", "mse"]
    ])


def performance_table(merged: pd.DataFrame, target_col: str = TARGET) -> pd.DataFrame:
    rows = []
    for col in [c for c in merged.columns if c.startswith("pred_")]:
        err = merged[target_col] - merged[col]
        rows.append({
            "model": col.removeprefix("pred_"), "n": int(err.notna().sum()),
            "rmse": float(np.sqrt((err**2).mean())), "mae": float(err.abs().mean()),
        })
    return pd.DataFrame(rows)


def holm_bonferroni(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running_max = {}, 0.0
    for i, (name, p) in enumerate(items):
        running_max = max(running_max, min((m - i) * p, 1.0))
        adjusted[name] = running_max
    return adjusted


def primary_holm(comparisons: pd.DataFrame) -> pd.DataFrame:
    """PAP Sec. 7 primary comparisons (BFS at h=0 and h=3; best ML model),
    Clark-West statistic, Holm-adjusted under each inference method."""
    primary = ["econ_h0", "econ_h3", "best_ml"]
    cw = comparisons[(comparisons["statistic"] == "cw") & comparisons["comparison"].isin(primary)]
    out = cw[["comparison"]].copy()
    for method in ["naive_p", "two_way_p", "wcb_quarter_p"]:
        raw = dict(zip(cw["comparison"], cw[method]))
        adj = holm_bonferroni(raw)
        out[method] = out["comparison"].map(raw)
        out[f"{method}_holm"] = out["comparison"].map(adj)
    return out


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    fc = pd.read_csv(PROCESSED_DIR / "forecast_dataset.csv")
    states = sorted(fc["geo"].unique())
    nsa = fc[fc["seasonal_adj"] == "Not seasonally adjusted"].copy()
    print(f"States: {len(states)}  Development rows (NSA): {(~nsa['in_test_window']).sum():,}", flush=True)

    merged, tuning = run_models(nsa, states)
    merged.to_csv(TABLE_DIR / "phase5_predictions.csv", index=False)
    tuning_table(tuning).to_csv(TABLE_DIR / "phase5_ml_tuning.csv", index=False)

    perf = performance_table(merged)
    perf.to_csv(TABLE_DIR / "phase5_model_performance.csv", index=False)
    print("\nAccuracy over the test window:")
    print(perf.to_string(index=False))

    comp = comparison_table(merged)
    comp.to_csv(TABLE_DIR / "phase5_comparisons.csv", index=False)
    cols = ["comparison", "statistic", "mean_diff_pct_of_benchmark_mse", "naive_p",
            "state_cluster_p", "quarter_cluster_p", "two_way_p", "wcb_quarter_p"]
    print("\nEach model vs. the benchmark (p-values by inference method):")
    print(comp[cols].round(4).to_string(index=False))

    holm = primary_holm(comp)
    holm.to_csv(TABLE_DIR / "phase5_primary_comparisons_holm.csv", index=False)
    print("\nPrimary comparisons, Holm-adjusted:")
    print(holm.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
