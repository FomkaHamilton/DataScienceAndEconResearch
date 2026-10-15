"""
Score the pre-registered live forecasts against a new BLS BED release
(pre_analysis_plan_addendum_3.md). Written and committed before BLS
published any 2026 establishment-birth data.

Usage (after BLS publishes a 2026 quarter):
    python src/acquisition/fetch_bed.py          # downloads into data/raw/bed/<date>/
    python src/analysis/evaluate_live_forecasts.py data/raw/bed/<date>

Reads only the new raw folder; nothing in data/processed is modified.
Writes outputs/live_forecasts/evaluation_<date>.csv.

Actual values are the year-over-year log change in establishment births
computed *within the new release* (2026 quarter vs. the same 2025 quarter
as revised in that release).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cleaning"))

from build_panel import GEO_TO_NAME  # noqa: E402
from clean_bed import load_bed  # noqa: E402
from make_live_forecasts import OUT_DIR, OUT_FILE, TARGET_QUARTERS  # noqa: E402

EXCL = "excl_2020_2022"

# (hypothesis, model, training) vs (reference model, reference training).
PRIMARY = [
    ("H1", "BA_h3", "full", "benchmark", "full"),
    ("H1", "BA_h0", "full", "benchmark", "full"),
    ("H2", "BA_h3", EXCL, "BA_h3", "full"),
    ("H2", "BA_h0", EXCL, "BA_h0", "full"),
]
SECONDARY = (
    [("secondary", f"BA_h{h}", t, "benchmark", "full") for h in [1, 2, 4] for t in ["full", EXCL]]
    + [("secondary", m, t, "benchmark", "full") for m in ["HBA_h0", "HBA_h3"] for t in ["full", EXCL]]
    + [("secondary", f"BA_h{h}", EXCL, "benchmark", "full") for h in [0, 3]]
    + [("secondary", m, EXCL, m, "full") for m in ["HBA_h0", "HBA_h3", "benchmark"]]
)


def actuals_from_release(raw_dir: Path) -> pd.DataFrame:
    bed = load_bed(raw_dir)
    b = bed[(bed["dataclass"] == "Establishment Births")
            & (bed["seasonal_adj"] == "Not seasonally adjusted") & (bed["ratelevel"] == "Level")]
    name_to_geo = {v: k for k, v in GEO_TO_NAME.items() if k not in ("US", "PR")}
    b = b[b["state_name"].isin(name_to_geo)].assign(geo=lambda x: x["state_name"].map(name_to_geo))
    level = b.set_index(["geo", "year", "quarter"])["value"]
    rows = []
    for (y, q) in TARGET_QUARTERS:
        for geo in name_to_geo.values():
            now, before = level.get((geo, y, q)), level.get((geo, y - 1, q))
            if now is not None and before is not None and now > 0 and before > 0 and np.isfinite(now):
                rows.append({"geo": geo, "year": y, "quarter": q,
                             "actual_births_yoy": float(np.log(now) - np.log(before))})
    return pd.DataFrame(rows, columns=["geo", "year", "quarter", "actual_births_yoy"])


def reading(hypothesis: str, diff_pct: float, share: float) -> str:
    """Pre-registered descriptive reading (Addendum 3). Not a significance test."""
    if hypothesis == "H1":
        if diff_pct <= 0:
            return "consistent with the paper (no gain over benchmark)"
        return "against the paper (gain, majority of states)" if share > 0.5 else "mixed"
    if hypothesis == "H2":
        if diff_pct > 0 and share > 0.5:
            return "supports H2 (excluding 2020-22 helps)"
        return "against H2" if diff_pct <= 0 and share <= 0.5 else "mixed"
    return ""


def evaluate(forecasts: pd.DataFrame, actuals: pd.DataFrame) -> pd.DataFrame:
    keys = ["geo", "year", "quarter"]
    m = forecasts.merge(actuals, on=keys, how="inner")
    m["sq_err"] = (m["actual_births_yoy"] - m["forecast_births_yoy"]) ** 2
    published = sorted(set(zip(m["year"], m["quarter"])))
    scopes = [(f"{y}Q{q}", [(y, q)]) for y, q in published] + [("all published", published)]

    rows = []
    for hyp, model, train, ref, ref_train in PRIMARY + SECONDARY:
        a = m[(m["model"] == model) & (m["training"] == train)][keys + ["sq_err"]]
        b = m[(m["model"] == ref) & (m["training"] == ref_train)][keys + ["sq_err"]]
        pair = a.merge(b, on=keys, suffixes=("_model", "_ref"))
        pair["d"] = pair["sq_err_ref"] - pair["sq_err_model"]  # + = model more accurate
        for scope, quarters in scopes:
            s = pair[pair[["year", "quarter"]].apply(tuple, axis=1).isin(quarters)]
            diff_pct = 100 * s["d"].mean() / s["sq_err_ref"].mean()
            share = float((s.groupby("geo")["d"].mean() > 0).mean())
            rows.append({
                "hypothesis": hyp, "model": model, "training": train,
                "reference": ref, "reference_training": ref_train, "scope": scope,
                "n_states": s["geo"].nunique(), "n_quarters": len(quarters),
                "accuracy_diff_pct_of_reference_mse": diff_pct,
                "share_states_model_better": share,
                "pre_registered_reading": reading(hyp, diff_pct, share) if scope == "all published" else "",
            })
    return pd.DataFrame(rows)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw_dir = Path(sys.argv[1]).resolve()
    forecasts = pd.read_csv(OUT_FILE)
    actuals = actuals_from_release(raw_dir)
    if actuals.empty:
        print(f"No 2026 target quarter is published in {raw_dir} yet; nothing to score.")
        return
    result = evaluate(forecasts, actuals)
    out = OUT_DIR / f"evaluation_{raw_dir.name}.csv"
    result.to_csv(out, index=False)
    primary = result[(result["hypothesis"] != "secondary") & (result["scope"] == "all published")]
    print(primary[["hypothesis", "model", "training", "reference", "accuracy_diff_pct_of_reference_mse",
                   "share_states_model_better", "pre_registered_reading"]].round(3).to_string(index=False))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
