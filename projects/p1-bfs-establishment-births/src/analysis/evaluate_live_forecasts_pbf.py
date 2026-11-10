"""
Score the pre-registered live forecasts from Census's projected business
formations (pre_analysis_plan_addendum_5.md, item F) against a new BLS BED
release. Written and committed before BLS published 2026Q2.

Usage (after BLS publishes 2026Q2 or 2026Q3):
    python src/acquisition/fetch_bed.py          # downloads into data/raw/bed/<date>/
    python src/analysis/evaluate_live_forecasts_pbf.py data/raw/bed/<date>

Reads only the new raw folder and the two frozen forecast files (this
item's and Addendum 3's, for the all-applications models). Writes
outputs/live_forecasts/evaluation_pbf_<date>.csv.

Actual values are computed within the new release, as in Addendum 3.
"""

import sys
from pathlib import Path

import pandas as pd

from evaluate_live_forecasts import actuals_from_release
from make_live_forecasts import OUT_FILE as A3_FILE
from make_live_forecasts_pbf import OUT_DIR, OUT_FILE, TARGET_QUARTERS

EXCL = "excl_2020_2022"
KEYS = ["geo", "year", "quarter"]

# (hypothesis, model, training) vs (reference model, reference training).
PRIMARY = [
    ("H3", "PBF_h3", "full", "benchmark", "full"),
    ("H3", "PBF_h0", "full", "benchmark", "full"),
]
SECONDARY = (
    [("secondary", f"PBF_h{h}", "full", f"BA_h{h}", "full") for h in [3, 0]]
    + [("secondary", f"PBF_h{h}", EXCL, "benchmark", "full") for h in [3, 0]]
    + [("secondary", f"PBF_h{h}", EXCL, f"PBF_h{h}", "full") for h in [3, 0]]
    + [("secondary", f"PBF_h{h}", EXCL, f"BA_h{h}", EXCL) for h in [3, 0]]
)


def reading(hypothesis: str, diff_pct: float, share: float) -> str:
    """Pre-registered descriptive reading (Addendum 5, item F; mirrors H1).
    Not a significance test."""
    if hypothesis != "H3":
        return ""
    if diff_pct <= 0:
        return "consistent with no gain"
    return "gain" if share > 0.5 else "mixed"


def evaluate(forecasts: pd.DataFrame, actuals: pd.DataFrame) -> pd.DataFrame:
    m = forecasts.merge(actuals, on=KEYS, how="inner")
    m["sq_err"] = (m["actual_births_yoy"] - m["forecast_births_yoy"]) ** 2
    published = sorted(set(zip(m["year"], m["quarter"])))
    scopes = [(f"{y}Q{q}", [(y, q)]) for y, q in published] + [("all published", published)]

    rows = []
    for hyp, model, train, ref, ref_train in PRIMARY + SECONDARY:
        a = m[(m["model"] == model) & (m["training"] == train)][KEYS + ["sq_err"]]
        b = m[(m["model"] == ref) & (m["training"] == ref_train)][KEYS + ["sq_err"]]
        pair = a.merge(b, on=KEYS, suffixes=("_model", "_ref"))
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


def load_forecasts() -> pd.DataFrame:
    """This item's forecasts plus the all-applications models at leads 0 and 3
    from the frozen Addendum 3 file, for the same target quarters."""
    pbf = pd.read_csv(OUT_FILE)
    a3 = pd.read_csv(A3_FILE)
    a3 = a3[a3["model"].isin(["BA_h0", "BA_h3"])
            & a3[["year", "quarter"]].apply(tuple, axis=1).isin(TARGET_QUARTERS)]
    return pd.concat([pbf, a3], ignore_index=True)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw_dir = Path(sys.argv[1]).resolve()
    actuals = actuals_from_release(raw_dir)
    actuals = actuals[actuals[["year", "quarter"]].apply(tuple, axis=1).isin(TARGET_QUARTERS)]
    if actuals.empty:
        print(f"Neither 2026Q2 nor 2026Q3 is published in {raw_dir} yet; nothing to score.")
        return
    result = evaluate(load_forecasts(), actuals)
    out = OUT_DIR / f"evaluation_pbf_{raw_dir.name}.csv"
    result.to_csv(out, index=False)
    primary = result[(result["hypothesis"] == "H3") & (result["scope"] == "all published")]
    print(primary[["hypothesis", "model", "training", "reference", "accuracy_diff_pct_of_reference_mse",
                   "share_states_model_better", "pre_registered_reading"]].round(3).to_string(index=False))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
