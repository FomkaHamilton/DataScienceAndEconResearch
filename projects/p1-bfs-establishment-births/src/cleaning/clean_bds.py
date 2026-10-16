"""
Clean BDS state x firm-age data into a state-year "new-firm share of
establishment entry" series, for RQ4.

new_firm_share = estabs_entry[firm age 0] / sum(estabs_entry, all firm ages)

This measures, per state-year, what share of new establishments belong to
new firms (in their first year of existence) rather than to existing
firms opening another location. Decker & Haltiwanger (2022) find ~36% of
establishment births nationally come from existing firms. RQ4 asks
whether BFS's predictive value for BED establishment births is larger in
states where the new-firm share is higher, since business applications
should track new firms more closely than an existing firm's decision to
open another location.

Note: BDS is annual, with a reference year running roughly March to
March. The share is an annual covariate for RQ4, not part of the core
quarterly forecasting panel (BFS/BED).

Output: data/processed/bds_state_new_firm_share.csv

Usage:
    python clean_bds.py [path_to_raw_csv]
"""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_BDS_DIR = PROJECT_ROOT / "data" / "raw" / "bds"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

NEW_FIRM_FAGE = "a) 0"
# The denominator includes every firm-age category, including "Left
# Censored" (firms that already existed when BDS begins, so their exact
# age is unknown). These are old firms opening new locations, which is
# exactly the "not a new firm" case. An earlier version excluded them,
# which overstated the new-firm share (2010-19 mean 0.69 instead of 0.61);
# corrected 2026-10-15, before this file was used in any analysis.
EXCLUDE_FAGE: set[str] = set()


def _latest_raw_file() -> Path:
    candidates = sorted(RAW_BDS_DIR.glob("bds2023_st_fa_*.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"No bds2023_st_fa_*.csv found under {RAW_BDS_DIR}. Run fetch_bds.py first."
        )
    return candidates[-1]


def clean(raw_path: str | None = None) -> Path:
    path = Path(raw_path) if raw_path else _latest_raw_file()
    print(f"Reading {path}")

    df = pd.read_csv(path, dtype={"st": str, "fage": str})
    df["estabs_entry"] = pd.to_numeric(df["estabs_entry"], errors="coerce")

    denom = (
        df[~df["fage"].isin(EXCLUDE_FAGE)]
        .groupby(["year", "st"])["estabs_entry"]
        .sum()
        .rename("estabs_entry_total")
    )
    numer = (
        df[df["fage"] == NEW_FIRM_FAGE]
        .groupby(["year", "st"])["estabs_entry"]
        .sum()
        .rename("estabs_entry_new_firms")
    )

    out = pd.concat([numer, denom], axis=1).reset_index()
    out["new_firm_share"] = out["estabs_entry_new_firms"] / out["estabs_entry_total"]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "bds_state_new_firm_share.csv"
    out.sort_values(["st", "year"]).to_csv(out_path, index=False)
    print(f"Wrote {len(out):,} rows to {out_path}")
    print(out["new_firm_share"].describe())
    return out_path


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    clean(arg)
